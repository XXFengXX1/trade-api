# Applicant: Finn(Feng) Xiong

from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class OrderBase(BaseModel):
    symbol: str
    price: float
    quantity: int
    order_type: str

    @validator('order_type')
    def validate_order_type(cls, v):
        if v not in ['buy', 'sell']:
            raise ValueError('order_type must be either "buy" or "sell"')
        return v

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('price must be positive')
        return v

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('quantity must be positive')
        return v

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True  # This is important for SQLAlchemy compatibility