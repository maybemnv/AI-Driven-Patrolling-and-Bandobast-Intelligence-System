"""RAG API router for ingestion and semantic search."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from rag import get_pipeline, get_retriever


router = APIRouter(prefix="/rag", tags=["RAG"])


class IngestResponse(BaseModel):
    status: str
    results: dict


class QueryRequest(BaseModel):
    query: str
    collection: Optional[str] = None
    top_k: int = 5
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    location_radius_km: float = 5.0


class SearchResult(BaseModel):
    id: str
    document: str
    meta: dict
    similarity: float
    relevance_score: float


class QueryResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int


class ContextResponse(BaseModel):
    query: str
    context: str
    token_estimate: int


class StatsResponse(BaseModel):
    collections: dict[str, int]
    state: dict


@router.post("/ingest", response_model=IngestResponse)
def trigger_ingestion(
    collection: Optional[str] = Query(None, description="Specific collection to ingest"),
    incremental: bool = Query(True, description="Only ingest new records")
):
    """Trigger document ingestion from database."""
    pipeline = get_pipeline()
    
    if collection:
        if collection == "patrol_logs":
            results = {"patrol_logs": pipeline.ingest_patrol_sessions(incremental=incremental)}
        elif collection == "alert_history":
            results = {"alert_history": pipeline.ingest_alerts(incremental=incremental)}
        elif collection == "incident_reports":
            results = {"incident_reports": pipeline.ingest_events(incremental=incremental)}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown collection: {collection}")
    else:
        results = pipeline.ingest_all(incremental=incremental)
    
    return IngestResponse(status="completed", results=results)


@router.post("/query", response_model=QueryResponse)
def semantic_search(request: QueryRequest):
    """Perform semantic search across collections."""
    retriever = get_retriever()
    
    if request.collection:
        results = retriever.search(
            query=request.query,
            collection=request.collection,
            top_k=request.top_k,
            date_from=request.date_from,
            date_to=request.date_to,
            category=request.category,
            severity=request.severity,
            location_lat=request.location_lat,
            location_lon=request.location_lon,
            location_radius_km=request.location_radius_km
        )
    else:
        all_results = retriever.search_all(
            query=request.query,
            top_k_per_collection=request.top_k,
            date_from=request.date_from,
            date_to=request.date_to,
            category=request.category,
            severity=request.severity
        )
        results = []
        for col_results in all_results.values():
            results.extend(col_results)
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        results = results[:request.top_k]
    
    return QueryResponse(
        query=request.query,
        results=[SearchResult(**r) for r in results],
        total=len(results)
    )


@router.post("/context", response_model=ContextResponse)
def get_llm_context(
    query: str = Query(..., description="Query to get context for"),
    max_tokens: int = Query(2000, description="Maximum tokens in context")
):
    """Get assembled context for LLM consumption."""
    retriever = get_retriever()
    context = retriever.get_context(query, max_tokens=max_tokens)
    
    return ContextResponse(
        query=query,
        context=context,
        token_estimate=len(context) // 4
    )


@router.get("/stats", response_model=StatsResponse)
def get_stats():
    """Get collection statistics."""
    pipeline = get_pipeline()
    stats = pipeline.get_stats()
    return StatsResponse(**stats)


@router.delete("/reset")
def reset_collection(collection: Optional[str] = Query(None)):
    """Reset collection(s) and ingestion state."""
    pipeline = get_pipeline()
    pipeline.reset(collection)
    return {"status": "reset", "collection": collection or "all"}
