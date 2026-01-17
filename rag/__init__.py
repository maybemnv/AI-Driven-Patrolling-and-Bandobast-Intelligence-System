"""RAG module for semantic search over patrol and incident data."""

from rag.embedder import Embedder, get_embedder
from rag.preprocessor import (
    patrol_session_to_text,
    alert_to_text,
    event_to_text,
    events_to_narrative,
    location_context_to_text
)
from rag.chunker import chunk_text, estimate_tokens
from rag.ingestion import IngestionPipeline, get_pipeline
from rag.retriever import Retriever, get_retriever

__all__ = [
    "Embedder", "get_embedder",
    "patrol_session_to_text", "alert_to_text", "event_to_text",
    "events_to_narrative", "location_context_to_text",
    "chunk_text", "estimate_tokens",
    "IngestionPipeline", "get_pipeline",
    "Retriever", "get_retriever"
]
