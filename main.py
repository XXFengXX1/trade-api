# Applicant: Finn(Feng) Xiong

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from models import Base, Order
from schemas import OrderCreate, OrderResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Trade Order API",
    description="A simple REST API for handling trade orders with WebSocket updates",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration from different environment variables
if os.getenv("GITHUB_ACTIONS"):
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"postgresql://{os.getenv('USER', 'xiongfeng')}@localhost:5432/trades"
    )
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"postgresql://{os.getenv('USER', 'xiongfeng')}@trade-api-db-1:5432/trades"
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables for db
Base.metadata.create_all(bind=engine)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        logger.info(f"Broadcasting to {len(self.active_connections)} connections")
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                logger.info("Broadcast successful")
            except Exception as e:
                logger.error(f"Failed to broadcast: {e}")
                disconnected.append(connection)

        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


manager = ConnectionManager()

#dwdw
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/ws-test")
def test_websocket():
    return {
        "status": "WebSocket endpoint is running",
        "active_connections": len(manager.active_connections),
        "host": os.getenv('HOST', 'not set')
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.post("/orders/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Creating new order: {order.dict()}")
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
            logger.info("Attempting to broadcast new order")
            await manager.broadcast({
                "event": "new_order",
                "data": response_data
            })
        except Exception as ws_error:
            logger.error(f"WebSocket broadcast failed: {ws_error}")

        return response_data

    except Exception as e:
        logger.error(f"Error creating order: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/orders/", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    try:
        orders = db.query(Order).all()
        logger.info(f"Retrieved {len(orders)} orders")
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
        logger.error(f"Error retrieving orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))