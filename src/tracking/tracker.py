"""Object tracking for static object detection."""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
import uuid

from src.detector.object_detector import Detection


@dataclass
class TrackedObject:
    object_id: str
    class_id: int
    class_name: str
    first_seen: float
    last_seen: float
    bbox: Tuple[int, int, int, int]
    center: Tuple[int, int]
    initial_center: Tuple[int, int]
    is_static: bool = False
    dwell_time: float = 0.0
    confidence: float = 0.0
    disappeared: int = 0
    _conf_sum: float = field(default=0.0, repr=False)
    _count: int = field(default=0, repr=False)
    
    def update(self, det: Detection, move_thresh: float = 20.0) -> None:
        self.last_seen = det.timestamp
        self.bbox = det.bbox
        self.center = det.center
        self.disappeared = 0
        
        self._conf_sum += det.confidence
        self._count += 1
        self.confidence = self._conf_sum / self._count
        
        dx = abs(self.center[0] - self.initial_center[0])
        dy = abs(self.center[1] - self.initial_center[1])
        
        if (dx**2 + dy**2)**0.5 <= move_thresh:
            self.dwell_time = self.last_seen - self.first_seen
        else:
            self.initial_center = self.center
            self.first_seen = det.timestamp
            self.dwell_time = 0.0
            self.is_static = False
    
    def to_dict(self) -> Dict:
        return {
            "object_id": self.object_id,
            "class_name": self.class_name,
            "is_static": self.is_static,
            "dwell_time": round(self.dwell_time, 2),
            "bbox": {"x": self.bbox[0], "y": self.bbox[1], "w": self.bbox[2], "h": self.bbox[3]},
            "confidence": round(self.confidence, 4),
        }


class ObjectTracker:
    """IoU-based tracker for detecting stationary objects."""
    
    def __init__(
        self,
        iou_thresh: float = 0.5,
        move_thresh: float = 20.0,
        static_thresh: float = 300.0,
        max_disappeared: int = 50,
    ):
        self.iou_thresh = iou_thresh
        self.move_thresh = move_thresh
        self.static_thresh = static_thresh
        self.max_disappeared = max_disappeared
        self._objects: Dict[str, TrackedObject] = {}
    
    def update(self, detections: List[Detection]) -> List[TrackedObject]:
        for obj in self._objects.values():
            obj.disappeared += 1
        
        matched: Set[str] = set()
        unmatched: List[Detection] = []
        
        for det in detections:
            best_id, best_iou = None, self.iou_thresh
            
            for oid, obj in self._objects.items():
                if oid in matched or obj.class_id != det.class_id:
                    continue
                iou = self._iou(obj.bbox, det.bbox)
                if iou > best_iou:
                    best_iou, best_id = iou, oid
            
            if best_id:
                self._objects[best_id].update(det, self.move_thresh)
                matched.add(best_id)
            else:
                unmatched.append(det)
        
        for det in unmatched:
            self._register(det)
        
        self._cleanup()
        
        newly_static = []
        for obj in self._objects.values():
            if obj.dwell_time >= self.static_thresh and not obj.is_static:
                obj.is_static = True
                newly_static.append(obj)
        
        return newly_static
    
    def _register(self, det: Detection) -> None:
        oid = str(uuid.uuid4())[:8]
        self._objects[oid] = TrackedObject(
            object_id=oid,
            class_id=det.class_id,
            class_name=det.class_name,
            first_seen=det.timestamp,
            last_seen=det.timestamp,
            bbox=det.bbox,
            center=det.center,
            initial_center=det.center,
            confidence=det.confidence,
            _conf_sum=det.confidence,
            _count=1,
        )
    
    def _cleanup(self) -> None:
        expired = [oid for oid, obj in self._objects.items() if obj.disappeared > self.max_disappeared]
        for oid in expired:
            del self._objects[oid]
    
    def _iou(self, b1: Tuple[int, int, int, int], b2: Tuple[int, int, int, int]) -> float:
        x1_1, y1_1, x2_1, y2_1 = b1[0], b1[1], b1[0] + b1[2], b1[1] + b1[3]
        x1_2, y1_2, x2_2, y2_2 = b2[0], b2[1], b2[0] + b2[2], b2[1] + b2[3]
        
        xi1, yi1 = max(x1_1, x1_2), max(y1_1, y1_2)
        xi2, yi2 = min(x2_1, x2_2), min(y2_1, y2_2)
        
        if xi2 < xi1 or yi2 < yi1:
            return 0.0
        
        inter = (xi2 - xi1) * (yi2 - yi1)
        union = b1[2] * b1[3] + b2[2] * b2[3] - inter
        return inter / union if union > 0 else 0.0
    
    def get_all(self) -> List[TrackedObject]:
        return list(self._objects.values())
    
    def get_static(self) -> List[TrackedObject]:
        return [o for o in self._objects.values() if o.is_static]
    
    def reset(self) -> None:
        self._objects.clear()
