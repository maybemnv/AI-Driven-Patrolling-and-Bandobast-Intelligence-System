"""Alert priority scoring system."""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional, Dict, Any


class AlertPriority(Enum):
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"          # Action within 15 minutes
    MEDIUM = "medium"      # Action within 1 hour
    LOW = "low"            # For awareness only


@dataclass
class PriorityFactors:
    severity_weight: float = 0.40
    location_weight: float = 0.30
    time_weight: float = 0.15
    history_weight: float = 0.15


SEVERITY_SCORES = {"critical": 1.0, "high": 0.75, "medium": 0.50, "low": 0.25}

LOCATION_CRITICALITY = {
    "vip_zone": 1.0,
    "main_gate": 0.9,
    "crowd_area": 0.8,
    "patrol_route": 0.6,
    "perimeter": 0.4,
    "default": 0.3,
}


def _get_time_factor(timestamp: Optional[datetime] = None) -> float:
    """Higher priority during peak hours and events."""
    if timestamp is None:
        timestamp = datetime.now()
    
    hour = timestamp.hour
    if 8 <= hour <= 20:  # Peak hours
        return 0.8
    elif 20 <= hour <= 23 or 5 <= hour <= 8:  # Transition hours
        return 0.6
    return 0.4  # Night hours


def _get_history_factor(occurrence_count: int) -> float:
    """Higher priority for recurring alerts."""
    if occurrence_count >= 5:
        return 1.0
    elif occurrence_count >= 3:
        return 0.7
    elif occurrence_count >= 2:
        return 0.5
    return 0.3


def calculate_priority(
    severity: str,
    location_type: str = "default",
    timestamp: Optional[datetime] = None,
    occurrence_count: int = 1,
    factors: Optional[PriorityFactors] = None,
) -> tuple[AlertPriority, float]:
    """Calculate alert priority and score."""
    if factors is None:
        factors = PriorityFactors()
    
    severity_score = SEVERITY_SCORES.get(severity.lower(), 0.25)
    location_score = LOCATION_CRITICALITY.get(location_type.lower(), 0.3)
    time_score = _get_time_factor(timestamp)
    history_score = _get_history_factor(occurrence_count)
    
    priority_score = (
        severity_score * factors.severity_weight +
        location_score * factors.location_weight +
        time_score * factors.time_weight +
        history_score * factors.history_weight
    )
    
    if priority_score >= 0.75:
        priority = AlertPriority.CRITICAL
    elif priority_score >= 0.55:
        priority = AlertPriority.HIGH
    elif priority_score >= 0.35:
        priority = AlertPriority.MEDIUM
    else:
        priority = AlertPriority.LOW
    
    return priority, round(priority_score, 4)
