# AI-Driven Patrolling and Bandobast Intelligence System

Real-time object detection and static object tracking system for surveillance and security applications.

## Features

- **YOLOv8 Detection**: Person, vehicle, and bag detection
- **Static Object Tracking**: IoU-based tracking with dwell time detection
- **Event System**: Structured events for detections, static objects, crowds

## Quick Start

```bash
# Install dependencies
uv sync

# Run demo
uv run python run_detection_demo.py
```

## Project Structure

```
model/
├── detector/
│   ├── model_loader.py     # Singleton YOLO loader
│   ├── frame_processor.py  # Video/image extraction
│   └── object_detector.py  # Detection wrapper
├── tracking/
│   └── tracker.py          # Static object tracking
└── events/
    └── event.py            # Event schema
```

## Configuration

Edit `config.yaml`:

```yaml
detection:
  model:
    path: "yolov8n.pt"
    device: "auto"
  inference:
    confidence_threshold: 0.5
    iou_threshold: 0.45
    image_size: 640
```

## Testing

```bash
uv run python -m pytest tests/ -v
```

## License

MIT
