"""Main alert engine for event processing and alert generation."""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Callable

from src.rules import RuleEngine, RuleContext, AlertOutput
from src.alerts.builder import AlertBuilder, BuiltAlert
from src.alerts.deduplication import AlertDeduplicator
from src.alerts.lifecycle import AlertLifecycle, AlertStatus
from src.alerts.notification import NotificationBuilder, NotificationDispatcher, NotificationChannel
from src.alerts.priority import AlertPriority

logger = logging.getLogger(__name__)


class AlertEngine:
    """Main engine for processing events and generating alerts."""
    
    def __init__(
        self,
        rule_engine: Optional[RuleEngine] = None,
        location_type: str = "default",
    ):
        self.rule_engine = rule_engine or RuleEngine()
        self.deduplicator = AlertDeduplicator()
        self.builder = AlertBuilder(location_type=location_type)
        self.lifecycle = AlertLifecycle()
        self.notification_builder = NotificationBuilder()
        self.dispatcher = NotificationDispatcher()
        self._listeners: List[Callable[[BuiltAlert], None]] = []
    
    def add_listener(self, callback: Callable[[BuiltAlert], None]) -> None:
        """Add callback for when alerts are generated."""
        self._listeners.append(callback)
    
    def process_event(
        self,
        camera_id: Optional[str],
        timestamp: datetime,
        detections: List[Any] = None,
        crowd_data: Optional[Dict] = None,
        tracked_objects: Optional[Dict] = None,
        location: Optional[Dict] = None,
    ) -> List[BuiltAlert]:
        """Process an event through rules and generate alerts."""
        context = RuleContext(
            timestamp=timestamp,
            camera_id=camera_id,
            detections=detections or [],
            crowd_data=crowd_data,
            tracked_objects=tracked_objects,
            location_metadata=location,
        )
        
        rule_alerts = self.rule_engine.evaluate_all(context)
        built_alerts = []
        
        for rule_alert in rule_alerts:
            alert = self._process_rule_output(rule_alert, camera_id, location)
            if alert:
                built_alerts.append(alert)
                self._notify_listeners(alert)
        
        return built_alerts
    
    def _process_rule_output(
        self,
        rule_alert: AlertOutput,
        camera_id: Optional[str],
        location: Optional[Dict],
    ) -> Optional[BuiltAlert]:
        """Convert rule output to built alert with deduplication."""
        should_emit, existing = self.deduplicator.should_emit(
            alert_type=rule_alert.rule_name,
            camera_id=camera_id,
            location=location,
            timestamp=rule_alert.timestamp,
        )
        
        if not should_emit:
            logger.debug(f"Alert deduplicated: {rule_alert.rule_name}")
            return None
        
        occurrence_count = 1
        if existing:
            occurrence_count = existing.occurrence_count + 1
        
        self.deduplicator.record(
            alert_type=rule_alert.rule_name,
            camera_id=camera_id,
            location=location,
            severity=rule_alert.severity.value,
            timestamp=rule_alert.timestamp,
            metadata=rule_alert.metadata,
        )
        
        built = self.builder.build(
            alert_type=rule_alert.rule_name,
            message=rule_alert.message,
            camera_id=camera_id,
            location=location,
            event_data=rule_alert.metadata,
            occurrence_count=occurrence_count,
        )
        
        self.lifecycle.create(built.alert_id, built.alert_type)
        
        return built
    
    def create_alert(
        self,
        alert_type: str,
        message: str,
        camera_id: Optional[str] = None,
        location: Optional[Dict] = None,
        event_data: Optional[Dict] = None,
        skip_deduplication: bool = False,
    ) -> Optional[BuiltAlert]:
        """Create an alert directly without rule evaluation."""
        if not skip_deduplication:
            should_emit, existing = self.deduplicator.should_emit(
                alert_type=alert_type,
                camera_id=camera_id,
                location=location,
            )
            if not should_emit:
                return None
        
        occurrence = self.deduplicator.get_occurrence_count(alert_type, camera_id, location) + 1
        
        self.deduplicator.record(
            alert_type=alert_type,
            camera_id=camera_id,
            location=location,
            severity=event_data.get("severity", "medium") if event_data else "medium",
        )
        
        built = self.builder.build(
            alert_type=alert_type,
            message=message,
            camera_id=camera_id,
            location=location,
            event_data=event_data,
            occurrence_count=occurrence,
        )
        
        self.lifecycle.create(built.alert_id, built.alert_type)
        self._notify_listeners(built)
        
        return built
    
    def send_notification(self, alert: BuiltAlert, channel: NotificationChannel = NotificationChannel.COPMAP_WEBHOOK):
        """Send notification for an alert."""
        payload = self.notification_builder.from_alert(alert)
        return self.dispatcher.send(payload, channel)
    
    def acknowledge_alert(self, alert_id: str, by: str) -> bool:
        return self.lifecycle.acknowledge(alert_id, by)
    
    def resolve_alert(self, alert_id: str, reason: str = "Resolved") -> bool:
        return self.lifecycle.resolve(alert_id, reason)
    
    def get_active_alerts(self) -> List:
        return self.lifecycle.get_active_alerts()
    
    def check_expirations(self) -> List[str]:
        return self.lifecycle.check_expirations()
    
    def cleanup(self, dedup_hours: int = 24, lifecycle_hours: int = 48) -> Dict[str, int]:
        """Run cleanup on deduplicator and lifecycle."""
        dedup_cleaned = self.deduplicator.clear_expired(dedup_hours)
        lifecycle_cleaned = self.lifecycle.cleanup(lifecycle_hours)
        return {"deduplication": dedup_cleaned, "lifecycle": lifecycle_cleaned}
    
    def _notify_listeners(self, alert: BuiltAlert) -> None:
        for listener in self._listeners:
            try:
                listener(alert)
            except Exception as e:
                logger.error(f"Listener error: {e}")
