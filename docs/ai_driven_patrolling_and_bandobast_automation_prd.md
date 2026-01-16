# Product Requirements Document (PRD)

## 1. Product Overview

### Product Name
AI-Driven Patrolling and Bandobast Intelligence System

### Problem Context
Police operations during routine patrolling and special bandobast events rely heavily on manual monitoring, fragmented data sources, and post-event reporting. This leads to delayed situational awareness, missed early risk indicators, and cognitive overload for officers and command staff.

This system aims to augment police operations by using AI and ML to continuously analyze operational data such as camera feeds, patrol logs, and location context to provide timely insights, alerts, and summaries. The system is assistive, not autonomous, and is designed to support decision-making rather than replace human judgment.

### Objectives
- Improve situational awareness during patrol and bandobast operations
- Reduce manual monitoring burden on officers
- Enable early identification of crowd risks and anomalies
- Generate structured intelligence summaries from raw operational data

---

## 2. Scope Definition

### In Scope
- Crowd density estimation from camera feeds
- Object detection relevant to public safety
- Rule-based anomaly and risk indicators
- AI-generated patrol and bandobast summaries
- Backend APIs for event ingestion and alerting
- RAG-based insight generation over historical data

### Out of Scope
- Crime prediction or forecasting
- Facial recognition or biometric identification
- Automated enforcement or decision making
- Real-time large scale video streaming infrastructure

---

## 3. User Personas

### Primary Users
- Field Police Officers
- Control Room Operators
- Station House Officers
- District Level Supervisors

### Secondary Users
- Data Analysts within police departments
- IT and system administrators

---

## 4. Functional Requirements

### 4.1 Crowd Analysis

**Features**
- Crowd count estimation per camera feed
- Crowd density classification low, medium, high
- Time-based crowd trend analysis

**Functionality**
- Sample frames at fixed intervals
- Detect and count people using object detection
- Aggregate counts over time windows

---

### 4.2 Object Detection

**Features**
- Detection of persons, vehicles, bags and barricades
- Static object persistence tracking

**Functionality**
- Object detection per frame
- Track object presence duration
- Flag static objects beyond threshold time

---

### 4.3 Suspicious Activity Indicators

**Features**
- Crowd surge alerts
- Unusual movement density indicators
- Static object alerts

**Functionality**
- Rule-based heuristics over detected events
- Threshold driven alert generation
- Confidence scoring

---

### 4.4 Alerts and Notifications

**Features**
- Severity based alerts low, medium, high
- Location aware alert context

**Functionality**
- Backend alert engine
- API based alert push to CopMap backend

---

### 4.5 LLM-Based Intelligence Summaries

**Features**
- Patrol session summaries
- Bandobast risk overview
- Pattern and trend insights

**Functionality**
- Periodic summarization jobs
- Context retrieval via vector database
- Cost-aware prompt construction

---

## 5. Non-Functional Requirements

- High precision preferred over high recall
- Explainable outputs
- Low latency for alert generation
- Modular and extensible architecture
- Cost-efficient inference strategy

---

## 6. System Architecture

### High-Level Components
- Camera and data input layer
- AI inference services
- Backend API services
- Vector database for RAG
- LLM inference service
- CopMap integration layer

### Data Flow Summary
1. Camera frames ingested at intervals
2. CV models generate structured events
3. Events stored in backend database
4. Alert engine evaluates risk thresholds
5. LLM generates summaries using RAG
6. Outputs sent to CopMap backend

---

## 7. Technical Stack and Concepts

### AI and ML
- Object Detection: YOLOv8 or equivalent
- Crowd estimation via detected person counts
- Rule-based anomaly detection

### Backend
- Python with FastAPI
- REST based microservices
- Background workers for summarization

### Data Storage
- PostgreSQL for structured data
- Vector DB FAISS or Chroma for embeddings

### LLM and RAG
- Open source LLM Llama or Mistral
- Embedding models Sentence Transformers
- Retrieval augmented summarization

### Infrastructure
- Local or single-node deployment
- Containerized services via Docker

---

## 8. API Design Overview

### Core APIs
- POST /events/ingest
- GET /alerts
- POST /alerts/acknowledge
- POST /summaries/generate
- GET /summaries/{date}

---

## 9. Database Design

### Core Tables
- cameras
- events
- alerts
- patrol_sessions
- summaries

### Vector Store
- Embedded patrol logs
- Historical alert records
- Location metadata

---

## 10. Planning and Pre-Development Design

### Mind Map Focus Areas
- Operational workflows
- Data ingestion paths
- Alert decision points
- LLM usage boundaries

### Design Principles
- Assistive AI only
- Conservative alerting
- Human in the loop
- Explainability over accuracy

---

## 11. Execution Plan and Timeline

### Phase 1 Problem Research and Design 2 days
- Police operations research
- Architecture and PRD finalization
- Diagram creation

### Phase 2 Core AI Implementation 4 days
- Object detection pipeline
- Crowd counting logic
- Event schema definition

### Phase 3 Backend and Alerts 3 days
- API implementation
- Alert engine
- Database integration

### Phase 4 LLM and RAG 3 days
- Embedding pipeline
- Summary generation
- Prompt optimization

### Phase 5 Integration and Outputs 2 days
- CopMap integration mock
- Sample outputs
- Testing

### Phase 6 Documentation and Video 2 days
- README writing
- Diagrams finalization
- Explanation video

Total Estimated Time 16 days

---

## 12. Milestones

- Architecture and PRD approved
- CV pipeline functional
- Alerts generated correctly
- LLM summaries validated
- Final submission ready

---

## 13. Trade-offs and Risks

- Heuristic based anomaly detection chosen over ML due to data scarcity
- Frame sampling over real time streaming for cost efficiency
- Open source models over paid APIs

---

## 14. Sources and Research References

- Open government police SOP documents
- Crowd analysis research papers
- OpenCV and YOLO documentation
- Public surveillance analytics case studies

---

## 15. Goals

### Outcome Goals
- Demonstrate applied AI system design
- Show real world constraint awareness

### Resume Goals
- End to end AI system ownership
- CV, backend and LLM integration

### Self-Oriented Journey Goals
- Improved systems thinking
- Better scope control
- Decision discipline

### Journey-Based Goals
- Strong planning before execution
- Reduced rework and context switching
- Higher execution confidence

---

## 16. Future Improvements

- Multi-camera correlation
- Temporal behavior modeling
- GIS based heatmaps
- Officer feedback loops

