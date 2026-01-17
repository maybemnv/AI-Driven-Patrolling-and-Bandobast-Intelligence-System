"""Retriever for semantic search with filtering and context assembly."""

import math
from datetime import datetime, timedelta
from typing import Optional
from functools import lru_cache

from database.vectordb import get_vectordb, VectorDB
from rag.embedder import get_embedder


class Retriever:
    """Semantic retriever with filtering and relevance scoring."""
    
    def __init__(self):
        self.vectordb = get_vectordb()
        self.embedder = get_embedder()
        self._query_cache: dict = {}
    
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
        location_radius_km: float = 5.0
    ) -> list[dict]:
        """Search with optional metadata filtering."""
        query_embedding = self.embedder.embed(query)[0]
        
        # Get more results to allow for post-filtering
        fetch_k = min(top_k * 3, 50)
        
        results = self.vectordb.query(
            collection_name=collection,
            query_embedding=query_embedding,
            n_results=fetch_k
        )
        
        if not results["documents"]:
            return []
        
        candidates = []
        for i, (doc, meta, doc_id, dist) in enumerate(zip(
            results["documents"],
            results["metadatas"],
            results["ids"],
            results["distances"]
        )):
            # Convert L2 distance to similarity score (0-1)
            similarity = 1 / (1 + dist)
            
            if similarity < similarity_threshold:
                continue
            
            # Apply metadata filters
            if not self._passes_filters(
                meta, date_from, date_to, category, severity,
                location_lat, location_lon, location_radius_km
            ):
                continue
            
            candidates.append({
                "id": doc_id,
                "document": doc,
                "meta": meta,
                "similarity": round(similarity, 4),
                "distance": round(dist, 4)
            })
        
        # Apply relevance scoring
        scored = self._score_results(candidates)
        
        # Diversify results
        diversified = self._diversify(scored, top_k)
        
        return diversified[:top_k]
    
    def _passes_filters(
        self,
        meta: dict,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
        category: Optional[str],
        severity: Optional[str],
        loc_lat: Optional[float],
        loc_lon: Optional[float],
        radius_km: float
    ) -> bool:
        """Check if document passes all filters."""
        # Date filter
        if date_from or date_to:
            ts_str = meta.get("timestamp")
            if ts_str:
                ts = datetime.fromisoformat(ts_str)
                if date_from and ts < date_from:
                    return False
                if date_to and ts > date_to:
                    return False
        
        # Category filter
        if category and meta.get("category") != category:
            return False
        
        # Severity filter
        if severity and meta.get("severity") != severity:
            return False
        
        # Location proximity filter
        if loc_lat is not None and loc_lon is not None:
            doc_lat = meta.get("location_lat")
            doc_lon = meta.get("location_lon")
            if doc_lat is not None and doc_lon is not None:
                dist = self._haversine(loc_lat, loc_lon, doc_lat, doc_lon)
                if dist > radius_km:
                    return False
        
        return True
    
    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in km between two points."""
        R = 6371
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(a))
    
    def _score_results(self, results: list[dict]) -> list[dict]:
        """Apply relevance scoring combining similarity and recency."""
        now = datetime.now()
        
        for r in results:
            base_score = r["similarity"]
            
            # Recency boost (documents from last 7 days get up to 20% boost)
            ts_str = r["meta"].get("timestamp")
            if ts_str:
                ts = datetime.fromisoformat(ts_str)
                days_old = (now - ts).days
                recency_boost = max(0, 0.2 * (1 - days_old / 7))
                base_score += recency_boost
            
            # Severity boost
            severity = r["meta"].get("severity", "low")
            severity_weights = {"critical": 0.15, "high": 0.1, "medium": 0.05, "low": 0}
            base_score += severity_weights.get(severity, 0)
            
            r["relevance_score"] = round(base_score, 4)
        
        return sorted(results, key=lambda x: x["relevance_score"], reverse=True)
    
    def _diversify(self, results: list[dict], target_count: int) -> list[dict]:
        """Ensure variety in results by avoiding too-similar documents."""
        if len(results) <= target_count:
            return results
        
        selected = [results[0]]
        
        for r in results[1:]:
            if len(selected) >= target_count:
                break
            
            # Check similarity to already selected documents
            is_diverse = True
            for s in selected:
                if r["meta"].get("type") == s["meta"].get("type"):
                    if abs(r["similarity"] - s["similarity"]) < 0.05:
                        is_diverse = False
                        break
            
            if is_diverse:
                selected.append(r)
        
        # Fill remaining slots if needed
        if len(selected) < target_count:
            for r in results:
                if r not in selected:
                    selected.append(r)
                if len(selected) >= target_count:
                    break
        
        return selected
    
    def search_all(
        self,
        query: str,
        top_k_per_collection: int = 3,
        **filters
    ) -> dict[str, list[dict]]:
        """Search across all collections."""
        results = {}
        for collection in self.vectordb.COLLECTIONS:
            results[collection] = self.search(
                query=query,
                collection=collection,
                top_k=top_k_per_collection,
                **filters
            )
        return results
    
    def get_context(
        self,
        query: str,
        max_tokens: int = 2000,
        **search_kwargs
    ) -> str:
        """Assemble context for LLM consumption."""
        results = self.search_all(query, **search_kwargs)
        
        context_parts = []
        total_chars = 0
        max_chars = max_tokens * 4
        
        for collection, docs in results.items():
            if not docs:
                continue
            
            for doc in docs:
                entry = f"[{collection}] {doc['document']}"
                
                if total_chars + len(entry) > max_chars:
                    break
                
                context_parts.append(entry)
                total_chars += len(entry)
        
        if not context_parts:
            return ""
        
        header = f"Relevant context for query: '{query}'\n\n"
        return header + "\n\n".join(context_parts)


@lru_cache(maxsize=1)
def get_retriever() -> Retriever:
    return Retriever()
