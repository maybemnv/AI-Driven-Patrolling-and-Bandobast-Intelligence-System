"""Vector database setup with ChromaDB."""

from pathlib import Path
from typing import Dict, List, Optional, Any
import chromadb
from chromadb.config import Settings


class VectorDB:
    """ChromaDB wrapper for semantic search."""
    
    COLLECTIONS = {
        "patrol_logs": "Patrol session logs and reports",
        "alert_history": "Historical alerts for pattern matching",
        "location_context": "Location-specific context and knowledge",
    }
    
    def __init__(self, persist_dir: str = "data/vectordb"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        self._collections: Dict[str, Any] = {}
    
    def get_collection(self, name: str):
        """Get or create a collection."""
        if name not in self._collections:
            self._collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"description": self.COLLECTIONS.get(name, "")}
            )
        return self._collections[name]
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Add documents to collection."""
        collection = self.get_collection(collection_name)
        
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]
        
        collection.add(
            documents=documents,
            metadatas=metadatas or [{} for _ in documents],
            ids=ids,
        )
    
    def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict] = None,
    ) -> Dict:
        """Query collection for similar documents."""
        collection = self.get_collection(collection_name)
        
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
        )
        return results
    
    def delete(self, collection_name: str, ids: List[str]) -> None:
        """Delete documents by IDs."""
        collection = self.get_collection(collection_name)
        collection.delete(ids=ids)
    
    def count(self, collection_name: str) -> int:
        """Get document count in collection."""
        collection = self.get_collection(collection_name)
        return collection.count()
    
    def reset_collection(self, collection_name: str) -> None:
        """Delete and recreate collection."""
        self.client.delete_collection(collection_name)
        self._collections.pop(collection_name, None)
        self.get_collection(collection_name)


def get_vectordb(persist_dir: str = "data/vectordb") -> VectorDB:
    """Get VectorDB instance."""
    return VectorDB(persist_dir)
