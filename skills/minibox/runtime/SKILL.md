---
name: minibox:runtime
description: Run and debug containers with minibox runtime operations
---

# Minibox Runtime Operations

Run, manage, and debug containers using the minibox container runtime.

## When to Use

Use this skill when:
- Running containers with minibox
- Debugging container runtime issues
- Inspecting container state and processes
- Understanding daemon operations
- Troubleshooting namespace/cgroup issues

## Running Containers

### Start the Daemon

**Start miniboxd:**
```bash
sudo ./target/debug/miniboxd
```

**Start in foreground with logging:**
```bash
sudo RUST_LOG=debug ./target/debug/miniboxd
```

**Check daemon status:**
```bash
ps aux | grep miniboxd
```

### Run Containers

**Run a simple container:**
```bash
sudo ./target/debug/minibox-cli run ubuntu:latest /bin/bash
```

**Run with resource limits:**
```bash
# Memory limit (default: 512MB)
sudo ./target/debug/minibox-cli run --memory 1024 ubuntu:latest /bin/bash

# CPU weight (default: 100)
sudo ./target/debug/minibox-cli run --cpu-weight 200 ubuntu:latest /bin/bash
```

**Run interactive container:**
```bash
sudo ./target/debug/minibox-cli run -it ubuntu:latest /bin/bash
```

### Container Management

**List running containers:**
```bash
sudo ./target/debug/minibox-cli ps
```

**Stop container:**
```bash
sudo ./target/debug/minibox-cli stop <container-id>
```

**Remove container:**
```bash
sudo ./target/debug/minibox-cli rm <container-id>
```

## Debugging Container Issues

### Check Container State

**Inspect container directory:**
```bash
sudo ls -la /var/lib/minibox/containers/<container-id>/
```

**Check PID file:**
```bash
sudo cat /var/lib/minibox/containers/<container-id>/pid
```

**Check overlay filesystem:**
```bash
sudo ls -la /var/lib/minibox/containers/<container-id>/rootfs/
```

### Inspect Namespaces

**List namespaces for process:**
```bash
sudo ls -la /proc/<pid>/ns/
```

**Check namespace isolation:**
```bash
# In container
hostname
# Outside container
hostname
```

### Inspect Cgroups

**Check container's cgroup:**
```bash
sudo cat /sys/fs/cgroup/minibox/<container-id>/cgroup.procs
```

**Check memory limit:**
```bash
sudo cat /sys/fs/cgroup/minibox/<container-id>/memory.max
```

**Check memory usage:**
```bash
sudo cat /sys/fs/cgroup/minibox/<container-id>/memory.current
```

**Check CPU weight:**
```bash
sudo cat /sys/fs/cgroup/minibox/<container-id>/cpu.weight
```

### Check Overlayfs

**Check mounted overlays:**
```bash
mount | grep overlay | grep minibox
```

**Inspect overlay layers:**
```bash
sudo ls -la /var/lib/minibox/containers/<container-id>/overlay/
sudo ls -la /var/lib/minibox/containers/<container-id>/overlay/lower/
sudo ls -la /var/lib/minibox/containers/<container-id>/overlay/upper/
sudo ls -la /var/lib/minibox/containers/<container-id>/overlay/work/
sudo ls -la /var/lib/minibox/containers/<container-id>/overlay/merged/
```

## Daemon Architecture

### Request Flow

1. CLI sends request to daemon via Unix socket (`/var/run/minibox.sock`)
2. Daemon handles request in `handler.rs`
3. Container lifecycle:
   - `handle_run`: Create container, setup overlay, spawn process
   - `handle_stop`: Send SIGTERM, wait, send SIGKILL if needed
   - `handle_remove`: Cleanup overlay, cgroups, directories

### Key Components

**Daemon (`miniboxd/src/`):**
- `main.rs` - Server initialization
- `handler.rs` - Request handlers
- `state.rs` - Container state management

**Core Library (`minibox/src/`):**
- `container/namespace.rs` - Namespace setup
- `container/cgroups.rs` - Cgroup management
- `container/process.rs` - Process spawning
- `container/rootfs.rs` - Filesystem operations
- `image/` - Image pulling and management

## Tracing and Logs

**Enable debug logging:**
```bash
export RUST_LOG=debug
sudo -E ./target/debug/miniboxd
```

**Filter specific modules:**
```bash
export RUST_LOG=miniboxd=debug,minibox::container=trace
sudo -E ./target/debug/miniboxd
```

**Common log events:**
- Container creation and spawning
- Namespace setup
- Cgroup creation and limit application
- Overlay filesystem mounting
- Process lifecycle events

## Bundled Scripts

**Start daemon with logging:**
```bash
sudo ./skills/minibox/runtime/scripts/start-daemon.sh
```
Starts miniboxd with proper logging and safety checks.

**Debug container:**
```bash
sudo ./skills/minibox/runtime/scripts/debug-container.sh <container-id>
```
Comprehensive container debugging (directory, process, namespaces, cgroups, overlay).

**Inspect cgroup:**
```bash
sudo ./skills/minibox/runtime/scripts/inspect-cgroup.sh <container-id>
```
Detailed cgroup inspection (processes, memory, CPU, statistics).

## Common Issues

**Permission denied:**
- Must run as root for namespace/cgroup operations
- Check `/var/lib/minibox/` permissions

**Container fails to start:**
- Check daemon logs with `RUST_LOG=debug`
- Verify image was pulled successfully
- Check overlay mount succeeded
- Verify cgroup v2 is available

**Process cleanup issues:**
- Check if process still exists: `ps aux | grep <pid>`
- Force kill: `sudo kill -9 <pid>`
- Check cgroup is empty before removal

**Overlay mount failures:**
- Check kernel has overlay support: `grep overlay /proc/filesystems`
- Verify work/upper/merged directories exist
- Check no processes have files open in overlay

## Detailed Debugging Guide

For comprehensive debugging guidance, load `references/debugging-guide.md` which covers:
- Quick diagnosis (container won't start, exits immediately, resource limits)
- Namespace debugging (isolation verification, creation failures)
- Cgroup debugging (v2 availability, creation/removal failures)
- Overlay filesystem debugging (mount failures, unmount issues)
- Process debugging (execvp failures, fd leaks)
- Image debugging (pull/extraction failures)
- Daemon debugging (socket errors, timeouts, state corruption)
- Advanced debugging (syscall tracing, kernel logs, profiling)
- Common error messages reference table
