#!/usr/bin/env bash
# Inspect cgroup v2 configuration and usage

CONTAINER_ID="$1"

if [ -z "$CONTAINER_ID" ]; then
    echo "Usage: $0 <container-id>"
    echo ""
    echo "Inspect cgroup v2 configuration for a container"
    exit 1
fi

CGROUP_PATH="/sys/fs/cgroup/minibox/$CONTAINER_ID"

if [ ! -d "$CGROUP_PATH" ]; then
    echo "❌ Error: Cgroup not found for container: $CONTAINER_ID"
    echo "Path: $CGROUP_PATH"
    exit 1
fi

echo "🔍 Cgroup Inspection: $CONTAINER_ID"
echo "===================================="
echo ""

echo "📁 Path: $CGROUP_PATH"
echo ""

echo "🔢 Processes"
echo "============"
PROCS=$(cat "$CGROUP_PATH/cgroup.procs" 2>/dev/null)
if [ -n "$PROCS" ]; then
    echo "PIDs in cgroup:"
    while IFS= read -r pid; do
        if [ -n "$pid" ]; then
            CMD=$(ps -p "$pid" -o comm= 2>/dev/null || echo "(unknown)")
            echo "  $pid - $CMD"
        fi
    done <<< "$PROCS"
else
    echo "  (no processes)"
fi
echo ""

echo "💾 Memory"
echo "========="
MAX=$(cat "$CGROUP_PATH/memory.max" 2>/dev/null)
CURRENT=$(cat "$CGROUP_PATH/memory.current" 2>/dev/null)
echo "  Limit:   $MAX bytes"
echo "  Current: $CURRENT bytes"
if [ -n "$MAX" ] && [ -n "$CURRENT" ] && [ "$MAX" != "max" ]; then
    PERCENT=$((CURRENT * 100 / MAX))
    echo "  Usage:   $PERCENT%"
fi
echo ""

echo "⚙️  CPU"
echo "======"
WEIGHT=$(cat "$CGROUP_PATH/cpu.weight" 2>/dev/null)
echo "  Weight: $WEIGHT"
echo ""

echo "📊 Controllers"
echo "=============="
CONTROLLERS=$(cat "$CGROUP_PATH/cgroup.controllers" 2>/dev/null)
echo "  Available: $CONTROLLERS"
SUBTREE=$(cat "$CGROUP_PATH/cgroup.subtree_control" 2>/dev/null)
echo "  Enabled:   $SUBTREE"
echo ""

echo "📈 Statistics"
echo "============="
if [ -f "$CGROUP_PATH/memory.stat" ]; then
    echo "Memory statistics (selected):"
    grep -E "^(anon|file|slab)" "$CGROUP_PATH/memory.stat" | sed 's/^/  /'
fi
echo ""

echo "✅ Inspection complete"
