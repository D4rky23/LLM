"""ChromaDB vector store implementation for Smart Librarian."""

import logging
from typing import List, Optional, Dict, Any
import uuid
import re

import chromadb
from chromadb.config import Settings

from .config import config
from .schema import Book
from .embeddings import get_embedding, prepare_text_for_embedding

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB-based vector store for book embeddings."""

    def __init__(
        self, persist_directory: str = None, collection_name: str = None
    ):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory or str(
            config.CHROMA_PERSIST_DIR
        )
        self.collection_name = collection_name or config.CHROMA_COLLECTION_NAME

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name
            )
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Book summaries and themes for Smart Librarian"
                },
            )
            logger.info(f"Created new collection: {self.collection_name}")

    def _generate_book_id(self, title: str) -> str:
        """
        Generate a unique ID for a book.

        Args:
            title: Book title

        Returns:
            Unique book ID
        """
        # Create a slug from the title
        slug = re.sub(r"[^a-zA-Z0-9\s]", "", title.lower())
        slug = re.sub(r"\s+", "-", slug.strip())
        return f"book:{slug}"

    def add_book(self, book: Book) -> bool:
        """
        Add a book to the vector store.

        Args:
            book: Book object to add

        Returns:
            True if successful
        """
        try:
            # Prepare text for embedding
            document_text = prepare_text_for_embedding(
                book.title, book.short_summary, book.themes
            )

            # Get embedding
            embedding = get_embedding(document_text)

            # Generate ID
            book_id = self._generate_book_id(book.title)

            # Prepare metadata
            metadata = {
                "title": book.title,
                "themes": book.themes,
                "source": "md",
                "summary_length": len(book.short_summary),
            }

            # Add to collection
            self.collection.add(
                documents=[document_text],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[book_id],
            )

            logger.info(f"Added book: {book.title}")
            return True

        except Exception as e:
            logger.error(f"Error adding book {book.title}: {e}")
            return False

    def add_books_batch(self, books: List[Book]) -> int:
        """
        Add multiple books to the vector store in batch.

        Args:
            books: List of Book objects

        Returns:
            Number of successfully added books
        """
        if not books:
            return 0

        documents = []
        embeddings = []
        metadatas = []
        ids = []

        successful_count = 0

        for book in books:
            try:
                # Prepare text for embedding
                document_text = prepare_text_for_embedding(
                    book.title, book.short_summary, book.themes
                )

                # Get embedding
                embedding = get_embedding(document_text)

                # Generate ID
                book_id = self._generate_book_id(book.title)

                # Prepare metadata
                metadata = {
                    "title": book.title,
                    "themes": book.themes,
                    "source": "md",
                    "summary_length": len(book.short_summary),
                }

                documents.append(document_text)
                embeddings.append(embedding)
                metadatas.append(metadata)
                ids.append(book_id)

                successful_count += 1

            except Exception as e:
                logger.error(f"Error preparing book {book.title}: {e}")
                continue

        if documents:
            try:
                self.collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids,
                )
                logger.info(f"Added {successful_count} books to vector store")
            except Exception as e:
                logger.error(f"Error adding batch to collection: {e}")
                return 0

        return successful_count

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for books similar to the query.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of search results with metadata
        """
        try:
            # Get query embedding
            query_embedding = get_embedding(query)

            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )

            # Format results
            formatted_results = []

            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    result = {
                        "title": results["metadatas"][0][i]["title"],
                        "themes": results["metadatas"][0][i]["themes"],
                        "document": results["documents"][0][i],
                        "distance": results["distances"][0][i],
                        "score": 1
                        - results["distances"][0][
                            i
                        ],  # Convert distance to similarity score
                    }
                    formatted_results.append(result)

            logger.info(
                f"Found {len(formatted_results)} results for query: {query}"
            )
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []

    def get_book_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific book by exact title match.

        Args:
            title: Exact book title

        Returns:
            Book data if found, None otherwise
        """
        try:
            book_id = self._generate_book_id(title)
            results = self.collection.get(
                ids=[book_id], include=["documents", "metadatas"]
            )

            if results["documents"]:
                return {
                    "title": results["metadatas"][0]["title"],
                    "themes": results["metadatas"][0]["themes"],
                    "document": results["documents"][0],
                }

            return None

        except Exception as e:
            logger.error(f"Error getting book by title {title}: {e}")
            return None

    def clear_collection(self) -> bool:
        """
        Clear all data from the collection.

        Returns:
            True if successful
        """
        try:
            # Delete the collection
            self.client.delete_collection(name=self.collection_name)

            # Recreate it
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Book summaries and themes for Smart Librarian"
                },
            )

            logger.info(f"Cleared collection: {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.

        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_books": count,
                "persist_directory": self.persist_directory,
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}


def initialize_vector_store(
    books: List[Book] = None, force_rebuild: bool = False
) -> VectorStore:
    """
    Initialize vector store with book data.

    Args:
        books: List of books to add (if None, loads from data files)
        force_rebuild: Whether to clear existing data and rebuild

    Returns:
        Initialized VectorStore instance
    """
    vector_store = VectorStore()

    # Check if we need to add data
    stats = vector_store.get_collection_stats()
    needs_data = stats.get("total_books", 0) == 0 or force_rebuild

    if needs_data:
        if force_rebuild:
            logger.info("Force rebuilding vector store...")
            vector_store.clear_collection()

        if books is None:
            from .data_loader import load_books_data

            books, _ = load_books_data()

        if books:
            added_count = vector_store.add_books_batch(books)
            logger.info(f"Initialized vector store with {added_count} books")
    else:
        logger.info(
            f"Vector store already initialized with {stats['total_books']} books"
        )

    return vector_store


if __name__ == "__main__":
    # Test vector store functionality
    try:
        from .data_loader import load_books_data

        # Load test data
        books, _ = load_books_data()

        # Initialize vector store
        vs = initialize_vector_store(
            books[:3], force_rebuild=True
        )  # Test with first 3 books

        # Test search
        results = vs.search("prietenie și magie", top_k=2)
        print(f"Search results: {len(results)}")
        for result in results:
            print(f"- {result['title']}: {result['score']:.3f}")

        # Test stats
        stats = vs.get_collection_stats()
        print(f"Collection stats: {stats}")

    except Exception as e:
        print(f"Error: {e}")
