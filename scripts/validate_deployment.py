import os
import sys
import subprocess
import requests
import logging
from pathlib import Path

# Configuration
API_BASE = "http://127.0.0.1:8000/api/v1"
PROJECT_ROOT = Path(__file__).parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("validation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_env_vars():
    logger.info("--- 1. Checking Environment Variables ---")
    required_vars = ["DATABASE_URL", "GROQ_API_KEY"]
    missing = []
    
    # Check .env file content
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        with open(env_path, "r") as f:
            content = f.read()
        for var in required_vars:
            if f"{var}=" not in content:
                missing.append(var)
    else:
        logger.warning(".env file not found!")
    
    if missing:
        logger.error(f"Missing required env vars: {missing}")
    else:
        logger.info("Environment configuration looks valid.")

def verify_copmap_integration():
    logger.info("--- 2. Verifying CopMap Integration ---")
    endpoint = f"{API_BASE}/copmap/alerts" # Correct endpoint
    
    payload = {
        "alert_type": "deployment_test",
        "severity": "low",
        "message": "Validating CopMap endpoint during deployment check",
        "location_lat": 28.0,
        "location_lon": 77.0
    }
    
    try:
        res = requests.post(endpoint, json=payload)
        if res.status_code == 200:
            data = res.json()
            logger.info(f"SUCCESS: CopMap alert accepted. Ref: {data.get('copmap_ref')}")
        else:
            logger.error(f"CopMap endpoint failed: {res.status_code} {res.text}")
    except Exception as e:
        logger.error(f"Failed to connect to backend: {e}")

def check_docker_config():
    logger.info("--- 3. Verifying Docker Config ---")
    compose_file = PROJECT_ROOT / "compose.yaml"
    if not compose_file.exists():
        logger.error("compose.yaml not found")
        return

    try:
        # Run docker compose config to validate syntax
        result = subprocess.run(
            ["docker", "compose", "config"], 
            cwd=str(PROJECT_ROOT),
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            logger.info("Docker Compose configuration is VALID.")
        else:
            logger.warning(f"Docker Compose validation warning/error: {result.stderr}")
            # Windows might not have docker installed or running, which is fine, we just check if file exists essentially if docker fails.
            if "not found" in result.stderr:
                 logger.warning("Docker command not found, skipping deep validation.")
    except FileNotFoundError:
        logger.warning("Docker executable not found. Skipping validation.")
    except Exception as e:
        logger.error(f"Docker check failed: {e}")

def main():
    logger.info("Starting System Validation...")
    check_env_vars()
    verify_copmap_integration()
    check_docker_config()
    logger.info("Validation Complete.")

if __name__ == "__main__":
    main()
