
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

PATROL_SUMMARY_SYSTEM = """You are a police intelligence analyst. Your task is to summarize patrol sessions in a concise, actionable format.

Guidelines:
- Be factual and objective
- Highlight key events and incidents
- Note any security concerns
- Provide actionable recommendations
- Use professional police terminology"""


PATROL_SUMMARY_HUMAN = """Summarize this patrol session:

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


BANDOBAST_RISK_SYSTEM = """You are a security operations analyst. Analyze bandobast (security arrangement) data to assess risk levels and provide recommendations.

Guidelines:
- Assess crowd density and movement patterns
- Identify potential security concerns
- Consider historical incident data
- Provide clear risk ratings (LOW/MEDIUM/HIGH/CRITICAL)
- Recommend specific mitigation measures"""


BANDOBAST_RISK_HUMAN = """Analyze this bandobast security arrangement:

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


PATTERN_ANALYSIS_SYSTEM = """You are a crime pattern analyst. Identify trends and patterns in security incident data to support predictive policing.

Guidelines:
- Look for temporal patterns (time of day, day of week)
- Identify location hotspots
- Note recurring incident types
- Assess severity trends
- Provide confidence levels for insights"""


PATTERN_ANALYSIS_HUMAN = """Analyze patterns in this security data:

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


DAILY_BRIEFING_SYSTEM = """You are a police shift supervisor preparing a daily briefing. Summarize the day's operations for the incoming shift.

Guidelines:
- Highlight critical incidents
- Note ongoing situations
- Summarize patrol coverage
- Identify areas needing attention
- Keep it concise and actionable"""


DAILY_BRIEFING_HUMAN = """Prepare a daily briefing summary:

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


PATROL_SUMMARY = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(PATROL_SUMMARY_SYSTEM),
    HumanMessagePromptTemplate.from_template(PATROL_SUMMARY_HUMAN),
])

BANDOBAST_RISK = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(BANDOBAST_RISK_SYSTEM),
    HumanMessagePromptTemplate.from_template(BANDOBAST_RISK_HUMAN),
])

PATTERN_ANALYSIS = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(PATTERN_ANALYSIS_SYSTEM),
    HumanMessagePromptTemplate.from_template(PATTERN_ANALYSIS_HUMAN),
])

DAILY_BRIEFING = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(DAILY_BRIEFING_SYSTEM),
    HumanMessagePromptTemplate.from_template(DAILY_BRIEFING_HUMAN),
])


def get_template(name: str) -> ChatPromptTemplate:
    """Get prompt template by name."""
    templates = {
        "patrol_summary": PATROL_SUMMARY,
        "bandobast_risk": BANDOBAST_RISK,
        "pattern_analysis": PATTERN_ANALYSIS,
        "daily_briefing": DAILY_BRIEFING,
    }
    return templates.get(name)


def format_messages(template: ChatPromptTemplate, **kwargs) -> list[dict]:
    """Format template to list of message dicts for API call."""
    messages = template.format_messages(**kwargs)
    
    role_map = {
        "human": "user",
        "ai": "assistant",
        "system": "system",
        "chat": "user"  # Fallback
    }
    
    return [
        {
            "role": role_map.get(m.type, "user"),
            "content": m.content
        } 
        for m in messages
    ]
