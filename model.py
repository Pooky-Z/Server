from orm import Model,StringField,BooleanField,FloatField,TextField,create_pool

import time,uuid,asyncio


def next_id():
    # id='%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)
    id="%.f" %(float(time.time() * 1000))
    return str(int(id)-155360000000)

class Water(Model):
    __table__="water"


    id=StringField(primary_key=True, default=next_id, ddl='varchar(200)')
    data=StringField(ddl="varchar(500)")
    arrivetime=StringField(ddl="varchar(50)")

async def test(loop):
    arrivetime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    await create_pool(loop=loop,host='127.0.0.1', port=3306,user="root",password="admin",db="data")
    u=Water(data="asdasd",arrivetime=arrivetime)
    u1=Water(id="1398294198835",data="zzzz")
    u2=Water()
    all=await u2.findAll()
    for i in all:
        print(i["data"])
    await u1.update()
    number=await u1.findNumber("data")

    print(number)
    print(all)
    await u.save()
    await u1.remove()
if __name__=="__main__":
    print(time.time())
    loop=asyncio.get_event_loop()
    loop.run_until_complete(test(loop))

