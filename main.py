from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import os

from models import Base, Order
from schemas import OrderCreate, OrderResponse

app = FastAPI(
    title="Trade Order API",
    description="A simple REST API for handling trade orders with WebSocket updates",
    version="1.0.0"
)

# Database configuration from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('USER', 'xiongfeng')}@trade-api-db-1:5432/trades"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        if self.active_connections:
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except:
                    self.active_connections.remove(connection)


manager = ConnectionManager()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)


@app.post("/orders/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        db_order = Order(
            symbol=order.symbol,
            price=order.price,
            quantity=order.quantity,
            order_type=order.order_type
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        response_data = {
            "id": db_order.id,
            "symbol": db_order.symbol,
            "price": db_order.price,
            "quantity": db_order.quantity,
            "order_type": db_order.order_type,
            "created_at": db_order.created_at.isoformat()
        }

        try:
            await manager.broadcast({
                "event": "new_order",
                "data": response_data
            })
        except Exception as ws_error:
            print(f"WebSocket broadcast failed: {ws_error}")

        return response_data

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/orders/", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    try:
        orders = db.query(Order).all()
        return [
            {
                "id": order.id,
                "symbol": order.symbol,
                "price": order.price,
                "quantity": order.quantity,
                "order_type": order.order_type,
                "created_at": order.created_at.isoformat()
            }
            for order in orders
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))