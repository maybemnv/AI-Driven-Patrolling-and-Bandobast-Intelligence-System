"""Crowd event generation."""

from typing import Dict, List, Optional
from model.events.event import Event, EventBuilder, EventType, Severity
from model.crowd.analyzer import CrowdSnapshot, DensityLevel, SurgeEvent, SurgeSeverity


class CrowdEventType:
    NORMAL = "crowd_normal"
    HIGH_DENSITY = "crowd_high_density"
    SURGE = "crowd_surge"
    DISPERSAL = "crowd_dispersal"


class CrowdEventBuilder:
    """Generate crowd-related events with deduplication."""
    
    def __init__(self, camera_id: str = "default", debounce_sec: float = 30.0):
        self._builder = EventBuilder(camera_id)
        self._debounce = debounce_sec
        self._last_events: Dict[str, float] = {}
    
    def _should_emit(self, event_type: str, timestamp: float) -> bool:
        last = self._last_events.get(event_type, 0)
        if timestamp - last < self._debounce:
            return False
        self._last_events[event_type] = timestamp
        return True
    
    def from_snapshot(
        self,
        snapshot: CrowdSnapshot,
        stats: Dict,
        emit_normal: bool = False,
    ) -> Optional[Event]:
        """Generate event from crowd snapshot based on density level."""
        if snapshot.level == DensityLevel.LOW:
            if not emit_normal:
                return None
            event_type = CrowdEventType.NORMAL
            severity = Severity.LOW.value
        elif snapshot.level == DensityLevel.MEDIUM:
            event_type = CrowdEventType.NORMAL
            severity = Severity.LOW.value
        elif snapshot.level == DensityLevel.HIGH:
            event_type = CrowdEventType.HIGH_DENSITY
            severity = Severity.MEDIUM.value
        else:  # CRITICAL
            event_type = CrowdEventType.HIGH_DENSITY
            severity = Severity.HIGH.value
        
        if not self._should_emit(event_type, snapshot.timestamp):
            return None
        
        return self._builder.crowd_detected(
            count=snapshot.count,
            detections=[],
            density=snapshot.density,
            density_level=snapshot.level.value,
            zones=self._zones_to_dict(snapshot.zones),
            stats=stats,
        )
    
    def from_surge(self, surge: SurgeEvent, timestamp: float) -> Optional[Event]:
        """Generate surge event."""
        if not self._should_emit(CrowdEventType.SURGE, timestamp):
            return None
        
        if surge.severity == SurgeSeverity.MAJOR:
            severity = Severity.CRITICAL.value
        elif surge.severity == SurgeSeverity.MODERATE:
            severity = Severity.HIGH.value
        else:
            severity = Severity.MEDIUM.value
        
        return Event(
            event_id=self._builder._id(),
            timestamp=self._builder._ts(),
            camera_id=self._builder.camera_id,
            event_type=EventType.CROWD_SURGE.value,
            confidence=0.9,
            severity=severity,
            data={
                "surge_severity": surge.severity.value,
                "previous_density": round(surge.prev_density, 4),
                "current_density": round(surge.curr_density, 4),
                "rate_of_change": round(surge.rate_of_change, 2),
                "trend": surge.trend,
            },
        )
    
    def dispersal(self, prev_count: int, curr_count: int, timestamp: float) -> Optional[Event]:
        """Generate dispersal event when crowd decreases significantly."""
        if not self._should_emit(CrowdEventType.DISPERSAL, timestamp):
            return None
        
        if prev_count == 0:
            return None
        
        decrease_pct = (prev_count - curr_count) / prev_count
        if decrease_pct < 0.5:  # Need 50%+ decrease
            return None
        
        return Event(
            event_id=self._builder._id(),
            timestamp=self._builder._ts(),
            camera_id=self._builder.camera_id,
            event_type=CrowdEventType.DISPERSAL,
            confidence=0.85,
            severity=Severity.LOW.value,
            data={
                "previous_count": prev_count,
                "current_count": curr_count,
                "decrease_percentage": round(decrease_pct * 100, 1),
            },
        )
    
    def _zones_to_dict(self, zones: Dict) -> Dict[str, int]:
        return {f"{r},{c}": cnt for (r, c), cnt in zones.items()}
    
    def calculate_priority(self, snapshot: CrowdSnapshot, surge: Optional[SurgeEvent] = None) -> int:
        """Calculate event priority score (1-10)."""
        score = 1
        
        # Density level adds 0-4
        density_scores = {DensityLevel.LOW: 0, DensityLevel.MEDIUM: 1, DensityLevel.HIGH: 2, DensityLevel.CRITICAL: 4}
        score += density_scores.get(snapshot.level, 0)
        
        # Count adds 0-2
        if snapshot.count > 50:
            score += 2
        elif snapshot.count > 20:
            score += 1
        
        # Surge adds 0-4
        if surge:
            surge_scores = {SurgeSeverity.MINOR: 1, SurgeSeverity.MODERATE: 2, SurgeSeverity.MAJOR: 4}
            score += surge_scores.get(surge.severity, 0)
        
        return min(score, 10)
    
    def reset(self) -> None:
        self._last_events.clear()
