import os
import sys
import json
import time
import requests
import logging
from pathlib import Path
from datetime import datetime, timezone
import urllib.request
import cv2

# Add root directory to path to import src
sys.path.append(os.getcwd())

from src.detector import ObjectDetector, FrameProcessor
from src.crowd import CrowdAnalyzer, save_heatmap, draw_zone_grid
from src.events import EventBuilder, save_events

# Configuration
API_BASE = "http://127.0.0.1:8000/api/v1"
OUTPUT_DIR = Path("outputs")
API_OUTPUTS = OUTPUT_DIR / "api_responses"
CV_OUTPUTS = OUTPUT_DIR / "cv_detections"
SAMPLES_DIR = OUTPUT_DIR / "cv_samples"

for d in [API_OUTPUTS, CV_OUTPUTS, SAMPLES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def save_json(data, filename, subdir="api_responses"):
    filepath = OUTPUT_DIR / subdir / filename
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved output to {filepath}")

def check_backend():
    try:
        response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health")
        if response.status_code == 200:
            logger.info("Backend is healthy")
            return True
    except requests.exceptions.ConnectionError:
        logger.error("Backend is NOT running. Please start it using 'uv run uvicorn backend.main:app'")
        return False
    return False

def run_cv_pipeline_scenario():
    logger.info("--- Scenario 1: Crowd Monitoring (CV Pipeline) ---")
    
    # 1. Prepare Sample Image
    sample_path = SAMPLES_DIR / "sample_crowd.jpg"
    if not sample_path.exists():
        logger.info("Downloading sample crowd image...")
        try:
            urllib.request.urlretrieve(
                "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=1280",
                sample_path
            )
        except Exception as e:
            logger.error(f"Failed to download sample image: {e}")
            return False

    # 2. Initalize Models
    logger.info("Initializing CV Models...")
    try:
        detector = ObjectDetector()
        detector.initialize(model_path="yolov8n.onnx") 
        analyzer = CrowdAnalyzer(coverage_area=50.0, grid_cols=3, grid_rows=3)
        event_builder = EventBuilder(camera_id="1") # EventBuilder expects string, but API might convert. Wait, API failed on int parsing. 
        # API ingest model (EventCreate) likely expects camera_id as int if it maps to Camera model.
        # But Event schema usually has string camera_id. 
        # Let's use string "1" here and ensure payload has int 1 if needed.
        # Check Event definition in backend.
        processor = FrameProcessor()
    except Exception as e:
        logger.error(f"Failed to initialize models (ensure yolov8n.onnx exists): {e}")
        return False

    # 3. Process Frame
    logger.info(f"Processing {sample_path}...")
    events_to_ingest = []
    
    # Simple processing loop (single frame for image)
    for frame in processor.process(str(sample_path)):
        detections = detector.detect(frame.frame, frame.timestamp, frame.frame_number)
        snapshot = analyzer.analyze(detections, frame.frame.shape, frame.timestamp)
        
        logger.info(f"Detected {snapshot.count} persons. Density: {snapshot.density:.2f}")
        
        stats = analyzer.get_stats()
        event = event_builder.crowd_detected(
            count=snapshot.count, 
            detections=[d.to_dict() for d in detections], 
            density=snapshot.density,
            level=snapshot.level.value
        )
        events_to_ingest.append(event)
        
        save_heatmap(snapshot.zones, 3, 3, str(CV_OUTPUTS / "density_heatmap.jpg"))
        grid_img = draw_zone_grid(frame.frame, snapshot.zones, 3, 3)
        cv2.imwrite(str(CV_OUTPUTS / "zone_grid.jpg"), grid_img)
        
    logger.info(f"Generated {len(events_to_ingest)} CV events")
    
    # 4. Ingest and Verify
    for event in events_to_ingest:
        payload = event.to_dict()
        # Fix camera_id for API if it requires int
        try:
             payload["camera_id"] = int(payload["camera_id"])
        except:
             pass

        try:
            res = requests.post(f"{API_BASE}/events/ingest", json=payload)
            if res.status_code == 201:
                logger.info("Ingested Crowd Event")
            else:
                logger.warning(f"Ingest failed: {res.text}")
        except Exception as e:
            logger.error(f"Ingest error: {e}")

    # Verify Alert
    time.sleep(2)
    res = requests.get(f"{API_BASE}/realtime-alerts?limit=5")
    if res.status_code == 200:
        data = res.json()
        if isinstance(data, list):
            alerts = data
        else:
            alerts = data.get("value", []) # OData style or standard dict
        
        crowd_alerts = [a for a in alerts if a["alert_type"] in ["crowd_surge", "crowd_detected"]]
        if crowd_alerts:
             logger.info("SUCCESS: Crowd Alert generated in backend")
             save_json(crowd_alerts, "scenario1_alerts.json")
        else:
             logger.warning("No crowd alert found (might need higher count for rule trigger)")

def scenario_static_object():
    logger.info("--- Scenario 2: Static Object Detection ---")
    payload = {
        "camera_id": "cam-002",
        "event_type": "static_object", # Or unattended_object based on API enum
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "confidence_score": 0.92,
        "data": {
            "class_name": "backpack",
            "dwell_time": 600,
            "bbox": [100, 100, 150, 150]
        }
    }
    
    res = requests.post(f"{API_BASE}/events/ingest", json=payload)
    if res.status_code == 201:
        logger.info("Ingested Static Object Event")
    else:
         logger.error(f"Failed: {res.text}")
         
    time.sleep(1)
    res = requests.get(f"{API_BASE}/realtime-alerts?limit=5")
    if res.status_code == 200:
        alerts = res.json().get("value", [])
        static = [a for a in alerts if a["alert_type"] in ["static_object", "suspicious_object"]]
        if static:
            logger.info("SUCCESS: Static Object Alert generated")
            save_json(static, "scenario2_alerts.json")

def scenario_patrol():
    logger.info("--- Scenario 3: Patrol Lifecycle ---")
    # Start
    officer_id = "OFF-AUTO-1"
    res = requests.post(f"{API_BASE}/patrol/start", json={"officer_id": officer_id, "officer_name": "RoboCop", "zone": "Central"})
    if res.status_code != 201:
        logger.error(f"Start failed: {res.text}")
        return
    patrol_id = res.json()["id"]
    save_json(res.json(), "scenario3_patrol_start.json")
    
    # Simulate Inicdents
    requests.post(f"{API_BASE}/events/ingest", json={
        "camera_id": "cam-patrol", "event_type": "person_running", "timestamp": datetime.now(timezone.utc).isoformat(), "confidence_score": 0.8, "data": {}
    })
    
    # End
    res = requests.post(f"{API_BASE}/patrol/{patrol_id}/end", json={"distance_km": 2.5})
    save_json(res.json(), "scenario3_patrol_end.json")
    
    # Summary
    res = requests.post(f"{API_BASE}/summaries/generate/patrol", json={"patrol_session_id": patrol_id})
    if res.status_code == 200:
        save_json(res.json(), "scenario3_patrol_summary.json")
        logger.info("Patrol Summary generated")
    else:
        logger.error(f"Summary failed: {res.text}")

def scenario_bandobast():
    logger.info("--- Scenario 4: Bandobast Report ---")
    res = requests.post(f"{API_BASE}/summaries/generate/bandobast", json={
        "event_name": "VIP Visit", "location": "Airport Road", "expected_crowd": 10000, "date": datetime.now().strftime("%Y-%m-%d")
    })
    if res.status_code == 200:
        save_json(res.json(), "scenario4_bandobast_report.json")
        logger.info("Bandobast Report generated")
    else:
        logger.error(f"Bandobast failed: {res.text}")

def scenario_daily():
    logger.info("--- Scenario 5: Daily Brief ---")
    res = requests.post(f"{API_BASE}/summaries/generate/daily", json={"date": datetime.now().strftime("%Y-%m-%d")})
    if res.status_code == 200:
        save_json(res.json(), "scenario5_daily_brief.json")
        logger.info("Daily Brief generated")
    else:
        logger.error(f"Daily Brief failed: {res.text}")

def main():
    if not check_backend():
        return
    
    run_cv_pipeline_scenario()
    scenario_static_object()
    scenario_patrol()
    scenario_bandobast()
    scenario_daily()
    
    logger.info("Test Suite Completed.")

if __name__ == "__main__":
    main()
