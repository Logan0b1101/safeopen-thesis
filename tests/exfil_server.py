# tests/exfil_server.py
import socket

HOST = "127.0.0.1"
PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"[server] Listening on {HOST}:{PORT} ... (Ctrl-C to stop)")
    conn, addr = s.accept()
    with conn:
        print(f"[server] Connection from {addr}")
        data = conn.recv(1024)
        print("[server] Received:", data.decode(errors="ignore"))
    print("[server] Done")
