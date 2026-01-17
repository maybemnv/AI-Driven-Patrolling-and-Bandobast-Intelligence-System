"""Test script for RAG system with sample data."""

import json
from datetime import datetime
from pathlib import Path

import numpy as np

from database import VectorDB
from rag import get_embedder, get_retriever


OUTPUT_DIR = Path("outputs/rag_tests")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


SAMPLE_DOCUMENTS = [
    {
        "collection": "patrol_logs",
        "text": "Patrol session #101 by Officer Sharma in South Zone. Started 2024-01-15 08:00. Completed 4 hour shift covering 12 checkpoints. 2 incidents: suspicious vehicle near market, minor crowd at temple.",
        "meta": {"type": "patrol", "timestamp": "2024-01-15T08:00:00", "officer_id": "OFF001", "category": "patrol", "severity": "medium"}
    },
    {
        "collection": "patrol_logs", 
        "text": "Patrol session #102 by Officer Patel in North Zone. Started 2024-01-15 14:00. Evening patrol, routine. No incidents reported. Distance covered: 8 km.",
        "meta": {"type": "patrol", "timestamp": "2024-01-15T14:00:00", "officer_id": "OFF002", "category": "patrol", "severity": "low"}
    },
    {
        "collection": "patrol_logs",
        "text": "Patrol session #103 by Officer Singh in Central Zone near railway station. Started 2024-01-16 10:00. High foot traffic observed. Assisted with crowd management during peak hours.",
        "meta": {"type": "patrol", "timestamp": "2024-01-16T10:00:00", "officer_id": "OFF003", "category": "patrol", "severity": "medium"}
    },
    {
        "collection": "alert_history",
        "text": "Alert #201: crowd_surge (high severity). Large crowd detected at festival ground exceeding 500 people. Occurred on 2024-01-14 18:30. Status: acknowledged.",
        "meta": {"type": "alert", "timestamp": "2024-01-14T18:30:00", "alert_type": "crowd_surge", "category": "crowd_surge", "severity": "high"}
    },
    {
        "collection": "alert_history",
        "text": "Alert #202: static_object (medium severity). Unattended bag detected near bus station platform 3. Occurred on 2024-01-15 11:00. Status: resolved.",
        "meta": {"type": "alert", "timestamp": "2024-01-15T11:00:00", "alert_type": "static_object", "category": "static_object", "severity": "medium"}  
    },
    {
        "collection": "alert_history",
        "text": "Alert #203: crowd_density (low severity). Morning crowd at market area within normal limits. Occurred on 2024-01-16 09:00. Status: auto-resolved.",
        "meta": {"type": "alert", "timestamp": "2024-01-16T09:00:00", "alert_type": "crowd_density", "category": "crowd_density", "severity": "low"}
    },
    {
        "collection": "incident_reports",
        "text": "Event #301: crowd_detected from camera 'Station Plaza Cam' at Railway Station. 2024-01-15 17:30. Crowd size: 150. Density: 2.1 persons per sq meter.",
        "meta": {"type": "event", "timestamp": "2024-01-15T17:30:00", "event_type": "crowd_detected", "category": "crowd_detected", "severity": "medium"}
    },
    {
        "collection": "incident_reports",
        "text": "Event #302: object_detected from camera 'Market Entry' at Main Bazaar. 2024-01-15 12:00. Detected vehicle in pedestrian zone.",
        "meta": {"type": "event", "timestamp": "2024-01-15T12:00:00", "event_type": "object_detected", "category": "object_detected", "severity": "medium"}
    },
    {
        "collection": "location_context",
        "text": "Location: Railway Station. Major transit hub with 50,000+ daily footfall. Characteristics: high crowd density, multiple entry points, requires continuous monitoring. Risk level: high.",
        "meta": {"type": "location", "category": "transit", "severity": "high"}
    },
    {
        "collection": "location_context",
        "text": "Location: South Zone Market Area. Commercial district with shops and vendors. Characteristics: moderate crowds, pickpocket risk, narrow lanes. Risk level: medium.",
        "meta": {"type": "location", "category": "commercial", "severity": "medium"}
    },
]


def ingest_sample_data():
    """Ingest sample documents into vector database."""
    embedder = get_embedder()
    vdb = VectorDB("data/vectordb")
    
    for col in vdb.COLLECTIONS:
        vdb.reset_collection(col)
    
    for col in vdb.COLLECTIONS:
        docs = [d for d in SAMPLE_DOCUMENTS if d["collection"] == col]
        if not docs:
            continue
        
        texts = [d["text"] for d in docs]
        metas = [d["meta"] for d in docs]
        ids = [f"{col}_{i}" for i in range(len(docs))]
        
        embeddings = embedder.embed_batch(texts)
        vdb.add_documents(col, texts, embeddings, metas, ids)
        print(f"Ingested {len(docs)} documents into {col}")
    
    return vdb


def test_queries(vdb):
    """Run test queries and save results."""
    from rag.retriever import Retriever
    
    retriever = Retriever()
    retriever.vectordb = vdb
    
    queries = [
        "patrol incidents in south zone",
        "crowd management challenges",
        "static object alerts near station",
        "high risk locations",
        "evening patrol reports"
    ]
    
    results = {}
    
    for query in queries:
        print(f"\nQuery: {query}")
        
        search_results = retriever.search_all(query, top_k_per_collection=2)
        
        query_results = {}
        for collection, docs in search_results.items():
            query_results[collection] = [
                {
                    "document": d["document"][:100] + "..." if len(d["document"]) > 100 else d["document"],
                    "similarity": d["similarity"],
                    "relevance_score": d["relevance_score"]
                }
                for d in docs
            ]
            
            if docs:
                print(f"  {collection}: {len(docs)} results (top: {docs[0]['similarity']:.3f})")
        
        results[query] = query_results
    
    return results


def benchmark_retrieval():
    """Benchmark query performance."""
    import time
    from rag.retriever import Retriever
    
    retriever = Retriever()
    
    queries = ["patrol incidents", "crowd alerts", "station security"]
    
    times = []
    for _ in range(3):
        for q in queries:
            start = time.perf_counter()
            retriever.search(q, collection="patrol_logs")
            times.append(time.perf_counter() - start)
    
    return {
        "avg_query_ms": round(sum(times) / len(times) * 1000, 2),
        "min_query_ms": round(min(times) * 1000, 2),
        "max_query_ms": round(max(times) * 1000, 2)
    }


def main():
    print("=" * 50)
    print("RAG System Test")
    print("=" * 50)
    
    print("\n1. Ingesting sample data...")
    vdb = ingest_sample_data()
    
    stats = {col: vdb.count(col) for col in vdb.COLLECTIONS}
    print(f"Collection counts: {stats}")
    
    print("\n2. Running test queries...")
    query_results = test_queries(vdb)
    
    print("\n3. Benchmarking retrieval...")
    benchmark = benchmark_retrieval()
    print(f"Query performance: {benchmark}")
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "collection_stats": stats,
        "query_results": query_results,
        "benchmark": benchmark
    }
    
    output_file = OUTPUT_DIR / "test_results.json"
    output_file.write_text(json.dumps(output, indent=2))
    print(f"\nResults saved to: {output_file}")
    
    print("\n" + "=" * 50)
    print("Test Complete")
    print("=" * 50)


if __name__ == "__main__":
    main()
