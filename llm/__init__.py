"""LangChain-based LLM module for intelligence generation."""

from llm.client import (
    GroqLangChainClient,
    LLMResponse,
    get_llm_client,
    create_chain,
)
from llm.prompts import (
    PATROL_SUMMARY,
    BANDOBAST_RISK,
    PATTERN_ANALYSIS,
    DAILY_BRIEFING,
    get_template,
    format_messages,
)
from llm.parser import (
    parse_summary,
    parse_risk_assessment,
    ParsedSummary,
    ParsedRiskAssessment,
    validate_response,
)
from llm.service import LLMService, SummaryResult, RiskResult, get_llm_service
from llm.summarizer import SummaryGenerator, GeneratedSummary, get_summary_generator

__all__ = [
    "GroqLangChainClient", "LLMResponse", "get_llm_client", "create_chain",
    "PATROL_SUMMARY", "BANDOBAST_RISK", "PATTERN_ANALYSIS", "DAILY_BRIEFING",
    "get_template", "format_messages",
    "parse_summary", "parse_risk_assessment", "ParsedSummary", "ParsedRiskAssessment",
    "validate_response",
    "LLMService", "SummaryResult", "RiskResult", "get_llm_service",
    "SummaryGenerator", "GeneratedSummary", "get_summary_generator",
]
