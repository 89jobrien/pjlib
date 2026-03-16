---
name: minibox:setup
description: Development environment setup for minibox container runtime
---

# Minibox Development Setup

Set up development environment and verify required kernel features for minibox.

## When to Use

Use this skill when:
- Setting up minibox for the first time
- Configuring development environment
- Verifying kernel feature support
- Troubleshooting environment issues
- Installing dependencies

## System Requirements

### Operating System

**Linux kernel 5.0+ required** for:
- Cgroups v2 unified hierarchy
- Modern namespace features
- Overlay filesystem support

**Supported distributions:**
- Ubuntu 20.04+
- Debian 11+
- Fedora 31+
- Arch Linux

**Not supported:**
- macOS (no namespace/cgroup support)
- Windows WSL (limited namespace support)

### Required Kernel Features

**Check cgroups v2:**
```bash
# Should show cgroup2
mount | grep cgroup2

# Should show /sys/fs/cgroup
cat /proc/mounts | grep cgroup2

# Verify unified hierarchy
ls /sys/fs/cgroup/cgroup.controllers
```

**Enable cgroups v2 (if needed):**
```bash
# Add to kernel boot parameters
# /etc/default/grub:
GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=1"

# Update grub
sudo update-grub
sudo reboot
```

**Check namespace support:**
```bash
# Should show namespace types
ls -la /proc/self/ns/

# Expected: ipc, mnt, net, pid, user, uts
```

**Check overlay filesystem:**
```bash
# Should show overlay
grep overlay /proc/filesystems
```

## Development Dependencies

### Rust Toolchain

**Install Rust:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**Verify installation:**
```bash
rustc --version
cargo --version
```

**Install toolchain components:**
```bash
rustup component add rustfmt clippy
```

### System Packages

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    pkg-config \
    libssl-dev \
    git
```

**Fedora:**
```bash
sudo dnf install -y \
    gcc \
    pkg-config \
    openssl-devel \
    git
```

**Arch:**
```bash
sudo pacman -S base-devel openssl git
```

## Project Setup

### Clone and Build

```bash
# Clone repository
git clone https://github.com/username/minibox.git
cd minibox

# Build all components
cargo build --all

# Build release version
cargo build --release --all
```

### Directory Structure

Minibox uses these directories at runtime:

**Container storage:**
```bash
sudo mkdir -p /var/lib/minibox/{containers,images}
sudo chmod 755 /var/lib/minibox
```

**Daemon socket:**
```bash
# Created automatically at /var/run/minibox.sock
# Requires root permissions
```

### Verify Setup

**Check build:**
```bash
./target/debug/minibox-cli --version
./target/debug/miniboxd --version
```

**Test daemon start:**
```bash
sudo ./target/debug/miniboxd &
# Should start without errors

# Check socket created
ls -la /var/run/minibox.sock

# Stop daemon
sudo pkill miniboxd
```

## Development Tools

### Recommended Tools

**Code quality:**
```bash
# Format on save
cargo install cargo-watch
cargo watch -x fmt

# Continuous testing
cargo watch -x test
```

**Performance profiling:**
```bash
cargo install flamegraph
sudo cargo flamegraph --bin miniboxd
```

**Dependency management:**
```bash
cargo install cargo-tree
cargo tree
```

### Editor Setup

**VS Code:**
```json
{
  "rust-analyzer.cargo.allFeatures": true,
  "rust-analyzer.checkOnSave.command": "clippy",
  "[rust]": {
    "editor.formatOnSave": true
  }
}
```

**Vim/Neovim:**
```vim
" Use rust-analyzer with coc.nvim or nvim-lsp
```

## Troubleshooting

### Cgroups v2 Not Available

**Check current setup:**
```bash
mount | grep cgroup
```

**If using cgroups v1:**
- Add `systemd.unified_cgroup_hierarchy=1` to kernel parameters
- Or use `cgroup_no_v1=all`
- Reboot system

### Build Failures

**Update Rust toolchain:**
```bash
rustup update
```

**Clear build cache:**
```bash
cargo clean
rm -rf target/
cargo build --all
```

### Permission Issues

**Daemon requires root:**
```bash
# Must use sudo
sudo ./target/debug/miniboxd
```

**Container operations require root:**
```bash
# namespaces, cgroups need CAP_SYS_ADMIN
sudo ./target/debug/minibox-cli run ubuntu:latest /bin/bash
```

### Overlay Mount Failures

**Missing kernel module:**
```bash
# Load overlay module
sudo modprobe overlay

# Auto-load on boot
echo overlay | sudo tee /etc/modules-load.d/overlay.conf
```

## Bundled Scripts

**Verify kernel features:**
```bash
./skills/minibox/setup/scripts/verify-kernel.sh
```
Comprehensive kernel feature verification with color-coded output.

**Setup environment:**
```bash
./skills/minibox/setup/scripts/setup-env.sh
```
Automated environment setup (directories, modules, Rust toolchain, build).

## Security Notes

**Root requirement:**
- Minibox daemon must run as root
- Required for namespace creation (clone with CLONE_NEWNS, etc.)
- Required for cgroup management
- Required for overlay filesystem mounting

**Future improvements:**
- User namespaces for rootless containers
- Proper permission model for daemon socket
- SELinux/AppArmor profiles

## Detailed Kernel Features Reference

For comprehensive kernel feature documentation, load `references/kernel-features.md` which covers:
- Minimum requirements (kernel version, architecture, configuration)
- Cgroups v2 (configuration, controllers, verification)
- Namespaces (types, required config, verification)
- Overlay filesystem (config, directory structure, limitations)
- Capabilities (required permissions, future improvements)
- Security features (seccomp, AppArmor, SELinux - future)
- Kernel parameters (recommended settings)
- Distribution-specific notes (Ubuntu, Debian, Fedora, Arch)
- Troubleshooting guide
