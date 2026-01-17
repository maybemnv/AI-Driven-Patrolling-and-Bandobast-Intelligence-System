"""Tests for RAG module."""

import pytest
import tempfile
import numpy as np
from pathlib import Path


class TestEmbedder:
    def test_embed_single(self):
        from rag import get_embedder
        embedder = get_embedder()
        result = embedder.embed("test text")
        assert result.shape == (1, 384)
    
    def test_embed_batch(self):
        from rag import get_embedder
        embedder = get_embedder()
        result = embedder.embed_batch(["text one", "text two"])
        assert result.shape == (2, 384)
    
    def test_benchmark(self):
        from rag import get_embedder
        embedder = get_embedder()
        stats = embedder.benchmark(n_samples=10)
        assert "texts_per_sec" in stats


class TestChunker:
    def test_short_text(self):
        from rag import chunk_text
        result = chunk_text("Short text.")
        assert result == ["Short text."]
    
    def test_long_text(self):
        from rag import chunk_text
        text = "First sentence. " * 50
        result = chunk_text(text, chunk_size=200)
        assert len(result) > 1


class TestPreprocessor:
    def test_patrol_to_text(self):
        from datetime import datetime
        from rag import patrol_session_to_text
        
        text = patrol_session_to_text(
            session_id=1,
            officer_id="OFF001",
            officer_name="John Doe",
            start_time=datetime(2024, 1, 1, 10, 0),
            end_time=datetime(2024, 1, 1, 12, 0),
            status="completed",
            incidents_count=2,
            distance_km=5.5,
            route_data=[{}, {}]
        )
        assert "Patrol session #1" in text
        assert "John Doe" in text
    
    def test_alert_to_text(self):
        from datetime import datetime
        from rag import alert_to_text
        
        text = alert_to_text(
            alert_id=1,
            alert_type="crowd_surge",
            severity="high",
            message="Large crowd detected",
            location_lat=19.0,
            location_lon=72.0,
            acknowledged=True,
            created_at=datetime(2024, 1, 1, 10, 0)
        )
        assert "Alert #1" in text
        assert "crowd_surge" in text


class TestVectorDB:
    def test_add_and_query(self, tmp_path):
        from database import VectorDB
        from rag import get_embedder
        
        vdb = VectorDB(str(tmp_path / "vectordb"))
        embedder = get_embedder()
        
        docs = ["hello world", "test document"]
        embeddings = embedder.embed_batch(docs)
        
        vdb.add_documents(
            "patrol_logs",
            documents=docs,
            embeddings=embeddings,
            ids=["1", "2"]
        )
        
        assert vdb.count("patrol_logs") == 2
        
        query_emb = embedder.embed("hello")[0]
        results = vdb.query("patrol_logs", query_emb, n_results=1)
        assert len(results["documents"]) >= 1


class TestRetriever:
    def test_search(self, tmp_path):
        from database import VectorDB
        from rag import get_embedder
        from rag.retriever import Retriever
        
        vdb = VectorDB(str(tmp_path / "vectordb"))
        embedder = get_embedder()
        
        docs = ["patrol in south zone", "crowd at station"]
        embeddings = embedder.embed_batch(docs)
        
        vdb.add_documents(
            "patrol_logs",
            documents=docs,
            embeddings=embeddings,
            ids=["1", "2"],
            metadatas=[{"type": "patrol"}, {"type": "crowd"}]
        )
        
        retriever = Retriever()
        retriever.vectordb = vdb
        retriever.embedder = embedder
        
        results = retriever.search("south zone patrol", collection="patrol_logs")
        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
