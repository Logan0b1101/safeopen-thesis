# tests/test_exfil.py
import socket, time

HOST = "127.0.0.1"
PORT = 9999
MSG = "HELLO_FROM_SANDBOX_TEST\n"

try:
    s = socket.create_connection((HOST, PORT), timeout=5)
    s.sendall(MSG.encode())
    s.close()
    print("[client] Sent data successfully")
    exit(0)
except Exception as e:
    print("[client] Connection failed:", repr(e))
    exit(1)
