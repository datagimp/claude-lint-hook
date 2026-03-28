"""JavaScript/TypeScript linter using ESLint."""

from typing import List

from .base import Linter, LinterResult
from .registry import LinterRegistry
from ..utils.command import run_command, command_exists


@LinterRegistry.register
class JavaScriptLinter(Linter):
    """JavaScript/TypeScript linter using ESLint."""

    @property
    def extensions(self) -> List[str]:
        return [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]

    def is_available(self, cwd: str) -> bool:
        """Check if eslint is available."""
        return command_exists("eslint", cwd)

    def fix(self, file_path: str, cwd: str) -> LinterResult:
        """
        Fix JavaScript/TypeScript issues using ESLint.

        Runs: eslint --fix
        """
        success, stdout, stderr = run_command(
            ["eslint", "--fix", file_path],
            cwd=cwd,
            timeout=30,
        )

        return LinterResult(
            success=success or "fixed" in stdout.lower(),
            fixed=True,
            issues=[],
            error=None if success else stderr,
        )

    def check(self, file_path: str, cwd: str) -> LinterResult:
        """
        Check JavaScript/TypeScript file for remaining issues using ESLint.

        Returns list of issues found.
        """
        success, stdout, stderr = run_command(
            ["eslint", "--format", "json", file_path],
            cwd=cwd,
            timeout=30,
        )

        if not success or stdout:
            # ESLint returns non-zero when issues are found
            # Parse JSON output
            try:
                import json

                data = json.loads(stdout)
                if isinstance(data, list) and len(data) > 0:
                    file_data = data[0]
                    messages = file_data.get("messages", [])
                    if messages:
                        issues = []
                        for msg in messages:
                            line = msg.get("line", "?")
                            column = msg.get("column", 0)
                            rule_id = msg.get("ruleId", "unknown")
                            message = msg.get("message", "")
                            severity = msg.get("severity", 0)

                            severity_str = "Error" if severity == 2 else "Warning"
                            issues.append(
                                f"  {file_path}:{line}:{column}: {severity_str} [{rule_id}] {message}"
                            )

                        return LinterResult(
                            success=True,
                            fixed=False,
                            issues=issues,
                        )
            except (json.JSONDecodeError, KeyError):
                pass

            # Fallback: parse plain text output
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
