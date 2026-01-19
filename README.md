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
| **Dashboard**         | React-based real-time command center                  |

## Quick Start

### 1. Backend Setup

```bash
# Clone repository
git clone https://github.com/maybemnv/AI-Driven-Patrolling-and-Bandobast-Intelligence-System.git
cd AI-Driven-Patrolling-and-Bandobast-Intelligence-System
uv sync

# Setup database
uv run python init_db.py
uv run alembic upgrade head

# Run API
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

API docs available at `http://127.0.0.1:8000/docs`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Dashboard available at `http://localhost:3001` or `http://localhost:5173`.

## Testing & Validation

We provide a comprehensive suite of scripts for testing and benchmarking.

### Integration Tests

Run full end-to-end scenarios (Crowd, Static Object, Patrol, Summaries):

```bash
uv run python run_integration_tests.py
```

### Performance Benchmarks

Measure CV FPS, DB Latency, and LLM Speed:

```bash
uv run python run_performance_tests.py
```

### Deployment Validation

Verify environment variables, CopMap connectivity, and Docker config:

```bash
uv run python scripts/validate_deployment.py
```

## Project Structure

```
├── backend/              # FastAPI application
│   ├── main.py           # App entry point
│   ├── routers/          # API endpoints
│   └── copmap.py         # CopMap integration
├── frontend/             # React Dashboard
├── database/             # Storage layer
├── rag/                  # RAG pipeline
├── src/                  # Computer vision components
│   ├── detector/         # YOLOv8 + ONNX
│   ├── crowd/            # Crowd analysis
│   └── events/           # Event generation
├── scripts/              # Validation & Utility scripts
├── outputs/              # Generated artifacts & reports
└── docs/                 # Documentation
```

## Configuration

- **Environment**: Copy `.env.example` to `.env` and set `DATABASE_URL` and `GROQ_API_KEY`.
- **Rules**: Edit `config/rules.yaml` for anomaly detection thresholds.

## Troubleshooting

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for solutions to common problems (e.g., `onnxruntime` installation, missing columns).

## Technology Stack

| Component    | Technology                     |
| ------------ | ------------------------------ |
| Detection    | YOLOv8n + ONNX Runtime         |
| Backend      | FastAPI + Pydantic             |
| Frontend     | React + Vite + Lucide          |
| Database     | SQLAlchemy + SQLite/PostgreSQL |
| Vector Store | FAISS                          |
| LLM          | Groq (Llama3-8b/70b)           |

## License

MIT License - see [LICENSE](LICENSE)
