"""Source package for object detection pipeline."""

from src.detector import ModelLoader, ObjectDetector, Detection, FrameProcessor, FrameData
from src.tracking import ObjectTracker, TrackedObject
from src.events import Event, EventType, EventBuilder, save_events
from src.crowd import CrowdAnalyzer, CrowdSnapshot, DensityLevel, SurgeSeverity, SurgeEvent
from src.crowd.events import CrowdEventBuilder

__all__ = [
    "ModelLoader", "ObjectDetector", "Detection", "FrameProcessor", "FrameData",
    "ObjectTracker", "TrackedObject",
    "Event", "EventType", "EventBuilder", "save_events",
    "CrowdAnalyzer", "CrowdSnapshot", "DensityLevel", "SurgeSeverity", "SurgeEvent",
    "CrowdEventBuilder",
]
