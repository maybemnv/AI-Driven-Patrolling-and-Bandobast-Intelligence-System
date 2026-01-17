"""Notification system for alerts."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    COPMAP_WEBHOOK = "copmap_webhook"
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"


@dataclass
class NotificationPayload:
    alert_id: str
    alert_type: str
    severity: str
    priority: str
    location_lat: Optional[float]
    location_lon: Optional[float]
    message: str
    description: str
    timestamp: str
    recommended_action: str
    media_ref: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "priority": self.priority,
            "location": {"lat": self.location_lat, "lon": self.location_lon} if self.location_lat else None,
            "message": self.message,
            "description": self.description,
            "timestamp": self.timestamp,
            "recommended_action": self.recommended_action,
            "media_ref": self.media_ref,
            "metadata": self.metadata,
        }


@dataclass
class NotificationResult:
    channel: NotificationChannel
    success: bool
    response: Optional[Dict] = None
    error: Optional[str] = None
    attempts: int = 1


class NotificationBuilder:
    """Builds notification payloads from alerts."""
    
    def from_alert(self, alert: Any) -> NotificationPayload:
        if hasattr(alert, "to_dict"):
            d = alert.to_dict()
        else:
            d = alert
        
        loc = d.get("location") or {}
        
        return NotificationPayload(
            alert_id=d.get("alert_id", ""),
            alert_type=d.get("alert_type", ""),
            severity=d.get("severity", "low"),
            priority=d.get("priority", "low"),
            location_lat=loc.get("lat") or d.get("location_lat"),
            location_lon=loc.get("lon") or d.get("location_lon"),
            message=d.get("message", ""),
            description=d.get("description", ""),
            timestamp=d.get("timestamp", datetime.now(timezone.utc).isoformat()),
            recommended_action=d.get("recommended_action", ""),
            media_ref=d.get("media_ref"),
            metadata=d.get("metadata", {}),
        )


class NotificationDispatcher:
    """Dispatches notifications through configured channels."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._log: List[Dict] = []
    
    def send(self, payload: NotificationPayload, channel: NotificationChannel) -> NotificationResult:
        """Send notification to specified channel."""
        for attempt in range(1, self.max_retries + 1):
            try:
                result = self._dispatch(payload, channel, attempt)
                self._log_notification(payload, channel, result)
                if result.success:
                    return result
            except Exception as e:
                logger.error(f"Notification attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    result = NotificationResult(channel=channel, success=False, error=str(e), attempts=attempt)
                    self._log_notification(payload, channel, result)
                    return result
        
        return NotificationResult(channel=channel, success=False, error="Max retries exceeded")
    
    def _dispatch(self, payload: NotificationPayload, channel: NotificationChannel, attempt: int) -> NotificationResult:
        """Internal dispatch - override for actual implementation."""
        if channel == NotificationChannel.COPMAP_WEBHOOK:
            return NotificationResult(channel=channel, success=True, response={"status": "queued"}, attempts=attempt)
        
        # Placeholder for other channels
        return NotificationResult(channel=channel, success=True, response={"status": "mock"}, attempts=attempt)
    
    def _log_notification(self, payload: NotificationPayload, channel: NotificationChannel, result: NotificationResult) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alert_id": payload.alert_id,
            "channel": channel.value,
            "success": result.success,
            "attempts": result.attempts,
            "error": result.error,
        }
        self._log.append(entry)
        logger.info(f"Notification: {entry}")
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        return self._log[-limit:]
