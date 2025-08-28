"""Embedding helpers (moved into vector package)."""

from typing import List
from core.config import config

import openai


def get_embedding(text: str) -> List[float]:
    openai.api_key = config.OPENAI_API_KEY
    resp = openai.Embedding.create(input=text, model=config.OPENAI_EMBED_MODEL)
    return resp["data"][0]["embedding"]


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    openai.api_key = config.OPENAI_API_KEY
    resp = openai.Embedding.create(
        input=texts, model=config.OPENAI_EMBED_MODEL
    )
    return [d["embedding"] for d in resp["data"]]
