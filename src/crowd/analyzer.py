"""Crowd analysis with density classification and surge detection."""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np

from src.detector.object_detector import Detection


class DensityLevel(Enum):
    LOW = "low"           # < 0.5 persons/sqm
    MEDIUM = "medium"     # 0.5-2 persons/sqm  
    HIGH = "high"         # 2-4 persons/sqm
    CRITICAL = "critical" # > 4 persons/sqm


class SurgeSeverity(Enum):
    NONE = "none"
    MINOR = "minor"       # 30-50% increase
    MODERATE = "moderate" # 50-100% increase
    MAJOR = "major"       # >100% increase


@dataclass
class CrowdSnapshot:
    timestamp: float
    count: int
    density: float
    level: DensityLevel
    zones: Dict[Tuple[int, int], int] = field(default_factory=dict)


@dataclass 
class SurgeEvent:
    severity: SurgeSeverity
    prev_density: float
    curr_density: float
    rate_of_change: float  # persons/min
    trend: str  # "increasing", "decreasing", "stable"


class CrowdAnalyzer:
    """Analyze crowd density, detect surges, and track temporal patterns."""
    
    DENSITY_THRESHOLDS = {
        DensityLevel.LOW: 0.5,
        DensityLevel.MEDIUM: 2.0,
        DensityLevel.HIGH: 4.0,
    }
    
    def __init__(
        self,
        coverage_area: float = 100.0,  # sqm
        grid_cols: int = 4,
        grid_rows: int = 3,
        buffer_size: int = 300,  # 5 min at 1 fps
        surge_window: float = 120.0,  # 2 min
        surge_threshold: float = 0.5,  # 50% increase
        min_crowd_for_surge: int = 5,
    ):
        self.coverage_area = coverage_area
        self.grid_cols = grid_cols
        self.grid_rows = grid_rows
        self.surge_window = surge_window
        self.surge_threshold = surge_threshold
        self.min_crowd_for_surge = min_crowd_for_surge
        
        self._history: deque = deque(maxlen=buffer_size)
        self._last_surge_time: float = 0
        self._surge_debounce: float = 60.0  # 1 min between alerts
    
    def analyze(
        self,
        detections: List[Detection],
        frame_shape: Tuple[int, int],
        timestamp: float,
    ) -> CrowdSnapshot:
        """Analyze crowd from person detections."""
        persons = [d for d in detections if d.class_id == 0]
        count = len(persons)
        density = count / self.coverage_area
        level = self._classify_density(density)
        zones = self._count_zones(persons, frame_shape)
        
        snapshot = CrowdSnapshot(
            timestamp=timestamp,
            count=count,
            density=density,
            level=level,
            zones=zones,
        )
        self._history.append(snapshot)
        return snapshot
    
    def _classify_density(self, density: float) -> DensityLevel:
        if density >= self.DENSITY_THRESHOLDS[DensityLevel.HIGH]:
            return DensityLevel.CRITICAL
        if density >= self.DENSITY_THRESHOLDS[DensityLevel.MEDIUM]:
            return DensityLevel.HIGH
        if density >= self.DENSITY_THRESHOLDS[DensityLevel.LOW]:
            return DensityLevel.MEDIUM
        return DensityLevel.LOW
    
    def _count_zones(
        self,
        persons: List[Detection],
        frame_shape: Tuple[int, int],
    ) -> Dict[Tuple[int, int], int]:
        h, w = frame_shape[:2]
        zone_w, zone_h = w // self.grid_cols, h // self.grid_rows
        zones: Dict[Tuple[int, int], int] = {}
        
        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                zones[(i, j)] = 0
        
        for p in persons:
            cx, cy = p.center
            col = min(cx // zone_w, self.grid_cols - 1)
            row = min(cy // zone_h, self.grid_rows - 1)
            zones[(row, col)] += 1
        
        return zones
    
    def detect_surge(self, timestamp: float) -> Optional[SurgeEvent]:
        """Detect crowd surge based on rate of change."""
        if len(self._history) < 2:
            return None
        
        curr = self._history[-1]
        if curr.count < self.min_crowd_for_surge:
            return None
        
        # Get baseline from surge_window ago
        baseline_ts = timestamp - self.surge_window
        baseline = None
        for snap in self._history:
            if snap.timestamp >= baseline_ts:
                baseline = snap
                break
        
        if baseline is None:
            return None
        
        # Calculate rate of change
        time_diff = max(curr.timestamp - baseline.timestamp, 1.0)
        count_diff = curr.count - baseline.count
        rate = (count_diff / time_diff) * 60  # per minute
        
        # Check for surge
        if baseline.count > 0:
            pct_change = count_diff / baseline.count
        else:
            pct_change = 1.0 if curr.count > 0 else 0.0
        
        # Determine trend
        if pct_change > 0.1:
            trend = "increasing"
        elif pct_change < -0.1:
            trend = "decreasing"
        else:
            trend = "stable"
        
        # Determine severity
        if pct_change >= 1.0:
            severity = SurgeSeverity.MAJOR
        elif pct_change >= 0.5:
            severity = SurgeSeverity.MODERATE
        elif pct_change >= 0.3:
            severity = SurgeSeverity.MINOR
        else:
            return None
        
        # Debounce
        if timestamp - self._last_surge_time < self._surge_debounce:
            return None
        
        self._last_surge_time = timestamp
        return SurgeEvent(
            severity=severity,
            prev_density=baseline.density,
            curr_density=curr.density,
            rate_of_change=rate,
            trend=trend,
        )
    
    def get_stats(self, window: float = 60.0) -> Dict:
        """Get statistics over time window (seconds)."""
        if not self._history:
            return {"count": 0, "mean": 0, "std": 0, "peak": 0, "trend": "stable"}
        
        now = self._history[-1].timestamp
        window_start = now - window
        
        counts = [s.count for s in self._history if s.timestamp >= window_start]
        if not counts:
            counts = [self._history[-1].count]
        
        arr = np.array(counts)
        mean_count = float(np.mean(arr))
        
        # Trend detection
        if len(counts) >= 3:
            first_half = np.mean(arr[:len(arr)//2])
            second_half = np.mean(arr[len(arr)//2:])
            if second_half > first_half * 1.2:
                trend = "increasing"
            elif second_half < first_half * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "count": int(self._history[-1].count),
            "mean": round(mean_count, 2),
            "std": round(float(np.std(arr)), 2),
            "peak": int(np.max(arr)),
            "trend": trend,
        }
    
    def get_rolling_avg(self, window: float = 60.0) -> float:
        """Get rolling average count over window (seconds)."""
        stats = self.get_stats(window)
        return stats["mean"]
    
    def get_smoothed_count(self, window_size: int = 5) -> float:
        """Get exponentially smoothed count to reduce fluctuations."""
        if not self._history:
            return 0.0
        
        recent = list(self._history)[-window_size:]
        if len(recent) < 2:
            return float(recent[-1].count)
        
        # Exponential moving average
        alpha = 2 / (len(recent) + 1)
        ema = recent[0].count
        for snap in recent[1:]:
            ema = alpha * snap.count + (1 - alpha) * ema
        return round(ema, 2)
    
    def get_history(self) -> List[CrowdSnapshot]:
        """Get history for visualization."""
        return list(self._history)
    
    def reset(self) -> None:
        self._history.clear()
        self._last_surge_time = 0
