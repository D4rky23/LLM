"""Top-level ai package wrapper that re-exports src.ai."""

from src.ai.llm import get_chatbot
from src.ai.tools import get_available_books, get_summary_by_title

__all__ = ["get_chatbot", "get_available_books", "get_summary_by_title"]
