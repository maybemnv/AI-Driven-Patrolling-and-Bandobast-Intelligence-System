"""Alert lifecycle management."""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List


class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"
    AUTO_RESOLVED = "auto_resolved"


TTL_SECONDS = {
    "static_object": 3600,     # 1 hour
    "crowd_surge": 1800,       # 30 minutes
    "route_blocked": 7200,     # 2 hours
    "after_hours": 3600,       # 1 hour
    "default": 3600,
}

VALID_TRANSITIONS = {
    AlertStatus.ACTIVE: [AlertStatus.ACKNOWLEDGED, AlertStatus.RESOLVED, AlertStatus.EXPIRED, AlertStatus.AUTO_RESOLVED],
    AlertStatus.ACKNOWLEDGED: [AlertStatus.RESOLVED],
    AlertStatus.RESOLVED: [],
    AlertStatus.EXPIRED: [],
    AlertStatus.AUTO_RESOLVED: [],
}


@dataclass
class AlertState:
    alert_id: str
    status: AlertStatus
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolution_reason: Optional[str] = None


class AlertLifecycle:
    """Manages alert status transitions and expiration."""
    
    def __init__(self):
        self._states: Dict[str, AlertState] = {}
    
    def _get_ttl(self, alert_type: str) -> int:
        return TTL_SECONDS.get(alert_type, TTL_SECONDS["default"])
    
    def create(self, alert_id: str, alert_type: str) -> AlertState:
        now = datetime.now(timezone.utc)
        ttl = self._get_ttl(alert_type)
        
        state = AlertState(
            alert_id=alert_id,
            status=AlertStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(seconds=ttl),
        )
        self._states[alert_id] = state
        return state
    
    def transition(self, alert_id: str, new_status: AlertStatus, reason: Optional[str] = None, by: Optional[str] = None) -> bool:
        state = self._states.get(alert_id)
        if not state:
            return False
        
        if new_status not in VALID_TRANSITIONS.get(state.status, []):
            return False
        
        now = datetime.now(timezone.utc)
        state.status = new_status
        state.updated_at = now
        
        if new_status == AlertStatus.ACKNOWLEDGED:
            state.acknowledged_at = now
            state.acknowledged_by = by
        elif new_status in (AlertStatus.RESOLVED, AlertStatus.AUTO_RESOLVED):
            state.resolved_at = now
            state.resolution_reason = reason
        
        return True
    
    def acknowledge(self, alert_id: str, by: str) -> bool:
        return self.transition(alert_id, AlertStatus.ACKNOWLEDGED, by=by)
    
    def resolve(self, alert_id: str, reason: str = "Manually resolved") -> bool:
        return self.transition(alert_id, AlertStatus.RESOLVED, reason=reason)
    
    def auto_resolve(self, alert_id: str, reason: str = "Condition cleared") -> bool:
        return self.transition(alert_id, AlertStatus.AUTO_RESOLVED, reason=reason)
    
    def get_state(self, alert_id: str) -> Optional[AlertState]:
        return self._states.get(alert_id)
    
    def check_expirations(self) -> List[str]:
        """Check and mark expired alerts. Returns list of expired alert IDs."""
        now = datetime.now(timezone.utc)
        expired = []
        
        for alert_id, state in self._states.items():
            if state.status == AlertStatus.ACTIVE and state.expires_at <= now:
                state.status = AlertStatus.EXPIRED
                state.updated_at = now
                expired.append(alert_id)
        
        return expired
    
    def cleanup(self, max_age_hours: int = 48) -> int:
        """Remove old resolved/expired alerts."""
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(hours=max_age_hours)
        
        terminal = (AlertStatus.RESOLVED, AlertStatus.EXPIRED, AlertStatus.AUTO_RESOLVED)
        to_remove = [
            aid for aid, state in self._states.items()
            if state.status in terminal and state.updated_at < threshold
        ]
        
        for aid in to_remove:
            del self._states[aid]
        return len(to_remove)
    
    def get_active_alerts(self) -> List[AlertState]:
        return [s for s in self._states.values() if s.status == AlertStatus.ACTIVE]
