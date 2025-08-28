"""Re-export vector.embeddings from src.vector.embeddings"""

from src.vector.embeddings import *

__all__ = getattr(
    __import__("src.vector.embeddings", fromlist=["__all__"]), "__all__", []
)
