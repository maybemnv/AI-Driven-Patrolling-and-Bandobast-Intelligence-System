"""Detection pipeline demo - downloads sample, runs detection, saves outputs."""

import json
import logging
from pathlib import Path
import urllib.request

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def download_sample(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "sample_input.jpg"
    
    if path.exists():
        return path
    
    url = "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=1280"
    try:
        urllib.request.urlretrieve(url, path)
        log.info(f"Downloaded: {path}")
    except Exception:
        import cv2
        import numpy as np
        img = np.ones((480, 640, 3), dtype=np.uint8) * 128
        cv2.imwrite(str(path), img)
        log.info(f"Created test image: {path}")
    
    return path


def load_config() -> dict:
    import yaml
    cfg_path = Path(__file__).parent / "config.yaml"
    if cfg_path.exists():
        with open(cfg_path) as f:
            return yaml.safe_load(f)
    return {
        "detection": {
            "model": {"path": "yolov8n.pt", "device": "auto"},
            "inference": {"confidence_threshold": 0.5, "iou_threshold": 0.45, "image_size": 640},
            "target_classes": [0, 2, 5, 7, 24, 26],
        }
    }


def main():
    log.info("Object Detection Pipeline Demo")
    
    project = Path(__file__).parent
    output = project / "outputs" / "cv_samples"
    output.mkdir(parents=True, exist_ok=True)
    
    cfg = load_config()
    det_cfg = cfg.get("detection", {})
    
    sample = download_sample(output)
    
    from model import ObjectDetector, FrameProcessor, EventBuilder, save_events
    
    detector = ObjectDetector(target_classes=set(det_cfg.get("target_classes", [0, 2, 5, 7, 24, 26])))
    model_cfg = det_cfg.get("model", {})
    inf_cfg = det_cfg.get("inference", {})
    
    detector.initialize(
        model_path=model_cfg.get("path", "yolov8n.pt"),
        device=model_cfg.get("device", "auto"),
        confidence=inf_cfg.get("confidence_threshold", 0.5),
        iou=inf_cfg.get("iou_threshold", 0.45),
        imgsz=inf_cfg.get("image_size", 640),
    )
    
    processor = FrameProcessor(imgsz=inf_cfg.get("image_size", 640))
    builder = EventBuilder(camera_id="demo_camera")
    events = []
    
    for frame in processor.process(str(sample)):
        detections = detector.detect(frame.frame, frame.timestamp, frame.frame_number)
        log.info(f"Found {len(detections)} objects")
        
        for det in detections:
            events.append(builder.object_detected(
                class_name=det.class_name,
                class_id=det.class_id,
                confidence=det.confidence,
                bbox={"x": det.bbox[0], "y": det.bbox[1], "w": det.bbox[2], "h": det.bbox[3]},
            ))
            log.info(f"  {det.class_name}: {det.confidence:.2f}")
        
        detector.save_annotated(frame.frame, detections, str(output / "annotated.jpg"))
    
    save_events(events, str(output / "detections.json"))
    
    log.info(f"Done! Outputs: {output}")
    print(json.dumps({"detections": len(events), "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
