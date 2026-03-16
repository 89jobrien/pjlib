#!/usr/bin/env bash
# Verify kernel features required for minibox

echo "🔍 Verifying kernel features for minibox..."
echo ""

PASS=0
FAIL=0

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check OS
echo "📋 Operating System"
echo "==================="
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    check_pass "Running on Linux"
    KERNEL_VERSION=$(uname -r)
    echo "   Kernel: $KERNEL_VERSION"

    MAJOR=$(echo "$KERNEL_VERSION" | cut -d. -f1)
    MINOR=$(echo "$KERNEL_VERSION" | cut -d. -f2)

    if [ "$MAJOR" -ge 5 ]; then
        check_pass "Kernel version >= 5.0 (required for cgroups v2)"
    else
        check_fail "Kernel version < 5.0 (need 5.0+ for cgroups v2)"
    fi
else
    check_fail "Not running on Linux (macOS/Windows not supported)"
fi
echo ""

# Check cgroups v2
echo "📊 Cgroups v2"
echo "============="
if mount | grep -q "cgroup2"; then
    check_pass "Cgroups v2 mounted"
    CGROUP_PATH=$(mount | grep cgroup2 | awk '{print $3}' | head -1)
    echo "   Path: $CGROUP_PATH"

    if [ -f "/sys/fs/cgroup/cgroup.controllers" ]; then
        check_pass "Cgroups v2 unified hierarchy"
        CONTROLLERS=$(cat /sys/fs/cgroup/cgroup.controllers)
        echo "   Controllers: $CONTROLLERS"

        if echo "$CONTROLLERS" | grep -q "memory"; then
            check_pass "Memory controller available"
        else
            check_fail "Memory controller not available"
        fi

        if echo "$CONTROLLERS" | grep -q "cpu"; then
            check_pass "CPU controller available"
        else
            check_fail "CPU controller not available"
        fi
    else
        check_fail "Cgroups v2 not in unified hierarchy mode"
        check_warn "Add 'systemd.unified_cgroup_hierarchy=1' to kernel parameters"
    fi
else
    check_fail "Cgroups v2 not mounted"
    check_warn "Enable with: systemd.unified_cgroup_hierarchy=1"
fi
echo ""

# Check namespace support
echo "🔒 Namespace Support"
echo "===================="
if [ -d "/proc/self/ns" ]; then
    check_pass "Namespace support available"

    for ns in pid mnt net ipc uts user; do
        if [ -e "/proc/self/ns/$ns" ]; then
            check_pass "$ns namespace supported"
        else
            check_fail "$ns namespace not supported"
        fi
    done
else
    check_fail "Namespace support not available"
fi
echo ""

# Check overlay filesystem
echo "🗂️  Overlay Filesystem"
echo "====================="
if grep -q overlay /proc/filesystems; then
    check_pass "Overlay filesystem supported"

    # Check if module is loaded
    if lsmod | grep -q overlay; then
        check_pass "Overlay module loaded"
    else
        check_warn "Overlay module not loaded (will load on first use)"
    fi
else
    check_fail "Overlay filesystem not supported"
    check_warn "Load module: sudo modprobe overlay"
fi
echo ""

# Check permissions
echo "🔑 Permissions"
echo "=============="
if [ "$EUID" -eq 0 ]; then
    check_pass "Running as root"
else
    check_warn "Not running as root (required for container operations)"
    echo "   Run with: sudo $0"
fi
echo ""

# Check directory permissions
echo "📁 Directory Setup"
echo "=================="
MINIBOX_DIR="/var/lib/minibox"
if [ -d "$MINIBOX_DIR" ]; then
    check_pass "Minibox directory exists: $MINIBOX_DIR"

    if [ -w "$MINIBOX_DIR" ]; then
        check_pass "Minibox directory writable"
    else
        check_fail "Minibox directory not writable"
    fi

    for subdir in containers images; do
        if [ -d "$MINIBOX_DIR/$subdir" ]; then
            check_pass "$subdir/ directory exists"
        else
            check_warn "$subdir/ directory missing (will be created)"
        fi
    done
else
    check_warn "Minibox directory not found (will be created)"
    echo "   Create with: sudo mkdir -p $MINIBOX_DIR/{containers,images}"
fi
echo ""

# Summary
echo "📊 Summary"
echo "=========="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ All critical features verified!${NC}"
    echo "Minibox should work on this system."
    exit 0
else
    echo -e "${RED}❌ Some required features missing${NC}"
    echo "Please fix the failed checks before using minibox."
    exit 1
fi
