"""Crowd analysis demo - tests density and surge detection."""

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
    
    from model import (
        ObjectDetector, FrameProcessor,
        CrowdAnalyzer, CrowdEventBuilder, DensityLevel, save_events
    )
    
    # Load config
    import yaml
    cfg_path = project / "config.yaml"
    if cfg_path.exists():
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
    else:
        cfg = {"detection": {"model": {"path": "yolov8n.pt"}}}
    
    det_cfg = cfg.get("detection", {})
    
    # Initialize detector
    detector = ObjectDetector()
    detector.initialize(
        model_path=det_cfg.get("model", {}).get("path", "yolov8n.pt"),
        device=det_cfg.get("model", {}).get("device", "auto"),
    )
    
    # Initialize crowd analyzer
    analyzer = CrowdAnalyzer(
        coverage_area=50.0,  # Smaller area for demo
        grid_cols=3,
        grid_rows=3,
    )
    
    event_builder = CrowdEventBuilder(camera_id="demo_cam")
    processor = FrameProcessor()
    
    # Use existing sample or download
    sample_path = project / "outputs" / "cv_samples" / "sample_input.jpg"
    if not sample_path.exists():
        import urllib.request
        output.mkdir(parents=True, exist_ok=True)
        url = "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=1280"
        urllib.request.urlretrieve(url, sample_path)
    
    events = []
    
    # Process frames
    for frame in processor.process(str(sample_path)):
        detections = detector.detect(frame.frame, frame.timestamp, frame.frame_number)
        
        # Analyze crowd
        snapshot = analyzer.analyze(
            detections,
            frame.frame.shape,
            frame.timestamp,
        )
        
        stats = analyzer.get_stats()
        
        log.info(f"Count: {snapshot.count}, Density: {snapshot.density:.3f}/sqm, Level: {snapshot.level.value}")
        log.info(f"Stats: mean={stats['mean']}, trend={stats['trend']}")
        log.info(f"Zones: {snapshot.zones}")
        
        # Check for surge
        surge = analyzer.detect_surge(frame.timestamp)
        if surge:
            log.info(f"SURGE: {surge.severity.value} - rate={surge.rate_of_change:.1f}/min")
            event = event_builder.from_surge(surge, frame.timestamp)
            if event:
                events.append(event)
        
        # Generate density event
        event = event_builder.from_snapshot(snapshot, stats, emit_normal=True)
        if event:
            events.append(event)
    
    # Save events
    save_events(events, str(output / "crowd_events.json"))
    
    # Save analysis summary
    summary = {
        "analysis": {
            "total_frames": 1,
            "final_count": snapshot.count,
            "density_level": snapshot.level.value,
            "density_persons_per_sqm": round(snapshot.density, 4),
            "zones": {f"{r},{c}": v for (r, c), v in snapshot.zones.items()},
        },
        "stats": stats,
    }
    
    with open(output / "crowd_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    log.info(f"Done! Outputs: {output}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
