"""Tests for database models and vectordb."""

import pytest
from datetime import datetime


class TestCameraModel:
    def test_enum_values(self):
        from database import CameraStatus
        assert CameraStatus.ACTIVE.value == "active"
        assert CameraStatus.INACTIVE.value == "inactive"


class TestEventModel:
    def test_event_types(self):
        from database import EventType
        assert EventType.OBJECT_DETECTED.value == "object_detected"
        assert EventType.CROWD_SURGE.value == "crowd_surge"


class TestAlertModel:
    def test_severity_levels(self):
        from database import AlertSeverity
        assert AlertSeverity.LOW.value == "low"
        assert AlertSeverity.CRITICAL.value == "critical"


class TestPatrolSession:
    def test_status_values(self):
        from database import PatrolStatus
        assert PatrolStatus.ACTIVE.value == "active"
        assert PatrolStatus.COMPLETED.value == "completed"


class TestSummary:
    def test_summary_types(self):
        from database import SummaryType
        assert SummaryType.PATROL.value == "patrol"
        assert SummaryType.DAILY.value == "daily"


class TestDatabaseInit:
    def test_create_engine(self):
        from database import create_db_engine
        engine = create_db_engine("sqlite:///:memory:")
        assert engine is not None
    
    def test_init_db(self, tmp_path):
        from database import create_db_engine, init_db
        db_path = tmp_path / "test.db"
        engine = create_db_engine(f"sqlite:///{db_path}")
        init_db(engine)
        assert db_path.exists()


class TestVectorDB:
    def test_init(self, tmp_path):
        from database import VectorDB
        vdb = VectorDB(str(tmp_path / "vectordb"))
        assert vdb is not None
    
    def test_get_collection(self, tmp_path):
        from database import VectorDB
        vdb = VectorDB(str(tmp_path / "vectordb"))
        col = vdb.get_collection("patrol_logs")
        assert col is not None
    
    def test_add_and_query(self, tmp_path):
        import numpy as np
        from database import VectorDB
        
        vdb = VectorDB(str(tmp_path / "vectordb"))
        
        docs = ["hello world", "test document"]
        embeddings = np.random.rand(2, 384).astype(np.float32)
        
        vdb.add_documents(
            "patrol_logs",
            documents=docs,
            embeddings=embeddings,
            ids=["1", "2"]
        )
        
        assert vdb.count("patrol_logs") == 2
        
        query_emb = np.random.rand(384).astype(np.float32)
        results = vdb.query("patrol_logs", query_emb, n_results=1)
        assert len(results["documents"]) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
