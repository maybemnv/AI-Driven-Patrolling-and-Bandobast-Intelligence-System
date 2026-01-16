"""ONNX-based object detector for faster inference."""

import time
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np
import onnxruntime as ort


class ONNXDetector:
    """YOLOv8 detector using ONNX Runtime."""
    
    COCO_CLASSES = {
        0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 4: "airplane",
        5: "bus", 6: "train", 7: "truck", 8: "boat", 24: "backpack",
        25: "umbrella", 26: "handbag", 28: "suitcase",
    }
    
    def __init__(
        self,
        model_path: str = "yolov8n.onnx",
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45,
    ):
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        self.session = ort.InferenceSession(model_path, providers=providers)
        
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        self.input_size = (self.input_shape[2], self.input_shape[3])
    
    def preprocess(self, image: np.ndarray) -> Tuple[np.ndarray, float, float]:
        h, w = image.shape[:2]
        target_h, target_w = self.input_size
        
        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        resized = cv2.resize(image, (new_w, new_h))
        
        canvas = np.full((target_h, target_w, 3), 114, dtype=np.uint8)
        pad_x, pad_y = (target_w - new_w) // 2, (target_h - new_h) // 2
        canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized
        
        blob = canvas.astype(np.float32) / 255.0
        blob = blob.transpose(2, 0, 1)[np.newaxis, ...]
        
        return blob, scale, (pad_x, pad_y)
    
    def postprocess(
        self,
        outputs: np.ndarray,
        scale: float,
        pad: Tuple[int, int],
        orig_shape: Tuple[int, int],
    ) -> List[dict]:
        predictions = outputs[0].T
        
        boxes = predictions[:, :4]
        scores = predictions[:, 4:]
        
        class_ids = np.argmax(scores, axis=1)
        max_scores = np.max(scores, axis=1)
        
        mask = max_scores > self.conf_threshold
        boxes = boxes[mask]
        class_ids = class_ids[mask]
        max_scores = max_scores[mask]
        
        if len(boxes) == 0:
            return []
        
        pad_x, pad_y = pad
        boxes[:, 0] = (boxes[:, 0] - pad_x) / scale
        boxes[:, 1] = (boxes[:, 1] - pad_y) / scale
        boxes[:, 2] = boxes[:, 2] / scale
        boxes[:, 3] = boxes[:, 3] / scale
        
        x1 = boxes[:, 0] - boxes[:, 2] / 2
        y1 = boxes[:, 1] - boxes[:, 3] / 2
        x2 = boxes[:, 0] + boxes[:, 2] / 2
        y2 = boxes[:, 1] + boxes[:, 3] / 2
        
        indices = cv2.dnn.NMSBoxes(
            np.column_stack([x1, y1, x2 - x1, y2 - y1]).tolist(),
            max_scores.tolist(),
            self.conf_threshold,
            self.iou_threshold,
        )
        
        detections = []
        for i in indices:
            idx = i[0] if isinstance(i, (list, np.ndarray)) else i
            detections.append({
                "class_id": int(class_ids[idx]),
                "class_name": self.COCO_CLASSES.get(int(class_ids[idx]), f"class_{class_ids[idx]}"),
                "confidence": float(max_scores[idx]),
                "bbox": {
                    "x1": max(0, int(x1[idx])),
                    "y1": max(0, int(y1[idx])),
                    "x2": min(orig_shape[1], int(x2[idx])),
                    "y2": min(orig_shape[0], int(y2[idx])),
                },
            })
        
        return detections
    
    def detect(self, image: np.ndarray) -> List[dict]:
        blob, scale, pad = self.preprocess(image)
        outputs = self.session.run(None, {self.input_name: blob})
        return self.postprocess(outputs[0], scale, pad, image.shape[:2])
    
    def benchmark(self, image: np.ndarray, runs: int = 100) -> dict:
        blob, _, _ = self.preprocess(image)
        
        for _ in range(10):
            self.session.run(None, {self.input_name: blob})
        
        times = []
        for _ in range(runs):
            start = time.perf_counter()
            self.session.run(None, {self.input_name: blob})
            times.append(time.perf_counter() - start)
        
        return {
            "avg_ms": np.mean(times) * 1000,
            "min_ms": np.min(times) * 1000,
            "max_ms": np.max(times) * 1000,
            "fps": 1 / np.mean(times),
        }
