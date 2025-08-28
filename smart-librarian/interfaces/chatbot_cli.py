"""Re-export interfaces.chatbot_cli from src.interfaces.chatbot_cli"""

from src.interfaces.chatbot_cli import *

__all__ = getattr(
    __import__("src.interfaces.chatbot_cli", fromlist=["__all__"]),
    "__all__",
    [],
)
