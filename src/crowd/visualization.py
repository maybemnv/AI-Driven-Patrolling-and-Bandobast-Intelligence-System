"""Crowd visualization utilities."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2

from src.crowd.analyzer import CrowdSnapshot, DensityLevel


def create_density_heatmap(
    zones: Dict[Tuple[int, int], int],
    grid_rows: int,
    grid_cols: int,
    output_size: Tuple[int, int] = (640, 480),
) -> np.ndarray:
    """Create heatmap image from zone counts."""
    grid = np.zeros((grid_rows, grid_cols), dtype=np.float32)
    
    for (r, c), count in zones.items():
        grid[r, c] = count
    
    # Normalize to 0-255
    if grid.max() > 0:
        grid = (grid / grid.max() * 255).astype(np.uint8)
    else:
        grid = grid.astype(np.uint8)
    
    # Resize to output size
    heatmap = cv2.resize(grid, output_size, interpolation=cv2.INTER_LINEAR)
    
    # Apply colormap
    heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    
    return heatmap_color


def overlay_heatmap(
    frame: np.ndarray,
    zones: Dict[Tuple[int, int], int],
    grid_rows: int,
    grid_cols: int,
    alpha: float = 0.4,
) -> np.ndarray:
    """Overlay density heatmap on frame."""
    h, w = frame.shape[:2]
    heatmap = create_density_heatmap(zones, grid_rows, grid_cols, (w, h))
    return cv2.addWeighted(frame, 1 - alpha, heatmap, alpha, 0)


def draw_zone_grid(
    frame: np.ndarray,
    zones: Dict[Tuple[int, int], int],
    grid_rows: int,
    grid_cols: int,
    thickness: int = 1,
) -> np.ndarray:
    """Draw zone grid with counts on frame."""
    h, w = frame.shape[:2]
    zone_h, zone_w = h // grid_rows, w // grid_cols
    result = frame.copy()
    
    # Draw grid lines
    for i in range(1, grid_rows):
        cv2.line(result, (0, i * zone_h), (w, i * zone_h), (255, 255, 255), thickness)
    for j in range(1, grid_cols):
        cv2.line(result, (j * zone_w, 0), (j * zone_w, h), (255, 255, 255), thickness)
    
    # Draw counts
    for (r, c), count in zones.items():
        if count > 0:
            cx = c * zone_w + zone_w // 2
            cy = r * zone_h + zone_h // 2
            cv2.putText(
                result, str(count), (cx - 10, cy + 10),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2
            )
    
    return result


def create_timeseries_chart(
    history: List[CrowdSnapshot],
    output_path: str,
    width: int = 800,
    height: int = 400,
) -> str:
    """Create simple line chart of crowd counts over time."""
    if not history:
        return ""
    
    # Create blank image
    chart = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    counts = [s.count for s in history]
    times = [s.timestamp for s in history]
    
    if len(counts) < 2:
        return ""
    
    # Normalize
    max_count = max(counts) or 1
    min_time, max_time = min(times), max(times)
    time_range = max_time - min_time or 1
    
    margin = 50
    plot_w = width - 2 * margin
    plot_h = height - 2 * margin
    
    # Draw axes
    cv2.line(chart, (margin, margin), (margin, height - margin), (0, 0, 0), 2)
    cv2.line(chart, (margin, height - margin), (width - margin, height - margin), (0, 0, 0), 2)
    
    # Plot points
    points = []
    for t, c in zip(times, counts):
        x = int(margin + ((t - min_time) / time_range) * plot_w)
        y = int(height - margin - (c / max_count) * plot_h)
        points.append((x, y))
    
    # Draw line
    for i in range(len(points) - 1):
        cv2.line(chart, points[i], points[i + 1], (255, 0, 0), 2)
    
    # Labels
    cv2.putText(chart, "Count", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.putText(chart, "Time", (width - 60, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.putText(chart, str(max_count), (10, margin + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.putText(chart, "0", (10, height - margin), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, chart)
    return output_path


def save_heatmap(
    zones: Dict[Tuple[int, int], int],
    grid_rows: int,
    grid_cols: int,
    output_path: str,
    size: Tuple[int, int] = (640, 480),
) -> str:
    """Save density heatmap to file."""
    heatmap = create_density_heatmap(zones, grid_rows, grid_cols, size)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, heatmap)
    return output_path
