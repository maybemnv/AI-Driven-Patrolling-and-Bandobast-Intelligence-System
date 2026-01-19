"""Real-time stream processor for video analysis."""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Callable
from dataclasses import dataclass, field

from src.video.source import VideoSource, Frame


logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Result from frame analysis."""
    frame_number: int
    timestamp: datetime
    event_type: str
    confidence: float
    details: dict = field(default_factory=dict)


class StreamProcessor:
    """Process video stream and generate events."""
    
    def __init__(
        self,
        source: VideoSource,
        detector: Optional[Callable] = None,
        frame_skip: int = 5,
        min_confidence: float = 0.5,
    ):
        self.source = source
        self.detector = detector
        self.frame_skip = frame_skip
        self.min_confidence = min_confidence
        self.running = False
        self.callbacks: list[Callable] = []
    
    def on_detection(self, callback: Callable[[DetectionResult], None]):
        """Register callback for detections."""
        self.callbacks.append(callback)
    
    def _notify(self, result: DetectionResult):
        """Notify all registered callbacks."""
        for cb in self.callbacks:
            try:
                cb(result)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def process_frame(self, frame: Frame) -> list[DetectionResult]:
        """Process single frame and return detections."""
        if not self.detector:
            return []
        
        try:
            raw_detections = self.detector(frame.image)
            
            results = []
            for det in raw_detections:
                if det.get("confidence", 0) < self.min_confidence:
                    continue
                
                result = DetectionResult(
                    frame_number=frame.frame_number,
                    timestamp=datetime.now(),
                    event_type=det.get("type", "unknown"),
                    confidence=det.get("confidence", 0),
                    details=det,
                )
                results.append(result)
                self._notify(result)
            
            return results
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def run(self, max_frames: Optional[int] = None):
        """Run synchronous processing loop."""
        self.running = True
        processed = 0
        
        with self.source:
            for frame in self.source.frames(skip=self.frame_skip):
                if not self.running:
                    break
                
                self.process_frame(frame)
                processed += 1
                
                if max_frames and processed >= max_frames:
                    break
        
        self.running = False
        return processed
    
    def stop(self):
        """Stop processing."""
        self.running = False


async def run_stream_async(
    source: VideoSource,
    detector: Callable,
    on_event: Callable[[DetectionResult], None],
    frame_skip: int = 5,
):
    """Run stream processing asynchronously."""
    processor = StreamProcessor(source, detector, frame_skip)
    processor.on_detection(on_event)
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, processor.run)
