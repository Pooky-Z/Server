from orm import Model, StringField, BooleanField, FloatField, TextField, create_pool, IntegerField

import time, uuid, asyncio


def next_id():
    # id='%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)
    id = "%.f" % (float(time.time() * 1000))
    return str(int(id) - 155360000000)


class Data(Model):
    __table__ = "data"

    id = StringField(primary_key=True, default=next_id, ddl='varchar(200)')
    cid = StringField(ddl="varchar(500)")
    illumination = StringField(ddl="varchar(500)")
    humidity = StringField(ddl="varchar(500)")
    temperature = StringField(ddl="varchar(500)")
    level = IntegerField()
    arrivetime = StringField(ddl="varchar(50)")


class Position(Model):
    __table__ = "position"

    id = IntegerField(primary_key=True, default=next_id)
    x = StringField(ddl="varchar(10)")
    y = StringField(ddl="varchar(10)")


async def test(loop):
    arrivetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    await create_pool(
        loop=loop,
        host='127.0.0.1',
        port=3306,
        user="root",
        password="admin",
        db="data")
    u = Data(
        cid=1,
        illumination=12345,
        temperature=312,
        humidity=134,
        level=10,
        arrivetime=arrivetime)
    u2 = Data()
    id = 1
    for i in range(5):
        for j in range(5):
            p = Position(id=id, x=i, y=j)
            id += 1
            await p.save()

    await u.save()
    all = await u2.findAll()
    for i in all:
        print(i["illumination"])
    number = await u.findNumber("illumination")

    print(number)
    print(all)
    # await u1.remove()


if __name__ == "__main__":
    print(time.time())
    data = "1223,1212,1222"
    data1, data2, data3 = data.split(",")
    print(data1, data2, data3)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test(loop))
