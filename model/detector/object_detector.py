"""Object detection with YOLOv8."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

import cv2
import numpy as np

from model.detector.model_loader import ModelLoader


@dataclass
class Detection:
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    bbox_xyxy: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]
    timestamp: float = 0.0
    frame_number: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 4),
            "bbox": {"x": self.bbox[0], "y": self.bbox[1], "w": self.bbox[2], "h": self.bbox[3]},
            "center": {"x": self.center[0], "y": self.center[1]},
            "timestamp": self.timestamp,
            "frame_number": self.frame_number,
        }


COCO_CLASSES = {
    0: "person", 2: "car", 5: "bus", 7: "truck",
    24: "backpack", 26: "handbag", 28: "suitcase",
}


class ObjectDetector:
    """YOLO-based object detector with visualization."""
    
    COLORS = {
        "person": (0, 255, 0),
        "vehicle": (255, 165, 0),
        "bag": (0, 0, 255),
        "default": (255, 255, 0),
    }
    
    def __init__(self, target_classes: Optional[Set[int]] = None):
        self._loader = ModelLoader()
        self._targets = target_classes or {0, 2, 5, 7, 24, 26, 28}
    
    def initialize(
        self,
        model_path: str,
        device: str = "auto",
        confidence: float = 0.5,
        iou: float = 0.45,
        imgsz: int = 640,
    ) -> None:
        self._loader.initialize(model_path, device, confidence, iou, imgsz)
    
    def detect(
        self,
        frame: np.ndarray,
        timestamp: float = 0.0,
        frame_number: int = 0,
        filter_classes: bool = True,
    ) -> List[Detection]:
        model = self._loader.model
        cfg = self._loader.config
        
        results = model(
            frame,
            conf=cfg["confidence"],
            iou=cfg["iou"],
            imgsz=cfg["imgsz"],
            verbose=False,
        )
        
        detections = []
        for result in results:
            if result.boxes is None:
                continue
            
            for i, box in enumerate(result.boxes):
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                
                if filter_classes and cls_id not in self._targets:
                    continue
                
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                w, h = x2 - x1, y2 - y1
                cx, cy = x1 + w // 2, y1 + h // 2
                
                detections.append(Detection(
                    class_id=cls_id,
                    class_name=COCO_CLASSES.get(cls_id, f"class_{cls_id}"),
                    confidence=conf,
                    bbox=(x1, y1, w, h),
                    bbox_xyxy=(x1, y1, x2, y2),
                    center=(cx, cy),
                    timestamp=timestamp,
                    frame_number=frame_number,
                ))
        
        return detections
    
    def visualize(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        thickness: int = 2,
        font_scale: float = 0.6,
    ) -> np.ndarray:
        img = frame.copy()
        
        for det in detections:
            color = self._get_color(det.class_id)
            x1, y1, x2, y2 = det.bbox_xyxy
            
            cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
            
            label = f"{det.class_name} {det.confidence:.2f}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            cv2.rectangle(img, (x1, y1 - th - 10), (x1 + tw + 4, y1), color, -1)
            cv2.putText(img, label, (x1 + 2, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
        
        return img
    
    def _get_color(self, cls_id: int) -> Tuple[int, int, int]:
        if cls_id == 0:
            return self.COLORS["person"]
        if cls_id in {2, 5, 7}:
            return self.COLORS["vehicle"]
        if cls_id in {24, 26, 28}:
            return self.COLORS["bag"]
        return self.COLORS["default"]
    
    def save_annotated(self, frame: np.ndarray, detections: List[Detection], path: str) -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(path, self.visualize(frame, detections))
        return path
