"""Demo script for anomaly detection rules engine."""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.rules import (
    RuleEngine,
    RuleContext,
    StaticObjectRule,
    CrowdSurgeRule,
    RouteBlockageRule,
    AfterHoursRule,
)


def main():
    output_dir = Path("outputs/anomaly_detection")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    engine = RuleEngine()
    engine.register(CrowdSurgeRule(rate_threshold_percent=50, min_initial_crowd=10))
    engine.register(StaticObjectRule(time_threshold_seconds=300))
    engine.register(RouteBlockageRule(
        route_zones=[{"zone_id": "z1", "name": "Main Gate", "importance": "high"}],
        blockage_threshold=0.3,
    ))
    engine.register(AfterHoursRule(min_activity_threshold=2))
    
    print(f"Registered {len(engine.rules)} rules")
    
    # Test 1: Static bag for 10 minutes
    print("\n--- Test 1: Static Bag ---")
    ctx1 = RuleContext(
        timestamp=datetime.now(timezone.utc),
        camera_id="cam_gate1",
        tracked_objects={
            "obj_123": {
                "is_static": True,
                "dwell_time": 600,
                "class_name": "backpack",
                "confidence": 0.92,
                "location": {"x": 320, "y": 240},
                "bbox": {"x": 300, "y": 220, "w": 40, "h": 50},
            }
        },
    )
    alerts1 = engine.evaluate_all(ctx1)
    for a in alerts1:
        print(f"  [{a.severity.value.upper()}] {a.message} (conf: {a.confidence:.2f})")
    
    # Test 2: Crowd surge
    print("\n--- Test 2: Crowd Surge ---")
    engine.clear_history()
    ctx2 = RuleContext(
        timestamp=datetime.now(timezone.utc),
        camera_id="cam_market",
        crowd_data={
            "count": 150,
            "previous_count": 60,
            "density": 3.5,
            "trend": "increasing",
        },
    )
    alerts2 = engine.evaluate_all(ctx2)
    for a in alerts2:
        print(f"  [{a.severity.value.upper()}] {a.message} (conf: {a.confidence:.2f})")
    
    # Test 3: Route blockage
    print("\n--- Test 3: Route Blockage ---")
    engine.clear_history()
    ctx3 = RuleContext(
        timestamp=datetime.now(timezone.utc),
        camera_id="cam_vip_route",
        detections=[
            {"class_name": "truck", "confidence": 0.88, "bbox": {}},
            {"class_name": "car", "confidence": 0.91, "bbox": {}},
        ],
    )
    alerts3 = engine.evaluate_all(ctx3)
    for a in alerts3:
        print(f"  [{a.severity.value.upper()}] {a.message} (conf: {a.confidence:.2f})")
    
    # Test 4: After hours
    print("\n--- Test 4: After-Hours Activity ---")
    engine.clear_history()
    ctx4 = RuleContext(
        timestamp=datetime(2026, 1, 16, 2, 30, tzinfo=timezone.utc),
        camera_id="cam_warehouse",
        detections=[
            {"class_name": "person", "confidence": 0.85},
            {"class_name": "person", "confidence": 0.78},
            {"class_name": "car", "confidence": 0.92},
        ],
    )
    alerts4 = engine.evaluate_all(ctx4)
    for a in alerts4:
        print(f"  [{a.severity.value.upper()}] {a.message} (conf: {a.confidence:.2f})")
    
    # Save all alerts
    all_alerts = alerts1 + alerts2 + alerts3 + alerts4
    output_file = output_dir / f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump([a.to_dict() for a in all_alerts], f, indent=2)
    
    print(f"\n✓ Saved {len(all_alerts)} alerts to {output_file}")


if __name__ == "__main__":
    main()
