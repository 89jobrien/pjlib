#!/usr/bin/env bash
# Run all quality checks before committing

set -e

echo "🔍 Running quality checks..."
echo ""

echo "1️⃣  Checking formatting..."
cargo fmt --all -- --check
echo "✅ Formatting check passed"
echo ""

echo "2️⃣  Running clippy..."
cargo clippy --all -- -D warnings
echo "✅ Clippy passed"
echo ""

echo "3️⃣  Running tests..."
cargo test --all
echo "✅ Tests passed"
echo ""

echo "4️⃣  Checking compilation..."
cargo check --all
echo "✅ Compilation check passed"
echo ""

echo "✅ All quality checks passed!"
echo "Ready to commit."
