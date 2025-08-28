"""Core package exports."""

from .config import config
from .schema import (
    Book,
    Query,
    Recommendation,
    ChatMessage,
    ToolCall,
    SearchResult,
)
from .data_loader import load_books_data, validate_data_consistency
from .retriever import get_retriever, search_books

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
