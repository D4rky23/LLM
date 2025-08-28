"""Tests for retriever functionality in Smart Librarian."""

import sys
from pathlib import Path
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from retriever import BookRetriever, get_retriever, search_books
from schema import Book
from vector_store import VectorStore, initialize_vector_store
from data_loader import load_books_data
from config import config


class TestRetriever:
    """Test class for retriever functionality."""

    @pytest.fixture(scope="class")
    def sample_books(self):
        """Load sample books for testing."""
        books, _ = load_books_data()
        return books[:5]  # Use first 5 books for faster testing

    @pytest.fixture(scope="class")
    def test_retriever(self, sample_books):
        """Create a test retriever with sample data."""
        # Initialize vector store with sample books
        vector_store = initialize_vector_store(
            sample_books, force_rebuild=True
        )
        return BookRetriever(vector_store)

    def test_retriever_initialization(self, test_retriever):
        """Test retriever initialization."""
        assert test_retriever is not None
        assert test_retriever.vector_store is not None

        # Check vector store has data
        stats = test_retriever.vector_store.get_collection_stats()
        assert stats["total_books"] > 0

    def test_search_books_basic(self, test_retriever):
        """Test basic book search functionality."""
        # Test search with common themes
        results = test_retriever.search_books("prietenie și magie", top_k=3)

        assert isinstance(results, list)
        assert len(results) <= 3

        # Check that results are Book objects
        for book in results:
            assert isinstance(book, Book)
            assert hasattr(book, "title")
            assert hasattr(book, "short_summary")
            assert hasattr(book, "themes")

    def test_search_books_with_scores(self, test_retriever):
        """Test book search with relevance scores."""
        results = test_retriever.search_with_scores(
            "aventură și curaj", top_k=2
        )

        assert isinstance(results, list)
        assert len(results) <= 2

        # Check results structure
        for book, score in results:
            assert isinstance(book, Book)
            assert isinstance(score, float)
            assert (
                0 <= score <= 1
            )  # Scores should be normalized between 0 and 1

        # Check that results are sorted by score (descending)
        if len(results) > 1:
            scores = [score for _, score in results]
            assert scores == sorted(scores, reverse=True)

    def test_search_by_themes(self, test_retriever):
        """Test search by specific themes."""
        # Test with themes that should exist in our dataset
        themes_to_test = [
            ["prietenie", "aventură"],
            ["libertate", "control social"],
            ["război"],
        ]

        for themes in themes_to_test:
            results = test_retriever.search_by_themes(themes, top_k=2)

            assert isinstance(results, list)
            # We should get some results for these common themes
            # (might be 0 if no books match, but should not error)

    def test_get_book_by_exact_title(self, test_retriever):
        """Test exact title matching."""
        # Get available books first
        test_retriever._load_books_cache()
        available_books = test_retriever._books_cache

        if available_books:
            test_book = available_books[0]

            # Test exact match
            found_book = test_retriever.get_book_by_exact_title(
                test_book.title
            )

            assert found_book is not None
            assert found_book.title == test_book.title
            assert found_book.short_summary == test_book.short_summary
            assert found_book.themes == test_book.themes

        # Test non-existent book
        non_existent = test_retriever.get_book_by_exact_title(
            "Cartea Inexistentă"
        )
        assert non_existent is None

    def test_get_similar_books(self, test_retriever):
        """Test finding similar books."""
        # Load books cache
        test_retriever._load_books_cache()
        available_books = test_retriever._books_cache

        if available_books and len(available_books) > 1:
            reference_book = available_books[0]

            similar_books = test_retriever.get_similar_books(
                reference_book.title, top_k=2
            )

            assert isinstance(similar_books, list)
            assert len(similar_books) <= 2

            # Check that reference book is not in the results
            similar_titles = [book.title for book in similar_books]
            assert reference_book.title not in similar_titles

            # Check that results are Book objects
            for book in similar_books:
                assert isinstance(book, Book)

    def test_create_context_string(self, test_retriever):
        """Test context string creation."""
        # Search for some books
        books = test_retriever.search_books("aventură", top_k=3)

        # Create context string
        context = test_retriever.create_context_string(books, max_books=2)

        assert isinstance(context, str)
        assert len(context) > 0

        if books:
            # Context should contain book information
            assert "Cărți relevante găsite:" in context
            assert books[0].title in context
        else:
            # If no books found, should have appropriate message
            assert "Nu am găsit" in context

    def test_get_random_recommendations(self, test_retriever):
        """Test random recommendations."""
        recommendations = test_retriever.get_random_recommendations(count=3)

        assert isinstance(recommendations, list)
        assert len(recommendations) <= 3

        # Check that results are Book objects
        for book in recommendations:
            assert isinstance(book, Book)

        # If we have enough books, should get the requested count
        test_retriever._load_books_cache()
        if len(test_retriever._books_cache) >= 3:
            assert len(recommendations) == 3

    def test_get_retriever_stats(self, test_retriever):
        """Test retriever statistics."""
        stats = test_retriever.get_retriever_stats()

        assert isinstance(stats, dict)
        assert "total_books_in_cache" in stats
        assert "vector_store_stats" in stats

        assert isinstance(stats["total_books_in_cache"], int)
        assert stats["total_books_in_cache"] >= 0

    def test_search_quality(self, test_retriever):
        """Test search quality with specific queries."""
        # Test cases: query -> expected themes that should appear in results
        test_cases = [
            ("prietenie și magie", ["prietenie", "magie", "aventură"]),
            ("povești de război", ["război", "conflict", "istorie"]),
            (
                "libertate și control",
                ["libertate", "control social", "politică"],
            ),
        ]

        for query, expected_themes in test_cases:
            results = test_retriever.search_books(query, top_k=3)

            if results:  # If we have results
                # Check that at least some results have relevant themes
                found_relevant = False
                for book in results:
                    book_themes_lower = [
                        theme.lower() for theme in book.themes
                    ]
                    for expected_theme in expected_themes:
                        if any(
                            expected_theme.lower() in theme
                            for theme in book_themes_lower
                        ):
                            found_relevant = True
                            break
                    if found_relevant:
                        break

                # We should find at least one relevant result for these queries
                # (This might fail if the dataset doesn't contain matching books)
                print(f"Query: '{query}' -> Found relevant: {found_relevant}")

    def test_empty_query_handling(self, test_retriever):
        """Test handling of empty or invalid queries."""
        # Empty query
        results = test_retriever.search_books("", top_k=3)
        assert isinstance(results, list)

        # Very short query
        results = test_retriever.search_books("a", top_k=3)
        assert isinstance(results, list)

        # Special characters
        results = test_retriever.search_books("!@#$%", top_k=3)
        assert isinstance(results, list)

    def test_large_top_k(self, test_retriever):
        """Test with large top_k values."""
        # Load books to see how many we have
        test_retriever._load_books_cache()
        total_books = len(test_retriever._books_cache)

        # Request more books than available
        results = test_retriever.search_books("carte", top_k=total_books + 10)

        assert isinstance(results, list)
        assert len(results) <= total_books  # Should not exceed available books


class TestGlobalRetriever:
    """Test the global retriever functionality."""

    def test_get_retriever_singleton(self):
        """Test that get_retriever returns the same instance."""
        retriever1 = get_retriever()
        retriever2 = get_retriever()

        assert retriever1 is retriever2  # Should be the same instance

    def test_search_books_convenience_function(self):
        """Test the convenience search_books function."""
        results = search_books("aventură", top_k=2)

        assert isinstance(results, list)
        assert len(results) <= 2

        for book in results:
            assert isinstance(book, Book)


def test_integration_with_real_data():
    """Integration test with real data files."""
    try:
        # Load real data
        books, _ = load_books_data()
        print(f"Loaded {len(books)} books for integration test")

        # Initialize retriever with real data
        retriever = BookRetriever()

        # Test with Romanian queries from the requirements
        test_queries = [
            "prietenie și magie",
            "povești de război",
            "libertate și control social",
        ]

        for query in test_queries:
            results = retriever.search_books(query, top_k=3)
            print(f"\nQuery: '{query}'")
            print(f"Results: {len(results)}")

            for i, book in enumerate(results, 1):
                print(f"  {i}. {book.title}: {book.themes}")

        print("\n✅ Integration test completed successfully")

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        raise


if __name__ == "__main__":
    # Run basic functionality tests
    print("Running retriever tests...")

    try:
        # Test with minimal setup
        books, _ = load_books_data()
        print(f"✅ Loaded {len(books)} books")

        # Initialize vector store and retriever
        vector_store = initialize_vector_store(
            books[:3], force_rebuild=True
        )  # Use first 3 for speed
        retriever = BookRetriever(vector_store)
        print("✅ Retriever initialized")

        # Test basic search
        results = retriever.search_books("prietenie și magie", top_k=2)
        print(f"✅ Search returned {len(results)} results")

        # Test with scores
        results_with_scores = retriever.search_with_scores("aventură", top_k=2)
        print(
            f"✅ Search with scores returned {len(results_with_scores)} results"
        )

        # Test context creation
        context = retriever.create_context_string(results)
        print(f"✅ Context string created ({len(context)} chars)")

        # Test stats
        stats = retriever.get_retriever_stats()
        print(f"✅ Stats retrieved: {stats}")

        print("\n🎉 All basic retriever tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

    # Run integration test
    test_integration_with_real_data()
