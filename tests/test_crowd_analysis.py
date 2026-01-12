"""Unit tests for crowd analysis."""

import numpy as np
import pytest


class TestDensityLevel:
    def test_enum_values(self):
        from model.crowd import DensityLevel
        assert DensityLevel.LOW.value == "low"
        assert DensityLevel.CRITICAL.value == "critical"


class TestCrowdAnalyzer:
    def test_init_defaults(self):
        from model.crowd import CrowdAnalyzer
        analyzer = CrowdAnalyzer()
        assert analyzer.coverage_area == 100.0
        assert analyzer.grid_cols == 4
        assert analyzer.grid_rows == 3
    
    def test_classify_density_low(self):
        from model.crowd import CrowdAnalyzer, DensityLevel
        analyzer = CrowdAnalyzer()
        assert analyzer._classify_density(0.2) == DensityLevel.LOW
    
    def test_classify_density_medium(self):
        from model.crowd import CrowdAnalyzer, DensityLevel
        analyzer = CrowdAnalyzer()
        assert analyzer._classify_density(1.0) == DensityLevel.MEDIUM
    
    def test_classify_density_high(self):
        from model.crowd import CrowdAnalyzer, DensityLevel
        analyzer = CrowdAnalyzer()
        assert analyzer._classify_density(3.0) == DensityLevel.HIGH
    
    def test_classify_density_critical(self):
        from model.crowd import CrowdAnalyzer, DensityLevel
        analyzer = CrowdAnalyzer()
        assert analyzer._classify_density(5.0) == DensityLevel.CRITICAL
    
    def test_get_stats_empty(self):
        from model.crowd import CrowdAnalyzer
        analyzer = CrowdAnalyzer()
        stats = analyzer.get_stats()
        assert stats["count"] == 0
        assert stats["mean"] == 0
    
    def test_reset(self):
        from model.crowd import CrowdAnalyzer
        analyzer = CrowdAnalyzer()
        analyzer.reset()
        assert len(analyzer._history) == 0


class TestSurgeSeverity:
    def test_enum_values(self):
        from model.crowd import SurgeSeverity
        assert SurgeSeverity.NONE.value == "none"
        assert SurgeSeverity.MAJOR.value == "major"


class TestCrowdEventBuilder:
    def test_init(self):
        from model.crowd.events import CrowdEventBuilder
        builder = CrowdEventBuilder("test_cam")
        assert builder._builder.camera_id == "test_cam"
    
    def test_reset(self):
        from model.crowd.events import CrowdEventBuilder
        builder = CrowdEventBuilder()
        builder._last_events["test"] = 100.0
        builder.reset()
        assert len(builder._last_events) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
