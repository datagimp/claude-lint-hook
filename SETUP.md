# Quick Setup Guide

## On a New Claude Code Instance

```bash
# 1. Clone the repository
git clone https://github.com/datagimp/claude-lint-hook.git ~/claude-lint-hook
cd ~/claude-lint-hook

# 2. Run the installer
./install.sh

# 3. Initialize in your project
cd /path/to/your-project
claude-lint-hook init
```

## Prerequisites

- **uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **jq**: `brew install jq` (macOS) or `sudo apt install jq` (Linux)

## Verify Installation

```bash
claude-lint-hook status
```

## Use in Any Project

```bash
cd /path/to/project
claude-lint-hook init
```

That's it! The hook will run automatically on every file edit.

---

**Repository**: https://github.com/datagimp/claude-lint-hook
**Full Documentation**: See README.md and INSTALL.md
