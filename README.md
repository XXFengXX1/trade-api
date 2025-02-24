# Trade Order API

A FastAPI-based REST API for handling trade orders with real-time WebSocket updates. This project includes a complete CI/CD pipeline and Docker deployment configuration.

## Features

- REST API endpoints for creating and retrieving trade orders
- Real-time order updates via WebSocket
- PostgreSQL database integration
- Docker containerization
- Automated CI/CD pipeline with GitHub Actions
- AWS EC2 deployment

## Tech Stack Usedd

- Python 3.9
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker & Docker Compose
- GitHub Actions
- AWS EC2

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


## Deployment

The application is automatically deployed to AWS EC2 when changes are pushed to the main branch.

## API Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Project Structure

```
trade-api/
├── main.py              # Main application file
├── models.py            # Database models
├── schemas.py           # Pydantic schemas
├── test_main.py         # Tests
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
└── websocket_test.html # WebSocket test page
```
