"""Crowd surge detection rule."""

from typing import Dict, List, Optional

from src.rules.engine import BaseRule, RuleContext, AlertOutput, RuleSeverity


class CrowdSurgeRule(BaseRule):
    """Alert on rapid crowd density increase."""
    
    def __init__(
        self,
        rate_threshold_percent: float = 50.0,
        min_initial_crowd: int = 20,
        critical_density: float = 3.0,
        window_seconds: int = 120,
        priority: int = 90,
    ):
        super().__init__("crowd_surge", priority=priority)
        self.rate_threshold = rate_threshold_percent
        self.min_initial_crowd = min_initial_crowd
        self.critical_density = critical_density
        self.window_seconds = window_seconds
    
    def evaluate(self, context: RuleContext) -> Optional[AlertOutput]:
        if not context.crowd_data:
            return None
        
        current_count = context.crowd_data.get("count", 0)
        previous_count = context.crowd_data.get("previous_count", 0)
        density = context.crowd_data.get("density", 0.0)
        trend = context.crowd_data.get("trend", "stable")
        
        if previous_count < self.min_initial_crowd:
            return None
        
        if previous_count == 0:
            return None
        
        rate_of_change = ((current_count - previous_count) / previous_count) * 100
        
        is_surge = rate_of_change >= self.rate_threshold or density >= self.critical_density
        if not is_surge:
            return None
        
        severity = self._get_severity(rate_of_change, density)
        confidence = self._calculate_surge_confidence(rate_of_change, density, trend)
        
        if confidence < self.min_confidence:
            return None
        
        return AlertOutput.create(
            rule_name=self.name,
            severity=severity,
            message=self._build_message(current_count, previous_count, rate_of_change, density),
            confidence=confidence,
            camera_id=context.camera_id,
            metadata={
                "current_count": current_count,
                "previous_count": previous_count,
                "rate_of_change": round(rate_of_change, 1),
                "density": round(density, 2),
                "trend": trend,
            },
        )
    
    def _get_severity(self, rate: float, density: float) -> RuleSeverity:
        if density >= self.critical_density or rate >= 100:
            return RuleSeverity.CRITICAL
        if rate >= 100:
            return RuleSeverity.HIGH
        if rate >= 50:
            return RuleSeverity.MEDIUM
        return RuleSeverity.LOW
    
    def _calculate_surge_confidence(self, rate: float, density: float, trend: str) -> float:
        rate_factor = min(1.0, rate / 100)
        density_factor = min(1.0, density / self.critical_density)
        trend_factor = 0.9 if trend == "increasing" else 0.5
        
        return self.calculate_confidence({
            "rate": rate_factor,
            "density": density_factor,
            "trend": trend_factor,
        })
    
    def _build_message(self, current: int, previous: int, rate: float, density: float) -> str:
        return f"Crowd surge: {previous}→{current} people (+{rate:.0f}%), density {density:.1f}/sqm"
