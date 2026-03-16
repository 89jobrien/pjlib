#!/usr/bin/env bash
# Run all tests with proper output

set -e

echo "🧪 Running minibox tests..."
echo ""

# Run tests with output
cargo test --all -- --nocapture --test-threads=1

echo ""
echo "✅ All tests passed!"
echo ""
echo "Note: minibox currently has no test coverage."
echo "See references/testing-guide.md for adding tests."
