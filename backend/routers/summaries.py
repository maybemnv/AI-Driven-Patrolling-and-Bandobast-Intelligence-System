"""Summaries API router."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.deps import get_db
from backend.schemas import SummaryGenerateRequest, SummaryResponse, PaginatedResponse
from database.models import Summary, SummaryType

router = APIRouter()


@router.post("/generate", response_model=SummaryResponse, status_code=201)
def generate_summary(request: SummaryGenerateRequest, db: Session = Depends(get_db)):
    content = f"Summary generated for {request.summary_type.value}"
    
    if request.summary_type.value == "patrol" and request.reference_id:
        content = f"Patrol session {request.reference_id} completed. Officer completed assigned route with no major incidents."
    elif request.summary_type.value == "bandobast":
        content = "Bandobast deployment summary: All positions manned. Crowd levels normal throughout event."
    elif request.summary_type.value == "daily":
        content = f"Daily summary for {datetime.now().strftime('%Y-%m-%d')}: Normal operations. No critical alerts."
    
    summary = Summary(
        summary_type=SummaryType(request.summary_type.value),
        patrol_session_id=request.reference_id if request.summary_type.value == "patrol" else None,
        reference_date=request.reference_date or datetime.utcnow(),
        content=content,
        key_insights=["Operations normal", "No critical incidents"],
        risk_score=0.2,
        generated_at=datetime.utcnow(),
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary


@router.get("", response_model=PaginatedResponse)
def list_summaries(
    summary_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Summary)
    
    if summary_type:
        query = query.filter(Summary.summary_type == SummaryType(summary_type))
    if start_date:
        query = query.filter(Summary.generated_at >= start_date)
    
    total = query.count()
    summaries = query.order_by(desc(Summary.generated_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    return PaginatedResponse(
        items=[SummaryResponse.model_validate(s) for s in summaries],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/{summary_id}", response_model=SummaryResponse)
def get_summary(summary_id: int, db: Session = Depends(get_db)):
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary
