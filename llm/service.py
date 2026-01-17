"""LangChain-based LLM service for generating summaries and analysis."""

import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from langchain_core.output_parsers import StrOutputParser

from llm.client import get_llm_client, LLMResponse
from llm.prompts import PATROL_SUMMARY, BANDOBAST_RISK, DAILY_BRIEFING, format_messages
from llm.parser import parse_summary, parse_risk_assessment
from rag import get_retriever


logger = logging.getLogger(__name__)


@dataclass
class SummaryResult:
    """Result from summary generation."""
    content: str
    parsed: Optional[object] = None
    tokens_used: int = 0
    duration_ms: float = 0
    success: bool = True
    error: Optional[str] = None


@dataclass
class RiskResult:
    """Result from risk assessment."""
    content: str
    parsed: Optional[object] = None
    tokens_used: int = 0
    duration_ms: float = 0
    success: bool = True
    error: Optional[str] = None


class LLMService:
    """LangChain-based LLM service for intelligence generation."""
    
    def __init__(self):
        self.client = get_llm_client()
        self.retriever = get_retriever()
        self.output_parser = StrOutputParser()
    
    def generate_patrol_summary(
        self,
        officer_name: str,
        officer_id: str,
        duration: str,
        distance_km: float,
        incidents_count: int,
        patrol_id: Optional[int] = None,
    ) -> SummaryResult:
        """Generate patrol session summary using LangChain."""
        try:
            context = self.retriever.get_context(
                f"patrol events officer {officer_id}",
                max_tokens=1500,
            )
            
            messages = format_messages(
                PATROL_SUMMARY,
                officer_name=officer_name,
                officer_id=officer_id,
                duration=duration,
                distance_km=distance_km,
                incidents_count=incidents_count,
                events_context=context or "No events recorded.",
            )
            
            response = self.client.chat(messages, temperature=0.3, max_tokens=800)
            parsed = parse_summary(response.content)
            
            return SummaryResult(
                content=response.content,
                parsed=parsed,
                tokens_used=response.tokens_prompt + response.tokens_completion,
                duration_ms=response.duration_ms,
            )
        except Exception as e:
            logger.error(f"Patrol summary generation failed: {e}")
            return SummaryResult(content="", success=False, error=str(e))
    
    def generate_risk_assessment(
        self,
        event_name: str,
        location: str,
        expected_crowd: int,
    ) -> RiskResult:
        """Generate bandobast risk assessment using LangChain."""
        try:
            alerts_context = self.retriever.get_context(
                f"alerts {location}",
                max_tokens=800,
            )
            
            historical_context = self.retriever.get_context(
                f"incidents history {location}",
                max_tokens=700,
            )
            
            messages = format_messages(
                BANDOBAST_RISK,
                event_name=event_name,
                location=location,
                expected_crowd=expected_crowd,
                alerts_context=alerts_context or "No recent alerts.",
                historical_context=historical_context or "No historical data.",
            )
            
            response = self.client.chat(messages, temperature=0.3, max_tokens=800)
            parsed = parse_risk_assessment(response.content)
            
            return RiskResult(
                content=response.content,
                parsed=parsed,
                tokens_used=response.tokens_prompt + response.tokens_completion,
                duration_ms=response.duration_ms,
            )
        except Exception as e:
            logger.error(f"Risk assessment generation failed: {e}")
            return RiskResult(content="", success=False, error=str(e))
    
    def generate_daily_briefing(self, date: str) -> SummaryResult:
        """Generate daily shift briefing using LangChain."""
        try:
            summary_context = self.retriever.get_context(
                f"patrol summary {date}",
                max_tokens=1200,
            )
            
            critical_context = self.retriever.get_context(
                f"critical alerts high severity {date}",
                max_tokens=600,
            )
            
            messages = format_messages(
                DAILY_BRIEFING,
                date=date,
                total_patrols="-",
                total_alerts="-",
                summary_context=summary_context or "No data available.",
                critical_incidents=critical_context or "No critical incidents.",
            )
            
            response = self.client.chat(messages, temperature=0.3, max_tokens=1000)
            parsed = parse_summary(response.content)
            
            return SummaryResult(
                content=response.content,
                parsed=parsed,
                tokens_used=response.tokens_prompt + response.tokens_completion,
                duration_ms=response.duration_ms,
            )
        except Exception as e:
            logger.error(f"Daily briefing generation failed: {e}")
            return SummaryResult(content="", success=False, error=str(e))
    
    def is_available(self) -> bool:
        """Check if LLM service is available."""
        return self.client.is_available()


def get_llm_service() -> LLMService:
    """Get LLM service instance."""
    return LLMService()
