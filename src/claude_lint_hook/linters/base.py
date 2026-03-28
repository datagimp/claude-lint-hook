"""Base linter interface and result types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LinterResult:
    """Result of a linter operation."""

    success: bool  # Whether the command executed successfully
    fixed: bool  # Whether any fixes were applied
    issues: List[str]  # List of remaining issues (if any)
    error: Optional[str] = None  # Error message if command failed

    @property
    def has_issues(self) -> bool:
        """Return True if there are remaining issues."""
        return len(self.issues) > 0


class Linter(ABC):
    """Abstract base class for linters."""

    @property
    @abstractmethod
    def extensions(self) -> List[str]:
        """Return list of file extensions this linter handles (e.g., ['.py', '.pyx'])."""
        pass

    @abstractmethod
    def is_available(self, cwd: str) -> bool:
        """Check if this linter is available in the given directory."""
        pass

    @abstractmethod
    def fix(self, file_path: str, cwd: str) -> LinterResult:
        """
        Attempt to automatically fix issues in the file.

        Args:
            file_path: Path to the file to fix
            cwd: Current working directory

        Returns:
            LinterResult with success status and whether fixes were applied
        """
        pass

    @abstractmethod
    def check(self, file_path: str, cwd: str) -> LinterResult:
        """
        Check the file for remaining issues.

        Args:
            file_path: Path to the file to check
            cwd: Current working directory

        Returns:
            LinterResult with list of any remaining issues
        """
        pass

    def can_handle(self, file_path: str) -> bool:
        """Check if this linter can handle the given file."""
        import os
        ext = os.path.splitext(file_path)[1].lower()
        return ext in [e.lower() for e in self.extensions]
