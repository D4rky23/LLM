"""Top-level vector package wrapper that re-exports src.vector."""

from src.vector.vector_store import VectorStore, initialize_vector_store
from src.vector.embeddings import get_embedding, get_embeddings_batch

__all__ = [
    "VectorStore",
    "initialize_vector_store",
    "get_embedding",
    "get_embeddings_batch",
]
