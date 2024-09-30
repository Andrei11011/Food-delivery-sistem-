from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

hostname = "127.0.0.1"
username = "root"
password = ""
port = 3306
database = "sistem_comanda_mancare"

DATABASE_URL = f'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}'

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Cont(Base):
    __tablename__ = "Accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)

class BasketItem(Base):
    __tablename__ = "BasketItems"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Accounts.id'), nullable=False)
    item_name = Column(String(200), nullable=False)
    item_price = Column(Integer, default=1)

    user = relationship("Cont")


class Order(Base):
    __tablename__ = "Orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Accounts.id'), nullable=False)
    adress = Column(String(200), nullable=False)
    phone_number = Column(String(20), nullable=False)
    status = Column(String(20), default="In Progress")
    items = Column(String(500), nullable=False)


    user = relationship("Cont")




Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)