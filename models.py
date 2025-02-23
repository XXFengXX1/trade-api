from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    quantity = Column(Integer)
    order_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "price": self.price,
            "quantity": self.quantity,
            "order_type": self.order_type,
            "created_at": self.created_at
        }