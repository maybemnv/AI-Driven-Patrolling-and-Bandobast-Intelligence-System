# Database Schema

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     CAMERAS     │       │     EVENTS      │       │     ALERTS      │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │──┐    │ id (PK)         │──┐    │ id (PK)         │
│ camera_name     │  │    │ camera_id (FK)  │◀─┘    │ event_id (FK)   │◀─┐
│ location_name   │  │    │ timestamp       │       │ alert_type      │  │
│ latitude        │  │    │ event_type      │───────│ severity        │  │
│ longitude       │  └───▶│ confidence_score│       │ message         │  │
│ status          │       │ data (JSON)     │       │ location_lat    │  │
│ installation_dt │       │ processed       │       │ location_lon    │  │
│ last_active_at  │       │ created_at      │       │ acknowledged    │  │
│ extra_data      │       └─────────────────┘       │ acknowledged_by │  │
│ created_at      │                │                │ acknowledged_at │  │
│ updated_at      │                │                │ expires_at      │  │
└─────────────────┘                │                │ created_at      │  │
                                   │                └─────────────────┘  │
                                   │                                     │
                                   └─────────────────────────────────────┘

┌─────────────────┐       ┌─────────────────┐
│ PATROL_SESSIONS │       │    SUMMARIES    │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │──┐    │ id (PK)         │
│ officer_id      │  │    │ summary_type    │
│ officer_name    │  │    │ patrol_sess_id  │◀─┐
│ start_time      │  │    │ reference_date  │  │
│ end_time        │  └───▶│ content         │  │
│ route_data(JSON)│       │ key_insights    │  │
│ status          │       │ risk_score      │  │
│ incidents_count │       │ generated_at    │  │
│ distance_km     │       │ extra_data      │  │
│ created_at      │       └─────────────────┘  │
└─────────────────┘                            │
         │                                     │
         └─────────────────────────────────────┘
```

## Table Definitions

### cameras

| Column            | Type         | Constraints      | Index         |
| ----------------- | ------------ | ---------------- | ------------- |
| id                | INTEGER      | PK, AUTO         | ✓             |
| camera_name       | VARCHAR(100) | NOT NULL         |               |
| location_name     | VARCHAR(200) | NOT NULL         |               |
| latitude          | FLOAT        |                  | ✓ (composite) |
| longitude         | FLOAT        |                  | ✓ (composite) |
| status            | ENUM         | DEFAULT 'active' | ✓             |
| installation_date | DATETIME     |                  |               |
| last_active_at    | DATETIME     |                  |               |
| extra_data        | JSON         | DEFAULT {}       |               |
| created_at        | DATETIME     | DEFAULT NOW      |               |
| updated_at        | DATETIME     | ON UPDATE NOW    |               |

### events

| Column           | Type     | Constraints    | Index         |
| ---------------- | -------- | -------------- | ------------- |
| id               | INTEGER  | PK, AUTO       | ✓             |
| camera_id        | INTEGER  | FK(cameras.id) | ✓ (composite) |
| timestamp        | DATETIME | NOT NULL       | ✓             |
| event_type       | ENUM     | NOT NULL       | ✓ (composite) |
| confidence_score | FLOAT    | DEFAULT 0.0    |               |
| data             | JSON     | DEFAULT {}     |               |
| processed        | BOOLEAN  | DEFAULT FALSE  |               |
| created_at       | DATETIME | DEFAULT NOW    |               |

**Event Types:**

- `object_detected`
- `crowd_detected`
- `crowd_surge`
- `static_object`
- `route_blocked`
- `intrusion`

### alerts

| Column          | Type         | Constraints             | Index         |
| --------------- | ------------ | ----------------------- | ------------- |
| id              | INTEGER      | PK, AUTO                | ✓             |
| event_id        | INTEGER      | FK(events.id), NULLABLE |               |
| alert_type      | VARCHAR(50)  | NOT NULL                |               |
| severity        | ENUM         | DEFAULT 'low'           | ✓             |
| message         | TEXT         | NOT NULL                |               |
| location_lat    | FLOAT        |                         |               |
| location_lon    | FLOAT        |                         |               |
| acknowledged    | BOOLEAN      | DEFAULT FALSE           | ✓ (composite) |
| acknowledged_by | VARCHAR(100) |                         |               |
| acknowledged_at | DATETIME     |                         |               |
| expires_at      | DATETIME     |                         |               |
| created_at      | DATETIME     | DEFAULT NOW             | ✓ (composite) |

**Severity Levels:** `low`, `medium`, `high`, `critical`

### patrol_sessions

| Column          | Type         | Constraints      | Index         |
| --------------- | ------------ | ---------------- | ------------- |
| id              | INTEGER      | PK, AUTO         | ✓             |
| officer_id      | VARCHAR(50)  | NOT NULL         | ✓ (composite) |
| officer_name    | VARCHAR(100) | NOT NULL         |               |
| start_time      | DATETIME     | NOT NULL         | ✓ (composite) |
| end_time        | DATETIME     |                  |               |
| route_data      | JSON         | DEFAULT []       |               |
| status          | ENUM         | DEFAULT 'active' | ✓             |
| incidents_count | INTEGER      | DEFAULT 0        |               |
| distance_km     | FLOAT        | DEFAULT 0.0      |               |
| created_at      | DATETIME     | DEFAULT NOW      |               |

**Status Values:** `active`, `completed`, `cancelled`

### summaries

| Column            | Type     | Constraints  | Index         |
| ----------------- | -------- | ------------ | ------------- |
| id                | INTEGER  | PK, AUTO     | ✓             |
| summary_type      | ENUM     | NOT NULL     | ✓ (composite) |
| patrol_session_id | INTEGER  | FK, NULLABLE |               |
| reference_date    | DATETIME |              |               |
| content           | TEXT     | NOT NULL     |               |
| key_insights      | JSON     | DEFAULT []   |               |
| risk_score        | FLOAT    | DEFAULT 0.0  |               |
| generated_at      | DATETIME | DEFAULT NOW  | ✓ (composite) |
| extra_data        | JSON     | DEFAULT {}   |               |

**Summary Types:** `patrol`, `bandobast`, `daily`, `weekly`

## Vector Database (FAISS)

### Collections

| Collection       | Purpose              | Metadata Fields            |
| ---------------- | -------------------- | -------------------------- |
| patrol_logs      | Session logs for RAG | officer_id, date, location |
| alert_history    | Historical alerts    | severity, type, date       |
| location_context | Location knowledge   | name, category, coords     |

### Embedding Configuration

- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Dimensions: 384
- Distance: L2 (Euclidean)
