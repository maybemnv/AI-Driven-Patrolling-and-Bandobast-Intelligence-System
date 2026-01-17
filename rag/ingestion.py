"""Document ingestion pipeline for RAG system."""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from database import (
    create_db_engine, get_session,
    PatrolSession, PatrolStatus, Alert, Event, Camera
)
from database.vectordb import get_vectordb
from rag.embedder import get_embedder
from rag.preprocessor import (
    patrol_session_to_text, alert_to_text, event_to_text, events_to_narrative
)
from rag.chunker import chunk_text


INGESTION_STATE_FILE = Path("data/vectordb/ingestion_state.json")


def _load_state() -> dict:
    if INGESTION_STATE_FILE.exists():
        return json.loads(INGESTION_STATE_FILE.read_text())
    return {"last_patrol_id": 0, "last_alert_id": 0, "last_event_id": 0}


def _save_state(state: dict):
    INGESTION_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    INGESTION_STATE_FILE.write_text(json.dumps(state))


def _doc_id(collection: str, record_id: int) -> str:
    return f"{collection}_{record_id}"


def _content_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:16]


class IngestionPipeline:
    """Pipeline for ingesting database records into vector store."""
    
    def __init__(self, db_url: str = "sqlite:///data/patrolling.db"):
        self.engine = create_db_engine(db_url)
        self.vectordb = get_vectordb()
        self.embedder = get_embedder()
        self.state = _load_state()
    
    def ingest_patrol_sessions(self, limit: int = 100, incremental: bool = True) -> dict:
        """Ingest completed patrol sessions."""
        session = get_session(self.engine)
        
        query = session.query(PatrolSession).filter(
            PatrolSession.status == PatrolStatus.COMPLETED
        )
        
        if incremental:
            query = query.filter(PatrolSession.id > self.state.get("last_patrol_id", 0))
        
        patrols = query.order_by(PatrolSession.id).limit(limit).all()
        
        if not patrols:
            session.close()
            return {"ingested": 0, "collection": "patrol_logs"}
        
        documents, metadatas, ids = [], [], []
        
        for p in patrols:
            text = patrol_session_to_text(
                session_id=p.id,
                officer_id=p.officer_id,
                officer_name=p.officer_name,
                start_time=p.start_time,
                end_time=p.end_time,
                status=p.status.value,
                incidents_count=p.incidents_count,
                distance_km=p.distance_km,
                route_data=p.route_data or []
            )
            
            documents.append(text)
            ids.append(_doc_id("patrol", p.id))
            metadatas.append({
                "type": "patrol_session",
                "timestamp": p.start_time.isoformat(),
                "officer_id": p.officer_id,
                "category": "patrol",
                "severity": "low" if p.incidents_count == 0 else "medium",
                "content_hash": _content_hash(text)
            })
        
        embeddings = self.embedder.embed_batch(documents, show_progress=True)
        
        self.vectordb.add_documents(
            collection_name="patrol_logs",
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        self.state["last_patrol_id"] = patrols[-1].id
        _save_state(self.state)
        session.close()
        
        return {"ingested": len(patrols), "collection": "patrol_logs"}
    
    def ingest_alerts(self, limit: int = 100, incremental: bool = True) -> dict:
        """Ingest acknowledged alerts."""
        session = get_session(self.engine)
        
        query = session.query(Alert).filter(Alert.acknowledged == True)
        
        if incremental:
            query = query.filter(Alert.id > self.state.get("last_alert_id", 0))
        
        alerts = query.order_by(Alert.id).limit(limit).all()
        
        if not alerts:
            session.close()
            return {"ingested": 0, "collection": "alert_history"}
        
        documents, metadatas, ids = [], [], []
        
        for a in alerts:
            text = alert_to_text(
                alert_id=a.id,
                alert_type=a.alert_type,
                severity=a.severity.value,
                message=a.message,
                location_lat=a.location_lat,
                location_lon=a.location_lon,
                acknowledged=a.acknowledged,
                created_at=a.created_at
            )
            
            documents.append(text)
            ids.append(_doc_id("alert", a.id))
            metadatas.append({
                "type": "alert",
                "timestamp": a.created_at.isoformat(),
                "alert_type": a.alert_type,
                "category": a.alert_type,
                "severity": a.severity.value,
                "location_lat": a.location_lat,
                "location_lon": a.location_lon,
                "content_hash": _content_hash(text)
            })
        
        embeddings = self.embedder.embed_batch(documents, show_progress=True)
        
        self.vectordb.add_documents(
            collection_name="alert_history",
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        self.state["last_alert_id"] = alerts[-1].id
        _save_state(self.state)
        session.close()
        
        return {"ingested": len(alerts), "collection": "alert_history"}
    
    def ingest_events(self, limit: int = 200, incremental: bool = True) -> dict:
        """Ingest processed events."""
        session = get_session(self.engine)
        
        query = session.query(Event).filter(Event.processed == True)
        
        if incremental:
            query = query.filter(Event.id > self.state.get("last_event_id", 0))
        
        events = query.order_by(Event.id).limit(limit).all()
        
        if not events:
            session.close()
            return {"ingested": 0, "collection": "incident_reports"}
        
        documents, metadatas, ids = [], [], []
        
        for e in events:
            camera_name = None
            location_name = None
            lat, lon = None, None
            
            if e.camera:
                camera_name = e.camera.camera_name
                location_name = e.camera.location_name
                lat = e.camera.latitude
                lon = e.camera.longitude
            
            text = event_to_text(
                event_id=e.id,
                event_type=e.event_type.value,
                confidence=e.confidence_score,
                timestamp=e.timestamp,
                camera_name=camera_name,
                location_name=location_name,
                data=e.data
            )
            
            documents.append(text)
            ids.append(_doc_id("event", e.id))
            metadatas.append({
                "type": "event",
                "timestamp": e.timestamp.isoformat(),
                "event_type": e.event_type.value,
                "category": e.event_type.value,
                "severity": "medium",
                "location_lat": lat,
                "location_lon": lon,
                "content_hash": _content_hash(text)
            })
        
        embeddings = self.embedder.embed_batch(documents, show_progress=True)
        
        self.vectordb.add_documents(
            collection_name="incident_reports",
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        self.state["last_event_id"] = events[-1].id
        _save_state(self.state)
        session.close()
        
        return {"ingested": len(events), "collection": "incident_reports"}
    
    def ingest_all(self, incremental: bool = True) -> dict:
        """Run full ingestion pipeline."""
        results = {
            "patrol_logs": self.ingest_patrol_sessions(incremental=incremental),
            "alert_history": self.ingest_alerts(incremental=incremental),
            "incident_reports": self.ingest_events(incremental=incremental)
        }
        
        results["total"] = sum(r["ingested"] for r in results.values())
        return results
    
    def get_stats(self) -> dict:
        """Get ingestion statistics."""
        return {
            "collections": {
                name: self.vectordb.count(name)
                for name in self.vectordb.COLLECTIONS
            },
            "state": self.state
        }
    
    def reset(self, collection: Optional[str] = None):
        """Reset ingestion state and/or collection."""
        if collection:
            self.vectordb.reset_collection(collection)
            if collection == "patrol_logs":
                self.state["last_patrol_id"] = 0
            elif collection == "alert_history":
                self.state["last_alert_id"] = 0
            elif collection == "incident_reports":
                self.state["last_event_id"] = 0
        else:
            for col in self.vectordb.COLLECTIONS:
                self.vectordb.reset_collection(col)
            self.state = {"last_patrol_id": 0, "last_alert_id": 0, "last_event_id": 0}
        
        _save_state(self.state)


def get_pipeline(db_url: str = "sqlite:///data/patrolling.db") -> IngestionPipeline:
    return IngestionPipeline(db_url)
