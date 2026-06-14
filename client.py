import socket
import time
import os

# ============================================================
# KONFIGURASI - SESUAIKAN IP INI SEBELUM DIJALANKAN
# ============================================================
PROXY_IP   = "127.0.0.1"   # IP Laptop B (Proxy Server)
PROXY_PORT = 8000

WEBSERVER_IP   = "127.0.0.1"  # IP Laptop A (Web Server)
WEBSERVER_PORT = 9000

BUFFER_SIZE = 4096
ENCODING    = "utf-8"
UDP_TIMEOUT = 2.0           # detik, sesuai kontrak

FILE_YANG_DIMINTA = "index.html"   # file yang akan di-request ke proxy
OUTPUT_DIR        = "received_files"  # folder penyimpanan file yang diterima
UDP_PING_COUNT    = 10              # jumlah paket ping
# ============================================================


def buat_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[INFO] Folder '{OUTPUT_DIR}' dibuat.")


# ------------------------------------------------------------
# TCP CLIENT - Request file ke Proxy Server
# ------------------------------------------------------------
def request_file_via_proxy(nama_file: str) -> bool:
    http_request = f"GET /{nama_file} HTTP/1.1\r\nHost: {PROXY_IP}\r\n\r\n"

    print("\n" + "="*55)
    print("  [TCP] MEMINTA FILE KE PROXY SERVER")
    print("="*55)
    print(f"  Target  : {PROXY_IP}:{PROXY_PORT}")
    print(f"  File    : /{nama_file}")
    print(f"  Request : {repr(http_request)}")
    print("-"*55)

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        tcp_socket.connect((PROXY_IP, PROXY_PORT))
        print(f"[OK] Terhubung ke Proxy {PROXY_IP}:{PROXY_PORT}")

        # Kirim request
        tcp_socket.sendall(http_request.encode(ENCODING))
        print("[OK] Request terkirim.")

        # Terima seluruh response
        response_bytes = b""
        while True:
            chunk = tcp_socket.recv(BUFFER_SIZE)
            if not chunk:
                break
            response_bytes += chunk

        if not response_bytes:
            print("[ERROR] Response kosong dari Proxy.")
            return False

        response_str = response_bytes.decode(ENCODING, errors="replace")
        print(f"[INFO] Total data diterima: {len(response_bytes)} bytes")

        # ── Parsing HTTP Response secara manual ──────────────
        # Format yang disepakati: "HTTP/1.1 200 OK\r\n\r\n<body>"
        # Pemisah header dan body adalah "\r\n\r\n"
        if "\r\n\r\n" in response_str:
            header_part, body = response_str.split("\r\n\r\n", 1)
        else:
            header_part = response_str
            body = ""

        # Ambil status line (baris pertama header)
        status_line = header_part.split("\r\n")[0]
        print(f"[INFO] Status dari Proxy : {status_line}")

        if "200 OK" in status_line:
            # Simpan file ke disk
            buat_output_dir()
            output_path = os.path.join(OUTPUT_DIR, nama_file)
            with open(output_path, "w", encoding=ENCODING) as f:
                f.write(body)
            print(f"[OK] File berhasil disimpan ke '{output_path}'")
            print(f"[INFO] Ukuran konten  : {len(body)} karakter")
            return True

        elif "404 Not Found" in status_line:
            print(f"[GAGAL] File '{nama_file}' tidak ditemukan di server.")
            return False

        else:
            print(f"[GAGAL] Response tidak dikenali: {status_line}")
            return False

    except ConnectionRefusedError:
        print(f"[ERROR] Koneksi ditolak. Pastikan Proxy berjalan di {PROXY_IP}:{PROXY_PORT}")
        return False
    except Exception as e:
        print(f"[ERROR] Exception TCP: {e}")
        return False
    finally:
        tcp_socket.close()
        print("[INFO] Koneksi TCP ditutup.")


# ------------------------------------------------------------
# UDP PINGER - QoS Test langsung ke Web Server
# ------------------------------------------------------------
def udp_pinger(jumlah_paket: int = UDP_PING_COUNT) -> dict:
    print("\n" + "="*55)
    print("  [UDP] QOS TEST - UDP PINGER KE WEB SERVER")
    print("="*55)
    print(f"  Target  : {WEBSERVER_IP}:{WEBSERVER_PORT}")
    print(f"  Paket   : {jumlah_paket}")
    print(f"  Timeout : {UDP_TIMEOUT} detik/paket")
    print("-"*55)

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.settimeout(UDP_TIMEOUT)   # sesuai kontrak

    rtt_list    = []   # daftar RTT dalam milidetik untuk paket yang diterima
    paket_hilang = 0

    for seq in range(1, jumlah_paket + 1):
        # Payload: "PING <seq> <timestamp>"
        timestamp_kirim = time.time()
        payload = f"PING {seq} {timestamp_kirim}".encode(ENCODING)

        try:
            # Kirim paket UDP
            udp_socket.sendto(payload, (WEBSERVER_IP, WEBSERVER_PORT))

            # Tunggu echo dari server
            data_kembali, _ = udp_socket.recvfrom(BUFFER_SIZE)
            timestamp_terima = time.time()

            # Hitung RTT dalam milidetik
            rtt_ms = (timestamp_terima - timestamp_kirim) * 1000
            rtt_list.append(rtt_ms)

            pesan_kembali = data_kembali.decode(ENCODING, errors="replace")
            print(f"  [{seq:>2}] Diterima dari {WEBSERVER_IP} | RTT = {rtt_ms:.3f} ms | Echo: {pesan_kembali[:40]}")

        except socket.timeout:
            paket_hilang += 1
            print(f"  [{seq:>2}] TIMEOUT - Paket hilang (Request timeout)")

        except Exception as e:
            paket_hilang += 1
            print(f"  [{seq:>2}] ERROR   - {e}")

    udp_socket.close()

    # ── Hitung statistik ─────────────────────────────────────
    paket_terkirim = jumlah_paket
    paket_diterima = len(rtt_list)
    paket_hilang   = paket_terkirim - paket_diterima
    packet_loss_persen = (paket_hilang / paket_terkirim) * 100

    hasil = {
        "paket_terkirim"     : paket_terkirim,
        "paket_diterima"     : paket_diterima,
        "paket_hilang"       : paket_hilang,
        "packet_loss_persen" : packet_loss_persen,
        "rtt_min_ms"         : min(rtt_list) if rtt_list else None,
        "rtt_max_ms"         : max(rtt_list) if rtt_list else None,
        "rtt_avg_ms"         : sum(rtt_list) / len(rtt_list) if rtt_list else None,
    }

    # ── Tampilkan ringkasan ───────────────────────────────────
    print("\n" + "-"*55)
    print("  STATISTIK QOS UDP PINGER")
    print("-"*55)
    print(f"  Paket Terkirim  : {hasil['paket_terkirim']}")
    print(f"  Paket Diterima  : {hasil['paket_diterima']}")
    print(f"  Paket Hilang    : {hasil['paket_hilang']}")
    print(f"  Packet Loss     : {hasil['packet_loss_persen']:.1f}%")
    print("-"*55)

    if rtt_list:
        print(f"  RTT Min         : {hasil['rtt_min_ms']:.3f} ms")
        print(f"  RTT Max         : {hasil['rtt_max_ms']:.3f} ms")
        print(f"  RTT Rata-rata   : {hasil['rtt_avg_ms']:.3f} ms")
    else:
        print("  RTT             : N/A (semua paket hilang)")

    print("="*55)
    return hasil


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    print("\n" + "#"*55)
    print("  CLIENT.PY - PRAKTIKUM JARINGAN KOMPUTER")
    print("  Topik: Client-Proxy-Server Socket Python")
    print("#"*55)

    # ── TAHAP 1: HTTP request via Proxy ──────────────────────
    sukses = request_file_via_proxy(FILE_YANG_DIMINTA)

    if sukses:
        print(f"\n[SUKSES] File '{FILE_YANG_DIMINTA}' berhasil diterima dari Proxy.")
    else:
        print(f"\n[GAGAL] File '{FILE_YANG_DIMINTA}' tidak berhasil diterima.")

    # ── TAHAP 2: UDP Pinger QoS Test ─────────────────────────
    print("\n[INFO] Memulai pengujian QoS via UDP Pinger...")
    hasil_qos = udp_pinger(UDP_PING_COUNT)

    # ── Ringkasan akhir ───────────────────────────────────────
    print("\n" + "#"*55)
    print("  RINGKASAN EKSEKUSI")
    print("#"*55)
    print(f"  Transfer File   : {'BERHASIL' if sukses else 'GAGAL'}")
    print(f"  Packet Loss UDP : {hasil_qos['packet_loss_persen']:.1f}%")
    if hasil_qos['rtt_avg_ms'] is not None:
        print(f"  RTT Avg         : {hasil_qos['rtt_avg_ms']:.3f} ms")
    print("#"*55 + "\n")


if __name__ == "__main__":
    main()
