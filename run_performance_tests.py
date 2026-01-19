import os
import sys
import time
import requests
import logging
import psutil
import json
import statistics
from pathlib import Path
from datetime import datetime
import cv2
import numpy as np

# Add src to path
sys.path.append(os.getcwd())

from src.detector import ObjectDetector, FrameProcessor
from src.crowd import CrowdAnalyzer

API_BASE = "http://127.0.0.1:8000/api/v1"
OUTPUT_DIR = Path("outputs")
SAMPLE_IMG = OUTPUT_DIR / "cv_samples" / "sample_crowd.jpg"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class PerformanceTester:
    def __init__(self):
        self.metrics = {
            "cv": {},
            "db": {},
            "llm": {}
        }
    
    def measure_cv_performance(self, iterations=50):
        logger.info(f"--- Benchmarking CV Pipeline ({iterations} frames) ---")
        
        if not SAMPLE_IMG.exists():
            logger.error("Sample image not found. Run integration tests first.")
            return

        # Load models
        detector = ObjectDetector()
        detector.initialize(model_path="yolov8n.onnx")
        analyzer = CrowdAnalyzer(coverage_area=50.0, grid_cols=3, grid_rows=3)
        
        # Load image
        img = cv2.imread(str(SAMPLE_IMG))
        if img is None:
            logger.error("Failed to load sample image")
            return

        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024 # MB
        
        latencies = []
        cpu_usages = []
        
        start_total = time.time()
        
        for i in range(iterations):
            t0 = time.time()
            # Simulation of frame processing
            detections = detector.detect(img, datetime.now(), i)
            _ = analyzer.analyze(detections, img.shape, datetime.now())
            latencies.append((time.time() - t0) * 1000) # ms
            
            if i % 10 == 0:
                cpu_usages.append(process.cpu_percent())
        
        total_time = time.time() - start_total
        fps = iterations / total_time
        mem_after = process.memory_info().rss / 1024 / 1024
        
        self.metrics["cv"] = {
            "avg_fps": round(fps, 2),
            "avg_latency_ms": round(statistics.mean(latencies), 2),
            "p95_latency_ms": round(np.percentile(latencies, 95), 2),
            "memory_increase_mb": round(mem_after - mem_before, 2),
            "cpu_usage_avg": round(statistics.mean(cpu_usages) if cpu_usages else 0, 2)
        }
        logger.info(f"CV Metrics: {json.dumps(self.metrics['cv'], indent=2)}")

    def measure_db_performance(self):
        logger.info("--- Benchmarking Database (API Latency) ---")
        
        # Write Latency (Create Events)
        write_latencies = []
        for _ in range(20):
            payload = {
                "camera_id": "perf_test_cam",
                "event_type": "crowd_detected",
                "timestamp": datetime.now().isoformat(),
                "confidence_score": 0.9,
                "data": {"count": 10}
            }
            t0 = time.time()
            requests.post(f"{API_BASE}/events/ingest", json=payload)
            write_latencies.append((time.time() - t0) * 1000)
            
        # Read Latency (List Events)
        read_latencies = []
        for _ in range(20):
            t0 = time.time()
            requests.get(f"{API_BASE}/events?limit=50")
            read_latencies.append((time.time() - t0) * 1000)
            
        self.metrics["db"] = {
            "avg_write_latency_ms": round(statistics.mean(write_latencies), 2),
            "avg_read_latency_ms": round(statistics.mean(read_latencies), 2),
            "min_read_ms": round(min(read_latencies), 2),
            "max_read_ms": round(max(read_latencies), 2)
        }
        logger.info(f"DB Metrics: {json.dumps(self.metrics['db'], indent=2)}")

    def measure_llm_performance(self):
        logger.info("--- Benchmarking LLM Generation ---")
        
        # Note: This depends on the actual LLM (Groq/Ollama). 
        # API returns 'duration_ms' usually, or we verify wall clock via API call.
        
        start_time = time.time()
        res = requests.post(f"{API_BASE}/summaries/generate/daily", json={"date": datetime.now().strftime("%Y-%m-%d")})
        total_duration = (time.time() - start_time) * 1000
        
        if res.status_code == 200:
            data = res.json()
            api_reported_duration = data.get("duration_ms", 0)
            tokens = data.get("tokens_used", 0)
            
            self.metrics["llm"] = {
                "total_request_ms": round(total_duration, 2),
                "api_reported_generation_ms": round(api_reported_duration, 2),
                "tokens_generated": tokens,
                "ms_per_token": round(api_reported_duration / tokens, 2) if tokens > 0 else 0
            }
        else:
            logger.error("LLM generation failed")
            self.metrics["llm"] = {"error": res.status_code}
            
        logger.info(f"LLM Metrics: {json.dumps(self.metrics['llm'], indent=2)}")

    def save_report(self):
        outfile = OUTPUT_DIR / "performance_metrics.json"
        with open(outfile, "w") as f:
            json.dump(self.metrics, f, indent=2)
        logger.info(f"Saved metrics to {outfile}")
        
        # Create Markdown Report
        md_report = f"""# Performance Test Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Computer Vision Pipeline
- **Average FPS**: {self.metrics['cv'].get('avg_fps')}
- **Latency (avg)**: {self.metrics['cv'].get('avg_latency_ms')} ms
- **Memory Delta**: {self.metrics['cv'].get('memory_increase_mb')} MB

## Database / API
- **Write Latency**: {self.metrics['db'].get('avg_write_latency_ms')} ms (Event Ingest)
- **Read Latency**: {self.metrics['db'].get('avg_read_latency_ms')} ms (List Events)

## LLM Generation
- **Total Request Time**: {self.metrics['llm'].get('total_request_ms')} ms
- **Tokens Generated**: {self.metrics['llm'].get('tokens_generated')}
- **Speed**: {self.metrics['llm'].get('ms_per_token')} ms/token
"""
        with open(OUTPUT_DIR / "PERFORMANCE_REPORT.md", "w") as f:
            f.write(md_report)
        logger.info("Saved report to outputs/PERFORMANCE_REPORT.md")

if __name__ == "__main__":
    tester = PerformanceTester()
    tester.measure_cv_performance()
    tester.measure_db_performance()
    tester.measure_llm_performance()
    tester.save_report()
