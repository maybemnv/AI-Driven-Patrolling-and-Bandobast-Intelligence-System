"""Alerts API router."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.deps import get_db
from backend.schemas import AlertAcknowledgeRequest, AlertResponse, PaginatedResponse
from database.models import Alert, AlertSeverity

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
def list_alerts(
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Alert)
    
    if severity:
        query = query.filter(Alert.severity == AlertSeverity(severity))
    if acknowledged is not None:
        query = query.filter(Alert.acknowledged == acknowledged)
    if start_date:
        query = query.filter(Alert.created_at >= start_date)
    if end_date:
        query = query.filter(Alert.created_at <= end_date)
    
    total = query.count()
    alerts = query.order_by(desc(Alert.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    return PaginatedResponse(
        items=[AlertResponse.model_validate(a) for a in alerts],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/stats")
def alert_stats(db: Session = Depends(get_db)):
    total = db.query(Alert).count()
    unacknowledged = db.query(Alert).filter(Alert.acknowledged == False).count()
    
    by_severity = {}
    for sev in AlertSeverity:
        count = db.query(Alert).filter(Alert.severity == sev).count()
        by_severity[sev.value] = count
    
    return {
        "total": total,
        "unacknowledged": unacknowledged,
        "by_severity": by_severity,
    }


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    request: AlertAcknowledgeRequest,
    db: Session = Depends(get_db),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    alert.acknowledged_by = request.acknowledged_by
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    return {"status": "deleted", "alert_id": alert_id}
