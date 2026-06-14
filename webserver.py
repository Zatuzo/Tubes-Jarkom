import socket
import threading
import os
import datetime

# ============================================================
# KONFIGURASI
# ============================================================
TCP_HOST = '0.0.0.0'
TCP_PORT = 8000
UDP_HOST = '0.0.0.0'
UDP_PORT = 9000
BUFFER_SIZE = 4096
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# HELPER: LOG
# ============================================================
def log(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

# ============================================================
# HELPER: BACA FILE
# ============================================================
def read_file(filepath):
    """Membaca file dari direktori BASE_DIR. Return (content_bytes, mime_type) atau raise exception."""
    full_path = os.path.join(BASE_DIR, filepath.lstrip('/'))
    full_path = os.path.normpath(full_path)

    # Keamanan: pastikan path tidak keluar dari BASE_DIR
    if not full_path.startswith(BASE_DIR):
        raise PermissionError("Path traversal detected")

    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")

    ext = os.path.splitext(full_path)[1].lower()
    mime_map = {
        '.html': 'text/html; charset=utf-8',
        '.css':  'text/css',
        '.js':   'application/javascript',
        '.png':  'image/png',
        '.jpg':  'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.ico':  'image/x-icon',
    }
    mime_type = mime_map.get(ext, 'application/octet-stream')

    with open(full_path, 'rb') as f:
        content = f.read()

    return content, mime_type

# ============================================================
# HELPER: BUILD HTTP RESPONSE
# ============================================================
def build_response(status_code, status_text, content_type, body_bytes):
    header = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    return header.encode('utf-8') + body_bytes

def response_404():
    body = b"<html><body><h1>404 Not Found</h1><p>The requested resource was not found.</p></body></html>"
    return build_response(404, "Not Found", "text/html; charset=utf-8", body)

def response_500():
    body = b"<html><body><h1>500 Internal Server Error</h1><p>An error occurred on the server.</p></body></html>"
    return build_response(500, "Internal Server Error", "text/html; charset=utf-8", body)

def response_400():
    body = b"<html><body><h1>400 Bad Request</h1></body></html>"
    return build_response(400, "Bad Request", "text/html; charset=utf-8", body)

# ============================================================
# HANDLER: SATU KONEKSI TCP (dijalankan di thread terpisah)
# ============================================================
def handle_tcp_client(conn, addr):
    client_ip = addr[0]
    log(f"[TCP] Koneksi masuk dari {client_ip}:{addr[1]} | Thread: {threading.current_thread().name}")

    try:
        raw_request = b""
        conn.settimeout(5)

        # Terima request hingga header selesai
        while b"\r\n\r\n" not in raw_request:
            chunk = conn.recv(BUFFER_SIZE)
            if not chunk:
                break
            raw_request += chunk

        if not raw_request:
            log(f"[TCP] Request kosong dari {client_ip}, koneksi ditutup.")
            return

        # Parse baris pertama HTTP request
        try:
            request_line = raw_request.decode('utf-8', errors='replace').split('\r\n')[0]
            parts = request_line.split(' ')
            if len(parts) < 2:
                raise ValueError("Malformed request line")
            method = parts[0]
            path   = parts[1]
        except Exception:
            log(f"[TCP] Malformed request dari {client_ip}")
            conn.sendall(response_400())
            return

        log(f"[TCP] {method} {path} dari {client_ip}")

        # Hanya mendukung metode GET
        if method != 'GET':
            body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
            resp = build_response(405, "Method Not Allowed", "text/html; charset=utf-8", body)
            conn.sendall(resp)
            log(f"[TCP] 405 Method Not Allowed | {client_ip} | {path}")
            return

        # Default path
        if path == '/' or path == '':
            path = '/index.html'

        # Baca dan kirim file
        try:
            content, mime_type = read_file(path)
            response = build_response(200, "OK", mime_type, content)
            conn.sendall(response)
            log(f"[TCP] 200 OK | {client_ip} | {path} | {len(content)} bytes")

        except FileNotFoundError:
            conn.sendall(response_404())
            log(f"[TCP] 404 Not Found | {client_ip} | {path}")

        except PermissionError:
            conn.sendall(response_404())
            log(f"[TCP] 404 (path traversal blocked) | {client_ip} | {path}")

        except Exception as e:
            conn.sendall(response_500())
            log(f"[TCP] 500 Internal Server Error | {client_ip} | {path} | Error: {e}")

    except socket.timeout:
        log(f"[TCP] Timeout membaca request dari {client_ip}")

    except Exception as e:
        log(f"[TCP] Error tidak terduga dari {client_ip}: {e}")

    finally:
        conn.close()
        log(f"[TCP] Koneksi ditutup: {client_ip}")

# ============================================================
# TCP SERVER (HTTP) — Thread utama listener
# ============================================================
def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((TCP_HOST, TCP_PORT))
    server.listen(10)
    log(f"[TCP] Web Server (HTTP) berjalan di port {TCP_PORT}")

    while True:
        try:
            conn, addr = server.accept()
            t = threading.Thread(
                target=handle_tcp_client,
                args=(conn, addr),
                daemon=True
            )
            t.start()
            log(f"[TCP] Thread baru dibuat: {t.name} untuk {addr[0]}:{addr[1]}")
        except Exception as e:
            log(f"[TCP] Error saat accept: {e}")

# ============================================================
# UDP SERVER (QoS Echo) — Thread terpisah
# ============================================================
def start_udp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((UDP_HOST, UDP_PORT))
    log(f"[UDP] Echo Server (QoS) berjalan di port {UDP_PORT}")

    while True:
        try:
            data, addr = server.recvfrom(BUFFER_SIZE)
            payload = data.decode('utf-8', errors='replace').strip()
            log(f"[UDP] Paket diterima dari {addr[0]}:{addr[1]} | Payload: '{payload}'")

            # Echo balik payload identik
            server.sendto(data, addr)
            log(f"[UDP] Echo dikirim ke {addr[0]}:{addr[1]} | Payload: '{payload}'")

        except Exception as e:
            log(f"[UDP] Error: {e}")

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    log("=" * 55)
    log("  Web Server - Tugas Besar Jaringan Komputer")
    log("  Laboratorium Praktikum Informatika - Tel-U")
    log("=" * 55)
    log(f"  Base directory : {BASE_DIR}")
    log(f"  TCP HTTP       : port {TCP_PORT}")
    log(f"  UDP Echo (QoS) : port {UDP_PORT}")
    log("=" * 55)

    # Jalankan UDP server di thread terpisah (daemon)
    udp_thread = threading.Thread(target=start_udp_server, daemon=True, name="UDP-Echo-Server")
    udp_thread.start()

    # Jalankan TCP server di main thread
    start_tcp_server()
