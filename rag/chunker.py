"""Text chunking utilities for document processing."""

import re
from typing import Generator


def chunk_text(
    text: str,
    chunk_size: int = 400,
    overlap: int = 50,
    preserve_sentences: bool = True
) -> list[str]:
    """Split text into overlapping chunks.
    
    Args:
        text: Input text
        chunk_size: Target chunk size in characters (~4 chars/token)
        overlap: Overlap between chunks
        preserve_sentences: Try to break at sentence boundaries
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []
    
    if preserve_sentences:
        return _chunk_by_sentences(text, chunk_size, overlap)
    
    return _chunk_fixed(text, chunk_size, overlap)


def _chunk_fixed(text: str, size: int, overlap: int) -> list[str]:
    """Fixed-size chunking with overlap."""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    
    return [c for c in chunks if c]


def _chunk_by_sentences(text: str, size: int, overlap: int) -> list[str]:
    """Chunk preserving sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current = []
    current_len = 0
    
    for sent in sentences:
        sent_len = len(sent)
        
        if current_len + sent_len > size and current:
            chunks.append(" ".join(current))
            
            # Keep overlap from end
            overlap_text = ""
            overlap_len = 0
            for s in reversed(current):
                if overlap_len + len(s) <= overlap:
                    overlap_text = s + " " + overlap_text
                    overlap_len += len(s) + 1
                else:
                    break
            
            current = [overlap_text.strip()] if overlap_text.strip() else []
            current_len = len(overlap_text)
        
        current.append(sent)
        current_len += sent_len + 1
    
    if current:
        chunks.append(" ".join(current))
    
    return [c.strip() for c in chunks if c.strip()]


def estimate_tokens(text: str) -> int:
    """Rough token count estimate (~4 chars per token)."""
    return len(text) // 4
