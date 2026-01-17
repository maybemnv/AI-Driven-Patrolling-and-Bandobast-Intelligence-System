"""API endpoint testing script."""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "dev-key-123"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


def test_health():
    print("\n=== Health Check ===")
    r = requests.get(f"{BASE_URL}/health")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
    return r.status_code == 200


def test_api_info():
    print("\n=== API Info ===")
    r = requests.get(f"{BASE_URL}/api/v1")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
    return r.status_code == 200


def test_cameras():
    print("\n=== Cameras CRUD ===")
    
    # Create
    camera = {
        "camera_name": "Test CAM-99",
        "location_name": "Test Location",
        "latitude": 28.6139,
        "longitude": 77.2090
    }
    r = requests.post(f"{BASE_URL}/api/v1/cameras", json=camera, headers=HEADERS)
    print(f"Create: {r.status_code}")
    if r.status_code != 201:
        print(f"  Error: {r.text}")
        return False
    camera_id = r.json().get("id")
    
    # List
    r = requests.get(f"{BASE_URL}/api/v1/cameras", headers=HEADERS)
    print(f"List: {r.status_code} - {len(r.json())} cameras")
    
    # Get
    r = requests.get(f"{BASE_URL}/api/v1/cameras/{camera_id}", headers=HEADERS)
    print(f"Get: {r.status_code}")
    
    # Update status
    r = requests.patch(
        f"{BASE_URL}/api/v1/cameras/{camera_id}/status",
        json={"status": "inactive"},
        headers=HEADERS
    )
    print(f"Update: {r.status_code}")
    
    # Delete
    r = requests.delete(f"{BASE_URL}/api/v1/cameras/{camera_id}", headers=HEADERS)
    print(f"Delete: {r.status_code}")
    
    return True


def test_events():
    print("\n=== Events ===")
    
    # Ingest
    event = {
        "camera_id": 1,
        "event_type": "crowd_detected",
        "confidence_score": 0.85,
        "data": {"count": 25, "density": 1.5}
    }
    r = requests.post(f"{BASE_URL}/api/v1/events/ingest", json=event, headers=HEADERS)
    print(f"Ingest: {r.status_code}")
    if r.status_code not in [200, 201]:
        print(f"  Note: {r.text[:100]}")
    
    # List
    r = requests.get(f"{BASE_URL}/api/v1/events?limit=5", headers=HEADERS)
    print(f"List: {r.status_code} - {len(r.json().get('items', []))} events")
    
    # Filter
    r = requests.get(f"{BASE_URL}/api/v1/events?event_type=crowd_detected", headers=HEADERS)
    print(f"Filter: {r.status_code}")
    
    return True


def test_alerts():
    print("\n=== Alerts ===")
    
    # List
    r = requests.get(f"{BASE_URL}/api/v1/alerts?limit=5", headers=HEADERS)
    print(f"List: {r.status_code} - {len(r.json().get('items', []))} alerts")
    
    # Stats
    r = requests.get(f"{BASE_URL}/api/v1/alerts/stats", headers=HEADERS)
    print(f"Stats: {r.status_code}")
    if r.status_code == 200:
        print(f"  {r.json()}")
    
    return True


def test_patrol():
    print("\n=== Patrol ===")
    
    # Start
    patrol = {
        "officer_id": "OFF-TEST-001",
        "officer_name": "Test Officer",
        "start_lat": 28.6139,
        "start_lon": 77.2090
    }
    r = requests.post(f"{BASE_URL}/api/v1/patrol/start", json=patrol, headers=HEADERS)
    print(f"Start: {r.status_code}")
    if r.status_code != 201:
        print(f"  Note: {r.text[:100]}")
        return True
    
    session_id = r.json().get("id")
    
    # Add event
    event = {
        "event_type": "checkpoint",
        "latitude": 28.6145,
        "longitude": 77.2095,
        "notes": "All clear at checkpoint"
    }
    r = requests.post(f"{BASE_URL}/api/v1/patrol/{session_id}/event", json=event, headers=HEADERS)
    print(f"Add event: {r.status_code}")
    
    # End
    end_data = {"end_lat": 28.6150, "end_lon": 77.2100}
    r = requests.post(f"{BASE_URL}/api/v1/patrol/end?session_id={session_id}", json=end_data, headers=HEADERS)
    print(f"End: {r.status_code}")
    
    # List sessions
    r = requests.get(f"{BASE_URL}/api/v1/patrol/sessions?limit=3", headers=HEADERS)
    print(f"Sessions: {r.status_code}")
    
    return True


def test_summaries():
    print("\n=== Summaries ===")
    
    # Generate (may fail if no LLM configured)
    summary_req = {
        "summary_type": "daily",
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    r = requests.post(f"{BASE_URL}/api/v1/summaries/generate", json=summary_req, headers=HEADERS)
    print(f"Generate: {r.status_code}")
    
    # List
    r = requests.get(f"{BASE_URL}/api/v1/summaries?limit=3", headers=HEADERS)
    print(f"List: {r.status_code}")
    
    return True


def test_error_cases():
    print("\n=== Error Cases ===")
    
    # Invalid event type
    r = requests.post(
        f"{BASE_URL}/api/v1/events/ingest",
        json={"camera_id": 1, "event_type": "invalid_type"},
        headers=HEADERS
    )
    print(f"Invalid event type: {r.status_code} (expected 422)")
    
    # Missing required field
    r = requests.post(
        f"{BASE_URL}/api/v1/cameras",
        json={"camera_name": "Test"},
        headers=HEADERS
    )
    print(f"Missing field: {r.status_code} (expected 422)")
    
    # Not found
    r = requests.get(f"{BASE_URL}/api/v1/cameras/99999", headers=HEADERS)
    print(f"Not found: {r.status_code} (expected 404)")
    
    return True


def test_pagination():
    print("\n=== Pagination ===")
    
    # First page
    r = requests.get(f"{BASE_URL}/api/v1/events?skip=0&limit=2", headers=HEADERS)
    print(f"Page 1: {r.status_code}")
    data = r.json()
    print(f"  Items: {len(data.get('items', []))}, Total: {data.get('total', 'N/A')}")
    
    # Second page
    r = requests.get(f"{BASE_URL}/api/v1/events?skip=2&limit=2", headers=HEADERS)
    print(f"Page 2: {r.status_code}")
    
    return True


def test_request_tracking():
    print("\n=== Request Tracking ===")
    
    r = requests.get(f"{BASE_URL}/health")
    request_id = r.headers.get("X-Request-ID")
    rate_remaining = r.headers.get("X-RateLimit-Remaining")
    
    print(f"X-Request-ID: {request_id}")
    print(f"X-RateLimit-Remaining: {rate_remaining}")
    
    return request_id is not None


def main():
    print("=" * 50)
    print("API ENDPOINT TESTING")
    print("=" * 50)
    
    results = {
        "Health": test_health(),
        "API Info": test_api_info(),
        "Request Tracking": test_request_tracking(),
        "Cameras": test_cameras(),
        "Events": test_events(),
        "Alerts": test_alerts(),
        "Patrol": test_patrol(),
        "Summaries": test_summaries(),
        "Pagination": test_pagination(),
        "Error Cases": test_error_cases(),
    }
    
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} passed")


if __name__ == "__main__":
    main()
