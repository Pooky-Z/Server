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

# ip_port = ("127.0.0.1", 9999)

# sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# sk.bind(ip_port)
# sk.listen(5)
# sk.setblocking(False)

# inputs = [
#     sk,
# ]
# outputs = []
# message = {}

# threads=threadManager(1000,10)
# pool=Pool(4)

# while True:
#     rlist, wlist, elist = select.select(inputs, outputs, inputs, 0.5)
#     print("inputs:", inputs)
#     print("rlist:", rlist)
#     print("wlist:",wlist)
#     print("message:", message)

#     for r in rlist:
#         if r == sk:
#             conn, address = r.accept()
#             inputs.append(conn)
#             message[conn] = queue.Queue()
#             print(address)
#         else:

#             client_data = r.recv(1024)
#             if client_data:
#                 pool.apply_async()
#                 outputs.append(r)
#                 message[r].put(client_data)
#                 print("data:",str(client_data,encoding="utf-8"))
#             else:
#                 inputs.remove(r)
#                 del message[r]
#     for w in wlist:
#         print("w:", w)
#         try:
#             data = message[w].get_nowait()
#             w.sendall(data)
#         except queue.Empty:
#             pass
#         outputs.remove(w)

#     for e in elist:
#         inputs.remove(e)
#         if e in outputs:
#             outputs.remove(e)
#         e.close()
#         del message[e]


class Server(object):
    def __init__(self):
        self.sk = self.socket()
        self.inputs = [
            self.sk,
        ]
        self.outputs = []
        self.message = {}
        self.pool = Pool(4)
        self.data = []

    def socket(self):
        ip_port = ("127.0.0.1", 9999)
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.bind(ip_port)
        sk.listen(5)
        sk.setblocking(False)
        return sk

    def IO_handle(self):
        while True:
            rlist, wlist, elist = select.select(self.inputs, self.outputs,
                                                self.inputs, 0.5)
            for r in rlist:
                if r == self.sk:

                    conn, address = r.accept()
                    self.inputs.append(conn)
                    self.message[conn] = queue.Queue()
                else:
                    loop = asyncio.get_event_loop()
                    client_data = self.handle_recv(r, loop)

                    if client_data:
                        self.outputs.append(r)
                        self.message[r].put(client_data)
                        print("data:", str(client_data, encoding="utf-8"))
                    else:
                        self.inputs.remove(r)
                        del self.message[r]

            for w in wlist:
                try:
                    data = self.message[w].get_nowait()
                    print(data)
                    w.sendall(data)
                except queue.Empty:
                    pass
                self.outputs.remove(w)

            for e in elist:
                self.inputs.remove(e)
                if e in self.outputs:
                    self.outputs.remove(e)
                e.close()
                del self.message[e]

    def handle_recv(self, r, loop):

        loop = asyncio.get_event_loop()
        try:
            client_data = r.recv(1024)
        except Exception:
            pass
        task = create_pool(
            loop=loop,
            host='127.0.0.1',
            port=3306,
            user="root",
            password="admin",
            db="data")
        loop.run_until_complete(task)
        print(client_data)

        if client_data:
            self.outputs.append(r)
            self.message[r].put(client_data)
            loop.run_until_complete(self.data_save(client_data))
        else:
            self.inputs.remove(r)
            del self.message[r]
        return client_data

    async def data_save(self, data):
        w = Water(
            data=data,
            arrivetime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        await w.save()

    async def all_data(self):
        w = Water()
        datas = await w.findAll()
        for data in datas:
            self.data.append(data["data"])


if __name__ == "__main__":
    server = Server()
    server.IO_handle()