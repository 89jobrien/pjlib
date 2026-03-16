#!/bin/bash
# slop_detect.sh - Detect AI slop patterns

BASE="${1:-dev}"
MERGE_BASE=$(git merge-base HEAD "$BASE")

echo "=== Slop Detection Report ==="
echo ""

# Unnecessary comments on trivial code
echo "Suspicious Comments:"
git diff "$MERGE_BASE"..HEAD | grep -E '^\+.*//.*\b(increment|decrement|return|set|get)\b' | head -5

# Defensive unwraps/clones
echo ""
echo "Defensive Code:"
git diff "$MERGE_BASE"..HEAD | grep -E '^\+.*\.unwrap_or|^\+.*\.clone\(\)' | head -5

# Type workarounds
echo ""
echo "Type Workarounds:"
git diff "$MERGE_BASE"..HEAD | grep -E '^\+.*as \w+|^\+.*::\s*<|^\+.*dyn ' | head -5

# Style inconsistencies (naming)
echo ""
echo "Naming Inconsistencies:"
ADDED_NAMES=$(git diff "$MERGE_BASE"..HEAD | grep -E '^\+.*\b(let|fn) [a-zA-Z_]' | grep -oE '\b[a-z][a-zA-Z_]*\b' | sort -u)
echo "$ADDED_NAMES" | while read name; do
  if echo "$name" | grep -qE '[A-Z]'; then
    echo "  CamelCase: $name"
  fi
done

echo ""
echo "=== End Report ==="
