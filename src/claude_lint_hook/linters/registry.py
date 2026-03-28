"""Linter registry for extension-based dispatch."""

import os
from typing import Dict, List, Optional, Type

from .base import Linter


class LinterRegistry:
    """Registry for mapping file extensions to linter implementations."""

    _extensions: Dict[str, Type[Linter]] = {}
    _linters: List[Type[Linter]] = []

    @classmethod
    def register(cls, linter_class: Type[Linter]) -> Type[Linter]:
        """
        Decorator to register a linter class.

        Usage:
            @LinterRegistry.register
            class PythonLinter(Linter):
                extensions = ['.py']
                ...
        """
        cls._linters.append(linter_class)

        # Create a temporary instance to get extensions
        # We'll instantiate later when needed
        return linter_class

    @classmethod
    def _register_extensions(cls, linter: Linter) -> None:
        """Register extensions for a linter instance."""
        for ext in linter.extensions:
            cls._extensions[ext.lower()] = type(linter)

    @classmethod
    def get_linter(cls, file_path: str) -> Optional[Linter]:
        """
        Get a linter instance for the given file path.

        Args:
            file_path: Path to the file

        Returns:
            Linter instance or None if no linter is registered
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext not in cls._extensions:
            # Initialize registry if empty
            for linter_class in cls._linters:
                linter_instance = linter_class()
                for linter_ext in linter_instance.extensions:
                    cls._extensions[linter_ext.lower()] = linter_class

        if ext not in cls._extensions:
            return None

        linter_class = cls._extensions[ext]
        return linter_class()

    @classmethod
    def get_all_extensions(cls) -> List[str]:
        """Get list of all registered extensions."""
        # Initialize extensions if not already done
        if not cls._extensions and cls._linters:
            for linter_class in cls._linters:
                linter_instance = linter_class()
                for linter_ext in linter_instance.extensions:
                    cls._extensions[linter_ext.lower()] = linter_class
        return sorted(set(cls._extensions.keys()))

    @classmethod
    def get_all_linters(cls) -> List[Linter]:
        """Get instances of all registered linters."""
        return [linter_class() for linter_class in cls._linters]
