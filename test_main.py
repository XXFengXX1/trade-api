import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db
from models import Base

# Test database URL
SQLALCHEMY_DATABASE_URL = "postgresql://test_user:test_password@trade-api-db-1:5432/test_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def test_create_order(client):
    response = client.post(
        "/orders/",
        json={"symbol": "AAPL", "price": 150.50, "quantity": 100, "order_type": "buy"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["price"] == 150.50
    assert data["quantity"] == 100
    assert data["order_type"] == "buy"


def test_get_orders(client):
    # First create an order
    client.post(
        "/orders/",
        json={"symbol": "AAPL", "price": 150.50, "quantity": 100, "order_type": "buy"}
    )

    response = client.get("/orders/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0