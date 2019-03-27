import socket
import select
import queue

ip_port=("127.0.0.1",4999)
sk=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.bind(ip_port)
sk.listen(5)
sk.setblocking(False    )

inputs=[sk,]
outputs=[]
message={}

while True:
    rlist,wlist,elist=select.select(inputs,outputs,inputs)
    for r in rlist:
        if r is sk:
            conn,address=r.accept()
            inputs.append(conn)
            message[conn]=queue.Queue()
        else:
            data=r.recv(1024)
            if data:
                outputs.append(r)
                message[r].put(data)
            else:
                inputs.remove(r)
                del message[r]
    for w in wlist:
        try:
            data=message[w].getnowait()
            w.sendall(data)
        except queue.Empty:
            pass
        outputs.remove(w)

    for e in elist:
        inputs.remove(e)
        if e in wlist:
            outputs.remove(e)
        e.close()
        del message[e]


m={}

m[sk]="ss"
print(m)