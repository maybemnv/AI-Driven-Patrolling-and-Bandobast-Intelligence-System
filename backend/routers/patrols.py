"""Patrol sessions API router."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.deps import get_db
from backend.schemas import (
    PatrolStartRequest,
    PatrolEndRequest,
    PatrolEventRequest,
    PatrolSessionResponse,
    PaginatedResponse,
)
from database.models import PatrolSession, PatrolStatus, Event, EventType

router = APIRouter()


@router.post("/start", response_model=PatrolSessionResponse, status_code=201)
def start_patrol(request: PatrolStartRequest, db: Session = Depends(get_db)):
    route_data = []
    if request.initial_location:
        route_data.append({
            "lat": request.initial_location.get("lat"),
            "lon": request.initial_location.get("lon"),
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    session = PatrolSession(
        officer_id=request.officer_id,
        officer_name=request.officer_name,
        start_time=datetime.utcnow(),
        route_data=route_data,
        status=PatrolStatus.ACTIVE,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/end", response_model=PatrolSessionResponse)
def end_patrol(request: PatrolEndRequest, db: Session = Depends(get_db)):
    session = db.query(PatrolSession).filter(PatrolSession.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != PatrolStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    if request.final_location:
        route = session.route_data or []
        route.append({
            "lat": request.final_location.get("lat"),
            "lon": request.final_location.get("lon"),
            "timestamp": datetime.utcnow().isoformat(),
        })
        session.route_data = route
    
    session.end_time = datetime.utcnow()
    session.status = PatrolStatus.COMPLETED
    
    duration_hours = (session.end_time - session.start_time).total_seconds() / 3600
    session.distance_km = round(duration_hours * 4, 2)  # Estimate ~4 km/hr walking
    
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=PaginatedResponse)
def list_sessions(
    officer_id: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(PatrolSession)
    
    if officer_id:
        query = query.filter(PatrolSession.officer_id == officer_id)
    if status:
        query = query.filter(PatrolSession.status == PatrolStatus(status))
    if start_date:
        query = query.filter(PatrolSession.start_time >= start_date)
    
    total = query.count()
    sessions = query.order_by(desc(PatrolSession.start_time)).offset((page - 1) * per_page).limit(per_page).all()
    
    return PaginatedResponse(
        items=[PatrolSessionResponse.model_validate(s) for s in sessions],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/{session_id}", response_model=PatrolSessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(PatrolSession).filter(PatrolSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/{session_id}/event")
def add_patrol_event(
    session_id: int,
    request: PatrolEventRequest,
    db: Session = Depends(get_db),
):
    session = db.query(PatrolSession).filter(PatrolSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    event = Event(
        timestamp=datetime.utcnow(),
        event_type=EventType.OBJECT_DETECTED,
        confidence_score=1.0,
        data={
            "patrol_session_id": session_id,
            "event_type": request.event_type,
            "description": request.description,
            "location": request.location,
        },
    )
    db.add(event)
    
    session.incidents_count = (session.incidents_count or 0) + 1
    db.commit()
    db.refresh(event)
    
    return {"status": "recorded", "event_id": event.id, "session_id": session_id}
