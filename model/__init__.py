"""Model package for object detection pipeline."""
from model.detector import ModelLoader, ObjectDetector, Detection, FrameProcessor, FrameData
from model.tracking import ObjectTracker, TrackedObject
from model.events import Event, EventType, EventBuilder, save_events

__all__ = [
    "ModelLoader", "ObjectDetector", "Detection", "FrameProcessor", "FrameData",
    "ObjectTracker", "TrackedObject",
    "Event", "EventType", "EventBuilder", "save_events",
]
