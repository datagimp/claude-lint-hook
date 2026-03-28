# Claude Lint Hook

A **globally installable linting hook system** for Claude Code that automatically fixes code and blocks completion until issues are resolved.

## Quick Start

```bash
# Install and initialize in one command
cd /path/to/claude-lint-hook
./install.sh --init

# Or in any existing project
cd /path/to/your-project
claude-lint-hook init
```

That's it! Now edit files with Claude Code and the hook will automatically fix linting issues.

## Features

- **Zero-config setup** - Initialize any project with a single command
- **Multi-language support** - Python (Ruff), JavaScript/TypeScript (ESLint), and extensible for more
- **Automatic fixing** - Runs linters with auto-fix before checking for remaining issues
- **Blocks on problems** - Uses Claude Code's iterative resolution loop to ensure clean code
- **Graceful degradation** - Allows operations if linters aren't installed

## Prerequisites

- **uv** - Python package installer ([install](https://github.com/astral-sh/uv))
- **jq** - JSON processor (install via `brew install jq` on macOS)
- **Python 3.10+** - Required runtime

Optional linters (install these in your projects):
- **ruff** - Python linter/formatter (`uv tool install ruff`)
- **eslint** - JavaScript/TypeScript linter (`npm install -D eslint`)

## Installation

### Quick Install (Recommended)

Run the automated installer:

```bash
cd /path/to/claude-lint-hook
./install.sh --init
```

This will:
- Install the `claude-lint-hook` tool
- Initialize the hook in your current directory
- Prompt to install recommended linters (ruff, eslint)

**Installer options:**
- `--global` - Install to global uv (default: local editable)
- `--init` - Initialize hook in current directory after install
- `--skip-linters` - Skip installing linters
- `--help` - Show all options

### Manual Install

Install using `uv`:

```bash
cd /path/to/claude-lint-hook
uv tool install --editable .
```

This installs the `claude-lint-hook` command to `~/.local/bin/`.

## Usage

### Initialize in a Project

Run the init command in your project directory:

```bash
cd /path/to/your-project
claude-lint-hook init
```

This creates or updates `.claude/settings.json` with the PostToolUse hook configuration.

### Check Status

See which linters are available:

```bash
claude-lint-hook status
```

## How It Works

1. **Hook Triggers**: When you use Write/Edit/MultiEdit in Claude Code, the hook fires
2. **Auto-Fix**: The hook runs the appropriate linter with auto-fix (e.g., `ruff check --fix`)
3. **Check**: The hook runs the linter again to check for remaining issues
4. **Decision**:
   - If clean: Returns `{"decision": "allow"}` - operation completes
   - If issues: Returns `{"decision": "block", "reason": "..."}` - Claude sees the issues and tries again

## Supported Languages

| Language | Linter | Extensions |
|----------|--------|------------|
| Python | Ruff | `.py`, `.pyx`, `.pyi` |
| JavaScript/TypeScript | ESLint | `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`, `.cjs` |

## Configuration

### Project Settings

The hook generates this configuration in `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "tool_name in ['Write', 'Edit', 'MultiEdit']",
        "hooks": [
          {
            "type": "command",
            "command": "~/.local/bin/claude-lint-hook",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Optional Project Config

Create `.claude/lint-hook.json` for project-specific settings:

```json
{
  "enabledLinters": ["ruff", "eslint"],
  "disabledLinters": [],
  "timeoutSeconds": 30,
  "warnOnMissing": true
}
```

## Adding New Linters

To add support for a new language, create a new linter class:

1. Create `src/claude_lint_hook/linters/mylang_linter.py`:

```python
from typing import List
from .base import Linter, LinterResult
from .registry import LinterRegistry

@LinterRegistry.register
class MyLangLinter(Linter):
    @property
    def extensions(self) -> List[str]:
        return ['.mylang', '.ml']

    def is_available(self, cwd: str) -> bool:
        from ..utils.command import command_exists
        return command_exists('mylang-linter', cwd)

    def fix(self, file_path: str, cwd: str) -> LinterResult:
        from ..utils.command import run_command
        success, stdout, stderr = run_command(
            ['mylang-linter', '--fix', file_path],
            cwd=cwd,
            timeout=30
        )
        return LinterResult(
            success=success,
            fixed=True,
            issues=[],
            error=stderr if not success else None
        )

    def check(self, file_path: str, cwd: str) -> LinterResult:
        from ..utils.command import run_command
        success, stdout, stderr = run_command(
            ['mylang-linter', '--check', file_path],
            cwd=cwd,
            timeout=30
        )
        issues = [line for line in stdout.split('\n') if line.strip()]
        return LinterResult(
            success=True,
            fixed=False,
            issues=issues
        )
```

2. Reinstall the tool:

```bash
uv tool install --editable . --reinstall
```

## Development

### Project Structure

```
claude-lint-hook/
├── pyproject.toml                 # Package configuration
├── README.md
├── src/
│   └── claude_lint_hook/
│       ├── __init__.py
│       ├── cli.py                 # CLI commands: init, status
│       ├── hook.py                # Core hook logic
│       ├── linters/
│       │   ├── __init__.py
│       │   ├── base.py            # Abstract Linter interface
│       │   ├── python_linter.py   # Ruff implementation
│       │   ├── javascript_linter.py   # ESLint implementation
│       │   └── registry.py        # Extension → linter mapping
│       └── utils/
│           ├── command.py         # Safe subprocess execution
│           └── jsonio.py          # JSON parsing/writing
├── scripts/
│   └── hook-entry.sh              # Shell entry point for Claude Code
└── tests/
    └── fixtures/                  # Sample files for testing
```

### Running Tests

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```

## Troubleshooting

### Hook not triggering

1. Verify `.claude/settings.json` exists and contains the PostToolUse hook
2. Check that `~/.local/bin/claude-lint-hook` is executable
3. Check Claude Code logs for hook errors

### Linter not found

1. Run `claude-lint-hook status` to see available linters
2. Install the required linter (e.g., `pip install ruff` or `npm install -D eslint`)

### Hook timing out

1. Increase timeout in `.claude/settings.json`
2. Check if linter is hanging on large files

## License

MIT
