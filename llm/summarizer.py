"""Summary generation service with LLM integration."""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field, asdict

from database import get_session, PatrolSession, Alert, Event, Summary, SummaryType
from llm import get_llm_service, parse_summary, parse_risk_assessment
from rag import get_retriever

logger = logging.getLogger(__name__)


@dataclass
class SummaryContent:
    """Structured summary content."""
    overview: str = ""
    key_events: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    risk_score: float = 0.0
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass 
class RiskContent:
    """Structured risk assessment content."""
    risk_level: str = "UNKNOWN"
    concerns: list[str] = field(default_factory=list)
    resource_assessment: str = ""
    recommendations: list[str] = field(default_factory=list)
    risk_score: float = 0.0
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GeneratedSummary:
    """Result from summary generation."""
    summary_type: str
    content: dict
    raw_text: str
    tokens_used: int
    duration_ms: float
    success: bool
    error: Optional[str] = None
    
    def to_markdown(self) -> str:
        """Convert to markdown format."""
        lines = [f"# {self.summary_type.replace('_', ' ').title()}"]
        lines.append("")
        
        if self.content.get("overview"):
            lines.append("## Overview")
            lines.append(self.content["overview"])
            lines.append("")
        
        if self.content.get("key_events"):
            lines.append("## Key Events")
            for event in self.content["key_events"]:
                lines.append(f"- {event}")
            lines.append("")
        
        if self.content.get("observations"):
            lines.append("## Observations")
            for obs in self.content["observations"]:
                lines.append(f"- {obs}")
            lines.append("")
        
        if self.content.get("recommendations"):
            lines.append("## Recommendations")
            for rec in self.content["recommendations"]:
                lines.append(f"- {rec}")
            lines.append("")
        
        if self.content.get("risk_level"):
            lines.append(f"**Risk Level**: {self.content['risk_level']}")
        
        if self.content.get("risk_score"):
            lines.append(f"**Risk Score**: {self.content['risk_score']:.2f}")
        
        return "\n".join(lines)


class SummaryGenerator:
    """Main summary generation service."""
    
    def __init__(self, model: str = "llama3.1:8b"):
        self.llm = get_llm_service(model)
        self.retriever = get_retriever()
    
    def generate_patrol_summary(
        self,
        patrol_session_id: int,
        db_session=None,
    ) -> GeneratedSummary:
        """Generate summary for a patrol session."""
        if db_session is None:
            db_session = next(get_session())
        
        patrol = db_session.query(PatrolSession).filter_by(id=patrol_session_id).first()
        if not patrol:
            return GeneratedSummary(
                summary_type="patrol",
                content={},
                raw_text="",
                tokens_used=0,
                duration_ms=0,
                success=False,
                error=f"Patrol session {patrol_session_id} not found",
            )
        
        duration = "Unknown"
        if patrol.start_time and patrol.end_time:
            delta = patrol.end_time - patrol.start_time
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            duration = f"{hours}h {minutes}m"
        
        result = self.llm.generate_patrol_summary(
            officer_name=patrol.officer_name,
            officer_id=patrol.officer_id,
            duration=duration,
            distance_km=patrol.distance_covered or 0,
            incidents_count=patrol.incidents_count or 0,
            patrol_id=patrol_session_id,
        )
        
        content = SummaryContent()
        if result.parsed:
            content.overview = result.parsed.overview
            content.key_events = result.parsed.key_events
            content.observations = result.parsed.observations
            content.recommendations = result.parsed.recommendations
        
        return GeneratedSummary(
            summary_type="patrol",
            content=content.to_dict(),
            raw_text=result.content,
            tokens_used=result.tokens_used,
            duration_ms=result.duration_ms,
            success=result.success,
            error=result.error,
        )
    
    def generate_bandobast_report(
        self,
        event_name: str,
        location: str,
        expected_crowd: int,
        date: Optional[str] = None,
    ) -> GeneratedSummary:
        """Generate bandobast risk assessment report."""
        result = self.llm.generate_risk_assessment(
            event_name=event_name,
            location=location,
            expected_crowd=expected_crowd,
        )
        
        content = RiskContent()
        if result.parsed:
            content.risk_level = result.parsed.risk_level
            content.concerns = result.parsed.concerns
            content.resource_assessment = result.parsed.resource_assessment
            content.recommendations = result.parsed.recommendations
            
            risk_scores = {"LOW": 0.25, "MEDIUM": 0.5, "HIGH": 0.75, "CRITICAL": 0.95}
            content.risk_score = risk_scores.get(content.risk_level, 0.5)
        
        return GeneratedSummary(
            summary_type="bandobast",
            content=content.to_dict(),
            raw_text=result.content,
            tokens_used=result.tokens_used,
            duration_ms=result.duration_ms,
            success=result.success,
            error=result.error,
        )
    
    def generate_daily_brief(
        self,
        date: Optional[str] = None,
        db_session=None,
    ) -> GeneratedSummary:
        """Generate daily intelligence briefing."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        result = self.llm.generate_daily_briefing(date)
        
        content = SummaryContent()
        if result.parsed:
            content.overview = result.parsed.overview
            content.key_events = result.parsed.key_events
            content.observations = result.parsed.observations
            content.recommendations = result.parsed.recommendations
        
        return GeneratedSummary(
            summary_type="daily_brief",
            content=content.to_dict(),
            raw_text=result.content,
            tokens_used=result.tokens_used,
            duration_ms=result.duration_ms,
            success=result.success,
            error=result.error,
        )
    
    def save_summary(
        self,
        generated: GeneratedSummary,
        reference_id: Optional[str] = None,
        db_session=None,
    ) -> Optional[int]:
        """Save generated summary to database."""
        if not generated.success:
            return None
        
        if db_session is None:
            db_session = next(get_session())
        
        type_map = {
            "patrol": SummaryType.PATROL,
            "bandobast": SummaryType.BANDOBAST,
            "daily_brief": SummaryType.DAILY,
        }
        
        summary = Summary(
            summary_type=type_map.get(generated.summary_type, SummaryType.DAILY),
            reference_id=reference_id,
            content=generated.raw_text,
            risk_score=generated.content.get("risk_score", 0.0),
            generated_at=datetime.utcnow(),
            metadata={
                "tokens_used": generated.tokens_used,
                "duration_ms": generated.duration_ms,
                "structured_content": generated.content,
            },
        )
        
        db_session.add(summary)
        db_session.commit()
        
        return summary.id


def get_summary_generator(model: str = "llama3.1:8b") -> SummaryGenerator:
    """Get summary generator instance."""
    return SummaryGenerator(model)
