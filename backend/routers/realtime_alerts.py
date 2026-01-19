"""Real-time alerts API with WebSocket support."""

import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.deps import get_db
from database.models import Alert, AlertSeverity, AlertStatus


router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections for real-time alerts."""
    
    def __init__(self):
        self.active: list[WebSocket] = []
    
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
    
    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        disconnected = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        
        for ws in disconnected:
            self.disconnect(ws)


manager = ConnectionManager()


class AlertPayload(BaseModel):
    alert_type: str
    severity: str = "medium"
    message: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    message: str
    status: str
    created_at: datetime
    location: Optional[str] = None

    class Config:
        from_attributes = True


@router.websocket("/ws")
async def alerts_websocket(ws: WebSocket):
    """WebSocket endpoint for real-time alert updates."""
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)


@router.post("", response_model=AlertResponse, status_code=201)
async def create_alert(payload: AlertPayload, db: Session = Depends(get_db)):
    """Create new alert and broadcast to dashboard."""
    alert = Alert(
        alert_type=payload.alert_type,
        severity=AlertSeverity(payload.severity),
        message=payload.message,
        location=payload.location,
        latitude=payload.latitude,
        longitude=payload.longitude,
        source=payload.source or "system",
        status=AlertStatus.ACTIVE,
        created_at=datetime.utcnow(),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    await manager.broadcast({
        "type": "new_alert",
        "alert": {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity.value,
            "message": alert.message,
            "location": alert.location,
            "created_at": alert.created_at.isoformat(),
        }
    })
    
    return alert


@router.get("", response_model=list[AlertResponse])
def list_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """List recent alerts."""
    query = db.query(Alert)
    
    if status:
        query = query.filter(Alert.status == AlertStatus(status))
    if severity:
        query = query.filter(Alert.severity == AlertSeverity(severity))
    
    return query.order_by(desc(Alert.created_at)).limit(limit).all()


@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """Acknowledge an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return {"error": "Alert not found"}
    
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    
    return {"status": "acknowledged"}


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Resolve an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return {"error": "Alert not found"}
    
    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.utcnow()
    db.commit()
    
    return {"status": "resolved"}


async def push_alert(alert_data: dict):
    """Push alert to all connected dashboards."""
    await manager.broadcast({"type": "new_alert", "alert": alert_data})
