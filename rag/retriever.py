"""LangChain-based RAG retriever with FAISS vector store."""

import math
from datetime import datetime, timedelta
from typing import Optional
from functools import lru_cache

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from database.vectordb import get_vectordb, VectorDB
from rag.embedder import get_embedder


class LangChainRetriever:
    """LangChain-compatible retriever with filtering and relevance scoring."""
    
    def __init__(self):
        self.vectordb = get_vectordb()
        self.embedder = get_embedder()
        self._query_cache: dict = {}
    
    def get_relevant_documents(self, query: str, collection: str = "patrol_logs", top_k: int = 5) -> list[Document]:
        """LangChain-compatible method to get relevant documents."""
        results = self.search(query, collection, top_k)
        
        return [
            Document(
                page_content=r["document"],
                metadata=r.get("meta", {}),
            )
            for r in results
        ]
    
    def search(
        self,
        query: str,
        collection: str = "patrol_logs",
        top_k: int = 5,
        similarity_threshold: float = 0.0,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        location_lat: Optional[float] = None,
        location_lon: Optional[float] = None,
        location_radius_km: float = 5.0,
    ) -> list[dict]:
        """Search with optional metadata filtering."""
        query_embedding = self.embedder.embed(query)
        
        raw_results = self.vectordb.query(collection, query_embedding, n_results=top_k * 2)
        
        results = []
        for i, doc in enumerate(raw_results.get("documents", [])):
            meta = raw_results.get("metadatas", [{}])[i] if i < len(raw_results.get("metadatas", [])) else {}
            distance = raw_results.get("distances", [0])[i] if i < len(raw_results.get("distances", [])) else 0
            doc_id = raw_results.get("ids", [""])[i] if i < len(raw_results.get("ids", [])) else ""
            
            similarity = 1 / (1 + distance)
            
            if similarity < similarity_threshold:
                continue
            
            if not self._passes_filters(meta, date_from, date_to, category, severity, location_lat, location_lon, location_radius_km):
                continue
            
            results.append({
                "id": doc_id,
                "document": doc,
                "meta": meta,
                "similarity": similarity,
                "relevance_score": similarity,
            })
        
        results = self._score_results(results)
        results = self._diversify(results, top_k)
        
        return results[:top_k]
    
    def _passes_filters(
        self,
        meta: dict,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
        category: Optional[str],
        severity: Optional[str],
        loc_lat: Optional[float],
        loc_lon: Optional[float],
        radius_km: float,
    ) -> bool:
        """Check if document passes all filters."""
        if date_from or date_to:
            ts_str = meta.get("timestamp")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    if date_from and ts < date_from:
                        return False
                    if date_to and ts > date_to:
                        return False
                except ValueError:
                    pass
        
        if category and meta.get("category") != category:
            return False
        
        if severity and meta.get("severity") != severity:
            return False
        
        if loc_lat is not None and loc_lon is not None:
            doc_lat = meta.get("latitude") or meta.get("location_lat")
            doc_lon = meta.get("longitude") or meta.get("location_lon")
            if doc_lat and doc_lon:
                dist = self._haversine(loc_lat, loc_lon, float(doc_lat), float(doc_lon))
                if dist > radius_km:
                    return False
        
        return True
    
    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in km between two points."""
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(a))
    
    def _score_results(self, results: list[dict]) -> list[dict]:
        """Apply relevance scoring combining similarity and recency."""
        now = datetime.utcnow()
        
        for r in results:
            base_score = r["similarity"]
            
            recency_boost = 0.0
            ts_str = r.get("meta", {}).get("timestamp")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    days_old = (now - ts.replace(tzinfo=None)).days
                    recency_boost = max(0, 0.2 - (days_old * 0.01))
                except ValueError:
                    pass
            
            severity_boost = 0.0
            sev = r.get("meta", {}).get("severity", "").lower()
            if sev == "critical":
                severity_boost = 0.15
            elif sev == "high":
                severity_boost = 0.1
            elif sev == "medium":
                severity_boost = 0.05
            
            r["relevance_score"] = base_score + recency_boost + severity_boost
        
        return sorted(results, key=lambda x: x["relevance_score"], reverse=True)
    
    def _diversify(self, results: list[dict], target_count: int) -> list[dict]:
        """Ensure variety in results by avoiding too-similar documents."""
        if len(results) <= target_count:
            return results
        
        diversified = [results[0]] if results else []
        
        for r in results[1:]:
            if len(diversified) >= target_count:
                break
            
            is_diverse = True
            for d in diversified:
                if r.get("meta", {}).get("category") == d.get("meta", {}).get("category"):
                    if abs(r["similarity"] - d["similarity"]) < 0.05:
                        is_diverse = False
                        break
            
            if is_diverse:
                diversified.append(r)
        
        while len(diversified) < target_count and len(diversified) < len(results):
            for r in results:
                if r not in diversified:
                    diversified.append(r)
                    break
        
        return diversified
    
    def search_all(
        self,
        query: str,
        top_k_per_collection: int = 3,
        **filters,
    ) -> dict[str, list[dict]]:
        """Search across all collections."""
        results = {}
        
        for collection in self.vectordb.COLLECTIONS:
            try:
                col_results = self.search(query, collection, top_k_per_collection, **filters)
                results[collection] = col_results
            except Exception:
                results[collection] = []
        
        return results
    
    def get_context(
        self,
        query: str,
        max_tokens: int = 2000,
        **search_kwargs,
    ) -> str:
        """Assemble context for LLM consumption."""
        all_results = self.search_all(query, **search_kwargs)
        
        context_parts = []
        estimated_tokens = 0
        
        for collection, results in all_results.items():
            if not results:
                continue
            
            for r in results:
                doc = r["document"]
                doc_tokens = len(doc) // 4
                
                if estimated_tokens + doc_tokens > max_tokens:
                    break
                
                context_parts.append(f"[{collection}] {doc}")
                estimated_tokens += doc_tokens
        
        return "\n\n".join(context_parts)


@lru_cache
def get_retriever() -> LangChainRetriever:
    return LangChainRetriever()
