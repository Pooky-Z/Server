import socket
import select
import queue
from model import Data
import threadManager
from multiprocessing import Pool
from orm import create_pool
import asyncio
import time
import io
import sys
from sklearn.externals import joblib
import numpy as np
import pandas as pd

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
        self.svm_clf = joblib.load('./model/filename.joblib')
        self.level = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        print("init succeed")

    def socket(self):
        ip_port = ("192.168.43.209", 8080)
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
            data = r.recv(1024)
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

        if data:
            self.outputs.append(r)
            self.message[r].put(data)
            loop.run_until_complete(self.data_save(data))
        else:
            self.inputs.remove(r)
            del self.message[r]
        return data

    async def data_save(self, data):
        data = str(data, encoding="utf-8")
        print(data)
        data1, data2, data3 = data.split("-")
        data1 = round(float(data1), 2)
        data2 = round((1 - float(data2) / 6000) * 100, 2)
        data3 = round(float(data3),2)
        data_set = {'N': [data1 + 100], 'P': [data2 + 100], 'K': [data3 + 100]}
        x = pd.DataFrame(data_set)
        output = self.svm_clf.predict(x)[0]
        level = self.setlevel(output)
        d = Data(
            cid=3,
            illumination=data3 ,
            humidity=data2 ,
            temperature=data1 ,
            level=level,
            arrivetime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        await d.save()

    async def all_data(self):
        d = Data()
        datas = await Data.findAll()
        for data in datas:
            self.data.append(data["data"])

    def setlevel(self, output):
        if (output > 6000):
            return self.level[9]
        if (output < 2000):
            return self.level[0]
        if (2000 < output < 2500):
            return self.level[1]
        if (2500 < output < 3000):
            return self.level[2]
        if (3000 < output < 3500):
            return self.level[3]
        if (3500 < output < 4000):
            return self.level[4]
        if (4000 < output < 4500):
            return self.level[5]
        if (4500 < output < 5000):
            return self.level[6]
        if (5000 < output < 5500):
            return self.level[7]
        if (5500 < output < 6000):
            return self.level[8]


if __name__ == "__main__":
    server = Server()
    server.IO_handle()