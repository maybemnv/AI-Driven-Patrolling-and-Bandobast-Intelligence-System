"""Database seed script for initial test data."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random

from sqlalchemy.orm import Session

from database.models import Camera, CameraStatus, Event, EventType, Alert, AlertSeverity


def seed_cameras(db: Session) -> list:
    cameras = [
        Camera(
            camera_name="Main Gate CAM-01",
            location_name="Police Station Main Entrance",
            latitude=28.6139,
            longitude=77.2090,
            status=CameraStatus.ACTIVE,
            installation_date=datetime.utcnow() - timedelta(days=90),
        ),
        Camera(
            camera_name="Market Area CAM-02",
            location_name="Central Market Junction",
            latitude=28.6145,
            longitude=77.2095,
            status=CameraStatus.ACTIVE,
            installation_date=datetime.utcnow() - timedelta(days=60),
        ),
        Camera(
            camera_name="VIP Route CAM-03",
            location_name="VIP Route Checkpoint Alpha",
            latitude=28.6150,
            longitude=77.2100,
            status=CameraStatus.ACTIVE,
            installation_date=datetime.utcnow() - timedelta(days=45),
        ),
        Camera(
            camera_name="Park Entrance CAM-04",
            location_name="City Park North Gate",
            latitude=28.6160,
            longitude=77.2110,
            status=CameraStatus.ACTIVE,
            installation_date=datetime.utcnow() - timedelta(days=30),
        ),
        Camera(
            camera_name="Railway Station CAM-05",
            location_name="Railway Station Platform 1",
            latitude=28.6170,
            longitude=77.2120,
            status=CameraStatus.INACTIVE,
            installation_date=datetime.utcnow() - timedelta(days=15),
        ),
    ]
    
    for cam in cameras:
        db.add(cam)
    db.commit()
    
    for cam in cameras:
        db.refresh(cam)
    
    return cameras


def seed_events(db: Session, cameras: list) -> list:
    events = []
    
    for i in range(20):
        cam = random.choice(cameras[:4])
        event_type = random.choice(list(EventType))
        
        event = Event(
            camera_id=cam.id,
            timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
            event_type=event_type,
            confidence_score=round(random.uniform(0.6, 0.98), 2),
            data={
                "count": random.randint(5, 50) if "crowd" in event_type.value else None,
                "density": round(random.uniform(0.5, 4.0), 1) if "crowd" in event_type.value else None,
            },
            processed=random.choice([True, False]),
        )
        events.append(event)
        db.add(event)
    
    db.commit()
    return events


def seed_alerts(db: Session, events: list) -> list:
    alerts = []
    
    severity_choices = [AlertSeverity.LOW, AlertSeverity.MEDIUM, AlertSeverity.HIGH]
    
    for event in events[:10]:
        severity = random.choice(severity_choices)
        
        alert = Alert(
            event_id=event.id,
            alert_type=event.event_type.value,
            severity=severity,
            message=f"Alert: {event.event_type.value} detected with confidence {event.confidence_score}",
            location_lat=28.6139 + random.uniform(-0.01, 0.01),
            location_lon=77.2090 + random.uniform(-0.01, 0.01),
            acknowledged=random.choice([True, False, False]),
        )
        alerts.append(alert)
        db.add(alert)
    
    db.commit()
    return alerts


def run_seed():
    from backend.deps import SessionLocal
    
    db = SessionLocal()
    try:
        existing = db.query(Camera).count()
        if existing > 0:
            print(f"Database already has {existing} cameras. Skipping seed.")
            return
        
        print("Seeding cameras...")
        cameras = seed_cameras(db)
        print(f"  Created {len(cameras)} cameras")
        
        print("Seeding events...")
        events = seed_events(db, cameras)
        print(f"  Created {len(events)} events")
        
        print("Seeding alerts...")
        alerts = seed_alerts(db, events)
        print(f"  Created {len(alerts)} alerts")
        
        print("✓ Seed complete!")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
