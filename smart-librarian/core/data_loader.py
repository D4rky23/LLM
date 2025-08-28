"""Re-export core.data_loader from src.core.data_loader"""

from src.core.data_loader import *

__all__ = getattr(
    __import__("src.core.data_loader", fromlist=["__all__"]), "__all__", []
)
