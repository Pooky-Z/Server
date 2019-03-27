import socket
import select
import queue
from model import Water
import threadManager
from multiprocessing import Pool
from orm import create_pool
import asyncio
import time
import io
import sys
#改变标准输出的默认编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

ip_port = ("127.0.0.1", 9999)

sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sk.bind(ip_port)
sk.listen(5)
sk.setblocking(False)

inputs = [
    sk,
]
outputs = []
message = {}


while True:
    rlist, wlist, elist = select.select(inputs, outputs, inputs, 0.5)
    print("inputs:", inputs)
    print("rlist:", rlist)
    print("wlist:",wlist)
    print("message:", message)

    for r in rlist:
        if r == sk:
            conn, address = r.accept()
            inputs.append(conn)
            message[conn] = queue.Queue()
            print(address)
        else:

            client_data = r.recv(1024)
            if client_data:
                outputs.append(r)
                message[r].put(client_data)
                print("data:",str(client_data,encoding="utf-8"))
            else:
                inputs.remove(r)
                del message[r]
    for w in wlist:
        print("w:", w)
        try:
            data = message[w].get_nowait()
            w.sendall(data)
        except queue.Empty:
            pass
        outputs.remove(w)

    for e in elist:
        inputs.remove(e)
        if e in outputs:
            outputs.remove(e)
        e.close()
        del message[e]

