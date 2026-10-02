"""Evidence about selected physical Unicode characters, never source execution."""
from .analysis import Limits, review_bytes
from .input import read_regular_file

__all__ = ["Limits", "review_bytes", "read_regular_file"]
