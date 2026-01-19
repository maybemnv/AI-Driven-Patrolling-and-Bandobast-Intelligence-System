"""Video source handler for webcam and video files."""

import cv2
from pathlib import Path
from typing import Optional, Iterator
from dataclasses import dataclass


@dataclass
class Frame:
    """Video frame with metadata."""
    image: any
    timestamp: float
    frame_number: int
    source: str


class VideoSource:
    """Unified video source for webcam and video files."""
    
    def __init__(self, source: str | int = 0):
        """
        Initialize video source.
        
        Args:
            source: 0 for webcam, or path to video file
        """
        self.source = source
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame_count = 0
        
    def open(self) -> bool:
        """Open video source."""
        self.cap = cv2.VideoCapture(self.source)
        return self.cap.isOpened()
    
    def close(self):
        """Release video source."""
        if self.cap:
            self.cap.release()
            self.cap = None
    
    @property
    def fps(self) -> float:
        if self.cap:
            return self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        return 30.0
    
    @property
    def width(self) -> int:
        if self.cap:
            return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        return 0
    
    @property
    def height(self) -> int:
        if self.cap:
            return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return 0
    
    def read(self) -> Optional[Frame]:
        """Read single frame."""
        if not self.cap:
            return None
        
        ret, image = self.cap.read()
        if not ret:
            return None
        
        self.frame_count += 1
        timestamp = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        
        return Frame(
            image=image,
            timestamp=timestamp,
            frame_number=self.frame_count,
            source=str(self.source)
        )
    
    def frames(self, skip: int = 1) -> Iterator[Frame]:
        """Iterate over frames with optional skip."""
        while True:
            frame = self.read()
            if frame is None:
                break
            
            if frame.frame_number % skip == 0:
                yield frame
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, *args):
        self.close()


def get_webcam(camera_id: int = 0) -> VideoSource:
    """Get webcam source."""
    return VideoSource(camera_id)


def get_video_file(path: str | Path) -> VideoSource:
    """Get video file source."""
    return VideoSource(str(path))
