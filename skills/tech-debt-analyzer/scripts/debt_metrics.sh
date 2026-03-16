#!/bin/bash
# debt_metrics.sh - Generate technical debt metrics

echo "=== Technical Debt Metrics ==="
echo ""

# Code duplication
echo "Code Duplication:"
TOTAL_LINES=$(find src -name "*.rs" -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "  Total lines: $TOTAL_LINES"
# Note: Actual duplication detection requires more sophisticated tools

# Complexity
echo ""
echo "Complexity:"
LONG_FUNCTIONS=$(find src -name "*.rs" -exec awk '/^fn |^pub fn / {start=NR} /^}/ && start {if (NR-start > 50) print}' {} + | wc -l)
echo "  Functions >50 lines: $LONG_FUNCTIONS"

# Dependencies
echo ""
echo "Dependencies:"
OUTDATED=$(cargo outdated --quiet --root-deps-only 2>/dev/null | tail -n +4 | wc -l)
echo "  Outdated dependencies: $OUTDATED"

# Test coverage
echo ""
echo "Test Coverage:"
TEST_FILES=$(find tests -name "*.rs" 2>/dev/null | wc -l)
SRC_FILES=$(find src -name "*.rs" | wc -l)
echo "  Test files: $TEST_FILES"
echo "  Source files: $SRC_FILES"
echo "  Ratio: $(awk "BEGIN {printf \"%.1f\", ($TEST_FILES/$SRC_FILES)*100}")%"

# Clippy warnings
echo ""
echo "Code Quality:"
WARNINGS=$(cargo clippy --quiet 2>&1 | grep "warning:" | wc -l)
echo "  Clippy warnings: $WARNINGS"

echo ""
echo "=== End Metrics ==="
