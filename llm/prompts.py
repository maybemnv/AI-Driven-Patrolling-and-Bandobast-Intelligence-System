"""Prompt templates for LLM summaries and analysis."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptTemplate:
    """Template for LLM prompts."""
    system: str
    user: str
    
    def format(self, **kwargs) -> dict:
        """Format template with variables."""
        return {
            "system": self.system.format(**kwargs) if kwargs else self.system,
            "user": self.user.format(**kwargs) if kwargs else self.user,
        }
    
    def to_messages(self, **kwargs) -> list[dict]:
        """Convert to chat messages format."""
        formatted = self.format(**kwargs)
        return [
            {"role": "system", "content": formatted["system"]},
            {"role": "user", "content": formatted["user"]},
        ]


PATROL_SUMMARY = PromptTemplate(
    system="""You are a police intelligence analyst. Your task is to summarize patrol sessions in a concise, actionable format.

Guidelines:
- Be factual and objective
- Highlight key events and incidents
- Note any security concerns
- Provide actionable recommendations
- Use professional police terminology""",
    
    user="""Summarize this patrol session:

**Officer**: {officer_name} ({officer_id})
**Duration**: {duration}
**Distance**: {distance_km} km
**Incidents**: {incidents_count}

**Patrol Events**:
{events_context}

Provide:
1. **Overview** (2-3 sentences)
2. **Key Events** (bullet list)
3. **Observations** (patterns or concerns)
4. **Recommendations** (actionable items)"""
)


BANDOBAST_RISK = PromptTemplate(
    system="""You are a security operations analyst. Analyze bandobast (security arrangement) data to assess risk levels and provide recommendations.

Guidelines:
- Assess crowd density and movement patterns
- Identify potential security concerns
- Consider historical incident data
- Provide clear risk ratings (LOW/MEDIUM/HIGH/CRITICAL)
- Recommend specific mitigation measures""",
    
    user="""Analyze this bandobast security arrangement:

**Event**: {event_name}
**Location**: {location}
**Expected Crowd**: {expected_crowd}

**Current Alerts**:
{alerts_context}

**Historical Context**:
{historical_context}

Provide:
1. **Risk Level**: LOW/MEDIUM/HIGH/CRITICAL
2. **Key Concerns** (bullet list)
3. **Resource Assessment** (adequacy of security coverage)
4. **Recommendations** (specific actions)"""
)


PATTERN_ANALYSIS = PromptTemplate(
    system="""You are a crime pattern analyst. Identify trends and patterns in security incident data to support predictive policing.

Guidelines:
- Look for temporal patterns (time of day, day of week)
- Identify location hotspots
- Note recurring incident types
- Assess severity trends
- Provide confidence levels for insights""",
    
    user="""Analyze patterns in this security data:

**Time Period**: {time_period}
**Total Incidents**: {total_incidents}

**Incident Data**:
{incidents_context}

**Historical Comparison**:
{historical_context}

Provide:
1. **Recurring Patterns** (with confidence: HIGH/MEDIUM/LOW)
2. **Temporal Trends** (time-based patterns)
3. **Location Hotspots** (areas of concern)
4. **Predictive Insights** (what to expect)
5. **Resource Recommendations** (deployment suggestions)"""
)


DAILY_BRIEFING = PromptTemplate(
    system="""You are a police shift supervisor preparing a daily briefing. Summarize the day's operations for the incoming shift.

Guidelines:
- Highlight critical incidents
- Note ongoing situations
- Summarize patrol coverage
- Identify areas needing attention
- Keep it concise and actionable""",
    
    user="""Prepare a daily briefing summary:

**Date**: {date}
**Total Patrols**: {total_patrols}
**Total Alerts**: {total_alerts}

**Summary Data**:
{summary_context}

**Critical Incidents**:
{critical_incidents}

Provide:
1. **Shift Summary** (2-3 sentences)
2. **Critical Items** (immediate attention needed)
3. **Ongoing Situations** (monitoring required)
4. **Areas of Concern** (increased patrol needed)
5. **Handover Notes** (for incoming shift)"""
)


def get_template(name: str) -> Optional[PromptTemplate]:
    """Get prompt template by name."""
    templates = {
        "patrol_summary": PATROL_SUMMARY,
        "bandobast_risk": BANDOBAST_RISK,
        "pattern_analysis": PATTERN_ANALYSIS,
        "daily_briefing": DAILY_BRIEFING,
    }
    return templates.get(name)
