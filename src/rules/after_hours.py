"""After-hours activity detection rule."""

from datetime import datetime, time, timezone
from typing import Dict, List, Optional

from src.rules.engine import BaseRule, RuleContext, AlertOutput, RuleSeverity


class AfterHoursRule(BaseRule):
    """Alert on activity outside normal operating hours."""
    
    def __init__(
        self,
        normal_start: time = time(6, 0),
        normal_end: time = time(22, 0),
        min_activity_threshold: int = 2,
        priority: int = 60,
    ):
        super().__init__("after_hours", priority=priority)
        self.normal_start = normal_start
        self.normal_end = normal_end
        self.min_activity = min_activity_threshold
        self.location_schedules: Dict[str, Dict] = {}
    
    def set_location_schedule(self, camera_id: str, start: time, end: time) -> None:
        self.location_schedules[camera_id] = {"start": start, "end": end}
    
    def evaluate(self, context: RuleContext) -> Optional[AlertOutput]:
        if not self._is_after_hours(context.timestamp, context.camera_id):
            return None
        
        activity_count = self._count_activity(context)
        if activity_count < self.min_activity:
            return None
        
        confidence = self._calculate_activity_confidence(activity_count, context)
        if confidence < self.min_confidence:
            return None
        
        return AlertOutput.create(
            rule_name=self.name,
            severity=RuleSeverity.MEDIUM,
            message=self._build_message(context.timestamp, activity_count),
            confidence=confidence,
            camera_id=context.camera_id,
            metadata={
                "activity_count": activity_count,
                "time": context.timestamp.strftime("%H:%M"),
                "normal_hours": f"{self.normal_start.strftime('%H:%M')}-{self.normal_end.strftime('%H:%M')}",
            },
        )
    
    def _is_after_hours(self, timestamp: datetime, camera_id: Optional[str]) -> bool:
        current_time = timestamp.time()
        
        if camera_id and camera_id in self.location_schedules:
            schedule = self.location_schedules[camera_id]
            start, end = schedule["start"], schedule["end"]
        else:
            start, end = self.normal_start, self.normal_end
        
        if start <= end:
            return not (start <= current_time <= end)
        else:
            return end < current_time < start
    
    def _count_activity(self, context: RuleContext) -> int:
        count = 0
        
        if context.detections:
            for det in context.detections:
                if det.get("class_name", "").lower() in {"person", "car", "truck", "motorcycle"}:
                    count += 1
        
        if context.crowd_data:
            count = max(count, context.crowd_data.get("count", 0))
        
        return count
    
    def _calculate_activity_confidence(self, count: int, context: RuleContext) -> float:
        activity_factor = min(1.0, count / 10)
        
        det_conf = 0.7
        if context.detections:
            det_conf = sum(d.get("confidence", 0.5) for d in context.detections) / len(context.detections)
        
        return self.calculate_confidence({
            "activity": activity_factor,
            "detection": det_conf,
        })
    
    def _build_message(self, timestamp: datetime, count: int) -> str:
        time_str = timestamp.strftime("%H:%M")
        return f"After-hours activity at {time_str}: {count} detections"
