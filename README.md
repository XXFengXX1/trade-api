# Trade Order API

A FastAPI-based REST API for handling trade orders with real-time WebSocket updates. This project includes a complete CI/CD pipeline and Docker deployment configuration.

## Features

- REST API endpoints for creating and retrieving trade orders
- Real-time order updates via WebSocket
- PostgreSQL database integration
- Docker containerization
- Automated CI/CD pipeline with GitHub Actions
- AWS EC2 deployment

## Tech Stack Used in this 

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker & Docker Compose
- GitHub Actions
- AWS EC2

## Local Development Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd trade-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL:
```bash
createdb trades
```

4. Run the application:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Access the API at `http://localhost:8000`

## API Endpoints

- `POST /orders/`: Create a new trade order
  ```json
  {
    "symbol": "AAPL",
    "price": 150.50,
    "quantity": 100,
    "order_type": "buy"
  }
  ```

- `GET /orders/`: Retrieve all trade orders

- WebSocket endpoint: `ws://localhost:8000/ws`

## Testing

Run tests using pytest:
```bash
pytest
```

## Deployment

The application is automatically deployed to AWS EC2 when changes are pushed to the main branch.


## API Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Project Structure

```
trade-api/
├── main.py              # Main application fil
├── models.py            # database models
├── schemas.py           # schemas
├── test_main.py         # tests
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
└── websocket_test.html # page to test websocket
```
