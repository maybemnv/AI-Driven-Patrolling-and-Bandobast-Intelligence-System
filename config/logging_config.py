"""Logging configuration."""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(
    level: str = "INFO",
    log_dir: str = "logs",
    log_to_file: bool = True,
) -> logging.Logger:
    """Configure application-wide logging."""
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Root logger
    root = logging.getLogger()
    root.setLevel(log_level)
    
    # Clear existing handlers
    root.handlers.clear()
    
    # Format
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    console.setFormatter(fmt)
    root.addHandler(console)
    
    # File handler
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        filename = log_path / f"app_{datetime.now():%Y%m%d}.log"
        file_handler = logging.FileHandler(filename, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)
    
    # Reduce noise from libraries
    logging.getLogger("ultralytics").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return root


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)
