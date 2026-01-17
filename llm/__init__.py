"""LLM module for intelligence generation."""

from llm.client import OllamaClient, LLMResponse, get_llm_client
from llm.prompts import (
    PromptTemplate,
    PATROL_SUMMARY,
    BANDOBAST_RISK,
    PATTERN_ANALYSIS,
    DAILY_BRIEFING,
    get_template,
)
from llm.parser import (
    parse_summary,
    parse_risk_assessment,
    ParsedSummary,
    ParsedRiskAssessment,
    validate_response,
)
from llm.service import LLMService, SummaryResult, RiskResult, get_llm_service

__all__ = [
    "OllamaClient", "LLMResponse", "get_llm_client",
    "PromptTemplate", "PATROL_SUMMARY", "BANDOBAST_RISK", "PATTERN_ANALYSIS",
    "DAILY_BRIEFING", "get_template",
    "parse_summary", "parse_risk_assessment", "ParsedSummary", "ParsedRiskAssessment",
    "validate_response",
    "LLMService", "SummaryResult", "RiskResult", "get_llm_service",
]
