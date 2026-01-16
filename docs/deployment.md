# Deployment Architecture

## Deployment Model: Single-Node (Development/POC)

```
┌─────────────────────────────────────────────────────────────────┐
│                        HOST MACHINE                              │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    DOCKER COMPOSE                         │    │
│  │                                                           │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │    │
│  │  │   FastAPI   │  │   Ollama    │  │  PostgreSQL │       │    │
│  │  │   :8000     │  │   :11434    │  │   :5432     │       │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │    │
│  │         │                │                │               │    │
│  │         └────────────────┼────────────────┘               │    │
│  │                          │                                │    │
│  │  ┌───────────────────────┴───────────────────────┐       │    │
│  │  │              Shared Volume                     │       │    │
│  │  │   /data (SQLite, FAISS, outputs)              │       │    │
│  │  └───────────────────────────────────────────────┘       │    │
│  │                                                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Container Services

### 1. API Service (FastAPI)

```yaml
service: api
image: patrolling-api:latest
ports: 8000:8000
volumes:
  - ./data:/app/data
  - ./outputs:/app/outputs
environment:
  - DATABASE_URL=sqlite:///data/patrolling.db
  - OLLAMA_HOST=http://ollama:11434
```

### 2. LLM Service (Ollama)

```yaml
service: ollama
image: ollama/ollama:latest
ports: 11434:11434
volumes:
  - ollama_models:/root/.ollama
```

### 3. Database (PostgreSQL - Production)

```yaml
service: db
image: postgres:15-alpine
ports: 5432:5432
volumes:
  - pgdata:/var/lib/postgresql/data
environment:
  - POSTGRES_DB=patrolling
  - POSTGRES_USER=patrol_user
```

## Configuration Management

### Environment Variables (.env)

```
# Database
DATABASE_URL=sqlite:///data/patrolling.db
VECTORDB_DIR=data/vectordb

# LLM
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=llama3.2:3b

# API
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your-secret-key

# CV
YOLO_MODEL=yolov8n.pt
CONFIDENCE_THRESHOLD=0.5
```

### Config File (config.yaml)

- Detection parameters
- Tracking thresholds
- Crowd analysis settings
- Logging configuration

## Monitoring & Logging

### Logging Strategy

```
logs/
├── app_20260116.log      # Application logs
├── cv_20260116.log       # CV inference logs
└── api_20260116.log      # API request logs
```

**Log Format:**

```
2026-01-16 12:00:00 | INFO | module | message
```

### Health Checks

- `/health` - API liveness
- `/health/db` - Database connectivity
- `/health/cv` - Model loaded status

## Scaling Considerations

### Horizontal Scaling (Future)

```
                    ┌─────────────┐
                    │   Nginx     │
                    │   (LB)      │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  API Pod 1  │ │  API Pod 2  │ │  API Pod 3  │
    └─────────────┘ └─────────────┘ └─────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           ▼
                    ┌─────────────┐
                    │  PostgreSQL │
                    │  (Primary)  │
                    └─────────────┘
```

### Bottlenecks & Mitigations

| Bottleneck   | Mitigation                          |
| ------------ | ----------------------------------- |
| CV Inference | GPU acceleration, batch processing  |
| LLM Latency  | Response caching, async generation  |
| DB Writes    | Connection pooling, async commits   |
| FAISS Search | Index sharding, memory optimization |

## Resource Requirements

### Minimum (Development)

- CPU: 4 cores
- RAM: 8 GB
- Storage: 20 GB
- GPU: Optional (CPU inference works)

### Recommended (Production)

- CPU: 8 cores
- RAM: 16 GB
- Storage: 100 GB SSD
- GPU: NVIDIA RTX 3060+ (for faster CV)
