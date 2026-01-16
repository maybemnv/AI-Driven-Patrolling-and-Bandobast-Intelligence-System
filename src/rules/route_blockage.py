"""Route blockage detection rule."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.rules.engine import BaseRule, RuleContext, AlertOutput, RuleSeverity


@dataclass
class RouteZone:
    """Represents a monitored route zone."""
    zone_id: str
    name: str
    polygon: List[Dict[str, float]]
    importance: str = "normal"


class RouteBlockageRule(BaseRule):
    """Alert when designated route is blocked."""
    
    BLOCKING_CLASSES = {"car", "truck", "bus", "motorcycle", "barrier"}
    
    def __init__(
        self,
        route_zones: Optional[List[Dict]] = None,
        blockage_threshold: float = 0.5,
        priority: int = 85,
    ):
        super().__init__("route_blockage", priority=priority)
        self.route_zones = route_zones or []
        self.blockage_threshold = blockage_threshold
    
    def evaluate(self, context: RuleContext) -> Optional[AlertOutput]:
        if not context.detections or not self.route_zones:
            return None
        
        blocking_detections = [
            d for d in context.detections
            if d.get("class_name", "").lower() in self.BLOCKING_CLASSES
        ]
        
        if not blocking_detections:
            return None
        
        for zone in self.route_zones:
            coverage = self._calculate_zone_coverage(blocking_detections, zone)
            
            if coverage < self.blockage_threshold:
                continue
            
            severity = self._get_severity(zone, coverage)
            confidence = self._calculate_confidence(coverage, blocking_detections)
            
            if confidence < self.min_confidence:
                continue
            
            return AlertOutput.create(
                rule_name=self.name,
                severity=severity,
                message=self._build_message(zone, coverage),
                confidence=confidence,
                camera_id=context.camera_id,
                metadata={
                    "zone_id": zone.get("zone_id"),
                    "zone_name": zone.get("name"),
                    "coverage_percent": round(coverage * 100, 1),
                    "blocking_objects": len(blocking_detections),
                },
            )
        
        return None
    
    def _calculate_zone_coverage(self, detections: List[Dict], zone: Dict) -> float:
        if not detections:
            return 0.0
        
        overlap_count = 0
        for det in detections:
            bbox = det.get("bbox", {})
            if self._bbox_overlaps_zone(bbox, zone.get("polygon", [])):
                overlap_count += 1
        
        return min(1.0, overlap_count / max(1, len(detections)))
    
    def _bbox_overlaps_zone(self, bbox: Dict, polygon: List) -> bool:
        if not polygon:
            return True
        return True  # Simplified - implement proper overlap check if needed
    
    def _get_severity(self, zone: Dict, coverage: float) -> RuleSeverity:
        importance = zone.get("importance", "normal")
        
        if importance == "vip":
            return RuleSeverity.CRITICAL
        if importance == "high" or coverage >= 0.8:
            return RuleSeverity.HIGH
        return RuleSeverity.MEDIUM
    
    def _calculate_confidence(self, coverage: float, detections: List) -> float:
        avg_det_conf = sum(d.get("confidence", 0.5) for d in detections) / len(detections)
        return self.calculate_confidence({
            "coverage": coverage,
            "detection": avg_det_conf,
        })
    
    def _build_message(self, zone: Dict, coverage: float) -> str:
        name = zone.get("name", "Route")
        return f"{name} blocked: {coverage*100:.0f}% coverage"
