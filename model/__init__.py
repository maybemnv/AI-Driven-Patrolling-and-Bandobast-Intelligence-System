"""Model package for object detection pipeline."""
from model.detector import ModelLoader, ObjectDetector, Detection, FrameProcessor, FrameData
from model.tracking import ObjectTracker, TrackedObject
from model.events import Event, EventType, EventBuilder, save_events
from model.crowd import CrowdAnalyzer, CrowdSnapshot, DensityLevel, SurgeSeverity, SurgeEvent
from model.crowd.events import CrowdEventBuilder

__all__ = [
    "ModelLoader", "ObjectDetector", "Detection", "FrameProcessor", "FrameData",
    "ObjectTracker", "TrackedObject",
    "Event", "EventType", "EventBuilder", "save_events",
    "CrowdAnalyzer", "CrowdSnapshot", "DensityLevel", "SurgeSeverity", "SurgeEvent",
    "CrowdEventBuilder",
]
