"""Base rule engine architecture."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class RuleSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RuleContext:
    """Context passed to rules for evaluation."""
    timestamp: datetime
    camera_id: Optional[str] = None
    detections: List[Any] = field(default_factory=list)
    crowd_data: Optional[Dict] = None
    tracked_objects: Optional[Dict] = None
    location_metadata: Optional[Dict] = None


@dataclass
class AlertOutput:
    """Output from a triggered rule."""
    alert_id: str
    rule_name: str
    severity: RuleSeverity
    message: str
    confidence: float
    timestamp: datetime
    camera_id: Optional[str]
    location: Optional[Dict]
    metadata: Dict = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        rule_name: str,
        severity: RuleSeverity,
        message: str,
        confidence: float,
        camera_id: Optional[str] = None,
        location: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ) -> "AlertOutput":
        return cls(
            alert_id=str(uuid.uuid4()),
            rule_name=rule_name,
            severity=severity,
            message=message,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc),
            camera_id=camera_id,
            location=location,
            metadata=metadata or {},
        )
    
    def to_dict(self) -> Dict:
        return {
            "alert_id": self.alert_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "message": self.message,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "camera_id": self.camera_id,
            "location": self.location,
            "metadata": self.metadata,
        }


class BaseRule(ABC):
    """Abstract base class for all rules."""
    
    def __init__(self, name: str, priority: int = 50, enabled: bool = True):
        self.name = name
        self.priority = priority
        self.enabled = enabled
        self.min_confidence = 0.6
    
    @abstractmethod
    def evaluate(self, context: RuleContext) -> Optional[AlertOutput]:
        """Evaluate rule against context. Return AlertOutput if triggered."""
        pass
    
    def calculate_confidence(self, factors: Dict[str, float]) -> float:
        """Calculate combined confidence score from factors."""
        if not factors:
            return 0.0
        weights = {k: 1.0 for k in factors}
        total_weight = sum(weights.values())
        weighted_sum = sum(factors[k] * weights[k] for k in factors)
        return min(1.0, weighted_sum / total_weight)


class RuleEngine:
    """Main rule evaluation engine."""
    
    def __init__(self):
        self.rules: List[BaseRule] = []
        self._alert_history: Dict[str, datetime] = {}
        self.cooldown_seconds = 300  # 5 minutes
    
    def register(self, rule: BaseRule) -> None:
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def evaluate_all(self, context: RuleContext) -> List[AlertOutput]:
        """Evaluate all enabled rules and return triggered alerts."""
        alerts = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                result = rule.evaluate(context)
                if result and self._should_emit(result):
                    alerts.append(result)
                    self._record_alert(result)
            except Exception:
                continue
        
        return alerts
    
    def _should_emit(self, alert: AlertOutput) -> bool:
        """Check if alert should be emitted (deduplication)."""
        key = f"{alert.rule_name}:{alert.camera_id}"
        last_time = self._alert_history.get(key)
        
        if last_time is None:
            return True
        
        elapsed = (alert.timestamp - last_time).total_seconds()
        return elapsed >= self.cooldown_seconds
    
    def _record_alert(self, alert: AlertOutput) -> None:
        key = f"{alert.rule_name}:{alert.camera_id}"
        self._alert_history[key] = alert.timestamp
    
    def clear_history(self) -> None:
        self._alert_history.clear()
