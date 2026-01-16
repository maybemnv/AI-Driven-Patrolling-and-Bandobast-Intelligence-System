"""Event schema and builder for detection events."""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class EventType(Enum):
    OBJECT_DETECTED = "object_detected"
    CROWD_DETECTED = "crowd_detected"
    STATIC_OBJECT = "static_object"
    CROWD_SURGE = "crowd_surge"
    ROUTE_BLOCKED = "route_blocked"


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Event:
    event_id: str
    timestamp: str
    camera_id: str
    event_type: str
    confidence: float
    data: Dict[str, Any]
    severity: str = Severity.LOW.value
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        try:
            uuid.UUID(self.event_id)
        except ValueError:
            raise ValueError(f"Invalid event_id: {self.event_id}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0-1: {self.confidence}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "camera_id": self.camera_id,
            "event_type": self.event_type,
            "confidence": round(self.confidence, 4),
            "severity": self.severity,
            "data": self.data,
            "metadata": self.metadata,
        }
    
    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Event":
        return cls(
            event_id=d["event_id"],
            timestamp=d["timestamp"],
            camera_id=d["camera_id"],
            event_type=d["event_type"],
            confidence=d["confidence"],
            data=d.get("data", {}),
            severity=d.get("severity", Severity.LOW.value),
            metadata=d.get("metadata", {}),
        )


class EventBuilder:
    """Factory for creating detection events."""
    
    def __init__(self, camera_id: str = "default"):
        self.camera_id = camera_id
    
    def _id(self) -> str:
        return str(uuid.uuid4())
    
    def _ts(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    def object_detected(
        self,
        class_name: str,
        class_id: int,
        confidence: float,
        bbox: Dict[str, int],
        **extra,
    ) -> Event:
        return Event(
            event_id=self._id(),
            timestamp=self._ts(),
            camera_id=self.camera_id,
            event_type=EventType.OBJECT_DETECTED.value,
            confidence=confidence,
            data={"class_name": class_name, "class_id": class_id, "bbox": bbox, **extra},
        )
    
    def static_object(
        self,
        class_name: str,
        class_id: int,
        confidence: float,
        bbox: Dict[str, int],
        dwell_time: float,
        object_id: str,
        **extra,
    ) -> Event:
        severity = Severity.HIGH.value if class_id in {24, 26, 28} else Severity.MEDIUM.value
        return Event(
            event_id=self._id(),
            timestamp=self._ts(),
            camera_id=self.camera_id,
            event_type=EventType.STATIC_OBJECT.value,
            confidence=confidence,
            severity=severity,
            data={"class_name": class_name, "bbox": bbox, "dwell_time": dwell_time, "object_id": object_id, **extra},
        )
    
    def crowd_detected(self, count: int, detections: List[Dict], **extra) -> Event:
        avg_conf = sum(d.get("confidence", 0) for d in detections) / len(detections) if detections else 0.5
        severity = Severity.HIGH.value if count > 50 else Severity.MEDIUM.value if count > 20 else Severity.LOW.value
        return Event(
            event_id=self._id(),
            timestamp=self._ts(),
            camera_id=self.camera_id,
            event_type=EventType.CROWD_DETECTED.value,
            confidence=avg_conf,
            severity=severity,
            data={"person_count": count, "detections": detections, **extra},
        )


def save_events(events: List[Event], path: str, indent: int = 2) -> str:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    data = {
        "events": [e.to_dict() for e in events],
        "count": len(events),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=indent)
    return path
