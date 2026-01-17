"""Alert builder for constructing alerts from events."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from src.alerts.priority import AlertPriority, calculate_priority


@dataclass
class BuiltAlert:
    alert_id: str
    alert_type: str
    severity: str
    priority: AlertPriority
    priority_score: float
    message: str
    description: str
    timestamp: datetime
    camera_id: Optional[str]
    location_lat: Optional[float]
    location_lon: Optional[float]
    recommended_action: str
    occurrence_count: int = 1
    event_id: Optional[str] = None
    media_ref: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "priority": self.priority.value,
            "priority_score": self.priority_score,
            "message": self.message,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "camera_id": self.camera_id,
            "location": {"lat": self.location_lat, "lon": self.location_lon} if self.location_lat else None,
            "recommended_action": self.recommended_action,
            "occurrence_count": self.occurrence_count,
            "event_id": self.event_id,
            "media_ref": self.media_ref,
            "metadata": self.metadata,
        }


SEVERITY_MAP = {
    "static_object": {"default": "high", "backpack": "critical", "suitcase": "critical"},
    "crowd_surge": {"low": "medium", "moderate": "high", "high": "critical"},
    "route_blocked": {"partial": "medium", "full": "high"},
    "after_hours": {"default": "medium"},
}

ACTION_MAP = {
    "static_object": "Dispatch patrol to investigate unattended object",
    "crowd_surge": "Deploy crowd control and monitor density",
    "route_blocked": "Reroute patrols and assess blockage",
    "after_hours": "Verify authorized access or dispatch patrol",
}


class AlertBuilder:
    """Factory for building alerts from rule outputs or events."""
    
    def __init__(self, location_type: str = "default"):
        self.location_type = location_type
    
    def _id(self) -> str:
        return str(uuid.uuid4())
    
    def _now(self) -> datetime:
        return datetime.now(timezone.utc)
    
    def _get_severity(self, alert_type: str, context: Optional[Dict] = None) -> str:
        type_map = SEVERITY_MAP.get(alert_type, {})
        if context:
            class_name = context.get("class_name", "").lower()
            if class_name in type_map:
                return type_map[class_name]
            level = context.get("level", "default")
            if level in type_map:
                return type_map[level]
        return type_map.get("default", "medium")
    
    def _get_action(self, alert_type: str) -> str:
        return ACTION_MAP.get(alert_type, "Investigate and assess situation")
    
    def build(
        self,
        alert_type: str,
        message: str,
        camera_id: Optional[str] = None,
        location: Optional[Dict] = None,
        event_data: Optional[Dict] = None,
        event_id: Optional[str] = None,
        occurrence_count: int = 1,
        media_ref: Optional[str] = None,
    ) -> BuiltAlert:
        severity = self._get_severity(alert_type, event_data)
        
        priority, priority_score = calculate_priority(
            severity=severity,
            location_type=self.location_type,
            timestamp=self._now(),
            occurrence_count=occurrence_count,
        )
        
        lat = lon = None
        if location:
            lat = location.get("lat", location.get("latitude"))
            lon = location.get("lon", location.get("longitude"))
        
        description = self._build_description(alert_type, event_data)
        
        return BuiltAlert(
            alert_id=self._id(),
            alert_type=alert_type,
            severity=severity,
            priority=priority,
            priority_score=priority_score,
            message=message,
            description=description,
            timestamp=self._now(),
            camera_id=camera_id,
            location_lat=lat,
            location_lon=lon,
            recommended_action=self._get_action(alert_type),
            occurrence_count=occurrence_count,
            event_id=event_id,
            media_ref=media_ref,
            metadata=event_data or {},
        )
    
    def _build_description(self, alert_type: str, data: Optional[Dict]) -> str:
        if not data:
            return f"Alert of type {alert_type} detected"
        
        if alert_type == "static_object":
            cls = data.get("class_name", "object")
            dwell = data.get("dwell_time", 0)
            return f"Static {cls} detected for {dwell:.0f} seconds"
        
        if alert_type == "crowd_surge":
            count = data.get("count", 0)
            prev = data.get("previous_count", 0)
            return f"Crowd increased from {prev} to {count} people"
        
        if alert_type == "route_blocked":
            return f"Route blockage detected: {data.get('reason', 'unknown')}"
        
        return f"{alert_type.replace('_', ' ').title()} detected"
