#!/usr/bin/env bash
# Debug container issues

if [ -z "$1" ]; then
    echo "Usage: $0 <container-id>"
    echo ""
    echo "Debug a minibox container by inspecting:"
    echo "  - Container directory structure"
    echo "  - Process state"
    echo "  - Namespace isolation"
    echo "  - Cgroup configuration"
    echo "  - Overlay filesystem"
    exit 1
fi

CONTAINER_ID="$1"
CONTAINER_DIR="/var/lib/minibox/containers/$CONTAINER_ID"

echo "🔍 Debugging container: $CONTAINER_ID"
echo ""

# Check if container exists
if [ ! -d "$CONTAINER_DIR" ]; then
    echo "❌ Error: Container directory not found"
    echo "Path: $CONTAINER_DIR"
    exit 1
fi

echo "📁 Container Directory Structure"
echo "================================"
tree -L 2 "$CONTAINER_DIR" || ls -la "$CONTAINER_DIR"
echo ""

# Check PID
if [ -f "$CONTAINER_DIR/pid" ]; then
    PID=$(cat "$CONTAINER_DIR/pid")
    echo "🔢 Process Information"
    echo "======================"
    echo "PID: $PID"

    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Status: Running ✅"
        echo ""
        ps -fp "$PID"
        echo ""

        echo "📊 Namespaces"
        echo "============="
        ls -la "/proc/$PID/ns/"
        echo ""
    else
        echo "Status: Not running ❌"
        echo ""
    fi
else
    echo "⚠️  No PID file found"
    echo ""
fi

# Check cgroup
CGROUP_DIR="/sys/fs/cgroup/minibox/$CONTAINER_ID"
if [ -d "$CGROUP_DIR" ]; then
    echo "📊 Cgroup Configuration"
    echo "======================="
    echo "Path: $CGROUP_DIR"
    echo ""

    echo "Processes in cgroup:"
    cat "$CGROUP_DIR/cgroup.procs" 2>/dev/null || echo "  (none)"
    echo ""

    echo "Memory limit:"
    cat "$CGROUP_DIR/memory.max" 2>/dev/null || echo "  (not set)"
    echo ""

    echo "Memory usage:"
    cat "$CGROUP_DIR/memory.current" 2>/dev/null || echo "  (not available)"
    echo ""

    echo "CPU weight:"
    cat "$CGROUP_DIR/cpu.weight" 2>/dev/null || echo "  (not set)"
    echo ""
else
    echo "⚠️  Cgroup not found: $CGROUP_DIR"
    echo ""
fi

# Check overlay
echo "🗂️  Overlay Filesystem"
echo "====================="
if mount | grep -q "$CONTAINER_ID"; then
    echo "Mounted overlays:"
    mount | grep "$CONTAINER_ID"
    echo ""

    OVERLAY_DIR="$CONTAINER_DIR/overlay"
    if [ -d "$OVERLAY_DIR" ]; then
        echo "Overlay directories:"
        for dir in lower upper work merged; do
            if [ -d "$OVERLAY_DIR/$dir" ]; then
                SIZE=$(du -sh "$OVERLAY_DIR/$dir" 2>/dev/null | cut -f1)
                echo "  $dir: $SIZE"
            fi
        done
        echo ""
    fi
else
    echo "⚠️  No overlay mounts found"
    echo ""
fi

# Check rootfs
ROOTFS_DIR="$CONTAINER_DIR/rootfs"
if [ -d "$ROOTFS_DIR" ]; then
    echo "📂 Root Filesystem"
    echo "=================="
    echo "Path: $ROOTFS_DIR"
    SIZE=$(du -sh "$ROOTFS_DIR" 2>/dev/null | cut -f1)
    echo "Size: $SIZE"
    echo ""
    echo "Contents:"
    ls -la "$ROOTFS_DIR" 2>/dev/null | head -20
    echo ""
else
    echo "⚠️  Root filesystem not found"
    echo ""
fi

echo "✅ Debugging complete"
