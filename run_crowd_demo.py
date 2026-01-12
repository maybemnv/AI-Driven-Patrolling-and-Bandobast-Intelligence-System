"""Crowd analysis demo with visualizations."""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def main():
    log.info("Crowd Analysis Demo")
    
    project = Path(__file__).parent
    output = project / "outputs" / "crowd_analysis"
    output.mkdir(parents=True, exist_ok=True)
    
    from model import ObjectDetector, FrameProcessor, CrowdEventBuilder, save_events
    from model.crowd import CrowdAnalyzer, save_heatmap, draw_zone_grid
    import cv2
    
    import yaml
    cfg_path = project / "config.yaml"
    cfg = yaml.safe_load(open(cfg_path)) if cfg_path.exists() else {}
    det_cfg = cfg.get("detection", {})
    
    detector = ObjectDetector()
    detector.initialize(
        model_path=det_cfg.get("model", {}).get("path", "yolov8n.pt"),
        device=det_cfg.get("model", {}).get("device", "auto"),
    )
    
    analyzer = CrowdAnalyzer(coverage_area=50.0, grid_cols=3, grid_rows=3)
    event_builder = CrowdEventBuilder(camera_id="demo_cam")
    processor = FrameProcessor()
    
    sample_path = project / "outputs" / "cv_samples" / "sample_input.jpg"
    if not sample_path.exists():
        import urllib.request
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(
            "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=1280",
            sample_path
        )
    
    events = []
    snapshot = None
    frame_img = None
    
    for frame in processor.process(str(sample_path)):
        frame_img = frame.frame
        detections = detector.detect(frame.frame, frame.timestamp, frame.frame_number)
        
        snapshot = analyzer.analyze(detections, frame.frame.shape, frame.timestamp)
        stats = analyzer.get_stats()
        smoothed = analyzer.get_smoothed_count()
        
        log.info(f"Count: {snapshot.count} (smoothed: {smoothed})")
        log.info(f"Density: {snapshot.density:.3f}/sqm, Level: {snapshot.level.value}")
        log.info(f"Zones: {snapshot.zones}")
        
        surge = analyzer.detect_surge(frame.timestamp)
        priority = event_builder.calculate_priority(snapshot, surge)
        log.info(f"Priority: {priority}/10")
        
        if surge:
            events.append(event_builder.from_surge(surge, frame.timestamp))
        
        event = event_builder.from_snapshot(snapshot, stats, emit_normal=True)
        if event:
            events.append(event)
    
    # Save visualizations
    if snapshot and frame_img is not None:
        save_heatmap(snapshot.zones, 3, 3, str(output / "density_heatmap.jpg"))
        log.info("Saved: density_heatmap.jpg")
        
        grid_img = draw_zone_grid(frame_img, snapshot.zones, 3, 3)
        cv2.imwrite(str(output / "zone_grid.jpg"), grid_img)
        log.info("Saved: zone_grid.jpg")
    
    save_events([e for e in events if e], str(output / "crowd_events.json"))
    
    summary = {
        "count": snapshot.count if snapshot else 0,
        "density": round(snapshot.density, 4) if snapshot else 0,
        "level": snapshot.level.value if snapshot else "unknown",
        "priority": priority if 'priority' in dir() else 0,
        "zones": {f"{r},{c}": v for (r, c), v in snapshot.zones.items()} if snapshot else {},
    }
    
    with open(output / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    log.info(f"Done! Outputs: {output}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
