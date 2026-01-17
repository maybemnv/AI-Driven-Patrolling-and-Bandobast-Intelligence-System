"""Embedder module using sentence-transformers for text embeddings.

Model: all-MiniLM-L6-v2
- 384 dimensions
- Fast inference (~14k sentences/sec on GPU)
- Good quality for semantic similarity
- ~22M parameters, ~80MB
"""

import time
from functools import lru_cache
from typing import List, Union
import numpy as np


class Embedder:
    """Text embedder with lazy model loading and caching."""
    
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    DIMENSION = 384
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.MODEL_NAME)
        return self._model
    
    def embed(self, text: Union[str, List[str]]) -> np.ndarray:
        """Embed text or list of texts."""
        if isinstance(text, str):
            text = [text]
        return self.model.encode(text, convert_to_numpy=True, show_progress_bar=False)
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """Embed texts in batches with optional progress tracking."""
        if not texts:
            return np.array([]).reshape(0, self.DIMENSION)
        
        all_embeddings = []
        total = len(texts)
        
        for i in range(0, total, batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.model.encode(
                batch, 
                convert_to_numpy=True, 
                show_progress_bar=False
            )
            all_embeddings.append(embeddings)
            
            if show_progress:
                done = min(i + batch_size, total)
                print(f"Embedded {done}/{total} texts")
        
        return np.vstack(all_embeddings)
    
    def benchmark(self, n_samples: int = 100) -> dict:
        """Benchmark embedding speed."""
        sample_texts = [f"Sample text number {i} for benchmarking embedding speed." for i in range(n_samples)]
        
        start = time.perf_counter()
        _ = self.embed_batch(sample_texts, batch_size=32)
        elapsed = time.perf_counter() - start
        
        return {
            "n_samples": n_samples,
            "total_time_sec": round(elapsed, 3),
            "texts_per_sec": round(n_samples / elapsed, 1),
            "ms_per_text": round(elapsed * 1000 / n_samples, 2)
        }


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    """Get cached embedder instance."""
    return Embedder()
