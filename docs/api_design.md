# API Design

## Base URL

```
/api/v1
```

## Authentication

- API Key header: `X-API-Key: <key>`
- Optional: JWT for user sessions

## Endpoints

### Events

#### POST /events

Ingest detection event.

**Request:**

```json
{
  "camera_id": 1,
  "event_type": "object_detected",
  "confidence_score": 0.85,
  "timestamp": "2026-01-16T12:00:00Z",
  "data": {
    "class_name": "person",
    "bbox": { "x": 100, "y": 50, "w": 80, "h": 200 },
    "count": 5
  }
}
```

**Response:** `201 Created`

```json
{
  "id": 123,
  "status": "created"
}
```

#### GET /events

List events with filters.

**Query Params:**

- `camera_id` (int)
- `event_type` (string)
- `start_time`, `end_time` (ISO datetime)
- `limit` (int, default 50)
- `offset` (int)

**Response:** `200 OK`

```json
{
  "events": [...],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

---

### Alerts

#### GET /alerts

List active alerts.

**Query Params:**

- `severity` (low/medium/high/critical)
- `acknowledged` (bool)
- `limit`, `offset`

**Response:**

```json
{
  "alerts": [
    {
      "id": 1,
      "alert_type": "crowd_surge",
      "severity": "high",
      "message": "Crowd surge detected at Gate 3",
      "location": { "lat": 19.076, "lon": 72.877 },
      "acknowledged": false,
      "created_at": "2026-01-16T12:00:00Z"
    }
  ]
}
```

#### POST /alerts/{id}/acknowledge

Acknowledge an alert.

**Request:**

```json
{
  "acknowledged_by": "Officer Singh"
}
```

**Response:** `200 OK`

---

### Patrols

#### POST /patrols/start

Start patrol session.

**Request:**

```json
{
  "officer_id": "OFF001",
  "officer_name": "Constable Kumar",
  "location": { "lat": 19.076, "lon": 72.877 }
}
```

**Response:** `201 Created`

```json
{
  "session_id": 45,
  "start_time": "2026-01-16T08:00:00Z"
}
```

#### POST /patrols/{id}/end

End patrol session.

#### POST /patrols/{id}/location

Update GPS location.

**Request:**

```json
{
  "lat": 19.078,
  "lon": 72.879,
  "timestamp": "2026-01-16T08:30:00Z"
}
```

---

### Summaries

#### POST /summaries/generate

Generate summary for patrol/date.

**Request:**

```json
{
  "summary_type": "patrol",
  "reference_id": 45
}
```

**Response:** `202 Accepted`

```json
{
  "job_id": "abc123",
  "status": "processing"
}
```

#### GET /summaries/{id}

Get generated summary.

**Response:**

```json
{
  "id": 1,
  "summary_type": "patrol",
  "content": "Patrol completed covering 5.2 km...",
  "key_insights": ["No incidents", "High crowd at Market"],
  "risk_score": 0.2,
  "generated_at": "2026-01-16T16:00:00Z"
}
```

---

### Cameras

#### GET /cameras

List all cameras.

#### POST /cameras

Register new camera.

#### GET /cameras/{id}/status

Get camera health status.

---

## Error Responses

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid event_type",
    "details": {
      "field": "event_type",
      "allowed": ["object_detected", "crowd_surge"]
    }
  }
}
```

**Status Codes:**

- `400` - Validation error
- `401` - Unauthorized
- `404` - Not found
- `429` - Rate limited
- `500` - Internal error

## Rate Limiting

| Endpoint        | Limit   |
| --------------- | ------- |
| POST /events    | 100/min |
| GET endpoints   | 200/min |
| POST /summaries | 10/min  |

Headers:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
