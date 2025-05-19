from sqlalchemy import Column, Integer, String, Float
from services.database import Base
from models.Stock import Stock

class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)