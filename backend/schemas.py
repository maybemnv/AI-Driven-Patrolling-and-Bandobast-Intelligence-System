"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class EventTypeSchema(str, Enum):
    OBJECT_DETECTED = "object_detected"
    CROWD_DETECTED = "crowd_detected"
    STATIC_OBJECT = "static_object"
    CROWD_SURGE = "crowd_surge"
    ROUTE_BLOCKED = "route_blocked"


class AlertSeveritySchema(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PatrolStatusSchema(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SummaryTypeSchema(str, Enum):
    PATROL = "patrol"
    BANDOBAST = "bandobast"
    DAILY = "daily"


# --- Request Schemas ---

class EventIngestRequest(BaseModel):
    camera_id: Optional[int] = None
    timestamp: datetime
    event_type: EventTypeSchema
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)
    data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "camera_id": 1,
                "timestamp": "2026-01-16T21:00:00Z",
                "event_type": "crowd_detected",
                "confidence_score": 0.85,
                "data": {"count": 45, "density": 2.3}
            }
        }


class AlertAcknowledgeRequest(BaseModel):
    acknowledged_by: str = Field(min_length=1, max_length=100)


class PatrolStartRequest(BaseModel):
    officer_id: str = Field(min_length=1, max_length=50)
    officer_name: str = Field(min_length=1, max_length=100)
    initial_location: Optional[Dict[str, float]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "officer_id": "OFF001",
                "officer_name": "Inspector Singh",
                "initial_location": {"lat": 28.6139, "lon": 77.2090}
            }
        }


class PatrolEndRequest(BaseModel):
    session_id: int
    final_location: Optional[Dict[str, float]] = None


class PatrolEventRequest(BaseModel):
    event_type: str
    description: str
    location: Optional[Dict[str, float]] = None


class SummaryGenerateRequest(BaseModel):
    summary_type: SummaryTypeSchema
    reference_id: Optional[int] = None
    reference_date: Optional[datetime] = None


class CameraCreateRequest(BaseModel):
    camera_name: str = Field(min_length=1, max_length=100)
    location_name: str = Field(min_length=1, max_length=200)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# --- Response Schemas ---

class EventResponse(BaseModel):
    id: int
    camera_id: Optional[int]
    timestamp: datetime
    event_type: str
    confidence_score: float
    data: Dict[str, Any]
    processed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: int
    event_id: Optional[int]
    alert_type: str
    severity: str
    message: str
    location_lat: Optional[float]
    location_lon: Optional[float]
    acknowledged: bool
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PatrolSessionResponse(BaseModel):
    id: int
    officer_id: str
    officer_name: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    incidents_count: int
    distance_km: float
    created_at: datetime

    class Config:
        from_attributes = True


class SummaryResponse(BaseModel):
    id: int
    summary_type: str
    patrol_session_id: Optional[int]
    reference_date: Optional[datetime]
    content: str
    key_insights: List[Any]
    risk_score: float
    generated_at: datetime

    class Config:
        from_attributes = True


class CameraResponse(BaseModel):
    id: int
    camera_name: str
    location_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
