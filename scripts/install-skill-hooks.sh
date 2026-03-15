#!/bin/bash
# Install git hooks for SKILL.md validation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Installing SKILL.md validation hooks..."

# Check if we're in a git repository
if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Install pre-commit hook
HOOK_SOURCE="$SCRIPT_DIR/hooks/pre-commit-skill-validation"
HOOK_TARGET="$HOOKS_DIR/pre-commit"

if [ -f "$HOOK_TARGET" ]; then
    echo "Warning: pre-commit hook already exists"
    echo "Backing up to pre-commit.backup"
    mv "$HOOK_TARGET" "$HOOK_TARGET.backup"
fi

# Create symlink
ln -sf "$HOOK_SOURCE" "$HOOK_TARGET"
chmod +x "$HOOK_TARGET"

echo "✅ Installed pre-commit hook for SKILL.md validation"
echo ""
echo "The hook will:"
echo "  - Validate SKILL.md files when committing"
echo "  - Block commits with errors"
echo "  - Allow commits with warnings"
echo ""
echo "To bypass validation (not recommended):"
echo "  git commit --no-verify"
