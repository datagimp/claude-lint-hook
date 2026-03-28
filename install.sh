#!/bin/bash
# Claude Lint Hook Installer
# Automatically installs and configures the linting hook system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Parse arguments
INSTALL_GLOBAL=false
INIT_CURRENT=false
SKIP_LINTERS=false

for arg in "$@"; do
    case $arg in
        --global)
            INSTALL_GLOBAL=true
            shift
            ;;
        --init)
            INIT_CURRENT=true
            shift
            ;;
        --skip-linters)
            SKIP_LINTERS=true
            shift
            ;;
        --help)
            echo "Claude Lint Hook Installer"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --global        Install to global uv (default: local editable)"
            echo "  --init          Initialize hook in current directory after install"
            echo "  --skip-linters  Skip installing linters (ruff, eslint)"
            echo "  --help          Show this help message"
            exit 0
            ;;
    esac
done

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

info "Claude Lint Hook Installer"
echo "=========================="
echo ""

# Check prerequisites
info "Checking prerequisites..."

if ! check_command uv; then
    error "uv is not installed. Install it from: https://github.com/astral-sh/uv"
fi

if ! check_command jq; then
    warn "jq is not installed. Installing jq..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if check_command brew; then
            brew install jq
        else
            error "Please install jq manually or install Homebrew"
        fi
    else
        error "Please install jq manually"
    fi
fi

if ! check_command python3 && ! check_command python; then
    error "Python is not installed"
fi

info "✓ All prerequisites installed"
echo ""

# Install the tool
info "Installing claude-lint-hook..."

if [ "$INSTALL_GLOBAL" = true ]; then
    uv tool install "$SCRIPT_DIR" --global
else
    uv tool install --editable "$SCRIPT_DIR" || {
        warn "Installation failed, trying with --reinstall..."
        uv tool install --editable "$SCRIPT_DIR" --reinstall
    }
fi

info "✓ claude-lint-hook installed"
echo ""

# Verify installation
if ! check_command claude-lint-hook; then
    warn "claude-lint-hook not found in PATH. Adding ~/.local/bin to PATH..."
    export PATH="$HOME/.local/bin:$PATH"

    if ! check_command claude-lint-hook; then
        error "Installation verification failed. Please add ~/.local/bin to your PATH"
    fi
fi

info "✓ Installation verified"
echo ""

# Optional: Install linters
if [ "$SKIP_LINTERS" = false ]; then
    info "Installing recommended linters..."

    # Check for ruff
    if ! check_command ruff; then
        info "Installing ruff (Python linter/formatter)..."
        uv tool install ruff || pip install ruff || warn "Failed to install ruff. Install manually with: uv tool install ruff"
    else
        info "✓ ruff already installed"
    fi

    # Check for eslint (only if package.json exists in current dir or parent)
    if [ "$INIT_CURRENT" = true ]; then
        if [ -f "package.json" ]; then
            if ! check_command eslint; then
                info "Installing eslint (JavaScript/TypeScript linter)..."
                npm install -D eslint || warn "Failed to install eslint. Install manually with: npm install -D eslint"
            else
                info "✓ eslint already available"
            fi
        fi
    fi
else
    info "Skipping linter installation (--skip-linters)"
fi

echo ""

# Initialize in current directory if requested
if [ "$INIT_CURRENT" = true ]; then
    info "Initializing hook in current directory..."
    claude-lint-hook init
fi

echo ""
info "═══════════════════════════════════════════════════"
info "Installation complete!"
echo ""
info "Next steps:"
info "  1. Run 'claude-lint-hook status' to verify installation"
info "  2. Run 'claude-lint-hook init' in your project directory"
info "  3. Edit files with Claude Code - hook will run automatically"
echo ""
info "For more information, see: $SCRIPT_DIR/README.md"
info "═══════════════════════════════════════════════════"
