"""CLI commands for claude-lint-hook."""

import os
import sys
from pathlib import Path

from .linters import LinterRegistry
from .utils.jsonio import read_json, write_json


def cmd_init(args: list[str]) -> int:
    """Initialize the linting hook in the current directory.

    Creates or updates .claude/settings.json with the PostToolUse hook configuration.
    """
    cwd = os.getcwd()
    claude_dir = Path(cwd) / ".claude"
    settings_file = claude_dir / "settings.json"

    # Create .claude directory if it doesn't exist
    claude_dir.mkdir(exist_ok=True)

    # Read existing settings
    existing_settings = read_json(str(settings_file))

    # Prepare the hook configuration
    hook_config = {
        "matcher": "tool_name in ['Write', 'Edit', 'MultiEdit']",
        "hooks": [
            {
                "type": "command",
                "command": "~/.local/bin/claude-lint-hook",
                "timeout": 30,
            }
        ],
    }

    # Merge with existing settings
    if "hooks" not in existing_settings:
        existing_settings["hooks"] = {}

    if "PostToolUse" not in existing_settings["hooks"]:
        existing_settings["hooks"]["PostToolUse"] = []

    # Check if the hook is already installed
    post_hooks = existing_settings["hooks"]["PostToolUse"]
    already_installed = False

    for hook_entry in post_hooks:
        if isinstance(hook_entry, dict):
            hooks = hook_entry.get("hooks", [])
            for hook in hooks:
                if hook.get("command") == "~/.local/bin/claude-lint-hook":
                    already_installed = True
                    break

    if not already_installed:
        post_hooks.append(hook_config)
        print("✓ Added PostToolUse hook to .claude/settings.json")
    else:
        print("✓ PostToolUse hook already configured")

    # Write the settings
    write_json(str(settings_file), existing_settings)

    # Detect project type and show info
    project_type = detect_project_type(cwd)
    print(f"\nDetected project: {project_type}")

    # Show available linters
    print("\nAvailable linters:")
    for linter in LinterRegistry.get_all_linters():
        exts = ", ".join(linter.extensions)
        available = "✓" if linter.is_available(cwd) else "✗"
        print(f"  {available} {linter.__class__.__name__}: {exts}")

    print("\n✓ Linting hook initialized successfully")
    print(f"  Configuration written to: {settings_file}")
    return 0


def cmd_hook(args: list[str]) -> int:
    """
    Run the hook logic on a file.

    This is the entry point called by the shell script when Claude Code triggers the hook.
    It reads JSON input from stdin and outputs the decision JSON.
    """
    import json
    import sys
    from .hook import handle_file

    # Read JSON input from stdin
    try:
        import sys
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        # Invalid or no input - allow
        print(json.dumps({"decision": "allow"}))
        return 0

    # Extract file_path from the input
    file_path = input_data.get("file_path") or input_data.get("tool_input", {}).get("file_path")

    if not file_path:
        print(json.dumps({"decision": "allow"}))
        return 0

    cwd = os.getcwd()

    try:
        result = handle_file(file_path, cwd)
        print(json.dumps(result))
        return 0
    except Exception as e:
        import traceback
        print(f"Error in linting hook: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"decision": "allow"}))
        return 0


def cmd_status(args: list[str]) -> int:
    """Show the status of available linters."""
    cwd = os.getcwd()

    print("Claude Lint Hook Status")
    print("=" * 50)

    print("\nSupported file extensions:")
    all_extensions = sorted(set(LinterRegistry.get_all_extensions()))
    for ext in all_extensions:
        linter = LinterRegistry.get_linter(f"test{ext}")
        if linter:
            status = "✓ Installed" if linter.is_available(cwd) else "✗ Not installed"
            print(f"  {ext}: {linter.__class__.__name__} ({status})")

    print("\nProject configuration:")
    settings_file = Path(cwd) / ".claude" / "settings.json"
    if settings_file.exists():
        settings = read_json(str(settings_file))
        hooks = settings.get("hooks", {}).get("PostToolUse", [])
        configured = any(
            h.get("hooks", [{}])[0].get("command") == "~/.local/bin/claude-lint-hook"
            for h in hooks
            if isinstance(h, dict)
        )
        if configured:
            print(f"  ✓ Hook configured in .claude/settings.json")
        else:
            print(f"  ✗ Hook not configured (run 'claude-lint-hook init')")
    else:
        print(f"  ✗ No .claude/settings.json found (run 'claude-lint-hook init')")

    return 0


def detect_project_type(cwd: str) -> str:
    """Detect the type of project in the current directory."""
    path = Path(cwd)

    # Check for Python project
    if (path / "pyproject.toml").exists() or (path / "setup.py").exists() or (path / "requirements.txt").exists():
        return "Python"

    # Check for Node.js/TypeScript project
    if (path / "package.json").exists():
        return "Node.js/TypeScript"

    # Check for Go project
    if (path / "go.mod").exists():
        return "Go"

    # Check for Rust project
    if (path / "Cargo.toml").exists():
        return "Rust"

    return "Unknown"


def print_usage() -> None:
    """Print usage information."""
    print("Usage: claude-lint-hook <command>")
    print("")
    print("Commands:")
    print("  init    Initialize the linting hook in the current directory")
    print("  status  Show the status of available linters")
    print("  hook    Run the hook on a file (internal use)")
    print("  help    Show this help message")


def main() -> int:
    """Main CLI entry point."""

    # Auto-detect hook mode: if called with no args and stdin has JSON input
    # This happens when Claude Code calls the command directly
    if len(sys.argv) < 2 and not sys.stdin.isatty():
        # Try to read and parse stdin as JSON
        try:
            import json
            content = sys.stdin.read()
            if content.strip().startswith('{'):
                # Restore stdin for cmd_hook
                import io
                sys.stdin = io.StringIO(content)
                return cmd_hook([])
        except Exception:
            pass

    if len(sys.argv) < 2:
        print_usage()
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "init":
        return cmd_init(args)
    elif command == "status":
        return cmd_status(args)
    elif command == "hook":
        return cmd_hook(args)
    elif command == "help":
        print_usage()
        return 0
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print_usage()
        return 1
