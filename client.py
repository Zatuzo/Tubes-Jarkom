import socket
import time
import argparse
import datetime
import statistics
import threading
import os
import csv

# ============================================================
# KONFIGURASI
# ============================================================
PROXY_HOST = '127.0.0.1'   # Ganti dengan IP Proxy jika beda perangkat
PROXY_PORT = 8080

WEBSERVER_HOST = '127.0.0.1'  # Untuk UDP QoS (langsung ke Web Server)
UDP_PORT = 9000

BUFFER_SIZE = 65535
UDP_COUNT   = 10            # Jumlah paket UDP yang dikirim
UDP_TIMEOUT = 1.0           # Timeout per paket (detik)

# ============================================================
# HELPER: LOG
# ============================================================
def log(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

# ============================================================
# MODE TCP — HTTP via Proxy
# ============================================================
def mode_tcp(path='/index.html'):
    """Mengirim HTTP GET request ke Proxy dan menampilkan response."""
    log(f"[TCP] Menghubungi Proxy {PROXY_HOST}:{PROXY_PORT}")
    log(f"[TCP] Meminta resource: {path}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((PROXY_HOST, PROXY_PORT))

        # Bangun HTTP GET request
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {PROXY_HOST}:{PROXY_PORT}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )

        start = time.time()
        sock.sendall(request.encode('utf-8'))

        # Terima response
        response = b""
        while True:
            chunk = sock.recv(BUFFER_SIZE)
            if not chunk:
                break
            response += chunk

        elapsed = (time.time() - start) * 1000  # ms

        # Pisahkan header dan body
        if b"\r\n\r\n" in response:
            header_part, body_part = response.split(b"\r\n\r\n", 1)
            header_text = header_part.decode('utf-8', errors='replace')
        else:
            header_text = response.decode('utf-8', errors='replace')
            body_part = b""

        print("\n" + "=" * 55)
        print("  RESPONSE HEADER")
        print("=" * 55)
        print(header_text)
        print("=" * 55)
        print("  RESPONSE BODY (HTML)")
        print("=" * 55)
        print(body_part.decode('utf-8', errors='replace')[:2000])  # Tampilkan max 2000 char
        print("=" * 55)
        log(f"[TCP] Response diterima | {len(response)} bytes | {elapsed:.2f} ms")

    except socket.timeout:
        log("[TCP] ERROR: Koneksi timeout saat menghubungi Proxy.")
    except ConnectionRefusedError:
        log(f"[TCP] ERROR: Proxy tidak dapat dihubungi di {PROXY_HOST}:{PROXY_PORT}")
    except Exception as e:
        log(f"[TCP] ERROR: {e}")
    finally:
        sock.close()

# ============================================================
# MODE UDP — QoS Ping ke Web Server
# ============================================================
def mode_udp(count=UDP_COUNT, target_host=WEBSERVER_HOST, target_port=UDP_PORT):
    """Mengirim paket UDP ping ke Web Server dan mengukur QoS."""
    log(f"[UDP] Target: {target_host}:{target_port}")
    log(f"[UDP] Mengirim {count} paket UDP...")
    print("=" * 55)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(UDP_TIMEOUT)

    rtt_list    = []
    sent        = 0
    received    = 0
    lost        = 0
    total_bytes = 0

    start_session = time.time()

    for seq in range(1, count + 1):
        timestamp_send = time.time()
        payload = f"Ping {seq} {timestamp_send:.6f}"
        data    = payload.encode('utf-8')

        try:
            sock.sendto(data, (target_host, target_port))
            sent += 1

            echo_data, server_addr = sock.recvfrom(BUFFER_SIZE)
            timestamp_recv = time.time()

            rtt_ms = (timestamp_recv - timestamp_send) * 1000
            rtt_list.append(rtt_ms)
            received += 1
            total_bytes += len(echo_data)

            echo_payload = echo_data.decode('utf-8', errors='replace').strip()
            print(f"  [{seq:02d}] RTT: {rtt_ms:.3f} ms | Echo: '{echo_payload}'")

        except socket.timeout:
            lost += 1
            print(f"  [{seq:02d}] Request timed out")

        except Exception as e:
            lost += 1
            print(f"  [{seq:02d}] Error: {e}")

        time.sleep(0.1)  # Jeda kecil antar paket

    end_session = time.time()
    duration    = end_session - start_session

    # -------------------------------------------------------
    # STATISTIK AKHIR
    # -------------------------------------------------------
    print("\n" + "=" * 55)
    print("  STATISTIK QoS UDP")
    print("=" * 55)
    print(f"  Target          : {target_host}:{target_port}")
    print(f"  Paket Terkirim  : {sent}")
    print(f"  Paket Diterima  : {received}")
    print(f"  Paket Hilang    : {lost}")

    packet_loss = (lost / sent * 100) if sent > 0 else 0
    print(f"  Packet Loss     : {packet_loss:.1f}%")

    if rtt_list:
        rtt_min = min(rtt_list)
        rtt_avg = sum(rtt_list) / len(rtt_list)
        rtt_max = max(rtt_list)
        print(f"  RTT Min         : {rtt_min:.3f} ms")
        print(f"  RTT Avg         : {rtt_avg:.3f} ms")
        print(f"  RTT Max         : {rtt_max:.3f} ms")

        # Jitter = standar deviasi selisih RTT berturut-turut
        if len(rtt_list) >= 2:
            rtt_diffs = [abs(rtt_list[i] - rtt_list[i-1]) for i in range(1, len(rtt_list))]
            jitter = statistics.stdev(rtt_diffs) if len(rtt_diffs) > 1 else rtt_diffs[0]
            print(f"  Jitter          : {jitter:.3f} ms")
        else:
            print(f"  Jitter          : N/A")

        # Throughput (kbps)
        if duration > 0:
            throughput_kbps = (total_bytes * 8) / duration / 1000
            print(f"  Throughput      : {throughput_kbps:.2f} kbps")
    else:
        print("  Tidak ada paket yang berhasil diterima.")

    print("=" * 55)
    sock.close()
    
    # IMPORT CSV:
    nama_file = "hasil_qos_jarkom.csv"
    file_baru = not os.path.exists(nama_file)
    
    with open(nama_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file_baru:
            writer.writerow(['Timestamp', 'Paket Dikirim', 'Paket Diterima', 'Packet Loss (%)', 'Min RTT (ms)', 'Avg RTT (ms)', 'Max RTT (ms)', 'Jitter (ms)'])
        
        timestamp_sekarang = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Mengambil nilai RTT dari variabel asli (rtt_min, rtt_avg, rtt_max) jika rtt_list tidak kosong
        v_min = rtt_min if rtt_list else 0
        v_avg = rtt_avg if rtt_list else 0
        v_max = rtt_max if rtt_list else 0
        
        # Mengambil nilai jitter jika variabelnya sudah terbuat di atas
        v_jitter = jitter if 'jitter' in locals() else 0
        
        writer.writerow([
            timestamp_sekarang, 
            count, 
            received,  # Menggunakan variabel 'received' dari kode Anda
            packet_loss, 
            v_min,     # Menggunakan variabel rtt_min yang disesuaikan
            v_avg,     # Menggunakan variabel rtt_avg yang disesuaikan
            v_max,     # Menggunakan variabel rtt_max yang disesuaikan
            v_jitter   # Menggunakan variabel jitter yang disesuaikan
        ])
    print(f"\n[CLIENT] Hasil QoS berhasil diekspor ke {nama_file} (Bisa dibuka di Excel!)")

# ============================================================
# MODE MULTI-CLIENT SIMULASI (jalankan beberapa request sekaligus)
# ============================================================
def mode_multi(paths=None, count=5):
    """Simulasi multi-client: kirim beberapa request HTTP secara bersamaan."""
    if paths is None:
        paths = ["/HTML/index.html", "/HTML/osi.html", "/HTML/tcpip.html", "/HTML/qos.html", "/HTML/implementation.html"]

    log(f"[MULTI] Menjalankan {count} request HTTP simultan...")
    threads = []
    results = {}

    def worker(idx, path):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((PROXY_HOST, PROXY_PORT))

            request = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {PROXY_HOST}:{PROXY_PORT}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            )

            start = time.time()
            sock.sendall(request.encode('utf-8'))

            response = b""
            while True:
                chunk = sock.recv(BUFFER_SIZE)
                if not chunk:
                    break
                response += chunk

            elapsed = (time.time() - start) * 1000

            # Ambil status line
            status_line = "UNKNOWN"
            if response:
                status_line = response.decode('utf-8', errors='replace').split('\r\n')[0]

            results[idx] = {
                'path': path,
                'status': status_line,
                'size': len(response),
                'elapsed_ms': elapsed
            }
            sock.close()

        except Exception as e:
            results[idx] = {'path': path, 'status': f'ERROR: {e}', 'size': 0, 'elapsed_ms': 0}

    # Buat dan jalankan semua thread hampir bersamaan
    for i in range(count):
        path = paths[i % len(paths)]
        t = threading.Thread(target=worker, args=(i+1, path), name=f"MultiClient-{i+1}")
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("\n" + "=" * 55)
    print("  HASIL SIMULASI MULTI-CLIENT")
    print("=" * 55)
    for idx in sorted(results.keys()):
        r = results[idx]
        print(f"  Client {idx:02d} | {r['path']:15s} | {r['status'][:30]:30s} | {r['size']} bytes | {r['elapsed_ms']:.2f} ms")
    print("=" * 55)

# ============================================================
# ARGUMENT PARSER & MAIN
# ============================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client - Tugas Besar Jarkom')
    parser.add_argument(
        '-mode', '--mode',
        choices=['tcp', 'udp', 'multi'],
        default='tcp',
        help='Mode operasi: tcp (HTTP via Proxy) | udp (QoS Ping) | multi (multi-client simulasi)'
    )
    parser.add_argument(
        '-path', '--path',
        default='/index.html',
        help='Path resource untuk mode TCP (default: /index.html)'
    )
    parser.add_argument(
        '-count', '--count',
        type=int,
        default=10,
        help='Jumlah paket UDP (mode udp) atau jumlah client (mode multi). Default: 10'
    )
    parser.add_argument(
        '-proxy', '--proxy',
        default=PROXY_HOST,
        help=f'IP Proxy Server (default: {PROXY_HOST})'
    )
    parser.add_argument(
        '-server', '--server',
        default=WEBSERVER_HOST,
        help=f'IP Web Server untuk UDP (default: {WEBSERVER_HOST})'
    )

    args = parser.parse_args()

    # Override host dari argumen
    PROXY_HOST      = args.proxy
    WEBSERVER_HOST  = args.server

    print("\n" + "=" * 55)
    print("  Client - Tugas Besar Jaringan Komputer")
    print("  Laboratorium Praktikum Informatika - Tel-U")
    print("=" * 55)
    print(f"  Mode           : {args.mode.upper()}")
    print(f"  Proxy          : {PROXY_HOST}:{PROXY_PORT}")
    print(f"  Web Server UDP : {WEBSERVER_HOST}:{UDP_PORT}")
    print("=" * 55 + "\n")

    if args.mode == 'tcp':
        mode_tcp(path=args.path)

    elif args.mode == 'udp':
        mode_udp(count=args.count, target_host=WEBSERVER_HOST, target_port=UDP_PORT)

    elif args.mode == 'multi':
        mode_multi(count=args.count)
