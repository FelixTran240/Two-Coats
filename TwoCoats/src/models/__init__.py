from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BuyTransaction(Base):
    __tablename__ = 'buy_transactions'

    id = Column(Integer, primary_key=True)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_item = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

class SellTransaction(Base):
    __tablename__ = 'sell_transactions'

    id = Column(Integer, primary_key=True)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_item = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)