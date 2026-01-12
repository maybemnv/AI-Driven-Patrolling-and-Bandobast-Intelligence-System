"""Unit tests for detection pipeline."""

import uuid
import numpy as np
import pytest


class TestModelLoader:
    def test_singleton(self):
        from model.detector.model_loader import ModelLoader
        ModelLoader.reset()
        assert ModelLoader() is ModelLoader()
        ModelLoader.reset()
    
    def test_not_initialized_error(self):
        from model.detector.model_loader import ModelLoader
        ModelLoader.reset()
        with pytest.raises(RuntimeError):
            ModelLoader().model
        ModelLoader.reset()


class TestFrameProcessor:
    def test_unsupported_file(self, tmp_path):
        from model.detector.frame_processor import FrameProcessor
        fake = tmp_path / "test.xyz"
        fake.write_text("fake")
        with pytest.raises(ValueError, match="Unsupported"):
            list(FrameProcessor().process(str(fake)))
    
    def test_file_not_found(self):
        from model.detector.frame_processor import FrameProcessor
        with pytest.raises(FileNotFoundError):
            list(FrameProcessor().process("nonexistent.jpg"))
    
    def test_preprocess_shape(self):
        from model.detector.frame_processor import FrameProcessor
        proc = FrameProcessor(imgsz=640)
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        out = proc.preprocess(frame)
        assert out.shape == (640, 640, 3)
        assert out.dtype == np.float32


class TestDetection:
    def test_to_dict(self):
        from model.detector.object_detector import Detection
        det = Detection(0, "person", 0.95, (100, 100, 50, 100), (100, 100, 150, 200), (125, 150))
        d = det.to_dict()
        assert d["class_name"] == "person"
        assert d["confidence"] == 0.95


class TestObjectTracker:
    def test_iou_same_box(self):
        from model.tracking.tracker import ObjectTracker
        tracker = ObjectTracker()
        assert tracker._iou((0, 0, 100, 100), (0, 0, 100, 100)) == 1.0
    
    def test_iou_no_overlap(self):
        from model.tracking.tracker import ObjectTracker
        tracker = ObjectTracker()
        assert tracker._iou((0, 0, 100, 100), (200, 200, 100, 100)) == 0.0


class TestEvent:
    def test_event_creation(self):
        from model.events.event import Event, EventType
        event = Event(
            event_id=str(uuid.uuid4()),
            timestamp="2024-01-01T00:00:00Z",
            camera_id="cam_001",
            event_type=EventType.OBJECT_DETECTED.value,
            confidence=0.95,
            data={"test": 1},
        )
        assert event.event_type == "object_detected"
    
    def test_invalid_confidence(self):
        from model.events.event import Event, EventType
        with pytest.raises(ValueError):
            Event(str(uuid.uuid4()), "", "", EventType.OBJECT_DETECTED.value, 1.5, {})
    
    def test_builder(self):
        from model.events.event import EventBuilder
        builder = EventBuilder("test_cam")
        event = builder.object_detected("person", 0, 0.9, {"x": 0, "y": 0, "w": 10, "h": 10})
        assert event.camera_id == "test_cam"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
