# AI-Driven Patrolling and Bandobast Intelligence System

Computer vision and NLP-powered surveillance intelligence platform for police patrol operations and security arrangements.

## Features

| Module                | Capability                                            |
| --------------------- | ----------------------------------------------------- |
| **Object Detection**  | YOLOv8n + ONNX Runtime (31ms inference)               |
| **Crowd Analysis**    | Density classification, surge detection               |
| **Anomaly Detection** | Static objects, route blockage, after-hours activity  |
| **Alert Engine**      | Deduplication, priority scoring, lifecycle management |
| **RAG Pipeline**      | FAISS vector store, semantic search, LLM context      |
| **REST API**          | FastAPI with OpenAPI docs, rate limiting              |

## Quick Start

```bash
# Install
git clone https://github.com/maybemnv/AI-Driven-Patrolling-and-Bandobast-Intelligence-System.git
cd AI-Driven-Patrolling-and-Bandobast-Intelligence-System
uv sync

# Setup database
uv run python init_db.py
uv run alembic upgrade head

# Run API
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

API docs at `http://127.0.0.1:8000/docs`

## Project Structure

```
├── backend/              # FastAPI application
│   ├── main.py           # App entry point
│   ├── routers/          # API endpoints
│   └── security.py       # Auth & rate limiting
├── database/             # Storage layer
│   ├── models.py         # SQLAlchemy models
│   └── vectordb.py       # FAISS vector store
├── rag/                  # RAG pipeline
│   ├── embedder.py       # Sentence-transformers
│   ├── ingestion.py      # Document ingestion
│   └── retriever.py      # Semantic search
├── src/                  # Computer vision
│   ├── detector/         # YOLOv8 + ONNX
│   ├── crowd/            # Crowd analysis
│   ├── alerts/           # Alert engine
│   └── rules/            # Anomaly detection
├── config/               # Configuration
├── scripts/              # Utility scripts
└── tests/                # Test suite
```

## API Endpoints

| Endpoint                | Method | Description             |
| ----------------------- | ------ | ----------------------- |
| `/api/v1/events/ingest` | POST   | Ingest detection events |
| `/api/v1/alerts`        | GET    | Query alerts            |
| `/api/v1/patrol/start`  | POST   | Start patrol session    |
| `/api/v1/rag/query`     | POST   | Semantic search         |
| `/api/v1/rag/ingest`    | POST   | Ingest documents        |
| `/health`               | GET    | Health check            |

## Demo Scripts

```bash
# Object detection demo
uv run python run_detection_demo.py

# Rules engine demo
uv run python run_rules_demo.py

# RAG system test
uv run python -m scripts.test_rag

# Run tests
uv run pytest tests/ -v
```

## Technology Stack

| Component    | Technology                     |
| ------------ | ------------------------------ |
| Detection    | YOLOv8n + ONNX Runtime         |
| Backend      | FastAPI + Pydantic             |
| Database     | SQLAlchemy + SQLite/PostgreSQL |
| Vector Store | FAISS                          |
| Embeddings   | all-MiniLM-L6-v2 (384 dims)    |
| LLM          | Ollama (llama3.1:8b)           |

## Configuration

Edit `config/rules.yaml` for anomaly detection:

```yaml
rules:
  static_object:
    enabled: true
    time_threshold_seconds: 300
  crowd_surge:
    rate_threshold_percent: 50.0
    window_seconds: 120
```

## Documentation

- [Architecture](docs/architecture.md)
- [API Design](docs/api_design.md)
- [Database Schema](docs/database_schema.md)
- [Research](docs/RESEARCH.md)

## License

MIT License - see [LICENSE](LICENSE)
