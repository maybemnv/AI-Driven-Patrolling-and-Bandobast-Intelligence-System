"""Rule configuration loader."""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from src.rules.engine import RuleEngine
from src.rules.static_object import StaticObjectRule
from src.rules.crowd_surge import CrowdSurgeRule
from src.rules.route_blockage import RouteBlockageRule
from src.rules.after_hours import AfterHoursRule


def load_rules_config(config_path: str = "config/rules.yaml") -> Dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        return {}
    
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


def create_engine_from_config(config_path: str = "config/rules.yaml") -> RuleEngine:
    config = load_rules_config(config_path)
    engine = RuleEngine()
    
    global_conf = config.get("global", {})
    engine.cooldown_seconds = global_conf.get("cooldown_seconds", 300)
    
    rules_conf = config.get("rules", {})
    
    # Static Object Rule
    static_conf = rules_conf.get("static_object", {})
    if static_conf.get("enabled", True):
        engine.register(StaticObjectRule(
            time_threshold_seconds=static_conf.get("time_threshold_seconds", 300),
            exclusion_zones=static_conf.get("exclusion_zones", []),
            priority=static_conf.get("priority", 80),
        ))
    
    # Crowd Surge Rule
    surge_conf = rules_conf.get("crowd_surge", {})
    if surge_conf.get("enabled", True):
        engine.register(CrowdSurgeRule(
            rate_threshold_percent=surge_conf.get("rate_threshold_percent", 50.0),
            min_initial_crowd=surge_conf.get("min_initial_crowd", 20),
            critical_density=surge_conf.get("critical_density", 3.0),
            window_seconds=surge_conf.get("window_seconds", 120),
            priority=surge_conf.get("priority", 90),
        ))
    
    # Route Blockage Rule
    route_conf = rules_conf.get("route_blockage", {})
    if route_conf.get("enabled", True):
        engine.register(RouteBlockageRule(
            route_zones=route_conf.get("route_zones", []),
            blockage_threshold=route_conf.get("blockage_threshold", 0.5),
            priority=route_conf.get("priority", 85),
        ))
    
    # After Hours Rule
    hours_conf = rules_conf.get("after_hours", {})
    if hours_conf.get("enabled", True):
        from datetime import time
        normal = hours_conf.get("normal_hours", {})
        start_str = normal.get("start", "06:00")
        end_str = normal.get("end", "22:00")
        
        engine.register(AfterHoursRule(
            normal_start=time.fromisoformat(start_str),
            normal_end=time.fromisoformat(end_str),
            min_activity_threshold=hours_conf.get("min_activity_threshold", 2),
            priority=hours_conf.get("priority", 60),
        ))
    
    return engine
