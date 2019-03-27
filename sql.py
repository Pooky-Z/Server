from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import time

Base = declarative_base()

class Data(Base):
    __tablename__ = "water"

    def __init__(self):
        self.id = Column(String(20), primary_key=True)
        self.data = Column(String(500))
        self.arrivetime = Column(String(30))

        engine = create_engine("mysql+mysqlconnector://root:admin@127.0.0.1:3306/data")
        DBSession = sessionmaker(bind=engine)
        session = DBSession

def add_data(*datas):
    arrivetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    for i in range(len(datas)):

        data = Data(id=str(i + 4), data=str(datas[i]), arrivetime=arrivetime)
        session.add(data)
    session.commit()
    session.close()


def update_data():
    pass


def delete_data(*time):
    if (len(time) != 2):
        print("two date input!")
    else:
        session.query(Data).filter(Data.arrivetime < time[0]
                                   and Data.arrivetime > time[1]).delete()
    session.commit()
    session.close()


def search_data(*time):
    datas = session.query(Data).filter(Data.arrivetime < time[0]
                                       and Data.arrivetime > time[1]).all()
    for data in datas:
        print(data.arrivetime)
    session.commit()
    session.close()


if __name__ == "__main__":
    session = DBSession()
    datas=["123","12313","123123"]

    # add_data("123","12313","123123")