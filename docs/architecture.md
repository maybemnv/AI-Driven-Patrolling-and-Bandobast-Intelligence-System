# System Architecture

## Overview

The AI-Driven Patrolling and Bandobast Intelligence System is a modular, assistive AI platform designed to augment police operations through real-time crowd analysis, object detection, and intelligent summarization.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INTEGRATION LAYER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  REST API   │  │  Webhooks   │  │   CopMap    │  │   Alerts    │        │
│  │  (FastAPI)  │  │  Handlers   │  │ Integration │  │  Push/SSE   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INTELLIGENCE LAYER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │     LLM     │  │     RAG     │  │   Summary   │  │   Pattern   │        │
│  │  (Ollama)   │  │  Retrieval  │  │  Generator  │  │  Analysis   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROCESSING LAYER                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  CV Engine  │  │   Crowd     │  │   Anomaly   │  │    Alert    │        │
│  │  (YOLOv8)   │  │  Analyzer   │  │   Engine    │  │   Engine    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                            STORAGE LAYER                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   SQLite/   │  │    FAISS    │  │    Media    │  │    Redis    │        │
│  │  PostgreSQL │  │  VectorDB   │  │   Storage   │  │   (Cache)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                             INPUT LAYER                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Camera    │  │   Patrol    │  │   Manual    │  │    GPS      │        │
│  │   Feeds     │  │    Logs     │  │   Events    │  │   Data      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Input Layer

| Component     | Description                        | Implementation         |
| ------------- | ---------------------------------- | ---------------------- |
| Camera Feeds  | Video/image ingestion at intervals | `FrameProcessor` class |
| Patrol Logs   | Officer activity and route data    | API endpoint + DB      |
| Manual Events | User-reported incidents            | API endpoint           |
| GPS Data      | Location tracking from devices     | JSON in PatrolSession  |

### Processing Layer

| Component      | Description                     | Implementation                  |
| -------------- | ------------------------------- | ------------------------------- |
| CV Engine      | YOLOv8 object detection         | `ModelLoader`, `ObjectDetector` |
| Crowd Analyzer | Density, zones, surge detection | `CrowdAnalyzer` class           |
| Anomaly Engine | Rule-based heuristics           | `AlertEngine` (planned)         |
| Alert Engine   | Threshold-based alerts          | `CrowdEventBuilder`             |

### Storage Layer

| Component     | Description                | Implementation                   |
| ------------- | -------------------------- | -------------------------------- |
| Relational DB | Events, alerts, sessions   | SQLite/PostgreSQL via SQLAlchemy |
| Vector DB     | Embeddings for RAG         | FAISS with persistence           |
| Media Storage | Annotated frames, heatmaps | Local filesystem (`outputs/`)    |
| Cache         | Session/config caching     | Redis (optional)                 |

### Intelligence Layer

| Component         | Description                | Implementation                |
| ----------------- | -------------------------- | ----------------------------- |
| LLM               | Local inference            | Ollama (Llama/Mistral)        |
| RAG Retrieval     | Context from vector DB     | FAISS + sentence-transformers |
| Summary Generator | Patrol/bandobast summaries | LLM + prompt templates        |
| Pattern Analysis  | Historical trend detection | Time-series analysis          |

### Integration Layer

| Component          | Description            | Implementation |
| ------------------ | ---------------------- | -------------- |
| REST API           | CRUD operations        | FastAPI        |
| Webhooks           | External notifications | POST callbacks |
| CopMap Integration | Mock interface         | API client     |
| Notifications      | Alert delivery         | SSE/WebSocket  |

## Technology Stack

| Layer            | Technology                            |
| ---------------- | ------------------------------------- |
| API Framework    | FastAPI (async, OpenAPI docs)         |
| CV/ML            | Ultralytics YOLOv8, OpenCV            |
| Database         | SQLAlchemy + SQLite/PostgreSQL        |
| Vector DB        | FAISS (faiss-cpu)                     |
| LLM              | Ollama (local), sentence-transformers |
| Containerization | Docker + docker-compose               |
| Configuration    | YAML + python-dotenv                  |
