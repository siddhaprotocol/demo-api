# Mint-Server

A high-performance API server for generating and serving mock invoice data with Redis caching.

## Overview

Mint-Server is a FastAPI-based application that provides a RESTful API for retrieving mock invoice data. It includes:

- Redis caching for improved performance
- Configurable invoice data generation
- Comprehensive test coverage
- Docker containerization for easy deployment

## Features

- **Mock Invoice Generation**: Creates realistic mock invoices with configurable properties
- **ProductA Status API**: Endpoints for tracking and updating ProductA processing status
- **Flexible Caching**: Supports both local Redis and AWS ElastiCache
- **TLS/SSL Support**: Secure connections to AWS ElastiCache
- **Configurable Limits**: Allows customization of data retrieval through query parameters
- **Resilient Design**: Graceful handling of cache connection failures
- **Docker Support**: Ready for containerized deployment with Docker and Docker Compose
- **Comprehensive Testing**: Complete test suite for all components

## Tech Stack

- **FastAPI**: Modern, high-performance web framework
- **Redis**: In-memory data store for caching
- **AWS ElastiCache**: Managed caching service in the cloud
- **Pydantic**: Data validation
- **Docker**: Containerization for consistent deployment
- **Pytest**: Testing framework

## Project Structure

```
Mint-Server/
   app/                      # Application code
      api/                  # API routes
         routes/           # Endpoint definitions
      constants/            # Constants and defaults
      core/                 # Core functionality (logging, etc.)
      errors/               # Custom error definitions
      repositories/         # Data access layer
      schemas/              # Data models and validation
      services/             # Business logic
   main.py               # Application entry point
   docs/                     # Documentation
      deployment.md        # AWS deployment guide
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
- AWS account (for ElastiCache deployment)

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

4. Create a `.env` file with your configuration (for local Redis):
   ```
   CACHE_PROVIDER=redis
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=your_password
   REDIS_DB=0
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Deployment with Local Redis

1. Build and start the containers with local Redis:
   ```bash
   docker compose --profile local-dev up -d
   ```

2. The API will be available at `http://localhost:8000`

## Deployment

For detailed instructions on deploying this application to AWS with multi-region support, see the [Deployment Guide](docs/deployment.md).

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

#### GET /producta/status

Retrieves the current status of ProductA processing.

**Response:**
```json
{
  "status": "processing"  // Can be "processing" or "done"
}
```

#### PATCH /producta/status

Updates the status of ProductA processing.

**Request Body:**
```json
{
  "status": "done"  // Can be "processing" or "done"
}
```

**Response:**
```json
{
  "status": "done"
}
```

## Configuration

The application can be configured through environment variables or a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `CACHE_PROVIDER` | Cache provider to use | `redis` |
| `REDIS_HOST` | Redis server hostname | `localhost` |
| `REDIS_PORT` | Redis server port | `6379` |
| `REDIS_PASSWORD` | Redis server password | `""` (empty string) |
| `REDIS_DB` | Redis database index | `0` |
| `ELASTICACHE_TLS_ENABLED` | Enable TLS for ElastiCache connection | `false` |
| `ELASTICACHE_SSL_CERT_REQS` | SSL verification mode: 'none', 'optional', 'required' | `null` |
| `AWS_REGION` | AWS region for ElastiCache | `null` |
| `REDIS_CONNECTION_POOL_SIZE` | Connection pool size | `10` |
| `REDIS_CONNECTION_TIMEOUT` | Connection timeout in seconds | `5` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `["*"]` |

## Caching

The application supports Redis for caching data:

- Invoice requests are cached based on the `limit` parameter with a 60-second TTL
- ProductA status is cached with a 10-minute TTL
- The application handles cache connection failures gracefully
- Connection pooling improves performance
- TLS/SSL support for secure connections to ElastiCache

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