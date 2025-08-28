"""Data loading utilities for Smart Librarian (moved into core package)."""

import json
from pathlib import Path
from typing import List, Tuple

from core.config import config
from core.schema import Book


def parse_markdown_books(md_path: Path) -> List[Book]:
    """Parse books from a markdown file into Book objects."""
    if not md_path.exists():
        return []

    text = md_path.read_text(encoding="utf-8")
    # Simple parser: split by '## ' headings for each book
    entries = [e.strip() for e in text.split("\n## ") if e.strip()]
    books = []
    for entry in entries:
        lines = entry.splitlines()
        title = lines[0].strip("# ").strip()
        short_summary = lines[1].strip() if len(lines) > 1 else ""
        books.append(
            Book(
                title=title,
                author=None,
                short_summary=short_summary,
                detailed_summary=None,
                themes=[],
            )
        )

    return books


def load_detailed_summaries(json_path: Path) -> dict:
    if not json_path.exists():
        return {}

    return json.loads(json_path.read_text(encoding="utf-8"))


def load_books_data() -> Tuple[List[Book], dict]:
    books = parse_markdown_books(config.BOOK_SUMMARIES_MD)
    summaries = load_detailed_summaries(config.BOOK_SUMMARIES_JSON)

    # Attach detailed summaries if available
    for book in books:
        if book.title in summaries:
            book.detailed_summary = summaries[book.title]

    return books, summaries


def validate_data_consistency() -> bool:
    # Basic checks for required data files
    if not config.BOOK_SUMMARIES_MD.exists():
        raise FileNotFoundError("Missing book_summaries.md")
    if not config.BOOK_SUMMARIES_JSON.exists():
        raise FileNotFoundError("Missing book_summaries.json")
    return True
