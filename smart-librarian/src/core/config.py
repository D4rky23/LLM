"""Configuration management for Smart Librarian (moved into core package)."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Smart Librarian application."""

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBED_MODEL: str = os.getenv(
        "OPENAI_EMBED_MODEL", "text-embedding-3-small"
    )

    # ChromaDB Configuration
    CHROMA_PERSIST_DIR: Path = Path(os.getenv("CHROMA_PERSIST_DIR", ".chroma"))
    CHROMA_COLLECTION_NAME: str = "book_summaries"

    # Data Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    BOOK_SUMMARIES_MD: Path = DATA_DIR / "book_summaries.md"
    BOOK_SUMMARIES_JSON: Path = DATA_DIR / "book_summaries.json"
    OUTPUT_DIR: Path = PROJECT_ROOT / "output"

    # Application Settings
    DEFAULT_TOP_K: int = 3
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7

    # Safety Settings
    OFFENSIVE_WORDS: list[str] = [
        "obscenități",
        "injurii",
        "blasfemii",
        "vulgară",
        "agresiv",
        "violent",
        "hate",
        "racist",
        "sexist",
    ]

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")

        if not cls.BOOK_SUMMARIES_MD.exists():
            raise FileNotFoundError(
                f"Book summaries file not found: {cls.BOOK_SUMMARIES_MD}"
            )

        if not cls.BOOK_SUMMARIES_JSON.exists():
            raise FileNotFoundError(
                f"Book summaries JSON not found: {cls.BOOK_SUMMARIES_JSON}"
            )

        # Create output directory if it doesn't exist
        cls.OUTPUT_DIR.mkdir(exist_ok=True)

        return True


# Global configuration instance
config = Config()
