"""Vector database using FAISS for semantic search."""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

try:
    import faiss
except ImportError:
    faiss = None


class VectorDB:
    """FAISS-based vector store for semantic search."""
    
    COLLECTIONS = ["patrol_logs", "alert_history", "location_context"]
    
    def __init__(self, persist_dir: str = "data/vectordb", dimension: int = 384):
        if faiss is None:
            raise ImportError("faiss-cpu not installed. Run: uv add faiss-cpu")
        
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.dimension = dimension
        
        self._indexes: Dict[str, faiss.IndexFlatL2] = {}
        self._documents: Dict[str, List[str]] = {}
        self._metadatas: Dict[str, List[Dict]] = {}
        self._ids: Dict[str, List[str]] = {}
        
        self._load_all()
    
    def _index_path(self, name: str) -> Path:
        return self.persist_dir / f"{name}.index"
    
    def _data_path(self, name: str) -> Path:
        return self.persist_dir / f"{name}.pkl"
    
    def _load_all(self) -> None:
        for name in self.COLLECTIONS:
            self._load_collection(name)
    
    def _load_collection(self, name: str) -> None:
        index_path = self._index_path(name)
        data_path = self._data_path(name)
        
        if index_path.exists() and data_path.exists():
            self._indexes[name] = faiss.read_index(str(index_path))
            with open(data_path, "rb") as f:
                data = pickle.load(f)
                self._documents[name] = data.get("documents", [])
                self._metadatas[name] = data.get("metadatas", [])
                self._ids[name] = data.get("ids", [])
        else:
            self._indexes[name] = faiss.IndexFlatL2(self.dimension)
            self._documents[name] = []
            self._metadatas[name] = []
            self._ids[name] = []
    
    def _save_collection(self, name: str) -> None:
        faiss.write_index(self._indexes[name], str(self._index_path(name)))
        with open(self._data_path(name), "wb") as f:
            pickle.dump({
                "documents": self._documents[name],
                "metadatas": self._metadatas[name],
                "ids": self._ids[name],
            }, f)
    
    def get_collection(self, name: str) -> "VectorDB":
        if name not in self._indexes:
            self._load_collection(name)
        return self
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: np.ndarray,
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Add documents with pre-computed embeddings."""
        if collection_name not in self._indexes:
            self._load_collection(collection_name)
        
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]
        
        if metadatas is None:
            metadatas = [{} for _ in documents]
        
        embeddings = np.array(embeddings, dtype=np.float32)
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        
        self._indexes[collection_name].add(embeddings)
        self._documents[collection_name].extend(documents)
        self._metadatas[collection_name].extend(metadatas)
        self._ids[collection_name].extend(ids)
        
        self._save_collection(collection_name)
    
    def query(
        self,
        collection_name: str,
        query_embedding: np.ndarray,
        n_results: int = 5,
    ) -> Dict[str, List]:
        """Query collection with embedding vector."""
        if collection_name not in self._indexes:
            self._load_collection(collection_name)
        
        index = self._indexes[collection_name]
        if index.ntotal == 0:
            return {"documents": [], "metadatas": [], "ids": [], "distances": []}
        
        query_embedding = np.array(query_embedding, dtype=np.float32)
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        n = min(n_results, index.ntotal)
        distances, indices = index.search(query_embedding, n)
        
        docs = [self._documents[collection_name][i] for i in indices[0] if i >= 0]
        metas = [self._metadatas[collection_name][i] for i in indices[0] if i >= 0]
        doc_ids = [self._ids[collection_name][i] for i in indices[0] if i >= 0]
        
        return {
            "documents": docs,
            "metadatas": metas,
            "ids": doc_ids,
            "distances": distances[0].tolist()[:len(docs)],
        }
    
    def delete(self, collection_name: str, ids: List[str]) -> None:
        """Delete documents by IDs (rebuilds index)."""
        if collection_name not in self._indexes:
            return
        
        indices_to_keep = [
            i for i, doc_id in enumerate(self._ids[collection_name])
            if doc_id not in ids
        ]
        
        if len(indices_to_keep) == len(self._ids[collection_name]):
            return
        
        self._documents[collection_name] = [self._documents[collection_name][i] for i in indices_to_keep]
        self._metadatas[collection_name] = [self._metadatas[collection_name][i] for i in indices_to_keep]
        self._ids[collection_name] = [self._ids[collection_name][i] for i in indices_to_keep]
        
        # Rebuild index - FAISS doesn't support direct deletion
        old_index = self._indexes[collection_name]
        if old_index.ntotal > 0 and indices_to_keep:
            vectors = np.array([old_index.reconstruct(i) for i in indices_to_keep], dtype=np.float32)
            new_index = faiss.IndexFlatL2(self.dimension)
            new_index.add(vectors)
            self._indexes[collection_name] = new_index
        else:
            self._indexes[collection_name] = faiss.IndexFlatL2(self.dimension)
        
        self._save_collection(collection_name)
    
    def count(self, collection_name: str) -> int:
        if collection_name not in self._indexes:
            return 0
        return self._indexes[collection_name].ntotal
    
    def reset_collection(self, collection_name: str) -> None:
        self._indexes[collection_name] = faiss.IndexFlatL2(self.dimension)
        self._documents[collection_name] = []
        self._metadatas[collection_name] = []
        self._ids[collection_name] = []
        self._save_collection(collection_name)


def get_vectordb(persist_dir: str = "data/vectordb", dimension: int = 384) -> VectorDB:
    return VectorDB(persist_dir, dimension)
