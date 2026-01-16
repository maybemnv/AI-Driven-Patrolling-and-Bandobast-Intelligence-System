"""Events API router."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.deps import get_db
from backend.schemas import EventIngestRequest, EventResponse, PaginatedResponse
from database.models import Event, EventType

router = APIRouter()


@router.post("/ingest", response_model=EventResponse, status_code=201)
def ingest_event(request: EventIngestRequest, db: Session = Depends(get_db)):
    event = Event(
        camera_id=request.camera_id,
        timestamp=request.timestamp,
        event_type=EventType(request.event_type.value),
        confidence_score=request.confidence_score,
        data=request.data,
        processed=False,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=PaginatedResponse)
def list_events(
    camera_id: Optional[int] = None,
    event_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    processed: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Event)
    
    if camera_id:
        query = query.filter(Event.camera_id == camera_id)
    if event_type:
        query = query.filter(Event.event_type == EventType(event_type))
    if start_date:
        query = query.filter(Event.timestamp >= start_date)
    if end_date:
        query = query.filter(Event.timestamp <= end_date)
    if processed is not None:
        query = query.filter(Event.processed == processed)
    
    total = query.count()
    events = query.order_by(desc(Event.timestamp)).offset((page - 1) * per_page).limit(per_page).all()
    
    return PaginatedResponse(
        items=[EventResponse.model_validate(e) for e in events],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.patch("/{event_id}/process")
def mark_processed(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.processed = True
    db.commit()
    return {"status": "processed", "event_id": event_id}
