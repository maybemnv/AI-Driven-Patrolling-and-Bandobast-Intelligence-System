"""LLM API router for summaries and analysis."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from llm import get_llm_service


router = APIRouter(prefix="/llm", tags=["LLM"])


class PatrolSummaryRequest(BaseModel):
    officer_name: str
    officer_id: str
    duration: str
    distance_km: float
    incidents_count: int 
    patrol_id: Optional[int] = None


class RiskAssessmentRequest(BaseModel):
    event_name: str
    location: str
    expected_crowd: int


class SummaryResponse(BaseModel):
    content: str
    tokens_used: int
    duration_ms: float
    success: bool
    error: Optional[str] = None


class RiskResponse(BaseModel):
    content: str
    risk_level: str
    concerns: list[str]
    recommendations: list[str]
    tokens_used: int
    duration_ms: float
    success: bool
    error: Optional[str] = None


@router.post("/patrol-summary", response_model=SummaryResponse)
def generate_patrol_summary(request: PatrolSummaryRequest):
    """Generate patrol session summary using LLM."""
    service = get_llm_service()
    
    if not service.is_available():
        raise HTTPException(status_code=503, detail="LLM service unavailable. Is Ollama running?")
    
    result = service.generate_patrol_summary(
        officer_name=request.officer_name,
        officer_id=request.officer_id,
        duration=request.duration,
        distance_km=request.distance_km,
        incidents_count=request.incidents_count,
        patrol_id=request.patrol_id,
    )
    
    return SummaryResponse(
        content=result.content,
        tokens_used=result.tokens_used,
        duration_ms=result.duration_ms,
        success=result.success,
        error=result.error,
    )


@router.post("/risk-assessment", response_model=RiskResponse)
def generate_risk_assessment(request: RiskAssessmentRequest):
    """Generate bandobast risk assessment using LLM."""
    service = get_llm_service()
    
    if not service.is_available():
        raise HTTPException(status_code=503, detail="LLM service unavailable. Is Ollama running?")
    
    result = service.generate_risk_assessment(
        event_name=request.event_name,
        location=request.location,
        expected_crowd=request.expected_crowd,
    )
    
    parsed = result.parsed
    return RiskResponse(
        content=result.content,
        risk_level=parsed.risk_level if parsed else "UNKNOWN",
        concerns=parsed.concerns if parsed else [],
        recommendations=parsed.recommendations if parsed else [],
        tokens_used=result.tokens_used,
        duration_ms=result.duration_ms,
        success=result.success,
        error=result.error,
    )


@router.post("/daily-briefing", response_model=SummaryResponse)
def generate_daily_briefing(date: str = Query(default=None)):
    """Generate daily shift briefing."""
    service = get_llm_service()
    
    if not service.is_available():
        raise HTTPException(status_code=503, detail="LLM service unavailable. Is Ollama running?")
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    result = service.generate_daily_briefing(date)
    
    return SummaryResponse(
        content=result.content,
        tokens_used=result.tokens_used,
        duration_ms=result.duration_ms,
        success=result.success,
        error=result.error,
    )


@router.get("/status")
def llm_status():
    """Check LLM service status."""
    service = get_llm_service()
    available = service.is_available()
    
    models = []
    if available:
        models = service.client.list_models()
    
    return {
        "available": available,
        "models": models,
        "default_model": service.client.model,
    }
