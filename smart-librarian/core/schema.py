"""Re-export core.schema from src.core.schema"""

from src.core.schema import *

__all__ = getattr(
    __import__("src.core.schema", fromlist=["__all__"]), "__all__", []
)
