"""YOLOv8 Model Loader - Singleton pattern for efficient model management."""

import threading
from pathlib import Path
from typing import Optional

import torch
from ultralytics import YOLO


class ModelLoader:
    """Thread-safe singleton for YOLOv8 model loading."""
    
    _instance: Optional["ModelLoader"] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> "ModelLoader":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._model = None
                    cls._instance._config = {}
                    cls._instance._device = "cpu"
        return cls._instance
    
    def initialize(
        self,
        model_path: str,
        device: str = "auto",
        confidence: float = 0.5,
        iou: float = 0.45,
        imgsz: int = 640,
    ) -> None:
        path = Path(model_path)
        
        if not path.exists():
            self._model = YOLO(path.name)
        else:
            self._model = YOLO(str(path))
        
        self._device = self._detect_device(device)
        self._config = {"confidence": confidence, "iou": iou, "imgsz": imgsz}
    
    def _detect_device(self, device: str) -> str:
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            return "cpu"
        return device
    
    @property
    def model(self) -> YOLO:
        if self._model is None:
            raise RuntimeError("Model not initialized. Call initialize() first.")
        return self._model
    
    @property
    def config(self) -> dict:
        return self._config.copy()
    
    @property
    def device(self) -> str:
        return self._device
    
    @property
    def is_ready(self) -> bool:
        return self._model is not None
    
    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            if cls._instance:
                cls._instance._model = None
                cls._instance._config = {}
            cls._instance = None
