"""Top-level core package wrapper that re-exports src.core."""

from src.core.config import config
from src.core.schema import (
    Book,
    Query,
    Recommendation,
    ChatMessage,
    ToolCall,
    SearchResult,
)
from src.core.data_loader import load_books_data, validate_data_consistency
from src.core.retriever import get_retriever, search_books

__all__ = [
    "config",
    "Book",
    "Query",
    "Recommendation",
    "ChatMessage",
    "ToolCall",
    "SearchResult",
    "load_books_data",
    "validate_data_consistency",
    "get_retriever",
    "search_books",
]
