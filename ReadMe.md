# Mint-Server

A high-performance API server for generating and serving mock invoice data with Redis caching.

## Overview

Mint-Server is a FastAPI-based application that provides a RESTful API for retrieving mock invoice data. It includes:

- Redis-based caching for improved performance
- Configurable invoice data generation
- Comprehensive test coverage
- Docker containerization for easy deployment

## Features

- **Mock Invoice Generation**: Creates realistic mock invoices with configurable properties
- **Redis Caching**: Implements efficient caching with TTL for improved response times
- **Configurable Limits**: Allows customization of data retrieval through query parameters
- **Resilient Design**: Graceful handling of Redis connection failures
- **Docker Support**: Ready for containerized deployment with Docker and Docker Compose
- **Comprehensive Testing**: Complete test suite for all components

## Tech Stack

- **FastAPI**: Modern, high-performance web framework
- **Redis**: In-memory data store for caching
- **Pydantic**: Data validation and settings management
- **Docker**: Containerization for consistent deployment
- **Pytest**: Testing framework

## Project Structure

```
Mint-Server/
   app/                      # Application code
      api/                  # API routes
         routes/           # Endpoint definitions
      config/               # Application configuration
      constants/            # Constants and defaults
      core/                 # Core functionality (logging, etc.)
      errors/               # Custom error definitions
      repositories/         # Data access layer
      schemas/              # Data models and validation
      services/             # Business logic
   main.py               # Application entry point
   scripts/                  # Utility scripts
   tests/                    # Test suite
   Dockerfile                # Docker image definition
   docker-compose.yml        # Docker Compose configuration
   requirements.txt          # Python dependencies
   pytest.ini                # Test configuration
```

## Getting Started

### Prerequisites

- Python 3.12+
- Redis server (optional for local development)
- Docker and Docker Compose (for containerized deployment)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Mint-Server
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=your_password
   REDIS_DB=0
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Deployment

1. Build and start the containers:
   ```bash
   docker compose up -d
   ```

2. The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Available Endpoints

#### GET /invoices

Retrieves a list of mock invoices.

**Query Parameters:**
- `limit` (optional): Number of invoices to return (default: 50, min: 1, max: 100)

**Response:**
```json
[
  {
    "id": "INV-123-ACME",
    "client": "Acme Corporation",
    "amount": 75000,
    "risk": 0.0325,
    "tokenId": "TIQ-4567",
    "status": "new"
  },
  // Additional invoices...
]
```

## Configuration

The application can be configured through environment variables or a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_HOST` | Redis server hostname | `localhost` |
| `REDIS_PORT` | Redis server port | `6379` |
| `REDIS_PASSWORD` | Redis server password | `""` (empty string) |
| `REDIS_DB` | Redis database index | `0` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `["*"]` |

## Caching

The application uses Redis for caching invoice data:

- Each request is cached based on the `limit` parameter
- Cache TTL is set to 60 seconds by default
- The application handles Redis connection failures gracefully

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage report:

```bash
pytest --cov=app tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.