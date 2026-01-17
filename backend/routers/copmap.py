"""CopMap integration router for alert webhooks."""

from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.deps import get_db
from database.models import Alert, AlertSeverity

router = APIRouter()


class CopMapAlertPayload(BaseModel):
    alert_type: str = Field(..., description="Type of alert")
    severity: str = Field(..., description="Alert severity: low, medium, high, critical")
    priority: Optional[str] = Field(None, description="Priority level")
    priority_score: Optional[float] = Field(None, ge=0, le=1)
    message: str = Field(..., description="Alert message")
    description: Optional[str] = None
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lon: Optional[float] = Field(None, ge=-180, le=180)
    camera_id: Optional[str] = None
    recommended_action: Optional[str] = None
    occurrence_count: int = Field(1, ge=1)
    media_ref: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "alert_type": "crowd_surge",
                "severity": "high",
                "priority": "high",
                "message": "Crowd surge detected at Gate 3",
                "description": "Crowd increased from 50 to 120 people in 2 minutes",
                "location_lat": 28.6139,
                "location_lon": 77.2090,
                "camera_id": "CAM_GATE3",
                "recommended_action": "Deploy crowd control personnel",
            }
        }


class CopMapWebhookResponse(BaseModel):
    status: str
    alert_id: int
    copmap_ref: Optional[str] = None
    message: str


class MockCopMapReceivePayload(BaseModel):
    alerts: List[CopMapAlertPayload]


@router.post("/alerts", response_model=CopMapWebhookResponse, summary="Send alert to CopMap")
def send_alert_to_copmap(
    payload: CopMapAlertPayload,
    db: Session = Depends(get_db),
):
    """
    Send an alert for CopMap integration.
    
    This endpoint accepts alert data, stores it in the database,
    and formats it for CopMap webhook consumption.
    """
    try:
        severity = AlertSeverity(payload.severity.lower())
    except ValueError:
        severity = AlertSeverity.MEDIUM
    
    alert = Alert(
        alert_type=payload.alert_type,
        severity=severity,
        message=payload.message,
        location_lat=payload.location_lat,
        location_lon=payload.location_lon,
        expires_at=None,
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    copmap_ref = f"COPMAP-{alert.id:06d}"
    
    return CopMapWebhookResponse(
        status="accepted",
        alert_id=alert.id,
        copmap_ref=copmap_ref,
        message="Alert queued for CopMap delivery",
    )


@router.post("/mock-receiver", summary="Mock CopMap receiver for testing")
def mock_copmap_receiver(payload: MockCopMapReceivePayload):
    """
    Mock endpoint simulating CopMap receiving alerts.
    Used for integration testing.
    """
    received = []
    for alert in payload.alerts:
        received.append({
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "location": {"lat": alert.location_lat, "lon": alert.location_lon},
            "received_at": datetime.now(timezone.utc).isoformat(),
        })
    
    return {
        "status": "received",
        "count": len(received),
        "alerts": received,
    }


@router.get("/sample-payload", summary="Get sample CopMap payload")
def get_sample_payload():
    """Returns a sample payload format for CopMap integration."""
    return {
        "webhook_format": {
            "alert_id": "string (UUID)",
            "alert_type": "string",
            "severity": "low | medium | high | critical",
            "priority": "low | medium | high | critical",
            "priority_score": "float (0-1)",
            "location": {"lat": "float", "lon": "float"},
            "message": "string",
            "description": "string",
            "timestamp": "ISO 8601 datetime",
            "recommended_action": "string",
            "occurrence_count": "integer",
            "media_ref": "string (URL or path)",
            "metadata": "object",
        },
        "example": CopMapAlertPayload.Config.json_schema_extra["example"],
    }
