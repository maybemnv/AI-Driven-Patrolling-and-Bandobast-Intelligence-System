"""Database models for the Patrolling and Bandobast Intelligence System."""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey,
    Enum, Index, UniqueConstraint, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class CameraStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class EventType(PyEnum):
    OBJECT_DETECTED = "object_detected"
    CROWD_DETECTED = "crowd_detected"
    CROWD_SURGE = "crowd_surge"
    STATIC_OBJECT = "static_object"
    ROUTE_BLOCKED = "route_blocked"
    INTRUSION = "intrusion"


class AlertSeverity(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(PyEnum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"
    AUTO_RESOLVED = "auto_resolved"


class AlertPriority(PyEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PatrolStatus(PyEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SummaryType(PyEnum):
    PATROL = "patrol"
    BANDOBAST = "bandobast"
    DAILY = "daily"
    WEEKLY = "weekly"


class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_name = Column(String(100), nullable=False)
    location_name = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(Enum(CameraStatus), default=CameraStatus.ACTIVE)
    installation_date = Column(DateTime, nullable=True)
    last_active_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    events = relationship("Event", back_populates="camera")
    
    __table_args__ = (
        Index("ix_cameras_status", "status"),
        Index("ix_cameras_location", "latitude", "longitude"),
    )


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    event_type = Column(Enum(EventType), nullable=False, index=True)
    confidence_score = Column(Float, default=0.0)
    data = Column(JSON, default=dict)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    camera = relationship("Camera", back_populates="events")
    alerts = relationship("Alert", back_populates="event")
    
    __table_args__ = (
        Index("ix_events_camera_time", "camera_id", "timestamp"),
        Index("ix_events_type_time", "event_type", "timestamp"),
    )


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.LOW)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    priority = Column(Enum(AlertPriority), default=AlertPriority.MEDIUM)
    priority_score = Column(Float, default=0.5)
    message = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    occurrence_count = Column(Integer, default=1)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    event = relationship("Event", back_populates="alerts")
    
    __table_args__ = (
        Index("ix_alerts_severity", "severity"),
        Index("ix_alerts_status", "status"),
        Index("ix_alerts_priority", "priority"),
        Index("ix_alerts_ack", "acknowledged", "created_at"),
    )


class PatrolSession(Base):
    __tablename__ = "patrol_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    officer_id = Column(String(50), nullable=False, index=True)
    officer_name = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    route_data = Column(JSON, default=list)  # GPS points
    status = Column(Enum(PatrolStatus), default=PatrolStatus.ACTIVE)
    incidents_count = Column(Integer, default=0)
    distance_km = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    summaries = relationship("Summary", back_populates="patrol_session")
    
    __table_args__ = (
        Index("ix_patrols_officer", "officer_id", "start_time"),
        Index("ix_patrols_status", "status"),
    )


class Summary(Base):
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    summary_type = Column(Enum(SummaryType), nullable=False)
    patrol_session_id = Column(Integer, ForeignKey("patrol_sessions.id"), nullable=True)
    reference_date = Column(DateTime, nullable=True)
    content = Column(Text, nullable=False)
    key_insights = Column(JSON, default=list)
    risk_score = Column(Float, default=0.0)
    generated_at = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON, default=dict)
    
    patrol_session = relationship("PatrolSession", back_populates="summaries")
    
    __table_args__ = (
        Index("ix_summaries_type", "summary_type", "generated_at"),
    )


def create_db_engine(url: str = "sqlite:///data/patrolling.db"):
    """Create database engine."""
    return create_engine(url, echo=False)


def init_db(engine):
    """Create all tables."""
    Base.metadata.create_all(engine)


def get_session(engine):
    """Get database session."""
    Session = sessionmaker(bind=engine)
    return Session()
