import socket

ip_port = ("192.168.43.209", 8080)
sk = socket.socket()
sk.connect(ip_port)

while True:
    inpu = input(">>:")
    sk.sendall(bytes(inpu, encoding="utf-8"))

    server_reply = sk.recv(1024)
    print(str(server_reply, encoding="utf-8"))

sk.close()