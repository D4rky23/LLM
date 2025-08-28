"""Vector store backed by ChromaDB (moved into vector package)."""

from typing import List, Optional
from chromadb.config import Settings
from chromadb import PersistentClient

from core.config import config
from core.schema import Book
from vector.embeddings import get_embedding


class VectorStore:
    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_directory = persist_directory or str(
            config.CHROMA_PERSIST_DIR
        )
        # ChromaDB persistent client
        self.client = PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            config.CHROMA_COLLECTION_NAME
        )

    def _generate_book_id(self, book: Book) -> str:
        return book.title.replace(" ", "_").lower()

    def add_book(self, book: Book):
        embedding = get_embedding(book.short_summary)
        _id = self._generate_book_id(book)
        self.collection.add(
            ids=[_id],
            metadatas=[{"title": book.title}],
            embeddings=[embedding],
        )

    def add_books_batch(self, books: List[Book]):
        ids = [self._generate_book_id(b) for b in books]
        embeddings = [get_embedding(b.short_summary) for b in books]
        metadatas = [{"title": b.title} for b in books]
        self.collection.add(
            ids=ids, metadatas=metadatas, embeddings=embeddings
        )

    def search(self, query: str, top_k: int = 3) -> List[dict]:
        embedding = get_embedding(query)
        results = self.collection.query(
            embedding=embedding,
            n_results=top_k,
            include=["metadatas", "distances"],
        )

        # normalize results
        hits = []
        for ids, metas, dists in zip(
            results["ids"], results["metadatas"], results["distances"]
        ):
            for id_, meta, dist in zip(ids, metas, dists):
                hits.append(
                    {
                        "id": id_,
                        "title": meta.get("title"),
                        "score": float(dist),
                    }
                )

        return hits

    def get_book_by_title(self, title: str) -> Optional[Book]:
        # This vector store doesn't store full books; lookups should be done via retriever cache
        return None

    def clear_collection(self):
        self.collection.delete()

    def get_collection_stats(self) -> dict:
        # Basic stats
        count = len(self.collection.get(include=["ids"])["ids"])
        return {
            "total_books": count,
            "persist_directory": self.persist_directory,
        }


def initialize_vector_store(
    books: List[Book] = None, force_rebuild: bool = False
) -> VectorStore:
    vs = VectorStore()
    if force_rebuild:
        vs.clear_collection()

    if books:
        vs.add_books_batch(books)

    return vs
