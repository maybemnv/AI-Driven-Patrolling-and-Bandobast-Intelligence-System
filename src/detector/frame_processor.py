"""Frame extraction from video and image files."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterator, Optional, Callable, List

import cv2
import numpy as np


class SamplingMode(Enum):
    TIME = "time"
    FRAME = "frame"


@dataclass
class FrameData:
    frame: np.ndarray
    frame_number: int
    timestamp: float
    source_path: str


class FrameProcessor:
    """Extract and preprocess frames from video/image files."""
    
    VIDEO_EXT = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}
    IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    
    def __init__(
        self,
        imgsz: int = 640,
        mode: SamplingMode = SamplingMode.TIME,
        time_interval: float = 1.0,
        frame_interval: int = 30,
    ):
        self.imgsz = imgsz
        self.mode = mode
        self.time_interval = time_interval
        self.frame_interval = frame_interval
    
    def process(
        self,
        path: str,
        progress: Optional[Callable[[int, int], None]] = None,
    ) -> Iterator[FrameData]:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        ext = p.suffix.lower()
        if ext in self.VIDEO_EXT:
            yield from self._process_video(path, progress)
        elif ext in self.IMAGE_EXT:
            yield from self._process_image(path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _process_video(
        self,
        path: str,
        progress: Optional[Callable[[int, int], None]] = None,
    ) -> Iterator[FrameData]:
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {path}")
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            skip = int(fps * self.time_interval) if self.mode == SamplingMode.TIME else self.frame_interval
            skip = max(1, skip)
            
            frame_num = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_num % skip == 0:
                    yield FrameData(frame, frame_num, frame_num / fps, path)
                    if progress:
                        progress(frame_num, total)
                
                frame_num += 1
        finally:
            cap.release()
    
    def _process_image(self, path: str) -> Iterator[FrameData]:
        frame = cv2.imread(path)
        if frame is None:
            raise ValueError(f"Cannot read image: {path}")
        yield FrameData(frame, 0, 0.0, path)
    
    def preprocess(self, frame: np.ndarray, normalize: bool = True) -> np.ndarray:
        resized = self._letterbox(frame, self.imgsz)
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        return rgb.astype(np.float32) / 255.0 if normalize else rgb
    
    def _letterbox(self, img: np.ndarray, size: int) -> np.ndarray:
        h, w = img.shape[:2]
        scale = min(size / h, size / w)
        new_h, new_w = int(h * scale), int(w * scale)
        
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        canvas = np.full((size, size, 3), 114, dtype=np.uint8)
        top, left = (size - new_h) // 2, (size - new_w) // 2
        canvas[top:top + new_h, left:left + new_w] = resized
        
        return canvas
