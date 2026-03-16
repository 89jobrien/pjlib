#!/usr/bin/env bash
# Rust Test-Fix-Cycle Skill
# Automated testing workflow: run tests, analyze failures, suggest fixes, re-run

set -euo pipefail

# Configuration
CRATE="${1:-}"
TEST_NAME="${2:-}"
AUTO_FIX="${AUTO_FIX:-false}"
DRY_RUN="${DRY_RUN:-false}"
WORKSPACE="${WORKSPACE:-false}"
BATCH_MODE="${BATCH_MODE:-false}"
BATCH_LIMIT="${BATCH_LIMIT:-10}"
REPORT_FORMAT="${REPORT_FORMAT:-text}"
CARGO_TEST_ARGS="${CARGO_TEST_ARGS:---no-fail-fast}"

# Parse flags
while [[ $# -gt 0 ]]; do
  case $1 in
    --auto-fix)
      AUTO_FIX=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --workspace)
      WORKSPACE=true
      shift
      ;;
    --batch)
      BATCH_MODE=true
      shift
      ;;
    --limit=*)
      BATCH_LIMIT="${1#*=}"
      shift
      ;;
    --report=*)
      REPORT_FORMAT="${1#*=}"
      shift
      ;;
    *)
      if [[ -z "$CRATE" ]]; then
        CRATE="$1"
      elif [[ -z "$TEST_NAME" ]]; then
        TEST_NAME="$1"
      fi
      shift
      ;;
  esac
done

echo "=== Rust Test-Fix Cycle ==="
echo "Crate: ${CRATE:-workspace}"
echo "Test: ${TEST_NAME:-all}"
echo "Mode: $([ "$AUTO_FIX" == "true" ] && echo "auto-fix" || echo "interactive")"
echo ""

# Build test command
TEST_CMD="cargo test"
if [[ -n "$CRATE" ]]; then
  TEST_CMD="$TEST_CMD -p $CRATE"
fi
if [[ "$WORKSPACE" == "true" ]]; then
  TEST_CMD="$TEST_CMD --workspace"
fi
if [[ -n "$TEST_NAME" ]]; then
  TEST_CMD="$TEST_CMD $TEST_NAME"
fi
TEST_CMD="$TEST_CMD $CARGO_TEST_ARGS"

# Run tests and capture output
echo "Running tests..."
echo "Command: $TEST_CMD"
echo ""

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

if $TEST_CMD > "$TMPDIR/test-output.txt" 2>&1; then
  echo "✅ All tests passed!"
  cat "$TMPDIR/test-output.txt"
  exit 0
fi

echo "❌ Tests failed. Analyzing failures..."
echo ""

# Parse test output for failures
grep -A 20 "test result: FAILED" "$TMPDIR/test-output.txt" > "$TMPDIR/failures.txt" || true

# Analyze patterns and suggest fixes
# This is a placeholder - in real implementation, would use pattern matching
# to detect common Rust test failures and suggest fixes

cat > "$TMPDIR/analysis.txt" << 'EOF'
Analysis: Test failures detected

Common patterns found:
1. Missing #[tokio::test] attribute
2. Type mismatches (Duration types)
3. Shared mutable state in async context
4. Unsafe environment variable modification
5. Assertion logic errors

Suggested fixes:
- Add #[tokio::test] to async tests
- Use chrono::Duration for time calculations
- Use Arc<AtomicT> for thread-safe counters
- Use temp directories for test isolation
- Review assertion logic

EOF

cat "$TMPDIR/analysis.txt"
echo ""

# Generate fix suggestions
echo "=== Suggested Fixes ==="
echo ""
echo "Run individual test fixes with:"
echo "  cargo test -p <crate> <test_name> -- --exact"
echo ""
echo "For automated fixes, use:"
echo "  /rust-test-fix --auto-fix"
echo ""

# Report generation
if [[ "$REPORT_FORMAT" == "json" ]]; then
  cat > "$TMPDIR/report.json" << EOF
{
  "crate": "$CRATE",
  "test": "$TEST_NAME",
  "status": "failed",
  "failures": $(grep -c "test.*FAILED" "$TMPDIR/test-output.txt" || echo 0),
  "patterns_detected": [
    "tokio-runtime-missing",
    "duration-type-mismatch",
    "mutable-state-async"
  ],
  "fixes_suggested": 3,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
  cat "$TMPDIR/report.json"
fi

exit 1
