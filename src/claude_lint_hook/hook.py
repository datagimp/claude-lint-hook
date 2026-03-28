"""Core hook logic for handling file changes."""

import json
import sys
from typing import Dict, Any

from .linters import LinterRegistry


def handle_file(file_path: str, cwd: str) -> Dict[str, Any]:
    """
    Handle a file change by running the appropriate linter.

    Args:
        file_path: Path to the file that was changed
        cwd: Current working directory

    Returns:
        Dictionary with "decision" key ("allow" or "block")
        If blocking, includes "reason" key
    """
    # Get the appropriate linter for this file
    linter = LinterRegistry.get_linter(file_path)

    # No linter available for this file type - allow
    if linter is None:
        return {"decision": "allow"}

    # Check if linter is available
    if not linter.is_available(cwd):
        # Linter not installed - allow with a warning
        import sys

        print(
            f"Warning: {linter.__class__.__name__} is not installed. "
            f"Install it to enable automatic linting.",
            file=sys.stderr,
        )
        return {"decision": "allow"}

    # Run the fix → check workflow
    # Step 1: Attempt to fix issues
    fix_result = linter.fix(file_path, cwd)

    # If fix failed catastrophically (command not found, etc), allow with warning
    if not fix_result.success and fix_result.error and "command not found" in fix_result.error.lower():
        import sys
        print(f"Warning: Linter not available: {fix_result.error}", file=sys.stderr)
        return {"decision": "allow"}

    # Step 2: Check for remaining issues (even if fix had warnings)
    check_result = linter.check(file_path, cwd)

    if check_result.has_issues:
        # Issues remain - block completion
        linter_name = linter.__class__.__name__
        issue_count = len(check_result.issues)
        issues_text = "\n".join(check_result.issues[:10])  # Limit to first 10 issues

        if issue_count > 10:
            issues_text += f"\n  ... and {issue_count - 10} more"

        return {
            "decision": "block",
            "reason": f"{linter_name} found {issue_count} issue(s):\n{issues_text}",
        }

    # No issues - allow completion
    return {"decision": "allow"}


def main():
    """Entry point when run as a module."""
    if len(sys.argv) < 2:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    file_path = sys.argv[1]
    cwd = sys.argv[2] if len(sys.argv) > 2 else "."

    try:
        result = handle_file(file_path, cwd)
        print(json.dumps(result))
    except Exception as e:
        # On any error, allow the operation
        import traceback

        print(f"Error in linting hook: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"decision": "allow"}))

    sys.exit(0)


if __name__ == "__main__":
    main()
