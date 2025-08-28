"""LLM integration for Smart Librarian (moved into ai package)."""

from typing import List
import openai

from core.config import config
from core.schema import ChatMessage
from ai.tools import get_summary_by_title


class SmartLibrarian:
    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY

    def chat(self, user_input: str) -> str:
        # Simple chat implementation using OpenAI ChatCompletion
        messages = [
            {
                "role": "system",
                "content": "Ești un asistent prietenos care recomandă cărți în limba română.",
            },
            {"role": "user", "content": user_input},
        ]

        resp = openai.ChatCompletion.create(
            model=config.OPENAI_MODEL,
            messages=messages,
            temperature=config.TEMPERATURE,
        )
        assistant_content = resp["choices"][0]["message"]["content"]

        # If assistant asks to call a tool to get a summary, we emulate that flow
        if "CALL_TOOL:get_summary_by_title" in assistant_content:
            # parse title after marker
            parts = assistant_content.split("CALL_TOOL:get_summary_by_title:")
            if len(parts) > 1:
                title = parts[1].strip()
                summary = get_summary_by_title(title)
                return f"Recomandare: {title}\n\n{summary}"

        return assistant_content


_global_chatbot = None


def get_chatbot() -> SmartLibrarian:
    global _global_chatbot
    if _global_chatbot is None:
        _global_chatbot = SmartLibrarian()
    return _global_chatbot
