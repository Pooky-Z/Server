import socket

ip_port = ("127.0.0.1", 9999)
sk = socket.socket()
sk.connect(ip_port)

while True:
    inpu = input(">>:")
    sk.sendall(bytes(inpu, encoding="utf-8"))

    server_reply = sk.recv(1024)
    print(str(server_reply, encoding="utf-8"))

sk.close()