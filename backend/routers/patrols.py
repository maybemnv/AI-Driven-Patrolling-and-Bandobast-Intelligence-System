"""Patrol management router for web dashboard."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.deps import get_db
from database.models import PatrolSession, PatrolStatus


router = APIRouter()


class PatrolStartRequest(BaseModel):
    officer_id: str
    officer_name: str
    zone: str
    start_latitude: Optional[float] = None
    start_longitude: Optional[float] = None


class PatrolUpdateRequest(BaseModel):
    latitude: float
    longitude: float
    notes: Optional[str] = None


class PatrolEndRequest(BaseModel):
    end_latitude: Optional[float] = None
    end_longitude: Optional[float] = None
    summary: Optional[str] = None


class PatrolResponse(BaseModel):
    id: int
    officer_id: str
    officer_name: str
    zone: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    distance_km: Optional[float] = None

    class Config:
        from_attributes = True


@router.post("/start", response_model=PatrolResponse, status_code=201)
def start_patrol(request: PatrolStartRequest, db: Session = Depends(get_db)):
    """Start a new patrol session from dashboard."""
    now = datetime.utcnow()
    session = PatrolSession(
        officer_id=request.officer_id,
        officer_name=request.officer_name,
        zone=request.zone,
        status=PatrolStatus.ACTIVE,
        start_time=now,
        started_at=now,
        start_latitude=request.start_latitude,
        start_longitude=request.start_longitude,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/{patrol_id}/update")
def update_patrol(patrol_id: int, request: PatrolUpdateRequest, db: Session = Depends(get_db)):
    """Update patrol position and notes."""
    session = db.query(PatrolSession).filter(PatrolSession.id == patrol_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Patrol not found")
    
    if session.status != PatrolStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Patrol is not active")
    
    session.current_latitude = request.latitude
    session.current_longitude = request.longitude
    if request.notes:
        session.notes = (session.notes or "") + f"\n[{datetime.utcnow().isoformat()}] {request.notes}"
    
    db.commit()
    return {"status": "updated"}


@router.post("/{patrol_id}/end", response_model=PatrolResponse)
def end_patrol(patrol_id: int, request: PatrolEndRequest, db: Session = Depends(get_db)):
    """End a patrol session."""
    session = db.query(PatrolSession).filter(PatrolSession.id == patrol_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Patrol not found")
    
    session.status = PatrolStatus.COMPLETED
    session.ended_at = datetime.utcnow()
    session.end_latitude = request.end_latitude
    session.end_longitude = request.end_longitude
    if request.summary:
        session.summary = request.summary
    
    db.commit()
    db.refresh(session)
    return session


@router.get("/active", response_model=list[PatrolResponse])
def list_active_patrols(db: Session = Depends(get_db)):
    """List all currently active patrols."""
    return db.query(PatrolSession).filter(
        PatrolSession.status == PatrolStatus.ACTIVE
    ).all()


@router.get("", response_model=list[PatrolResponse])
def list_patrols(
    zone: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """List patrol sessions."""
    query = db.query(PatrolSession)
    
    if zone:
        query = query.filter(PatrolSession.zone == zone)
    if status:
        query = query.filter(PatrolSession.status == PatrolStatus(status))
    
    return query.order_by(desc(PatrolSession.started_at)).limit(limit).all()


@router.get("/{patrol_id}", response_model=PatrolResponse)
def get_patrol(patrol_id: int, db: Session = Depends(get_db)):
    """Get patrol session details."""
    session = db.query(PatrolSession).filter(PatrolSession.id == patrol_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Patrol not found")
    return session
