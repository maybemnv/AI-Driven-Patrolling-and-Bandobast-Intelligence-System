"""LLM response parsing and validation."""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedSummary:
    """Parsed patrol summary."""
    overview: str = ""
    key_events: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    raw_text: str = ""
    is_valid: bool = False


@dataclass
class ParsedRiskAssessment:
    """Parsed risk assessment."""
    risk_level: str = "UNKNOWN"
    concerns: list[str] = field(default_factory=list)
    resource_assessment: str = ""
    recommendations: list[str] = field(default_factory=list)
    raw_text: str = ""
    is_valid: bool = False


def parse_summary(text: str) -> ParsedSummary:
    """Parse patrol summary response."""
    result = ParsedSummary(raw_text=text)
    
    sections = _split_sections(text)
    
    if "overview" in sections:
        result.overview = sections["overview"].strip()
    
    if "key events" in sections:
        result.key_events = _extract_bullets(sections["key events"])
    
    if "observations" in sections:
        result.observations = _extract_bullets(sections["observations"])
    
    if "recommendations" in sections:
        result.recommendations = _extract_bullets(sections["recommendations"])
    
    result.is_valid = bool(result.overview or result.key_events)
    return result


def parse_risk_assessment(text: str) -> ParsedRiskAssessment:
    """Parse bandobast risk assessment response."""
    result = ParsedRiskAssessment(raw_text=text)
    
    # Extract risk level
    risk_match = re.search(r"risk\s*level[:\s]*\**(LOW|MEDIUM|HIGH|CRITICAL)\**", text, re.IGNORECASE)
    if risk_match:
        result.risk_level = risk_match.group(1).upper()
    
    sections = _split_sections(text)
    
    if "key concerns" in sections:
        result.concerns = _extract_bullets(sections["key concerns"])
    elif "concerns" in sections:
        result.concerns = _extract_bullets(sections["concerns"])
    
    if "resource assessment" in sections:
        result.resource_assessment = sections["resource assessment"].strip()
    
    if "recommendations" in sections:
        result.recommendations = _extract_bullets(sections["recommendations"])
    
    result.is_valid = result.risk_level != "UNKNOWN"
    return result


def _split_sections(text: str) -> dict[str, str]:
    """Split text into sections by headers."""
    sections = {}
    
    # Match headers like **Header** or ## Header or Header:
    pattern = r"(?:\*\*|##?\s*)?([A-Za-z\s]+)(?:\*\*|:)\s*\n?"
    parts = re.split(pattern, text)
    
    current_header = None
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        
        # Check if this looks like a header
        if len(part) < 50 and not part.startswith("-") and not part.startswith("•"):
            current_header = part.lower()
        elif current_header:
            sections[current_header] = part
    
    return sections


def _extract_bullets(text: str) -> list[str]:
    """Extract bullet points from text."""
    bullets = []
    
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith(("-", "•", "*", "–")):
            bullet = re.sub(r"^[-•*–]\s*", "", line).strip()
            if bullet:
                bullets.append(bullet)
        elif re.match(r"^\d+\.", line):
            bullet = re.sub(r"^\d+\.\s*", "", line).strip()
            if bullet:
                bullets.append(bullet)
    
    return bullets


def validate_response(text: str, min_length: int = 50) -> tuple[bool, str]:
    """Validate LLM response quality."""
    if not text:
        return False, "Empty response"
    
    if len(text) < min_length:
        return False, f"Response too short ({len(text)} chars)"
    
    # Check for common error patterns
    error_patterns = [
        "i cannot",
        "i don't have",
        "i'm unable",
        "as an ai",
        "i apologize",
    ]
    
    lower_text = text.lower()
    for pattern in error_patterns:
        if pattern in lower_text:
            return False, f"Response contains refusal pattern: {pattern}"
    
    return True, "OK"
