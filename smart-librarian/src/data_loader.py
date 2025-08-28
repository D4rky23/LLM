"""Data loading utilities for Smart Librarian."""

import json
import re
from pathlib import Path
from typing import List, Dict

from .config import config
from .schema import Book


def parse_markdown_books(file_path: Path) -> List[Book]:
    """
    Parse book summaries from markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        List of Book objects

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    books = []

    # Split by book entries (## Title: pattern)
    book_sections = re.split(r"\n## Title: ", content)

    # Skip the first empty section
    for section in book_sections[1:]:
        lines = section.strip().split("\n")
        if len(lines) < 3:
            continue

        # Extract title (first line)
        title = lines[0].strip()

        # Find summary and themes
        short_summary = ""
        themes = []

        for line in lines[1:]:
            line = line.strip()
            if line.startswith("Rezumat scurt:"):
                short_summary = line.replace("Rezumat scurt:", "").strip()
            elif line.startswith("Teme:"):
                themes_str = line.replace("Teme:", "").strip()
                themes = [theme.strip() for theme in themes_str.split(",")]

        if title and short_summary and themes:
            book = Book(
                title=title, short_summary=short_summary, themes=themes
            )
            books.append(book)

    return books


def load_detailed_summaries(file_path: Path) -> Dict[str, str]:
    """
    Load detailed summaries from JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary mapping titles to detailed summaries

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the JSON is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")


def load_books_data() -> tuple[List[Book], Dict[str, str]]:
    """
    Load all books data from configured files.

    Returns:
        Tuple of (books list, detailed summaries dict)
    """
    books = parse_markdown_books(config.BOOK_SUMMARIES_MD)
    detailed_summaries = load_detailed_summaries(config.BOOK_SUMMARIES_JSON)

    # Validate that all books in MD have detailed summaries
    missing_summaries = []
    for book in books:
        if book.title not in detailed_summaries:
            missing_summaries.append(book.title)

    if missing_summaries:
        raise ValueError(
            f"Missing detailed summaries for: {missing_summaries}"
        )

    # Add detailed summaries to book objects
    for book in books:
        book.detailed_summary = detailed_summaries[book.title]

    return books, detailed_summaries


def validate_data_consistency() -> bool:
    """
    Validate consistency between MD and JSON files.

    Returns:
        True if data is consistent

    Raises:
        ValueError: If data is inconsistent
    """
    books = parse_markdown_books(config.BOOK_SUMMARIES_MD)
    detailed_summaries = load_detailed_summaries(config.BOOK_SUMMARIES_JSON)

    md_titles = {book.title for book in books}
    json_titles = set(detailed_summaries.keys())

    if md_titles != json_titles:
        missing_in_json = md_titles - json_titles
        missing_in_md = json_titles - md_titles

        error_msg = []
        if missing_in_json:
            error_msg.append(
                f"Titles in MD but not in JSON: {missing_in_json}"
            )
        if missing_in_md:
            error_msg.append(f"Titles in JSON but not in MD: {missing_in_md}")

        raise ValueError(". ".join(error_msg))

    return True


if __name__ == "__main__":
    # Test data loading
    try:
        validate_data_consistency()
        books, summaries = load_books_data()
        print(f"Successfully loaded {len(books)} books")
        for book in books[:3]:  # Show first 3 books
            print(f"- {book.title}: {book.themes}")
    except Exception as e:
        print(f"Error: {e}")
