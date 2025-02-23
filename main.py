from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import os
import json

from models import Base, Order
from schemas import OrderCreate, OrderResponse

app = FastAPI(
    title="Trade Order API",
    description="A simple REST API for handling trade orders with WebSocket updates",
    version="1.0.0"
)

# PostgreSQL Database configuration
POSTGRES_USER = os.getenv("USER", "xiongfeng")
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "trades"

DATABASE_URL = f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

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
        if self.active_connections:  # Only try to broadcast if there are connections
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except:
                    # If sending fails, remove the connection
                    self.active_connections.remove(connection)


manager = ConnectionManager()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Trade Order API</title>
        </head>
        <body>
            <h1>Trade Order API</h1>
            <p>Available endpoints:</p>
            <ul>
                <li><a href="/docs">API Documentation (Swagger UI)</a></li>
                <li><a href="/redoc">Alternative API Documentation (ReDoc)</a></li>
            </ul>
        </body>
    </html>
    """


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # You could handle incoming WebSocket messages here if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)


@app.post("/orders/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        # Create new order
        db_order = Order(
            symbol=order.symbol,
            price=order.price,
            quantity=order.quantity,
            order_type=order.order_type
        )

        # Add to database
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        # Prepare response data
        response_data = {
            "id": db_order.id,
            "symbol": db_order.symbol,
            "price": db_order.price,
            "quantity": db_order.quantity,
            "order_type": db_order.order_type,
            "created_at": db_order.created_at.isoformat()
        }

        # Try to broadcast to WebSocket clients
        try:
            await manager.broadcast({
                "event": "new_order",
                "data": response_data
            })
        except Exception as ws_error:
            print(f"WebSocket broadcast failed: {ws_error}")
            # Continue even if WebSocket broadcast fails

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