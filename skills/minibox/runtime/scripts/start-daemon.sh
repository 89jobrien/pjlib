#!/usr/bin/env bash
# Start miniboxd daemon with proper logging

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: miniboxd must run as root"
    echo "Please run: sudo $0"
    exit 1
fi

# Set log level (override with environment variable)
: ${RUST_LOG:=debug}
export RUST_LOG

echo "🚀 Starting miniboxd daemon..."
echo "📊 Log level: $RUST_LOG"
echo ""

# Check if daemon already running
if pgrep -x miniboxd > /dev/null; then
    echo "⚠️  Warning: miniboxd is already running"
    echo "PID: $(pgrep -x miniboxd)"
    echo ""
    read -p "Kill existing daemon and restart? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -9 miniboxd
        sleep 1
    else
        exit 0
    fi
fi

# Start daemon
echo "Starting daemon..."
./target/debug/miniboxd

echo ""
echo "✅ Daemon started successfully"
echo "Socket: /var/run/minibox.sock"
