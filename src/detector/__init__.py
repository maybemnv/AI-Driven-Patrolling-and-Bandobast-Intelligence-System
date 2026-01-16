"""Detector subpackage."""
from src.detector.model_loader import ModelLoader
from src.detector.object_detector import ObjectDetector, Detection
from src.detector.frame_processor import FrameProcessor, FrameData, SamplingMode

__all__ = ["ModelLoader", "ObjectDetector", "Detection", "FrameProcessor", "FrameData", "SamplingMode"]
