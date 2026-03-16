---
name: minibox:architecture
description: Navigate and understand minibox codebase architecture
---

# Minibox Architecture

Navigate and understand the minibox container runtime architecture and codebase.

## When to Use

Use this skill when:
- Understanding minibox architecture
- Finding specific components or features
- Learning how container operations work
- Planning code changes
- Reviewing implementation details

## Project Structure

```
minibox/
├── minibox/              # Core library
│   ├── src/
│   │   ├── container/    # Container primitives
│   │   │   ├── namespace.rs   # Namespace setup
│   │   │   ├── cgroups.rs     # Cgroup v2 management
│   │   │   ├── process.rs     # Process spawning
│   │   │   └── rootfs.rs      # Filesystem operations
│   │   ├── image/        # Image management
│   │   │   ├── registry.rs    # Docker Hub client
│   │   │   ├── manifest.rs    # OCI manifest parsing
│   │   │   └── layers.rs      # Layer extraction
│   │   ├── network/      # Network setup (future)
│   │   └── lib.rs
│   └── Cargo.toml
├── miniboxd/             # Daemon
│   ├── src/
│   │   ├── main.rs       # Server initialization
│   │   ├── handler.rs    # Request handlers
│   │   ├── state.rs      # Container state
│   │   └── protocol.rs   # Wire protocol
│   └── Cargo.toml
├── minibox-cli/          # CLI tool
│   ├── src/
│   │   ├── main.rs       # Command parsing
│   │   └── client.rs     # Daemon client
│   └── Cargo.toml
└── Cargo.toml            # Workspace config
```

## Core Components

### Container Primitives (`minibox/src/container/`)

**namespace.rs** - Namespace isolation
- `clone_with_namespaces()` - Create child process with namespaces
- Supports: PID, mount, network, IPC, UTS namespaces
- Uses `libc::clone()` with namespace flags

**cgroups.rs** - Resource management
- `CgroupManager` - Lifecycle for cgroups v2
- `create()` - Setup cgroup hierarchy under `/sys/fs/cgroup/minibox/`
- `add_process()` - Add PID to cgroup
- `set_limits()` - Apply memory/CPU limits
- Only supports cgroups v2 unified hierarchy

**process.rs** - Container process lifecycle
- `spawn_container_process()` - Clone and initialize child
- Initialization sequence:
  1. Set hostname (UTS namespace)
  2. Add to cgroup
  3. Pivot root to overlay
  4. Close leaked file descriptors
  5. `execvp()` user command
- `wait_for_exit()` - Wait for process completion

**rootfs.rs** - Filesystem operations
- `setup_overlay()` - Create overlay filesystem
- `pivot_root()` - Switch root filesystem
- `mount_proc()` - Mount /proc in container
- Manages lower/upper/work/merged directories

### Image Management (`minibox/src/image/`)

**registry.rs** - Docker Hub client
- `pull_image()` - Download image from Docker Hub
- Handles authentication and registry API v2
- Downloads manifests and layers

**manifest.rs** - OCI manifest parsing
- Parse Docker/OCI manifest JSON
- Extract layer information
- Handle multi-arch images

**layers.rs** - Layer extraction
- Extract tar.gz layers
- Build overlay lower directories
- Cache layer contents

### Daemon (`miniboxd/src/`)

**main.rs** - Server initialization
- Creates Unix domain socket at `/var/run/minibox.sock`
- Tokio async runtime
- Request handling loop

**handler.rs** - Request handlers
- `handle_run()` - Create and start container
  - Pull image if needed
  - Generate container ID
  - Setup overlay filesystem
  - Create cgroups
  - Spawn container process
- `handle_stop()` - Stop container
  - Send SIGTERM
  - Wait 10 seconds
  - Send SIGKILL if needed
- `handle_remove()` - Cleanup container
  - Unmount overlay
  - Remove cgroups
  - Delete directories

**state.rs** - Container state management
- In-memory state tracking
- Container metadata storage
- State transitions

**protocol.rs** - Wire protocol
- `DaemonRequest` - Client → Daemon messages
- `DaemonResponse` - Daemon → Client messages
- Serialization/deserialization

### CLI (`minibox-cli/src/`)

**main.rs** - Command-line interface
- Argument parsing
- Command routing (run, stop, rm, ps)

**client.rs** - Daemon communication
- Unix socket client
- Request/response handling

## Key Concepts

### Namespace Setup

Namespaces provide isolation:
- **PID namespace** - Process ID isolation
- **Mount namespace** - Filesystem isolation
- **Network namespace** - Network stack isolation
- **IPC namespace** - Inter-process communication isolation
- **UTS namespace** - Hostname isolation

Implementation:
```rust
// container/namespace.rs
clone_with_namespaces(
    CLONE_NEWPID | CLONE_NEWNS | CLONE_NEWNET |
    CLONE_NEWIPC | CLONE_NEWUTS
)
```

### Cgroups v2 Resource Limiting

Cgroups control resources:
- **memory.max** - Memory+swap limit
- **cpu.weight** - CPU scheduling weight

Directory structure:
```
/sys/fs/cgroup/minibox/<container-id>/
├── cgroup.procs        # PIDs in cgroup
├── memory.max          # Memory limit
└── cpu.weight          # CPU weight
```

### Overlay Filesystem

Overlay provides copy-on-write:
- **Lower** - Read-only image layers
- **Upper** - Container modifications
- **Work** - Overlay working directory
- **Merged** - Combined view (container root)

Mount command:
```bash
mount -t overlay overlay \
  -o lowerdir=<layers>,upperdir=<upper>,workdir=<work> \
  <merged>
```

### Container Lifecycle

1. **Create** (`handle_run`)
   - Pull image → Setup overlay → Create cgroup → Spawn process

2. **Run** (Process execution)
   - Initialize namespaces → Pivot root → Execute command

3. **Stop** (`handle_stop`)
   - SIGTERM → Wait → SIGKILL (if needed)

4. **Remove** (`handle_remove`)
   - Unmount overlay → Remove cgroup → Delete directories

## Observability

### Tracing Instrumentation

All components use `tracing` crate:
```rust
#[instrument]
fn handle_run(...) {
    info!("Starting container");
    debug!("Container ID: {}", id);
}
```

Enable with environment variables:
```bash
RUST_LOG=debug ./miniboxd
RUST_LOG=minibox::container=trace ./miniboxd
```

## Data Flow

### Container Run Flow

```
CLI (minibox-cli run ubuntu /bin/bash)
  ↓ Unix socket
Daemon (miniboxd)
  ↓ handle_run
Pull image (if not cached)
  ↓
Generate container ID
  ↓
Setup overlay filesystem
  ├─ Create directories
  ├─ Mount overlay
  └─ Setup /proc
  ↓
Create cgroup
  ├─ Create /sys/fs/cgroup/minibox/<id>
  ├─ Write memory.max
  └─ Write cpu.weight
  ↓
Spawn container process
  ├─ clone() with namespaces
  ├─ Child: set hostname
  ├─ Child: add to cgroup
  ├─ Child: pivot_root
  ├─ Child: close fds
  └─ Child: execvp /bin/bash
  ↓
Return container ID to CLI
```

## File Paths

Key runtime paths:
- `/var/run/minibox.sock` - Daemon socket
- `/var/lib/minibox/containers/<id>/` - Container data
  - `pid` - Process ID file
  - `overlay/` - Overlay directories
  - `rootfs/` - Merged root filesystem
- `/var/lib/minibox/images/` - Image cache
- `/sys/fs/cgroup/minibox/<id>/` - Container cgroup

## Implementation Notes

### No Test Coverage

Currently no tests exist. Priority areas for testing:
- Namespace isolation verification
- Cgroup limit enforcement
- Overlay filesystem operations
- Error handling paths

### Async/Sync Bridging

Daemon uses hybrid approach:
- Tokio async for request handling
- Blocking operations wrapped with `spawn_blocking`
- `libc` syscalls are inherently synchronous

Example:
```rust
spawn_blocking(move || {
    spawn_container_process(...)  // Blocking clone()
}).await
```

### Error Handling

- Convert errors to `DaemonResponse::Error`
- Prevents daemon crashes from client input
- Proper cleanup on error paths

## Visual Architecture

For a comprehensive visual overview, view `assets/architecture-diagram.txt` which shows:
- User interaction layer (minibox-cli)
- Daemon layer (miniboxd with Tokio runtime)
- Core library layer (container primitives, image management)
- Linux kernel layer (namespaces, cgroups, overlayfs)
- Container lifecycle flow
- Filesystem layout
- Data flow diagrams

## Detailed Component Reference

For implementation-level details, load `references/component-details.md` which covers:
- Container primitives (namespace management, cgroup management, process spawning, filesystem operations)
- Complete code examples for each component
- Daemon architecture (request handling, async/sync bridging, state management)
- Error handling patterns
- Performance considerations

## Reference Files

For detailed implementation patterns:
- Load `minibox/src/container/process.rs` for process spawning details
- Load `minibox/src/container/cgroups.rs` for resource management
- Load `miniboxd/src/handler.rs` for request handling flow
