"""Pydantic models for Smart Librarian."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Book(BaseModel):
    """Book model with title, summary, and themes."""

    title: str = Field(..., description="Book title")
    short_summary: str = Field(
        ..., description="Short book summary (3-5 lines)"
    )
    themes: List[str] = Field(..., description="List of book themes")
    detailed_summary: Optional[str] = Field(
        None, description="Detailed book summary"
    )

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True


class Query(BaseModel):
    """User query model."""

    text: str = Field(..., description="User query text")
    top_k: int = Field(
        default=3, description="Number of top results to return"
    )

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True


class Recommendation(BaseModel):
    """Book recommendation model."""

    book: Book = Field(..., description="Recommended book")
    score: float = Field(..., description="Relevance score")
    reason: str = Field(..., description="Reason for recommendation")

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str = Field(
        ..., description="Message role (user, assistant, system)"
    )
    content: str = Field(..., description="Message content")

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True


class ToolCall(BaseModel):
    """Tool call model for OpenAI function calling."""

    name: str = Field(..., description="Tool name")
    arguments: dict = Field(..., description="Tool arguments")

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True


class SearchResult(BaseModel):
    """Search result model."""

    books: List[Book] = Field(..., description="List of found books")
    query: str = Field(..., description="Original search query")
    total_results: int = Field(..., description="Total number of results")

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True
