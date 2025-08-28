"""Re-export core.config from src.core.config"""

from src.core.config import *

__all__ = getattr(
    __import__("src.core.config", fromlist=["__all__"]), "__all__", []
)
