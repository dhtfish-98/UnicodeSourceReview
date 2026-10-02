"""Evidence about selected physical Unicode characters, never source execution."""
__version__ = "1.0.1"

from .analysis import Limits, review_bytes
from .input import read_regular_file

__all__ = ["Limits", "review_bytes", "read_regular_file"]
