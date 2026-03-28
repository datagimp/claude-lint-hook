# Installation Guide for New Claude Code Instances

## Quick Start (3 steps)

```bash
# 1. Clone or copy the project
git clone <your-repo-url> ~/claude-lint-hook
cd ~/claude-lint-hook

# 2. Run the installer
./install.sh

# 3. Initialize in your project
cd /path/to/your-project
claude-lint-hook init
```

## Prerequisites

The installer will check for these, but you can install them first:

- **uv** - Python package manager
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- **jq** - JSON processor
  ```bash
  # macOS
  brew install jq

  # Linux
  sudo apt-get install jq  # Ubuntu/Debian
  sudo yum install jq      # CentOS/RHEL
  ```

## Installation Options

### Option 1: Full Install with Linters
```bash
cd ~/claude-lint-hook
./install.sh
```
This installs:
- claude-lint-hook tool
- ruff (Python linter/formatter)

### Option 2: Install Without Linters
```bash
./install.sh --skip-linters
```
Then install linters manually in your projects:
```bash
# For Python projects
uv tool install ruff

# For JavaScript/TypeScript projects
npm install -D eslint
```

### Option 3: Install and Initialize Current Directory
```bash
cd ~/your-project
~/claude-lint-hook/install.sh --init
```

## Verify Installation

```bash
claude-lint-hook status
```

Expected output:
```
Claude Lint Hook Status
==================================================

Supported file extensions:
  .py: PythonLinter (✓ Installed or ✗ Not installed)
  .js: JavaScriptLinter (✓ Installed or ✗ Not installed)
  ...

Project configuration:
  ✓ Hook configured in .claude/settings.json
```

## Use in Your Projects

### Initialize a Single Project
```bash
cd /path/to/project
claude-lint-hook init
```

### Initialize Multiple Projects
```bash
for dir in ~/projects/*/; do
    (cd "$dir" && claude-lint-hook init)
done
```

## How It Works

Once initialized in a project:
1. Every Write/Edit/MultiEdit operation triggers the hook
2. Linter auto-fixes issues (formatting, unused imports, etc.)
3. Hook blocks if unfixable issues remain
4. Claude Code iterates until all issues are resolved

## Troubleshooting

### Hook not triggering?
- Check `.claude/settings.json` exists
- Verify the command path: `~/.local/bin/claude-lint-hook`
- Check Claude Code logs for errors

### Linter not found?
```bash
# Check linter status
claude-lint-hook status

# Install missing linter
uv tool install ruff  # Python
npm install -D eslint # JavaScript/TypeScript
```

###PATH issues?
Add to your `~/.zshrc` or `~/.bashrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Uninstall

```bash
# Remove the tool
uv tool uninstall claude-lint-hook

# Remove from projects (optional)
rm ~/.local/bin/claude-lint-hook
# Or just don't initialize new projects
```

## Updates

```bash
cd ~/claude-lint-hook
git pull
./install.sh --skip-linters
```
