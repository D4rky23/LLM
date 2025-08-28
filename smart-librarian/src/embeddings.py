"""OpenAI embeddings utilities for Smart Librarian."""

import logging
from typing import List

import openai
import tiktoken

from .config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = config.OPENAI_API_KEY


def get_embedding(text: str, model: str = None) -> List[float]:
    """
    Get embedding for a text using OpenAI API.

    Args:
        text: Text to embed
        model: Model to use (default from config)

    Returns:
        List of floats representing the embedding

    Raises:
        Exception: If API call fails
    """
    if model is None:
        model = config.OPENAI_EMBED_MODEL

    try:
        # Clean and prepare text
        text = text.replace("\n", " ").strip()
        if not text:
            raise ValueError("Text cannot be empty")

        # Make API call
        response = openai.embeddings.create(input=[text], model=model)

        return response.data[0].embedding

    except Exception as e:
        logger.error(f"Error getting embedding: {e}")
        raise


def get_embeddings_batch(
    texts: List[str], model: str = None
) -> List[List[float]]:
    """
    Get embeddings for multiple texts in batch.

    Args:
        texts: List of texts to embed
        model: Model to use (default from config)

    Returns:
        List of embeddings

    Raises:
        Exception: If API call fails
    """
    if model is None:
        model = config.OPENAI_EMBED_MODEL

    if not texts:
        return []

    try:
        # Clean texts
        cleaned_texts = []
        for text in texts:
            cleaned = text.replace("\n", " ").strip()
            if cleaned:
                cleaned_texts.append(cleaned)

        if not cleaned_texts:
            raise ValueError("No valid texts to embed")

        # Make API call
        response = openai.embeddings.create(input=cleaned_texts, model=model)

        return [data.embedding for data in response.data]

    except Exception as e:
        logger.error(f"Error getting batch embeddings: {e}")
        raise


def count_tokens(text: str, model: str = None) -> int:
    """
    Count tokens in text using tiktoken.

    Args:
        text: Text to count tokens for
        model: Model to use for tokenization

    Returns:
        Number of tokens
    """
    if model is None:
        model = config.OPENAI_EMBED_MODEL

    try:
        # Get encoding for the model
        if "ada" in model or "embedding" in model:
            encoding = tiktoken.get_encoding("cl100k_base")
        else:
            encoding = tiktoken.encoding_for_model(model)

        return len(encoding.encode(text))

    except Exception as e:
        logger.warning(f"Could not count tokens for model {model}: {e}")
        # Fallback to approximate count
        return len(text.split())


def prepare_text_for_embedding(
    title: str, summary: str, themes: List[str]
) -> str:
    """
    Prepare book data for embedding by concatenating relevant fields.

    Args:
        title: Book title
        summary: Book summary
        themes: List of themes

    Returns:
        Concatenated text ready for embedding
    """
    themes_str = ", ".join(themes) if themes else ""

    parts = []
    if title:
        parts.append(f"Titlu: {title}")
    if summary:
        parts.append(f"Rezumat: {summary}")
    if themes_str:
        parts.append(f"Teme: {themes_str}")

    return ". ".join(parts)


def validate_embedding_dimensions(
    embedding: List[float], expected_dim: int = 1536
) -> bool:
    """
    Validate embedding dimensions.

    Args:
        embedding: Embedding vector
        expected_dim: Expected dimensions (1536 for text-embedding-3-small)

    Returns:
        True if dimensions are correct
    """
    if not isinstance(embedding, list):
        return False

    if len(embedding) != expected_dim:
        logger.warning(
            f"Unexpected embedding dimension: {len(embedding)}, expected: {expected_dim}"
        )
        return False

    # Check if all values are numbers
    try:
        all(isinstance(x, (int, float)) for x in embedding)
        return True
    except:
        return False


if __name__ == "__main__":
    # Test embedding functionality
    test_text = "Această este o carte despre prietenie și magie."

    try:
        embedding = get_embedding(test_text)
        print(
            f"Embedding generated successfully. Dimensions: {len(embedding)}"
        )
        print(f"Token count: {count_tokens(test_text)}")
        print(f"Validation: {validate_embedding_dimensions(embedding)}")
    except Exception as e:
        print(f"Error: {e}")
