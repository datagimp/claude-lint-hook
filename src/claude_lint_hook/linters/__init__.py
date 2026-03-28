"""Linter implementations for different file types."""

from .base import Linter, LinterResult
from .registry import LinterRegistry

# Import all linter implementations to trigger registration
from . import python_linter  # noqa: F401
from . import javascript_linter  # noqa: F401

__all__ = ["Linter", "LinterResult", "LinterRegistry"]
