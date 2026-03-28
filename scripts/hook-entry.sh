#!/bin/bash
# Shell entry point for Claude Code linting hook
# Reads JSON from stdin and passes it to the CLI tool

set -e

# Read the entire JSON input from stdin
INPUT=$(cat)

# Verify we have valid JSON
if ! echo "$INPUT" | jq -e '.' >/dev/null 2>&1; then
    echo '{"decision": "allow"}'
    exit 0
fi

# Call the CLI tool's hook command
# The tool will handle the linting and output the decision JSON
echo "$INPUT" | claude-lint-hook hook

# Always exit 0 - communication is via JSON output
exit 0
