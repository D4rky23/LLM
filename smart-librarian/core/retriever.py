"""Re-export core.retriever from src.core.retriever"""

from src.core.retriever import *

__all__ = getattr(
    __import__("src.core.retriever", fromlist=["__all__"]), "__all__", []
)
