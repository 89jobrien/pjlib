#!/usr/bin/env bash
# Setup minibox development environment

set -e

echo "🚀 Setting up minibox development environment..."
echo ""

# Check if running as root for some operations
SUDO=""
if [ "$EUID" -ne 0 ]; then
    SUDO="sudo"
    echo "Note: Some operations require sudo permissions"
    echo ""
fi

# Create minibox directories
echo "📁 Creating minibox directories..."
$SUDO mkdir -p /var/lib/minibox/{containers,images}
$SUDO chmod 755 /var/lib/minibox
echo "✅ Created /var/lib/minibox/{containers,images}"
echo ""

# Load overlay module
echo "🗂️  Loading overlay filesystem module..."
if ! grep -q overlay /proc/filesystems; then
    $SUDO modprobe overlay
    echo "overlay" | $SUDO tee /etc/modules-load.d/overlay.conf > /dev/null
    echo "✅ Overlay module loaded and configured to auto-load"
else
    echo "✅ Overlay filesystem already available"
fi
echo ""

# Verify cgroups v2
echo "📊 Verifying cgroups v2..."
if mount | grep -q cgroup2; then
    echo "✅ Cgroups v2 already enabled"
else
    echo "❌ Cgroups v2 not enabled"
    echo ""
    echo "To enable cgroups v2, add to kernel boot parameters:"
    echo "  systemd.unified_cgroup_hierarchy=1"
    echo ""
    echo "Edit /etc/default/grub and add to GRUB_CMDLINE_LINUX:"
    echo "  GRUB_CMDLINE_LINUX=\"systemd.unified_cgroup_hierarchy=1\""
    echo ""
    echo "Then run:"
    echo "  sudo update-grub"
    echo "  sudo reboot"
    echo ""
fi

# Check Rust installation
echo "🦀 Checking Rust installation..."
if command -v cargo &> /dev/null; then
    RUST_VERSION=$(rustc --version)
    echo "✅ Rust installed: $RUST_VERSION"

    # Check for rustfmt and clippy
    if command -v rustfmt &> /dev/null; then
        echo "✅ rustfmt installed"
    else
        echo "📦 Installing rustfmt..."
        rustup component add rustfmt
    fi

    if command -v cargo-clippy &> /dev/null; then
        echo "✅ clippy installed"
    else
        echo "📦 Installing clippy..."
        rustup component add clippy
    fi
else
    echo "❌ Rust not installed"
    echo ""
    echo "Install Rust with:"
    echo "  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    echo "  source \$HOME/.cargo/env"
    echo ""
fi
echo ""

# Build minibox
echo "🔨 Building minibox..."
if [ -f "Cargo.toml" ]; then
    cargo build --all
    echo "✅ Build complete"
    echo ""
    echo "Binaries:"
    echo "  - ./target/debug/miniboxd"
    echo "  - ./target/debug/minibox-cli"
else
    echo "⚠️  Not in minibox project directory"
    echo "   Navigate to minibox directory and run cargo build"
fi
echo ""

# Summary
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Verify kernel features: ./skills/minibox/setup/scripts/verify-kernel.sh"
echo "  2. Start daemon: sudo ./target/debug/miniboxd"
echo "  3. Run a container: sudo ./target/debug/minibox-cli run ubuntu:latest /bin/bash"
