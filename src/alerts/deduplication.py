"""Alert deduplication system."""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any
import math


@dataclass
class AlertRecord:
    alert_type: str
    location_key: str
    last_seen: datetime
    occurrence_count: int = 1
    severity: str = "low"
    metadata: Dict[str, Any] = field(default_factory=dict)


COOLDOWN_SECONDS = {
    "static_object": 600,   # 10 minutes
    "crowd_surge": 300,     # 5 minutes
    "route_blocked": 900,   # 15 minutes
    "after_hours": 600,     # 10 minutes
    "default": 300,         # 5 minutes
}

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class AlertDeduplicator:
    """Manages alert deduplication with type-specific cooldowns."""
    
    def __init__(self):
        self._history: Dict[str, AlertRecord] = {}
    
    def _make_key(self, alert_type: str, camera_id: Optional[str], location: Optional[Dict]) -> str:
        loc_key = ""
        if location:
            lat = location.get("lat", location.get("latitude", 0))
            lon = location.get("lon", location.get("longitude", 0))
            loc_key = f"{lat:.3f},{lon:.3f}"
        return f"{alert_type}:{camera_id or 'unknown'}:{loc_key}"
    
    def _get_cooldown(self, alert_type: str) -> int:
        return COOLDOWN_SECONDS.get(alert_type, COOLDOWN_SECONDS["default"])
    
    def _is_similar(self, existing: AlertRecord, new_type: str, new_location: str) -> float:
        """Calculate similarity score between existing and new alert."""
        if existing.alert_type != new_type:
            return 0.0
        if existing.location_key == new_location:
            return 1.0
        return 0.5  # Same type, different location
    
    def should_emit(
        self,
        alert_type: str,
        camera_id: Optional[str],
        location: Optional[Dict],
        timestamp: Optional[datetime] = None,
    ) -> tuple[bool, Optional[AlertRecord]]:
        """Check if alert should be emitted or is duplicate."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        key = self._make_key(alert_type, camera_id, location)
        existing = self._history.get(key)
        
        if existing is None:
            return True, None
        
        cooldown = self._get_cooldown(alert_type)
        elapsed = (timestamp - existing.last_seen).total_seconds()
        
        if elapsed >= cooldown:
            return True, existing
        
        return False, existing
    
    def record(
        self,
        alert_type: str,
        camera_id: Optional[str],
        location: Optional[Dict],
        severity: str = "low",
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
    ) -> AlertRecord:
        """Record an alert emission."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        key = self._make_key(alert_type, camera_id, location)
        loc_key = key.split(":")[-1]
        
        existing = self._history.get(key)
        if existing:
            existing.last_seen = timestamp
            existing.occurrence_count += 1
            if SEVERITY_ORDER.get(severity, 0) > SEVERITY_ORDER.get(existing.severity, 0):
                existing.severity = severity
            if metadata:
                existing.metadata.update(metadata)
            return existing
        
        record = AlertRecord(
            alert_type=alert_type,
            location_key=loc_key,
            last_seen=timestamp,
            occurrence_count=1,
            severity=severity,
            metadata=metadata or {},
        )
        self._history[key] = record
        return record
    
    def get_occurrence_count(self, alert_type: str, camera_id: Optional[str], location: Optional[Dict]) -> int:
        key = self._make_key(alert_type, camera_id, location)
        record = self._history.get(key)
        return record.occurrence_count if record else 0
    
    def clear_expired(self, max_age_hours: int = 24) -> int:
        """Remove records older than max_age_hours."""
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(hours=max_age_hours)
        
        expired = [k for k, v in self._history.items() if v.last_seen < threshold]
        for k in expired:
            del self._history[k]
        return len(expired)
    
    def clear(self) -> None:
        self._history.clear()
