"""Retriever for semantic book search using vector store."""

import logging
from typing import List, Optional

from .schema import Book, SearchResult
from .vector_store import VectorStore, initialize_vector_store
from .config import config
from .data_loader import load_books_data

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BookRetriever:
    """Semantic search retriever for books."""

    def __init__(self, vector_store: VectorStore = None):
        """
        Initialize the retriever.

        Args:
            vector_store: VectorStore instance (creates new if None)
        """
        self.vector_store = vector_store or initialize_vector_store()
        self._books_cache = None
        self._detailed_summaries_cache = None

    def _load_books_cache(self):
        """Load books data into cache."""
        if self._books_cache is None or self._detailed_summaries_cache is None:
            self._books_cache, self._detailed_summaries_cache = (
                load_books_data()
            )

    def _get_book_by_title(self, title: str) -> Optional[Book]:
        """
        Get full Book object by title.

        Args:
            title: Book title

        Returns:
            Book object if found
        """
        self._load_books_cache()

        for book in self._books_cache:
            if book.title == title:
                return book

        return None

    def search_books(self, query: str, top_k: int = None) -> List[Book]:
        """
        Search for books based on query.

        Args:
            query: Search query (themes, keywords, etc.)
            top_k: Number of results to return (default from config)

        Returns:
            List of Book objects matching the query
        """
        if top_k is None:
            top_k = config.DEFAULT_TOP_K

        try:
            # Search in vector store
            search_results = self.vector_store.search(query, top_k=top_k)

            # Convert to Book objects
            books = []
            for result in search_results:
                book = self._get_book_by_title(result["title"])
                if book:
                    books.append(book)

            logger.info(f"Retrieved {len(books)} books for query: '{query}'")
            return books

        except Exception as e:
            logger.error(f"Error searching books: {e}")
            return []

    def search_with_scores(
        self, query: str, top_k: int = None
    ) -> List[tuple[Book, float]]:
        """
        Search for books with relevance scores.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of (Book, score) tuples
        """
        if top_k is None:
            top_k = config.DEFAULT_TOP_K

        try:
            # Search in vector store
            search_results = self.vector_store.search(query, top_k=top_k)

            # Convert to Book objects with scores
            books_with_scores = []
            for result in search_results:
                book = self._get_book_by_title(result["title"])
                if book:
                    books_with_scores.append((book, result["score"]))

            logger.info(
                f"Retrieved {len(books_with_scores)} books with scores for query: '{query}'"
            )
            return books_with_scores

        except Exception as e:
            logger.error(f"Error searching books with scores: {e}")
            return []

    def get_book_by_exact_title(self, title: str) -> Optional[Book]:
        """
        Get a book by exact title match.

        Args:
            title: Exact book title

        Returns:
            Book object if found
        """
        return self._get_book_by_title(title)

    def search_by_themes(
        self, themes: List[str], top_k: int = None
    ) -> List[Book]:
        """
        Search books by specific themes.

        Args:
            themes: List of themes to search for
            top_k: Number of results to return

        Returns:
            List of Book objects
        """
        # Create query from themes
        query = f"Teme: {', '.join(themes)}"
        return self.search_books(query, top_k)

    def get_random_recommendations(self, count: int = 3) -> List[Book]:
        """
        Get random book recommendations.

        Args:
            count: Number of recommendations

        Returns:
            List of random Book objects
        """
        import random

        self._load_books_cache()

        if len(self._books_cache) <= count:
            return self._books_cache[:]

        return random.sample(self._books_cache, count)

    def get_similar_books(self, book_title: str, top_k: int = 3) -> List[Book]:
        """
        Find books similar to a given book.

        Args:
            book_title: Title of the reference book
            top_k: Number of similar books to return

        Returns:
            List of similar Book objects (excluding the reference book)
        """
        reference_book = self._get_book_by_title(book_title)
        if not reference_book:
            logger.warning(f"Reference book not found: {book_title}")
            return []

        # Create query from book's themes and summary
        query = f"{reference_book.short_summary}. Teme: {', '.join(reference_book.themes)}"

        # Search for similar books
        similar_books = self.search_books(
            query, top_k + 1
        )  # +1 to account for the reference book

        # Remove the reference book from results
        return [book for book in similar_books if book.title != book_title][
            :top_k
        ]

    def create_context_string(
        self, books: List[Book], max_books: int = 3
    ) -> str:
        """
        Create a context string from search results for LLM.

        Args:
            books: List of Book objects
            max_books: Maximum number of books to include

        Returns:
            Formatted context string
        """
        if not books:
            return "Nu am găsit cărți relevante pentru această căutare."

        context_parts = ["Cărți relevante găsite:"]

        for i, book in enumerate(books[:max_books], 1):
            themes_str = ", ".join(book.themes)
            context_parts.append(
                f"{i}. **{book.title}** - {book.short_summary} (Teme: {themes_str})"
            )

        return "\n".join(context_parts)

    def get_retriever_stats(self) -> dict:
        """
        Get statistics about the retriever.

        Returns:
            Dictionary with statistics
        """
        self._load_books_cache()
        vector_stats = self.vector_store.get_collection_stats()

        return {
            "total_books_in_cache": (
                len(self._books_cache) if self._books_cache else 0
            ),
            "vector_store_stats": vector_stats,
        }


# Global retriever instance
_global_retriever = None


def get_retriever() -> BookRetriever:
    """
    Get the global retriever instance (singleton pattern).

    Returns:
        BookRetriever instance
    """
    global _global_retriever
    if _global_retriever is None:
        _global_retriever = BookRetriever()
    return _global_retriever


def search_books(query: str, top_k: int = 3) -> List[Book]:
    """
    Convenience function for book search.

    Args:
        query: Search query
        top_k: Number of results

    Returns:
        List of Book objects
    """
    retriever = get_retriever()
    return retriever.search_books(query, top_k)


if __name__ == "__main__":
    # Test retriever functionality
    try:
        retriever = BookRetriever()

        # Test queries
        test_queries = [
            "prietenie și magie",
            "povești de război",
            "libertate și control social",
            "aventură și curaj",
        ]

        for query in test_queries:
            print(f"\nQuery: '{query}'")
            books = retriever.search_books(query, top_k=2)
            for book in books:
                print(f"- {book.title}: {book.themes}")

        # Test context creation
        books = retriever.search_books("prietenie", top_k=3)
        context = retriever.create_context_string(books)
        print(f"\nContext string:\n{context}")

        # Test stats
        stats = retriever.get_retriever_stats()
        print(f"\nRetriever stats: {stats}")

    except Exception as e:
        print(f"Error: {e}")
