"""Top-level interfaces package wrapper that re-exports src.interfaces."""

from src.interfaces.chatbot_cli import app as cli_app

__all__ = ["cli_app"]
