"""Python linter using Ruff."""

from typing import List

from .base import Linter, LinterResult
from .registry import LinterRegistry
from ..utils.command import run_command, command_exists


@LinterRegistry.register
class PythonLinter(Linter):
    """Python linter using Ruff for linting and formatting."""

    @property
    def extensions(self) -> List[str]:
        return [".py", ".pyx", ".pyi"]

    def is_available(self, cwd: str) -> bool:
        """Check if ruff is available."""
        return command_exists("ruff", cwd)

    def fix(self, file_path: str, cwd: str) -> LinterResult:
        """
        Fix Python issues using Ruff.

        Runs both:
        1. ruff check --fix (lint fixes)
        2. ruff format (code formatting)
        """
        # First run ruff check --fix
        success_check, stdout_check, stderr_check = run_command(
            ["ruff", "check", "--fix", file_path],
            cwd=cwd,
            timeout=30,
        )

        # Then run ruff format
        success_format, stdout_format, stderr_format = run_command(
            ["ruff", "format", file_path],
            cwd=cwd,
            timeout=30,
        )

        # Consider it successful if at least one command worked
        success = success_check or success_format

        return LinterResult(
            success=success,
            fixed=True,  # Assume fixes were applied if command succeeded
            issues=[],
            error=None if success else (stderr_check or stderr_format),
        )

    def check(self, file_path: str, cwd: str) -> LinterResult:
        """
        Check Python file for remaining issues using Ruff.

        Returns list of issues found.
        """
        success, stdout, stderr = run_command(
            ["ruff", "check", "--output-format", "json", file_path],
            cwd=cwd,
            timeout=30,
        )

        if not success:
            # Ruff returns non-zero when issues are found
            # Parse JSON output to get issues
            if stdout:
                try:
                    import json

                    data = json.loads(stdout)
                    if isinstance(data, list):
                        issues = []
                        for error in data:
                            msg = error.get("message", "")
                            location = error.get("location", {})
                            row = location.get("row", "?")
                            col = location.get("column", 0)
                            code = error.get("code", "???")
                            issues.append(f"  {file_path}:{row}:{col}: {code} {msg}")

                        return LinterResult(
                            success=True,  # Successfully checked
                            fixed=False,
                            issues=issues,
                        )
                except (json.JSONDecodeError, KeyError):
                    pass

            # Fallback: just return the raw output
            issues = [line for line in stdout.split("\n") if line.strip()]
            if not issues and stderr:
                issues = [line for line in stderr.split("\n") if line.strip()]

            return LinterResult(
                success=True,
                fixed=False,
                issues=issues if issues else ["Unknown linting issue"],
            )

        # No issues found
        return LinterResult(
            success=True,
            fixed=False,
            issues=[],
        )
