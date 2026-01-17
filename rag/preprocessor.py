"""Text preprocessor for converting database models to documents."""

from datetime import datetime
from typing import Optional


def patrol_session_to_text(
    session_id: int,
    officer_id: str,
    officer_name: str,
    start_time: datetime,
    end_time: Optional[datetime],
    status: str,
    incidents_count: int,
    distance_km: float,
    route_data: list
) -> str:
    """Convert PatrolSession to text document."""
    duration = ""
    if end_time and start_time:
        delta = end_time - start_time
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        duration = f"{hours}h {minutes}m"
    
    route_summary = ""
    if route_data:
        route_summary = f" covering {len(route_data)} checkpoints"
    
    return (
        f"Patrol session #{session_id} by Officer {officer_name} ({officer_id}). "
        f"Started {start_time.strftime('%Y-%m-%d %H:%M')}. "
        f"Status: {status}. Duration: {duration or 'ongoing'}. "
        f"Distance: {distance_km:.1f} km{route_summary}. "
        f"Incidents recorded: {incidents_count}."
    )


def alert_to_text(
    alert_id: int,
    alert_type: str,
    severity: str,
    message: str,
    location_lat: Optional[float],
    location_lon: Optional[float],
    acknowledged: bool,
    created_at: datetime
) -> str:
    """Convert Alert to text document."""
    location = ""
    if location_lat and location_lon:
        location = f" at coordinates ({location_lat:.4f}, {location_lon:.4f})"
    
    ack_status = "acknowledged" if acknowledged else "unacknowledged"
    
    return (
        f"Alert #{alert_id}: {alert_type} ({severity} severity). "
        f"{message} "
        f"Occurred on {created_at.strftime('%Y-%m-%d %H:%M')}{location}. "
        f"Status: {ack_status}."
    )


def event_to_text(
    event_id: int,
    event_type: str,
    confidence: float,
    timestamp: datetime,
    camera_name: Optional[str] = None,
    location_name: Optional[str] = None,
    data: Optional[dict] = None
) -> str:
    """Convert Event to text document."""
    location_info = ""
    if camera_name:
        location_info = f" from camera '{camera_name}'"
    if location_name:
        location_info += f" at {location_name}"
    
    details = ""
    if data:
        if "object_count" in data:
            details = f" Detected {data['object_count']} objects."
        if "crowd_count" in data:
            details = f" Crowd size: {data['crowd_count']}."
        if "density" in data:
            details += f" Density: {data['density']:.2f}."
    
    return (
        f"Event #{event_id}: {event_type.replace('_', ' ')} "
        f"at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}{location_info}. "
        f"Confidence: {confidence:.0%}.{details}"
    )


def events_to_narrative(events: list[dict]) -> str:
    """Convert sequence of events to narrative format."""
    if not events:
        return ""
    
    lines = ["Event sequence:"]
    for e in events:
        line = event_to_text(
            event_id=e.get("id", 0),
            event_type=e.get("event_type", "unknown"),
            confidence=e.get("confidence_score", 0),
            timestamp=e.get("timestamp", datetime.now()),
            camera_name=e.get("camera_name"),
            location_name=e.get("location_name"),
            data=e.get("data")
        )
        lines.append(f"- {line}")
    
    return "\n".join(lines)


def location_context_to_text(
    location_name: str,
    description: str,
    characteristics: list[str],
    risk_level: str = "normal"
) -> str:
    """Create location context document."""
    chars = ", ".join(characteristics) if characteristics else "no special characteristics"
    return (
        f"Location: {location_name}. "
        f"{description} "
        f"Characteristics: {chars}. "
        f"Risk level: {risk_level}."
    )
