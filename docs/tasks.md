# AI-Driven Patrolling and Bandobast System

## Complete Implementation Tasks (15 Hours)

---

## TIME ALLOCATION OVERVIEW

| Phase                     | Duration | Key Focus                         |
| ------------------------- | -------- | --------------------------------- |
| Phase 1: Setup & Research | 1.5h     | Environment + Domain Knowledge    |
| Phase 2: System Design    | 2h       | Architecture + Planning           |
| Phase 3: CV/ML Core       | 4h       | Object Detection + Crowd Analysis |
| Phase 4: Backend API      | 3h       | REST API + Database               |
| Phase 5: LLM & RAG        | 3.5h     | Intelligence Summaries            |
| Phase 6: Integration      | 1.5h     | Testing + CopMap Mock             |
| Phase 7: Documentation    | 3h       | README + Diagrams                 |
| Phase 8: Video            | 1h       | Explanation Recording             |
| **TOTAL**                 | **20h**  | **Optimize to 15h**               |

---

## PHASE 1: SETUP & RESEARCH (1.5 hours)

### Task 1.1: Development Environment Setup (30 minutes)

#### Repository Initialization

- [x] Create new GitHub repository with descriptive name
- [x] Initialize with README.md template
- [x] Add LICENSE file (MIT or Apache 2.0)
- [x] Create .gitignore for Python projects
- [x] Set up branch protection (if applicable)

#### Project Structure Creation

- [x] Create root directory structure:
  - `/cv_engine/` - Computer vision processing
  - `/backend/` - FastAPI application
  - `/database/` - Database models and migrations
  - `/rag_engine/` - LLM and RAG implementation
  - `/utils/` - Shared utilities
  - `/config/` - Configuration files
  - `/tests/` - Test files
  - `/data/` - Sample data and test media
  - `/outputs/` - Generated outputs and samples
  - `/docs/` - Documentation and diagrams

#### Python Environment Setup

- [x] Create virtual environment (venv or conda)
- [x] Create requirements.txt with core dependencies
- [x] Install essential packages:
  - Computer Vision: ultralytics, opencv-python, pillow
  - Backend: fastapi, uvicorn, pydantic, python-multipart
  - Database: sqlalchemy, alembic, psycopg2-binary (or sqlite3)
  - LLM/RAG: sentence-transformers, chromadb, langchain
  - Utilities: python-dotenv, pyyaml, requests, numpy, pandas
- [x] Verify installations with version checks
- [x] Document any installation issues encountered

#### Configuration Files Setup

- [x] Create .env.example file with all required variables
- [x] Create config.yaml for application settings
- [x] Set up logging configuration
- [x] Create docker-compose.yml (optional but recommended)
- [x] Add Dockerfile for containerization

#### Development Tools Setup

- [x] Install and configure code formatter (black, autopep8)
- [x] Set up linter (pylint, flake8)
- [x] Configure pre-commit hooks (optional)
- [x] Set up Postman or Thunder Client for API testing

---

### Task 1.2: Police Operations Research (1 hour)

#### Understanding Bandobast Operations

- [x] Research definition and scope of bandobast (special security arrangements)
- [x] Identify typical bandobast scenarios:
  - VIP movements and protocols
  - Public events (rallies, festivals, sports)
  - Religious gatherings
  - Political meetings
  - Emergency situations
- [x] Document key security concerns during bandobast:
  - Crowd management challenges
  - Route security requirements
  - Communication coordination needs
  - Resource allocation issues
- [x] Note personnel roles: field officers, control room, supervisors
- [x] Understand timing: pre-event planning, live monitoring, post-event review

#### Understanding Routine Patrolling

- [x] Research different types of patrol:
  - Beat patrol (fixed area)
  - Mobile patrol (vehicle-based)
  - Foot patrol
  - Nakabandi (checkpoints)
- [x] Identify patrol objectives:
  - Crime prevention through visibility
  - Community engagement
  - Suspicious activity detection
  - Emergency response readiness
- [x] Document current pain points:
  - Manual log entries
  - Delayed incident reporting
  - Limited situational awareness
  - Post-shift report burden
- [x] Understand patrol data: routes, timings, incidents, observations

#### Identifying Realistic AI Use Cases

- [x] List where AI can genuinely help:
  - Automated crowd density monitoring
  - Unusual activity flagging
  - Pattern recognition in incidents
  - Intelligent report summarization
  - Historical data insights
- [x] List what AI should NOT do (avoid over-promising):
  - Replace human judgment
  - Predict specific crimes
  - Make enforcement decisions
  - Identify individuals without context
- [ ] Document ethical boundaries and privacy concerns

#### Understanding False Positive Risks

- [ ] Research consequences of false alerts:
  - Officer alert fatigue
  - Wasted resources on false alarms
  - Reduced trust in system
  - Potential public panic
- [ ] Identify high-risk false positive scenarios:
  - Normal crowds flagged as surges
  - Legitimate objects flagged as suspicious
  - Routine activities flagged as unusual
- [ ] Plan mitigation strategies:
  - Conservative thresholds
  - Confidence score requirements
  - Human verification requirements
  - Alert deduplication logic

#### Research Documentation

- [x] Create RESEARCH.md file in /docs/ folder
- [ ] Write 2-3 paragraph summary of bandobast operations
- [ ] Write 2-3 paragraph summary of patrollin g needs
- [ ] Document 5-7 realistic AI use cases with justification
- [ ] List 3-5 "anti-patterns" (what NOT to build)
- [ ] Include references to any sources consulted
- [ ] Add notes on ethical considerations

---

## PHASE 2: SYSTEM DESIGN & ARCHITECTURE (2 hours)

### Task 2.1: High-Level Architecture Design (1 hour)

#### System Components Identification

- [ ] Define Input Layer components:
  - Camera feed ingestion mechanism
  - Patrol log input system
  - Manual event entry interface
  - GPS/location data integration
- [ ] Define Processing Layer components:
  - Computer vision inference service
  - Event detection and classification
  - Anomaly detection engine
  - Alert generation system
- [ ] Define Storage Layer components:
  - Relational database (events, alerts, sessions)
  - Vector database (embeddings for RAG)
  - Media storage (images, video frames)
  - Cache layer (optional)
- [ ] Define Intelligence Layer components:
  - LLM inference service
  - RAG retrieval system
  - Summary generation engine
  - Pattern analysis module
- [ ] Define Integration Layer components:
  - REST API endpoints
  - Webhook handlers
  - CopMap integration interface
  - Notification system

#### Architecture Diagram Creation

- [ ] Create system architecture diagram showing:
  - All major components
  - Data flow directions
  - Communication protocols
  - External system integrations
- [ ] Add component responsibilities in diagram
- [ ] Show synchronous vs asynchronous operations
- [ ] Indicate scalability points
- [ ] Use standard notation (boxes, arrows, labels)
- [ ] Choose tool: draw.io, Lucidchart, Excalidraw, or Mermaid
- [ ] Export as PNG/SVG for documentation

#### Data Flow Diagram Creation

- [ ] Map end-to-end data flow:
  - Camera frame → CV processing → Event generation
  - Event → Alert engine → Notification
  - Patrol start → Activity logging → Summary generation
  - Query → RAG retrieval → LLM → Response
- [ ] Show decision points in flow
- [ ] Indicate data transformations
- [ ] Mark critical latency points
- [ ] Add error handling paths

#### API Architecture Design

- [ ] Design RESTful API structure
- [ ] Define resource endpoints (events, alerts, patrols, summaries)
- [ ] Plan request/response formats
- [ ] Define authentication/authorization approach
- [ ] Plan versioning strategy (v1, v2)
- [ ] Document rate limiting strategy
- [ ] Plan error response structure

#### Deployment Architecture

- [ ] Define deployment model (single-node, distributed)
- [ ] Plan service containerization approach
- [ ] Design inter-service communication
- [ ] Plan configuration management
- [ ] Define monitoring and logging strategy
- [ ] Document scaling considerations

---

### Task 2.2: Database Schema Design (45 minutes)

#### Core Tables Design

**Cameras Table**

- [ ] Define fields:
  - id (primary key)
  - camera_name (string)
  - location_name (string)
  - latitude (float)
  - longitude (float)
  - status (active/inactive)
  - installation_date
  - last_active_timestamp
  - metadata (JSON for additional info)
- [ ] Define indexes for performance
- [ ] Plan relationships with other tables

**Events Table**

- [ ] Define fields:
  - id (primary key)
  - camera_id (foreign key)
  - timestamp
  - event_type (enum: object_detected, crowd_surge, static_object, etc.)
  - confidence_score (float 0-1)
  - data (JSON with detection details)
  - processed (boolean)
  - created_at
- [ ] Plan partitioning strategy for scale
- [ ] Define indexes on timestamp, camera_id, event_type
- [ ] Design JSON structure for data field

**Alerts Table**

- [ ] Define fields:
  - id (primary key)
  - event_id (foreign key, nullable)
  - alert_type (string)
  - severity (low/medium/high)
  - message (text)
  - location_lat (float)
  - location_lon (float)
  - acknowledged (boolean)
  - acknowledged_by (string, nullable)
  - acknowledged_at (timestamp, nullable)
  - created_at
  - expires_at (nullable)
- [ ] Plan alert lifecycle management
- [ ] Define compound indexes for queries

**Patrol Sessions Table**

- [ ] Define fields:
  - id (primary key)
  - officer_id (string)
  - officer_name (string)
  - start_time
  - end_time (nullable)
  - route_data (JSON with GPS points)
  - status (active/completed)
  - incidents_count (integer)
  - distance_covered (float, km)
  - created_at
- [ ] Plan session tracking mechanism
- [ ] Define relationship with events

**Summaries Table**

- [ ] Define fields:
  - id (primary key)
  - summary_type (patrol/bandobast/daily)
  - reference_id (patrol_session_id or date)
  - content (text)
  - key_insights (JSON array)
  - risk_score (float 0-1)
  - generated_at
  - metadata (JSON)
- [ ] Plan storage optimization for long text
- [ ] Define retention policy

#### Database Diagram Creation

- [ ] Create ER diagram showing all tables
- [ ] Show primary and foreign key relationships
- [ ] Indicate cardinality (one-to-many, etc.)
- [ ] Add field types and constraints
- [ ] Mark indexed fields
- [ ] Use crow's foot notation or similar
- [ ] Export as image for documentation

#### Vector Database Design

- [ ] Choose vector DB (ChromaDB, FAISS, or Pinecone)
- [ ] Design collection structure:
  - patrol_logs collection
  - alert_history collection
  - location_context collection
- [ ] Plan metadata schema for filtering
- [ ] Define embedding dimensions (384 for MiniLM)
- [ ] Design retrieval query patterns
- [ ] Plan periodic reindexing strategy

---

### Task 2.3: Technical Decisions Documentation (15 minutes)

#### Technology Stack Justification

- [ ] Document CV model choice:
  - Why YOLOv8 (speed, accuracy, ease of use)
  - Why not Faster R-CNN or other models
  - Trade-offs: accuracy vs speed
- [ ] Document backend framework choice:
  - Why FastAPI (async, auto-docs, modern)
  - Why not Flask or Django
  - Performance considerations
- [ ] Document database choice:
  - Why PostgreSQL or SQLite
  - Trade-offs: features vs simplicity
  - Scale considerations
- [ ] Document LLM choice:
  - Why local model (Ollama) vs API (GPT-4)
  - Cost implications
  - Latency trade-offs
  - Privacy benefits

#### Design Trade-offs Documentation

- [ ] Frame sampling vs real-time streaming:
  - Decision: Frame sampling every 2-5 seconds
  - Reason: Cost, computational efficiency
  - Trade-off: Slight delay in detection
- [ ] Rule-based vs ML-based anomaly detection:
  - Decision: Rule-based heuristics
  - Reason: No training data, interpretability
  - Trade-off: Less sophisticated detection
- [ ] Synchronous vs asynchronous processing:
  - Decision: Async for CV, sync for API
  - Reason: Non-blocking operations
  - Implementation complexity
- [ ] Local deployment vs cloud:
  - Decision: Local/single-node deployment
  - Reason: Data privacy, cost
  - Trade-off: Limited scalability

#### Create Trade-offs Document

- [ ] Create TRADE_OFFS.md in /docs/
- [ ] List each major decision
- [ ] Explain reasoning for each choice
- [ ] Document alternatives considered
- [ ] Note potential future improvements
- [ ] Be honest about limitations

---

## PHASE 3: CORE CV/ML IMPLEMENTATION (4 hours)

### Task 3.1: Object Detection Pipeline Setup (1.5 hours)

#### YOLOv8 Model Integration

- [x] Download pre-trained YOLOv8 model (yolov8n.pt or yolov8s.pt)
- [x] Create model loader class with singleton pattern
- [x] Implement model initialization with error handling
- [x] Configure inference parameters:
  - Confidence threshold (e.g., 0.5)
  - IoU threshold for NMS (e.g., 0.45)
  - Image size (640x640)
  - Device (CPU/GPU auto-detection)
- [x] Test model loading with sample image
- [x] Document model parameters in config file

#### Frame Extraction Module

- [x] Create frame processor class
- [x] Implement video file loading with OpenCV
- [x] Add support for image file input
- [x] Implement frame extraction at intervals:
  - Time-based sampling (every N seconds)
  - Frame-based sampling (every N frames)
  - Configurable via settings
- [x] Add frame preprocessing:
  - Resize to model input size
  - Normalization
  - Format conversion (BGR to RGB)
- [x] Implement error handling for corrupted files
- [x] Add progress tracking for batch processing

#### Object Detection Implementation

- [x] Create object detector class wrapping YOLOv8
- [x] Implement detection method accepting frame/image
- [x] Parse YOLO output to structured format:
  - Class ID to class name mapping
  - Bounding box coordinates (x, y, w, h)
  - Confidence scores
  - Frame timestamp
- [x] Filter detections by confidence threshold
- [x] Focus on relevant classes:
  - Person (class 0)
  - Car, truck, bus (vehicles)
  - Backpack, suitcase (bags)
  - Any custom classes needed
- [x] Implement visualization function:
  - Draw bounding boxes on frame
  - Add labels with confidence scores
  - Color-code by class type
  - Save annotated images

#### Static Object Tracking Logic

- [ ] Design object tracking data structure:
  - Object ID
  - Class type
  - First seen timestamp
  - Last seen timestamp
  - Location (bounding box center)
  - Movement threshold
- [ ] Implement simple tracking algorithm:
  - Match objects across frames by location
  - Calculate IoU (Intersection over Union)
  - Assign persistent IDs to objects
  - Track dwell time
- [ ] Add static object detection logic:
  - Identify objects in same location across frames
  - Calculate stationary duration
  - Set threshold (e.g., 5 minutes)
  - Generate static object event
- [ ] Implement object removal logic (when object moves/disappears)

#### Event Schema Definition

- [ ] Create Event data model with fields:
  - event_id (UUID)
  - timestamp (ISO format)
  - camera_id
  - event_type (enum)
  - confidence_score
  - data (flexible JSON structure)
  - metadata
- [ ] Define event types:
  - OBJECT_DETECTED
  - CROWD_DETECTED
  - STATIC_OBJECT
  - CROWD_SURGE
  - ROUTE_BLOCKED
- [ ] Create event builder/factory class
- [ ] Implement event validation
- [ ] Add event serialization (to JSON)

#### Testing and Sample Outputs

- [ ] Download 3-5 sample videos/images:
  - Crowd scenes
  - Vehicles and people
  - Static objects (bags)
  - Different lighting conditions
- [ ] Run detection pipeline on all samples
- [ ] Generate annotated output images
- [ ] Save detection events as JSON
- [ ] Verify accuracy and performance
- [ ] Document any issues or limitations
- [ ] Save outputs to /outputs/cv_samples/

---

### Task 3.2: Crowd Analysis Implementation (1.5 hours)

#### Person Counting Logic

- [ ] Create crowd analyzer class
- [ ] Implement person detection counter:
  - Filter YOLO detections for "person" class
  - Count total persons per frame
  - Apply confidence filtering
  - Handle overlapping detections
- [ ] Implement spatial analysis:
  - Define camera coverage area (sqm)
  - Calculate people density (persons/sqm)
  - Divide frame into grid zones
  - Count persons per zone
- [ ] Add temporal aggregation:
  - Store counts in time-series buffer
  - Calculate rolling averages (1 min, 5 min windows)
  - Detect trends (increasing/decreasing)

#### Crowd Density Classification

- [ ] Define density categories based on research:
  - LOW: < 0.5 persons/sqm (normal)
  - MEDIUM: 0.5-2 persons/sqm (moderate)
  - HIGH: 2-4 persons/sqm (crowded)
  - CRITICAL: > 4 persons/sqm (dangerous)
- [ ] Implement classification function
- [ ] Add safety margin/buffer zones
- [ ] Consider camera angle and FOV adjustments
- [ ] Create density heatmap visualization (optional)
- [ ] Document classification thresholds with sources

#### Crowd Surge Detection

- [ ] Implement surge detection algorithm:
  - Compare current density to baseline
  - Calculate rate of change (persons/minute)
  - Set surge threshold (e.g., 50% increase in 2 min)
  - Require sustained increase (not just spike)
- [ ] Add surge severity levels:
  - Minor: 30-50% increase
  - Moderate: 50-100% increase
  - Major: >100% increase
- [ ] Implement false positive reduction:
  - Require minimum initial crowd size
  - Smooth out brief fluctuations
  - Debounce repeated alerts
- [ ] Generate surge event with context:
  - Previous density
  - Current density
  - Rate of change
  - Predicted trend

#### Time-Series Analysis

- [ ] Create time-series data structure for counts
- [ ] Implement sliding window calculations
- [x] Add statistical measures:
  - Mean crowd size over window
  - Standard deviation (volatility)
  - Peak crowd times
  - Trend direction
- [ ] Store historical data for comparison
- [x] Generate time-series visualizations (line charts)

#### Crowd Event Generation

- [x] Define crowd event types:
  - CROWD_NORMAL
  - CROWD_HIGH_DENSITY
  - CROWD_SURGE
  - CROWD_DISPERSAL
- [x] Implement event generation with metadata:
  - Count statistics
  - Density level
  - Trend information
  - Zone-wise breakdown
  - Confidence score
- [x] Add event deduplication logic
- [x] Implement event priority scoring

#### Testing and Validation

- [x] Test with various crowd scenarios:
  - Empty areas (baseline)
  - Small groups (2-10 people)
  - Medium crowds (10-50 people)
  - Large crowds (50+ people)
  - Rapidly changing crowd sizes
- [x] Validate density calculations
- [x] Test surge detection sensitivity
- [x] Generate sample crowd analysis reports
- [x] Save test outputs to /outputs/crowd_analysis/

---

### Task 3.3: Anomaly Detection Rules Engine (1 hour)

#### Rule Engine Architecture

- [ ] Design rule-based system structure:
  - Rule definitions (conditions + actions)
  - Rule evaluator
  - Rule priority system
  - Rule configuration file
- [ ] Create base Rule class/interface
- [ ] Implement rule evaluation pipeline
- [ ] Add rule chaining support
- [ ] Design rule output format

#### Static Object Alert Rule

- [ ] Define rule: "Object stationary > threshold time"
- [ ] Set parameters:
  - Time threshold: 5 minutes (configurable)
  - Allowed object classes: backpack, suitcase, handbag
  - Exclusion zones (where static objects are normal)
- [ ] Implement rule logic:
  - Check object tracking data
  - Calculate dwell time
  - Filter by object class
  - Check location against exclusions
- [ ] Set severity based on:
  - Object type (bag = high, vehicle = low)
  - Location (sensitive area = high)
  - Time of day
- [ ] Generate alert with context:
  - Object class and location
  - First seen and current timestamp
  - Annotated image
  - Recommended action

#### Crowd Surge Alert Rule

- [ ] Define rule: "Rapid crowd density increase"
- [ ] Set parameters:
  - Rate threshold: 50% increase in 2 minutes
  - Minimum initial crowd: 20 people
  - Critical density: > 3 persons/sqm
- [ ] Implement rule logic:
  - Evaluate crowd time-series data
  - Calculate rate of change
  - Check against thresholds
  - Assess safety risk
- [ ] Set severity:
  - LOW: 30-50% increase
  - MEDIUM: 50-100% increase
  - HIGH: >100% increase or critical density
- [ ] Generate alert with:
  - Current and previous counts
  - Rate of increase
  - Density level
  - Safety recommendations

#### Route Blockage Detection Rule

- [ ] Define rule: "Obstacle in designated route"
- [ ] Set parameters:
  - Define route zones (polygon coordinates)
  - Blocking object classes: vehicles, barriers
  - Blockage percentage threshold: 50%
- [ ] Implement rule logic:
  - Check detected objects in route zones
  - Calculate coverage percentage
  - Determine blockage severity
  - Consider time context (planned vs unplanned)
- [ ] Set severity based on:
  - Route importance (VIP route = high)
  - Blockage extent
  - Event timing
- [ ] Generate alert with route visualization

#### After-Hours Activity Rule

- [ ] Define rule: "Activity detected outside normal hours"
- [ ] Set parameters:
  - Normal hours: 6 AM - 10 PM (configurable)
  - Minimum activity threshold
  - Location-specific schedules
- [ ] Implement rule logic:
  - Check current time
  - Detect any significant activity (person/vehicle count)
  - Compare to baseline
  - Filter false positives (security personnel)
- [ ] Set severity: MEDIUM by default
- [ ] Generate alert with activity details

#### Confidence Scoring System

- [ ] Implement confidence calculation per alert:
  - Detection confidence (from CV model)
  - Rule match strength
  - Historical context
  - Environmental factors
- [ ] Combine factors into overall score (0-1)
- [ ] Set minimum confidence threshold for alerts (0.6)
- [ ] Document scoring formula
- [ ] Allow threshold adjustment per rule

#### Alert Deduplication Logic

- [ ] Implement deduplication strategy:
  - Track recent alerts by type and location
  - Set cooldown period (e.g., 5 minutes)
  - Suppress duplicate alerts within period
  - Update existing alert instead of creating new
- [ ] Add alert escalation logic:
  - Increase severity if condition persists
  - Send reminder alerts at intervals
  - Clear alerts when condition resolves

#### Rule Configuration File

- [ ] Create YAML configuration for all rules
- [ ] Define structure:
  - Rule name and description
  - Enable/disable flag
  - Parameters and thresholds
  - Severity levels
  - Alert message templates
- [ ] Implement config loader
- [ ] Add runtime rule reload capability
- [ ] Document configuration options

#### Testing Anomaly Detection

- [ ] Create test scenarios for each rule:
  - Static bag left for 10 minutes
  - Crowd doubling in 1 minute
  - Vehicle blocking route
  - Activity at 2 AM
- [ ] Validate rule triggering
- [ ] Test false positive scenarios
- [ ] Verify confidence scoring
- [ ] Test alert deduplication
- [ ] Generate test alert outputs
- [ ] Save to /outputs/anomaly_detection/

---

## PHASE 4: BACKEND API & DATABASE (3 hours)

### Task 4.1: Database Setup and Models (1 hour)

#### Database Selection and Setup

- [ ] Choose database: PostgreSQL (production) or SQLite (development)
- [ ] Install database (or use containerized version)
- [ ] Create database instance
- [ ] Configure connection parameters in .env file:
  - Database URL
  - Username/password (if applicable)
  - Pool size and connection limits
- [ ] Test database connectivity

#### SQLAlchemy Setup

- [ ] Create database module structure
- [ ] Set up SQLAlchemy engine and session
- [ ] Configure connection pooling
- [ ] Create base model class
- [ ] Set up session management (dependency injection)
- [ ] Implement context managers for transactions
- [ ] Add database initialization function

#### Camera Model Implementation

- [ ] Create Camera model class
- [ ] Define all fields with appropriate types
- [ ] Add constraints (unique, not null)
- [ ] Implement table indexes
- [ ] Add timestamps (created_at, updated_at)
- [ ] Create helper methods:
  - to_dict() for serialization
  - Location validation
  - Status management
- [ ] Document model with docstrings

#### Event Model Implementation

- [ ] Create Event model class
- [ ] Define all fields including JSON data field
- [ ] Set up foreign key to Camera
- [ ] Add indexes on frequently queried fields
- [ ] Implement enum for event_type
- [ ] Create helper methods:
  - Serialization
  - Data validation
  - Confidence score validation
- [ ] Add table partitioning hints (for scale)

#### Alert Model Implementation

- [ ] Create Alert model class
- [ ] Define fields with severity enum
- [ ] Set up foreign key to Event (nullable)
- [ ] Add spatial indexes for lat/lon if supported
- [ ] Implement alert lifecycle methods:
  - acknowledge()
  - expire()
  - is_active()
- [ ] Add alert filtering helpers
- [ ] Create compound indexes for common queries

#### Patrol Session Model Implementation

- [ ] Create PatrolSession model class
- [ ] Define fields for officer and route tracking
- [ ] Implement status enum (active/completed)
- [ ] Add relationship to events
- [ ] Create helper methods:
  - start_session()
  - end_session()
  - add_incident()
  - calculate_duration()
- [ ] Add validation for route_data JSON

#### Summary Model Implementation

- [ ] Create Summary model class
- [ ] Define summary_type enum
- [ ] Implement flexible reference system
- [ ] Add full-text search index on content (if supported)
- [ ] Create JSON fields for structured data
- [ ] Add helper methods for retrieval
- [ ] Implement retention policy logic

#### Database Migration Setup

- [ ] Install and configure Alembic
- [ ] Initialize Alembic in project
- [ ] Create initial migration for all models
- [ ] Test migration up and down
- [ ] Create seed data migration:
  - 3-5 sample cameras
  - Sample locations
  - Initial configuration
- [ ] Document migration commands
- [ ] Create database reset script for development

#### Database Utilities

- [ ] Create database initialization script
- [ ] Implement connection health check
- [ ] Add database backup utility (optional)
- [ ] Create data seeding functions
- [ ] Implement cleanup utilities:
  - Old events purge
  - Expired alerts cleanup
  - Summary retention management
- [ ] Add database statistics queries

---

### Task 4.2: FastAPI Application Structure (1.5 hours)

#### FastAPI App Initialization

- [ ] Create main FastAPI application instance
- [ ] Configure CORS middleware
- [ ] Set up exception handlers
- [ ] Add request logging middleware
- [ ] Configure API metadata (title, description, version)
- [ ] Set up API versioning (/api/v1)
- [ ] Create startup and shutdown event handlers
- [ ] Implement health check endpoint

#### Pydantic Schemas Creation

- [ ] Create schemas module
- [ ] Define request schemas:
  - EventIngestRequest
  - AlertAcknowledgeRequest
  - PatrolStartRequest
  - PatrolEndRequest
  - SummaryGenerateRequest
- [ ] Define response schemas:
  - EventResponse
  - AlertResponse
  - PatrolSessionResponse
  - SummaryResponse
  - ErrorResponse
- [ ] Add validation rules:
  - Field constraints (min/max)
  - Custom validators
  - Regex patterns
- [ ] Implement schema inheritance for common fields
- [ ] Add example values for documentation

#### Events API Endpoints

- [ ] Create events router
- [ ] Implement POST /api/v1/events/ingest:
  - Accept event data
  - Validate schema
  - Store in database
  - Trigger alert engine
  - Return event ID
- [ ] Implement GET /api/v1/events:
  - Support filtering by:
    - camera_id
    - event_type
    - date range
    - processed status
  - Add pagination
  - Return sorted results
- [ ] Implement GET /api/v1/events/{event_id}:
  - Retrieve single event
  - Include related data
  - Handle not found
- [ ] Add request validation and error handling
- [ ] Document with OpenAPI descriptions

#### Alerts API Endpoints

- [ ] Create alerts router
- [ ] Implement GET /api/v1/alerts:
  - Filter by severity, status, date
  - Support location-based queries
  - Add pagination and sorting
  - Return alert count
- [ ] Implement GET /api/v1/alerts/{alert_id}:
  - Retrieve alert details
  - Include related event data
  - Add location information
- [ ] Implement POST /api/v1/alerts/{alert_id}/acknowledge:
  - Mark alert as acknowledged
  - Record acknowledging user
  - Timestamp action
  - Return updated alert
- [ ] Implement DELETE /api/v1/alerts/{alert_id}:
  - Soft delete or mark as resolved
  - Require authorization
  - Log action
- [ ] Add alert statistics endpoint

#### Patrol API Endpoints

- [ ] Create patrol router
- [ ] Implement POST /api/v1/patrol/start:
  - Create new patrol session
  - Validate officer ID
  - Store initial location
  - Return session ID
- [ ] Implement POST /api/v1/patrol/end:
  - End active session
  - Calculate duration and distance
  - Trigger summary generation
  - Return session summary
- [ ] Implement GET /api/v1/patrol/sessions:
  - List patrol sessions
  - Filter by officer, date, status
  - Add pagination
- [ ] Implement GET /api/v1/patrol/{session_id}:
  - Retrieve session details
  - Include all events during patrol
  - Show route if available
  - Calculate statistics
- [ ] Implement POST /api/v1/patrol/{session_id}/event:
  - Add event to patrol session
  - Link event to session
  - Update session statistics

#### Summaries API Endpoints

- [ ] Create summaries router
- [ ] Implement POST /api/v1/summaries/generate:
  - Accept summary type and parameters
  - Trigger async summary generation
  - Return job ID or summary
  - Handle errors gracefully
- [ ] Implement GET /api/v1/summaries:
  - List summaries by type, date
  - Support search/filtering
  - Add pagination
  - Return metadata only
- [ ] Implement GET /api/v1/summaries/{summary_id}:
  - Retrieve full summary content
  - Include key insights
  - Show generation metadata
  - Format for readability

#### Error Handling and Validation

- [ ] Create custom exception classes:
  - ValidationError
  - NotFoundError
  - DatabaseError
  - ExternalServiceError
- [ ] Implement global exception handler
- [ ] Add structured error responses

**port YOLOv8 to ONNX:**

bash

```bash
# After training or loading YOLOv8 model
yolo exportmodel=yolov8n.pt format=onnx
```

**2. Add to Requirements:**

```
onnxruntime  # For CPU
onnxruntime-gpu  # If GPU available
```

**3. Update Your Tasks.md:**
Add these tasks under CV Implementation:

- [ ] Export YOLOv8 model to ONNX format (5 min)
- [ ] Install onnxruntime package
- [ ] Load ONNX model using onnxruntime.InferenceSession
- [ ] Benchmark: Compare PyTorch vs ONNX inference speed
- [ ] Document performance improvements in README
