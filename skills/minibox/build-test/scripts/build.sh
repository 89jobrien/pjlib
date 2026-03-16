#!/usr/bin/env bash
# Build all minibox components

set -e

echo "🔨 Building minibox components..."
echo ""

# Build in order
echo "📦 Building core library (minibox)..."
cargo build -p minibox --all-features

echo "📦 Building daemon (miniboxd)..."
cargo build -p miniboxd

echo "📦 Building CLI (minibox-cli)..."
cargo build -p minibox-cli

echo ""
echo "✅ All components built successfully!"
echo ""
echo "Binaries location:"
echo "  - Daemon: ./target/debug/miniboxd"
echo "  - CLI:    ./target/debug/minibox-cli"
echo ""
echo "To build release versions, run:"
echo "  cargo build --release --all"
