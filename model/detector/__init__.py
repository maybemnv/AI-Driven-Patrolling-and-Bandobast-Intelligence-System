"""Detector subpackage."""
from model.detector.model_loader import ModelLoader
from model.detector.object_detector import ObjectDetector, Detection
from model.detector.frame_processor import FrameProcessor, FrameData, SamplingMode

__all__ = ["ModelLoader", "ObjectDetector", "Detection", "FrameProcessor", "FrameData", "SamplingMode"]
