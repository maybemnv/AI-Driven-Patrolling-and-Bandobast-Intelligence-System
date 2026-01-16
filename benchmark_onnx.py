"""Benchmark PyTorch vs ONNX inference speed."""

import time
import cv2
import numpy as np
from pathlib import Path

from src.detector.onnx_detector import ONNXDetector


def benchmark_onnx(image_path: str = None, runs: int = 50):
    if image_path and Path(image_path).exists():
        image = cv2.imread(image_path)
    else:
        image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        print("Using random image for benchmark")
    
    print("\n=== ONNX Detector Benchmark ===")
    detector = ONNXDetector("yolov8n.onnx", conf_threshold=0.5)
    
    results = detector.benchmark(image, runs=runs)
    
    print(f"Average: {results['avg_ms']:.2f}ms")
    print(f"Min: {results['min_ms']:.2f}ms")
    print(f"Max: {results['max_ms']:.2f}ms")
    print(f"FPS: {results['fps']:.1f}")
    
    print("\n=== YOLOv8 PyTorch Benchmark ===")
    try:
        from ultralytics import YOLO
        model = YOLO("yolov8n.pt")
        
        for _ in range(10):
            model.predict(image, verbose=False)
        
        times = []
        for _ in range(runs):
            start = time.perf_counter()
            model.predict(image, verbose=False)
            times.append(time.perf_counter() - start)
        
        avg = np.mean(times) * 1000
        print(f"Average: {avg:.2f}ms")
        print(f"FPS: {1 / np.mean(times):.1f}")
        
        speedup = avg / results['avg_ms']
        print(f"\n✓ ONNX is {speedup:.2f}x faster than PyTorch")
    except Exception as e:
        print(f"Could not benchmark PyTorch: {e}")
    
    print("\n=== Detection Test ===")
    detections = detector.detect(image)
    print(f"Detected {len(detections)} objects")
    for det in detections[:5]:
        print(f"  - {det['class_name']}: {det['confidence']:.2f}")


if __name__ == "__main__":
    import sys
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    benchmark_onnx(image_path)
