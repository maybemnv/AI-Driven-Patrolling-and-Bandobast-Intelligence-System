"""Static object detection rule."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.rules.engine import BaseRule, RuleContext, AlertOutput, RuleSeverity


class StaticObjectRule(BaseRule):
    """Alert when object remains stationary beyond threshold."""
    
    SUSPICIOUS_CLASSES = {"backpack", "suitcase", "handbag", "bag"}
    VEHICLE_CLASSES = {"car", "truck", "bus", "motorcycle"}
    
    def __init__(
        self,
        time_threshold_seconds: int = 300,
        exclusion_zones: Optional[List[Dict]] = None,
        priority: int = 80,
    ):
        super().__init__("static_object", priority=priority)
        self.time_threshold = time_threshold_seconds
        self.exclusion_zones = exclusion_zones or []
    
    def evaluate(self, context: RuleContext) -> Optional[AlertOutput]:
        if not context.tracked_objects:
            return None
        
        for obj_id, obj in context.tracked_objects.items():
            if not obj.get("is_static", False):
                continue
            
            dwell_time = obj.get("dwell_time", 0)
            if dwell_time < self.time_threshold:
                continue
            
            class_name = obj.get("class_name", "").lower()
            if self._in_exclusion_zone(obj.get("location")):
                continue
            
            severity = self._get_severity(class_name, dwell_time, context)
            confidence = self._calculate_object_confidence(obj, dwell_time)
            
            if confidence < self.min_confidence:
                continue
            
            return AlertOutput.create(
                rule_name=self.name,
                severity=severity,
                message=self._build_message(class_name, dwell_time),
                confidence=confidence,
                camera_id=context.camera_id,
                location=obj.get("location"),
                metadata={
                    "object_id": obj_id,
                    "class_name": class_name,
                    "dwell_time_seconds": dwell_time,
                    "first_seen": obj.get("first_seen"),
                    "bbox": obj.get("bbox"),
                },
            )
        
        return None
    
    def _get_severity(self, class_name: str, dwell_time: int, context: RuleContext) -> RuleSeverity:
        if class_name in self.SUSPICIOUS_CLASSES:
            if dwell_time > 600:
                return RuleSeverity.CRITICAL
            return RuleSeverity.HIGH
        
        if class_name in self.VEHICLE_CLASSES:
            return RuleSeverity.LOW
        
        return RuleSeverity.MEDIUM
    
    def _calculate_object_confidence(self, obj: Dict, dwell_time: int) -> float:
        detection_conf = obj.get("confidence", 0.5)
        time_factor = min(1.0, dwell_time / (self.time_threshold * 2))
        return self.calculate_confidence({
            "detection": detection_conf,
            "time": time_factor,
        })
    
    def _in_exclusion_zone(self, location: Optional[Dict]) -> bool:
        if not location or not self.exclusion_zones:
            return False
        
        for zone in self.exclusion_zones:
            if self._point_in_polygon(location, zone.get("polygon", [])):
                return True
        return False
    
    def _point_in_polygon(self, point: Dict, polygon: List) -> bool:
        if not polygon or len(polygon) < 3:
            return False
        return False  # Simplified - implement ray casting if needed
    
    def _build_message(self, class_name: str, dwell_time: int) -> str:
        minutes = dwell_time // 60
        return f"Static {class_name} detected for {minutes}+ minutes"
