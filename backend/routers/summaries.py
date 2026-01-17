"""Summaries API router with LLM-powered generation."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.deps import get_db
from backend.schemas import SummaryGenerateRequest, SummaryResponse, PaginatedResponse
from database.models import Summary, SummaryType
from llm.summarizer import get_summary_generator


router = APIRouter()


class PatrolSummaryRequest(BaseModel):
    patrol_session_id: int


class BandobastReportRequest(BaseModel):
    event_name: str
    location: str
    expected_crowd: int
    date: Optional[str] = None


class DailyBriefRequest(BaseModel):
    date: Optional[str] = None


class GeneratedSummaryResponse(BaseModel):
    summary_type: str
    content: dict
    raw_text: str
    tokens_used: int
    duration_ms: float
    success: bool
    error: Optional[str] = None
    markdown: Optional[str] = None


@router.post("/generate/patrol", response_model=GeneratedSummaryResponse)
def generate_patrol_summary(
    request: PatrolSummaryRequest,
    db: Session = Depends(get_db),
):
    """Generate AI-powered patrol session summary."""
    generator = get_summary_generator()
    
    if not generator.llm.is_available():
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    
    result = generator.generate_patrol_summary(request.patrol_session_id, db)
    
    if result.success:
        generator.save_summary(result, str(request.patrol_session_id), db)
    
    return GeneratedSummaryResponse(
        summary_type=result.summary_type,
        content=result.content,
        raw_text=result.raw_text,
        tokens_used=result.tokens_used,
        duration_ms=result.duration_ms,
        success=result.success,
        error=result.error,
        markdown=result.to_markdown() if result.success else None,
    )


@router.post("/generate/bandobast", response_model=GeneratedSummaryResponse)
def generate_bandobast_report(
    request: BandobastReportRequest,
    db: Session = Depends(get_db),
):
    """Generate AI-powered bandobast risk assessment."""
    generator = get_summary_generator()
    
    if not generator.llm.is_available():
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    
    result = generator.generate_bandobast_report(
        event_name=request.event_name,
        location=request.location,
        expected_crowd=request.expected_crowd,
        date=request.date,
    )
    
    if result.success:
        generator.save_summary(result, request.event_name, db)
    
    return GeneratedSummaryResponse(
        summary_type=result.summary_type,
        content=result.content,
        raw_text=result.raw_text,
        tokens_used=result.tokens_used,
        duration_ms=result.duration_ms,
        success=result.success,
        error=result.error,
        markdown=result.to_markdown() if result.success else None,
    )


@router.post("/generate/daily", response_model=GeneratedSummaryResponse)
def generate_daily_brief(
    request: DailyBriefRequest,
    db: Session = Depends(get_db),
):
    """Generate AI-powered daily intelligence briefing."""
    generator = get_summary_generator()
    
    if not generator.llm.is_available():
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    
    result = generator.generate_daily_brief(request.date, db)
    
    if result.success:
        generator.save_summary(result, request.date or datetime.now().strftime("%Y-%m-%d"), db)
    
    return GeneratedSummaryResponse(
        summary_type=result.summary_type,
        content=result.content,
        raw_text=result.raw_text,
        tokens_used=result.tokens_used,
        duration_ms=result.duration_ms,
        success=result.success,
        error=result.error,
        markdown=result.to_markdown() if result.success else None,
    )


@router.post("/generate", response_model=SummaryResponse, status_code=201)
def generate_summary_legacy(request: SummaryGenerateRequest, db: Session = Depends(get_db)):
    """Legacy summary generation (mock data)."""
    content = f"Summary generated for {request.summary_type.value}"
    
    if request.summary_type.value == "patrol" and request.reference_id:
        content = f"Patrol session {request.reference_id} completed."
    elif request.summary_type.value == "bandobast":
        content = "Bandobast deployment summary."
    elif request.summary_type.value == "daily":
        content = f"Daily summary for {datetime.now().strftime('%Y-%m-%d')}."
    
    summary = Summary(
        summary_type=SummaryType(request.summary_type.value),
        patrol_session_id=request.reference_id if request.summary_type.value == "patrol" else None,
        reference_date=request.reference_date or datetime.utcnow(),
        content=content,
        key_insights=["Operations normal"],
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
    """List all summaries with filtering."""
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
    """Get summary by ID."""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary
