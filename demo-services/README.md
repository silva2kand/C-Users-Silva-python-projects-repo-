# Demo Microservices

Collection of lightweight service demonstrations and prototypes.

## 🚀 Features

- **Microservice Architecture**: Lightweight, containerized services
- **Docker Support**: Full containerization with docker-compose
- **Testing Framework**: Comprehensive test coverage
- **REST APIs**: Well-defined API endpoints

## 🏗️ Structure

```
demo-services/
├── src/
│   └── main.py            # Main service application
├── docker-compose.yml     # Multi-service orchestration
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
└── test_services.py      # Service tests
```

## 📋 Requirements

```bash
pip install fastapi uvicorn pytest
```

## 🛠️ Setup

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the service:
   ```bash
   python src/main.py
   ```

### Docker Deployment

1. Build and run with docker-compose:
   ```bash
   docker-compose up --build
   ```

2. Or build individually:
   ```bash
   docker build -t demo-service .
   docker run -p 8000:8000 demo-service
   ```

## 🧪 Testing

Run the test suite:

```bash
python -m pytest test_services.py -v
```

## 📡 API

Service endpoints (when running):
- `GET /` - Service health check
- `GET /api/v1/status` - Detailed status information
- `POST /api/v1/process` - Process requests

## 🔧 Configuration

Services can be configured through:
- Environment variables
- Configuration files
- Docker environment settings

## 📊 Monitoring

- Health checks at `/health`
- Metrics available at `/metrics`
- Logs via standard output