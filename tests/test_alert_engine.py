"""Tests for alert engine module."""

import pytest
from datetime import datetime, timezone, timedelta

from src.alerts.priority import AlertPriority, calculate_priority, PriorityFactors
from src.alerts.deduplication import AlertDeduplicator, COOLDOWN_SECONDS
from src.alerts.builder import AlertBuilder
from src.alerts.lifecycle import AlertLifecycle, AlertStatus
from src.alerts.notification import NotificationBuilder, NotificationPayload
from src.alerts.engine import AlertEngine
from src.rules import RuleEngine, StaticObjectRule, CrowdSurgeRule


class TestPriorityScoring:
    def test_critical_severity_high_priority(self):
        priority, score = calculate_priority(
            severity="critical",
            location_type="vip_zone",
            occurrence_count=5,
        )
        assert priority == AlertPriority.CRITICAL
        assert score >= 0.75
    
    def test_low_severity_low_priority(self):
        priority, score = calculate_priority(
            severity="low",
            location_type="perimeter",
            occurrence_count=1,
        )
        assert priority in (AlertPriority.LOW, AlertPriority.MEDIUM)
        assert score < 0.55
    
    def test_custom_factors(self):
        factors = PriorityFactors(
            severity_weight=0.5,
            location_weight=0.3,
            time_weight=0.1,
            history_weight=0.1,
        )
        priority, score = calculate_priority(
            severity="high",
            location_type="main_gate",
            factors=factors,
        )
        assert 0 <= score <= 1


class TestDeduplication:
    def test_first_alert_emits(self):
        dedup = AlertDeduplicator()
        should_emit, existing = dedup.should_emit("crowd_surge", "cam1", {"lat": 28.6, "lon": 77.2})
        assert should_emit is True
        assert existing is None
    
    def test_duplicate_within_cooldown_blocked(self):
        dedup = AlertDeduplicator()
        now = datetime.now(timezone.utc)
        
        dedup.record("crowd_surge", "cam1", {"lat": 28.6, "lon": 77.2}, timestamp=now)
        should_emit, existing = dedup.should_emit("crowd_surge", "cam1", {"lat": 28.6, "lon": 77.2}, timestamp=now)
        
        assert should_emit is False
        assert existing is not None
    
    def test_alert_after_cooldown_emits(self):
        dedup = AlertDeduplicator()
        now = datetime.now(timezone.utc)
        cooldown = COOLDOWN_SECONDS["crowd_surge"]
        
        dedup.record("crowd_surge", "cam1", {"lat": 28.6, "lon": 77.2}, timestamp=now)
        after_cooldown = now + timedelta(seconds=cooldown + 1)
        should_emit, _ = dedup.should_emit("crowd_surge", "cam1", {"lat": 28.6, "lon": 77.2}, timestamp=after_cooldown)
        
        assert should_emit is True
    
    def test_occurrence_count_increments(self):
        dedup = AlertDeduplicator()
        dedup.record("static_object", "cam1", None)
        dedup.record("static_object", "cam1", None)
        dedup.record("static_object", "cam1", None)
        
        count = dedup.get_occurrence_count("static_object", "cam1", None)
        assert count == 3


class TestAlertBuilder:
    def test_builds_alert_with_priority(self):
        builder = AlertBuilder(location_type="main_gate")
        alert = builder.build(
            alert_type="static_object",
            message="Unattended bag detected",
            camera_id="cam1",
            location={"lat": 28.6139, "lon": 77.2090},
            event_data={"class_name": "backpack", "dwell_time": 600},
        )
        
        assert alert.alert_type == "static_object"
        assert alert.priority in AlertPriority
        assert alert.priority_score > 0
        assert alert.location_lat == 28.6139
    
    def test_to_dict_format(self):
        builder = AlertBuilder()
        alert = builder.build("crowd_surge", "Crowd surge detected", camera_id="cam2")
        d = alert.to_dict()
        
        assert "alert_id" in d
        assert "priority" in d
        assert "recommended_action" in d


class TestLifecycle:
    def test_create_active_alert(self):
        lifecycle = AlertLifecycle()
        state = lifecycle.create("alert-123", "static_object")
        
        assert state.status == AlertStatus.ACTIVE
        assert state.expires_at > state.created_at
    
    def test_acknowledge_transition(self):
        lifecycle = AlertLifecycle()
        lifecycle.create("alert-123", "crowd_surge")
        
        success = lifecycle.acknowledge("alert-123", by="Officer Singh")
        state = lifecycle.get_state("alert-123")
        
        assert success is True
        assert state.status == AlertStatus.ACKNOWLEDGED
        assert state.acknowledged_by == "Officer Singh"
    
    def test_resolve_from_acknowledged(self):
        lifecycle = AlertLifecycle()
        lifecycle.create("alert-123", "crowd_surge")
        lifecycle.acknowledge("alert-123", by="Officer")
        
        success = lifecycle.resolve("alert-123", reason="Crowd dispersed")
        state = lifecycle.get_state("alert-123")
        
        assert success is True
        assert state.status == AlertStatus.RESOLVED
    
    def test_invalid_transition_fails(self):
        lifecycle = AlertLifecycle()
        lifecycle.create("alert-123", "crowd_surge")
        lifecycle.resolve("alert-123")
        
        success = lifecycle.acknowledge("alert-123", by="Officer")
        assert success is False


class TestNotification:
    def test_build_payload_from_dict(self):
        builder = NotificationBuilder()
        alert_dict = {
            "alert_id": "abc-123",
            "alert_type": "crowd_surge",
            "severity": "high",
            "priority": "high",
            "message": "Test alert",
            "description": "Test description",
            "location": {"lat": 28.6, "lon": 77.2},
            "recommended_action": "Dispatch patrol",
        }
        
        payload = builder.from_alert(alert_dict)
        
        assert payload.alert_id == "abc-123"
        assert payload.severity == "high"
        assert payload.location_lat == 28.6


class TestAlertEngine:
    def test_create_alert_directly(self):
        engine = AlertEngine()
        alert = engine.create_alert(
            alert_type="crowd_surge",
            message="Manual alert test",
            camera_id="cam1",
            location={"lat": 28.6, "lon": 77.2},
        )
        
        assert alert is not None
        assert alert.alert_type == "crowd_surge"
    
    def test_deduplication_in_engine(self):
        engine = AlertEngine()
        
        alert1 = engine.create_alert("static_object", "First alert", camera_id="cam1")
        alert2 = engine.create_alert("static_object", "Duplicate", camera_id="cam1")
        
        assert alert1 is not None
        assert alert2 is None
    
    def test_active_alerts_tracking(self):
        engine = AlertEngine()
        engine.create_alert("crowd_surge", "Test 1", camera_id="cam1", skip_deduplication=True)
        engine.create_alert("static_object", "Test 2", camera_id="cam2", skip_deduplication=True)
        
        active = engine.get_active_alerts()
        assert len(active) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
