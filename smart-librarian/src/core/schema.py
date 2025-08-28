"""Pydantic models for Smart Librarian (moved into core package)."""

from pydantic import BaseModel
from typing import List, Optional


class Book(BaseModel):
    title: str
    author: Optional[str]
    short_summary: str
    detailed_summary: Optional[str]
    themes: List[str]


class Query(BaseModel):
    text: str
    top_k: int = 3


class Recommendation(BaseModel):
    title: str
    reason: Optional[str]


class ChatMessage(BaseModel):
    role: str
    content: str


class ToolCall(BaseModel):
    name: str
    arguments: dict


class SearchResult(BaseModel):
    id: str
    title: str
    score: float
