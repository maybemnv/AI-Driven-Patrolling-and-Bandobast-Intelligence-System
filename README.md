# AI-Driven Patrolling and Bandobast Intelligence System

A computer vision and NLP-powered surveillance intelligence platform designed to augment police operations during routine patrolling and special security arrangements (bandobast).

---

## Project Status

| Phase                        | Status      | Progress |
| ---------------------------- | ----------- | -------- |
| System Design & Architecture | Complete    | 100%     |
| Computer Vision Pipeline     | Complete    | 100%     |
| Backend API Development      | Complete    | 100%     |
| Anomaly Detection Engine     | Complete    | 100%     |
| LLM & RAG Integration        | In Progress | 40%      |
| Testing & Integration        | Pending     | 0%       |

**Current Focus:** Implementing RAG-based intelligence summaries with local LLM inference.

---

## Problem Statement

Police departments managing large-scale events and routine patrols face operational challenges:

1. **Information Overload** - Manual monitoring of multiple camera feeds leads to delayed situational awareness
2. **Documentation Gaps** - Paper-based patrol logs lack structure for pattern analysis
3. **Reactive Response** - Limited ability to detect anomalies before escalation
4. **Post-Incident Analysis** - Time-consuming without structured, searchable data

This system addresses these gaps through automated event detection, intelligent alerting, and AI-generated operational summaries.

---

## Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Input Sources                           │
│   Camera Feeds  │  Patrol Logs  │  GPS Data  │  Manual Entry │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   Processing Pipeline                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ CV Engine    │  │ Rule Engine  │  │ Alert Engine │       │
│  │ YOLOv8+ONNX  │─▶│ Anomaly Det. │─▶│ Deduplication│       │
│  │ 31.5 FPS     │  │ 4 Rules      │  │ Priority     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    Storage Layer                             │
│                                                              │
│  SQLite/PostgreSQL           │  FAISS Vector Store           │
│  • Events, Alerts, Sessions  │  • Semantic Search            │
│  • Cameras, Summaries        │  • RAG Context Retrieval      │
│                                                              │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                 Intelligence Layer                           │
│                                                              │
│  Ollama (llama3.1:8b)  │  RAG Pipeline  │  Summary Generator │
│                                                              │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    API Layer                                 │
│  FastAPI REST API  │  Swagger UI  │  CopMap Integration      │
└─────────────────────────────────────────────────────────────┘
```

---

## Technical Implementation

### Computer Vision Pipeline

| Component        | Implementation           | Performance                         |
| ---------------- | ------------------------ | ----------------------------------- |
| Object Detection | YOLOv8n exported to ONNX | 31.7ms inference                    |
| Object Tracking  | IoU-based matching       | Persistent IDs                      |
| Crowd Analysis   | Density classification   | 4 levels (LOW/MEDIUM/HIGH/CRITICAL) |
| Static Detection | Dwell time tracking      | Configurable threshold              |

**Optimization:** ONNX Runtime provides 1.47x speedup over PyTorch inference.

### Anomaly Detection Rules

The rule engine evaluates incoming events against configurable detection rules:

| Rule           | Trigger Condition                   | Severity                |
| -------------- | ----------------------------------- | ----------------------- |
| Static Object  | Object stationary > 5 minutes       | Based on object class   |
| Crowd Surge    | Density increase > 50% in 2 minutes | Based on rate of change |
| Route Blockage | > 50% route coverage by obstacles   | Based on route priority |
| After Hours    | Activity outside 6AM-10PM           | Medium (configurable)   |

All rules support confidence scoring, alert deduplication, and YAML-based configuration.

### REST API

Built with FastAPI, the API provides:

| Endpoint                          | Method | Description                   |
| --------------------------------- | ------ | ----------------------------- |
| `/api/v1/events/ingest`           | POST   | Ingest detection events       |
| `/api/v1/events`                  | GET    | Query events with filters     |
| `/api/v1/alerts`                  | GET    | Retrieve active alerts        |
| `/api/v1/alerts/{id}/acknowledge` | POST   | Acknowledge alert             |
| `/api/v1/patrol/start`            | POST   | Initialize patrol session     |
| `/api/v1/patrol/end`              | POST   | Complete patrol session       |
| `/api/v1/summaries/generate`      | POST   | Generate intelligence summary |
| `/api/v1/cameras`                 | CRUD   | Camera management             |

Full API documentation available at `/docs` (Swagger UI) when server is running.

### Database Schema

Five core tables with SQLAlchemy ORM:

- **cameras** - Camera metadata and location
- **events** - Detection events with JSON payload
- **alerts** - Generated alerts with lifecycle tracking
- **patrol_sessions** - Officer patrol tracking
- **summaries** - LLM-generated intelligence reports

Migrations managed with Alembic.

---

## Technology Stack

| Layer        | Technology            | Rationale                                         |
| ------------ | --------------------- | ------------------------------------------------- |
| Detection    | YOLOv8 + ONNX Runtime | Balance of accuracy and inference speed           |
| Backend      | FastAPI + Pydantic    | Async support, automatic validation, OpenAPI docs |
| Database     | SQLAlchemy + Alembic  | ORM with migration support                        |
| Vector Store | FAISS                 | Fast similarity search for RAG                    |
| LLM          | Ollama (local)        | Privacy-preserving, no API costs                  |
| Embeddings   | sentence-transformers | MiniLM-L6-v2 (384 dimensions)                     |

---

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

```bash
# Clone and install
git clone https://github.com/maybemnv/AI-Driven-Patrolling-and-Bandobast-Intelligence-System.git
cd AI-Driven-Patrolling-and-Bandobast-Intelligence-System
uv sync

# Initialize database
uv run python init_db.py
uv run alembic upgrade head
uv run python scripts/seed_db.py

# Start API server
uv run uvicorn backend.main:app --reload
```

### Verification

```bash
# Run detection demo
uv run python run_detection_demo.py

# Run rules engine demo
uv run python run_rules_demo.py

# Benchmark inference
uv run python benchmark_onnx.py

# Run tests
uv run pytest tests/ -v
```

---

## Roadmap

### Completed

- [x] YOLOv8 detection with ONNX optimization
- [x] Static object and crowd tracking
- [x] Rule-based anomaly detection engine
- [x] FastAPI backend with full CRUD
- [x] Database schema and migrations
- [x] FAISS vector store setup

### In Progress

- [ ] LLM integration with Ollama
- [ ] RAG pipeline for context retrieval
- [ ] Patrol summary generation
- [ ] Bandobast risk assessment reports

### Planned

- [ ] CopMap webhook integration
- [ ] End-to-end testing suite
- [ ] Docker deployment configuration
- [ ] Performance benchmarking at scale

---

## Documentation

| Document                                           | Description                           |
| -------------------------------------------------- | ------------------------------------- |
| [docs/RESEARCH.md](docs/RESEARCH.md)               | Domain research and use case analysis |
| [docs/architecture.md](docs/architecture.md)       | System design documentation           |
| [docs/api_design.md](docs/api_design.md)           | API specification                     |
| [docs/database_schema.md](docs/database_schema.md) | ER diagrams and schema details        |
| [docs/TRADE_OFFS.md](docs/TRADE_OFFS.md)           | Technical decision rationale          |

---

## License

MIT License - see [LICENSE](LICENSE) for details.
