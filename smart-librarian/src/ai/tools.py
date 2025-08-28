"""Tool registry and helpers (moved into ai package)."""

from core.config import config
from core.data_loader import load_books_data


def get_available_books():
    books, _ = load_books_data()
    return [b.title for b in books]


def get_summary_by_title(title: str) -> str:
    _, summaries = load_books_data()
    return summaries.get(title, "")
