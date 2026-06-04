import socket
import os

# Konfigurasi berdasarkan Kontrak Sistem
PROXY_HOST = '0.0.0.0'  # Mendengarkan semua interface (Localhost & LAN)
PROXY_PORT = 8000
WEB_SERVER_HOST = '192.168.1.10' # <--- GANTI INI NANTI dengan IP LAN Laptop A (Web Server)
WEB_SERVER_PORT = 9000
BUFFER_SIZE = 4096

def start_proxy():
    # Setup TCP Socket untuk Proxy Server
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind((PROXY_HOST, PROXY_PORT))
    proxy_socket.listen(5)
    
    print(f"[*] Proxy Server berjalan dan mendengarkan di {PROXY_HOST}:{PROXY_PORT}...")

    while True:
        client_conn, client_addr = proxy_socket.accept()
        print(f"\n[+] Menerima koneksi TCP dari Client: {client_addr}")

        try:
            # Menerima request dari Client (Buffer Size WAJIB 4096 bytes)
            client_request_bytes = client_conn.recv(BUFFER_SIZE)
            if not client_request_bytes:
                client_conn.close()
                continue
                
            # Decoding WAJIB menggunakan 'utf-8'
            client_request = client_request_bytes.decode('utf-8')
            print(f"[*] Request dari Client:\n{client_request.strip()}")

            # Parsing manual HTTP Request untuk mendapatkan nama file
            # Format kontrak: "GET /<namafile> HTTP/1.1\r\nHost: <ip>\r\n\r\n"
            request_lines = client_request.split('\r\n')
            first_line_parts = request_lines[0].split()

            if len(first_line_parts) >= 2 and first_line_parts[0] == 'GET':
                # Ambil path dan hilangkan karakter '/' di awal untuk nama file lokal
                filename = first_line_parts[1][1:]
                
                # Handling jika root (kosong)
                if filename == "":
                    filename = "index.html"

                # ==========================================
                # LOGIKA CACHING
                # ==========================================
                if os.path.exists(filename):
                    # --- CACHE HIT ---
                    print(f"[*] Cache HIT: File '{filename}' ditemukan di direktori Proxy.")
                    
                    # Baca isi file yang di-cache
                    with open(filename, 'r', encoding='utf-8') as file:
                        file_content = file.read()
                    
                    # Buat respons sukses sesuai kontrak
                    response = f"HTTP/1.1 200 OK\r\n\r\n{file_content}"
                    client_conn.sendall(response.encode('utf-8'))
                    print("[*] Respons sukses dikirim ke Client (dari Cache lokal).")
                    
                else:
                    # --- CACHE MISS ---
                    print(f"[*] Cache MISS: File '{filename}' tidak ada. Membuat koneksi baru ke Web Server...")
                    
                    # Buka koneksi TCP client baru ke Web Server
                    web_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    
                    try:
                        web_server_socket.connect((WEB_SERVER_HOST, WEB_SERVER_PORT))
                        
                        # Teruskan request dari Client ke Web Server sesuai kontrak
                        proxy_to_server_request = f"GET /{filename} HTTP/1.1\r\nHost: {WEB_SERVER_HOST}\r\n\r\n"
                        web_server_socket.sendall(proxy_to_server_request.encode('utf-8'))
                        
                        # Terima respons dari Web Server
                        server_response_bytes = web_server_socket.recv(BUFFER_SIZE)
                        server_response_str = server_response_bytes.decode('utf-8')
                        
                        # Evaluasi status code secara manual
                        if server_response_str.startswith("HTTP/1.1 200 OK"):
                            # Pisahkan Header dan Body dengan \r\n\r\n untuk menyimpan file
                            parts = server_response_str.split('\r\n\r\n', 1)
                            if len(parts) == 2:
                                file_content = parts[1]
                                # Simpan (Cache) file ke direktori proxy
                                with open(filename, 'w', encoding='utf-8') as file:
                                    file.write(file_content)
                                print(f"[*] File '{filename}' berhasil di-cache dari Web Server.")
                        else:
                            print(f"[-] Web Server merespons dengan kegagalan (e.g., 404).")

                        # Teruskan kembali respons persis dari Web Server ke Client
                        client_conn.sendall(server_response_bytes)
                        print("[*] Respons dari Web Server selesai diteruskan ke Client.")
                        
                    except Exception as e:
                        print(f"[-] Gagal menghubungi Web Server: {e}")
                        # Jika Web Server mati, kembalikan 404 sesuai kontrak fail
                        error_response = "HTTP/1.1 404 Not Found\r\n\r\n"
                        client_conn.sendall(error_response.encode('utf-8'))
                    finally:
                        web_server_socket.close()

        except Exception as e:
            print(f"[-] Terjadi kesalahan saat memproses request: {e}")
        finally:
            client_conn.close()

if __name__ == "__main__":
    start_proxy()