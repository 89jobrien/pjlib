# Minibox Component Details

Deep dive into minibox implementation details.

## Container Primitives

### Namespace Management (namespace.rs)

**Core function: `clone_with_namespaces()`**

Creates a child process with requested Linux namespaces.

```rust
pub fn clone_with_namespaces(
    flags: c_int,
) -> Result<pid_t, std::io::Error> {
    // Stack for child process
    const STACK_SIZE: usize = 1024 * 1024;
    let mut stack = vec![0u8; STACK_SIZE];

    // clone() syscall with namespace flags
    let pid = unsafe {
        libc::clone(
            child_fn,
            stack.as_mut_ptr().add(STACK_SIZE) as *mut c_void,
            flags | libc::SIGCHLD,
            std::ptr::null_mut(),
        )
    };

    if pid < 0 {
        return Err(std::io::Error::last_os_error());
    }

    Ok(pid)
}
```

**Namespace flags used:**
- `CLONE_NEWPID` - PID namespace isolation
- `CLONE_NEWNS` - Mount namespace isolation
- `CLONE_NEWNET` - Network namespace isolation
- `CLONE_NEWIPC` - IPC namespace isolation
- `CLONE_NEWUTS` - UTS (hostname) namespace isolation

**Implementation notes:**
- Uses raw `libc::clone()` instead of `fork()`
- Requires custom stack allocation for child
- Child function receives namespace setup
- Returns child PID to parent

### Cgroup Management (cgroups.rs)

**CgroupManager struct:**

```rust
pub struct CgroupManager {
    container_id: String,
    cgroup_path: PathBuf,
}

impl CgroupManager {
    pub fn new(container_id: String) -> Self {
        let cgroup_path = PathBuf::from("/sys/fs/cgroup")
            .join("minibox")
            .join(&container_id);

        Self {
            container_id,
            cgroup_path,
        }
    }

    pub fn create(&self, limits: &ResourceLimits) -> Result<()> {
        // Create cgroup directory
        std::fs::create_dir_all(&self.cgroup_path)?;

        // Set memory limit
        let memory_path = self.cgroup_path.join("memory.max");
        std::fs::write(
            memory_path,
            format!("{}", limits.memory_bytes)
        )?;

        // Set CPU weight
        let cpu_path = self.cgroup_path.join("cpu.weight");
        std::fs::write(
            cpu_path,
            format!("{}", limits.cpu_weight)
        )?;

        Ok(())
    }

    pub fn add_process(&self, pid: pid_t) -> Result<()> {
        let procs_path = self.cgroup_path.join("cgroup.procs");
        std::fs::write(procs_path, format!("{}", pid))?;
        Ok(())
    }

    pub fn remove(&self) -> Result<()> {
        // Cgroup must be empty (no processes)
        std::fs::remove_dir(&self.cgroup_path)?;
        Ok(())
    }
}
```

**Resource limits:**
```rust
pub struct ResourceLimits {
    pub memory_bytes: u64,  // memory.max (memory + swap)
    pub cpu_weight: u64,     // cpu.weight (1-10000, default 100)
}
```

**Cgroup hierarchy:**
```
/sys/fs/cgroup/
└── minibox/              # Created by daemon
    └── <container-id>/   # Per-container cgroup
        ├── cgroup.procs      # PIDs in this cgroup
        ├── memory.max        # Memory limit
        ├── memory.current    # Current usage
        ├── cpu.weight        # CPU scheduling weight
        └── ...
```

### Process Spawning (process.rs)

**Container initialization sequence:**

```rust
pub fn spawn_container_process(
    config: ContainerConfig,
) -> Result<pid_t> {
    // 1. Clone with namespaces
    let pid = clone_with_namespaces(
        libc::CLONE_NEWPID |
        libc::CLONE_NEWNS |
        libc::CLONE_NEWNET |
        libc::CLONE_NEWIPC |
        libc::CLONE_NEWUTS
    )?;

    if pid == 0 {
        // Child process
        child_init(config)?;
        unreachable!(); // execvp never returns
    }

    // Parent process
    Ok(pid)
}

fn child_init(config: ContainerConfig) -> Result<()> {
    // 1. Set hostname (UTS namespace)
    sethostname(&config.hostname)?;

    // 2. Add self to cgroup
    // Write "0" (current process) to cgroup.procs
    let procs_path = format!(
        "/sys/fs/cgroup/minibox/{}/cgroup.procs",
        config.container_id
    );
    std::fs::write(procs_path, "0")?;

    // 3. Pivot root to overlay merged directory
    pivot_root(&config.rootfs_path)?;

    // 4. Close leaked file descriptors
    close_leaked_fds()?;

    // 5. Execute container command
    execvp(&config.command, &config.args)?;

    // Never reached
    unreachable!();
}
```

**File descriptor cleanup:**
```rust
fn close_leaked_fds() -> Result<()> {
    // Close all fds except stdin/stdout/stderr (0,1,2)
    let fd_dir = PathBuf::from("/proc/self/fd");

    for entry in std::fs::read_dir(fd_dir)? {
        let entry = entry?;
        let fd: i32 = entry.file_name()
            .to_string_lossy()
            .parse()
            .unwrap_or(-1);

        if fd > 2 {
            unsafe { libc::close(fd) };
        }
    }

    Ok(())
}
```

**execvp wrapper:**
```rust
fn execvp(command: &str, args: &[String]) -> Result<()> {
    let c_command = CString::new(command)?;
    let c_args: Vec<CString> = args
        .iter()
        .map(|a| CString::new(a.as_str()).unwrap())
        .collect();

    let mut arg_ptrs: Vec<*const c_char> = c_args
        .iter()
        .map(|a| a.as_ptr())
        .collect();
    arg_ptrs.push(std::ptr::null());

    unsafe {
        libc::execvp(c_command.as_ptr(), arg_ptrs.as_ptr());
    }

    // If we get here, execvp failed
    Err(std::io::Error::last_os_error())
}
```

### Filesystem Operations (rootfs.rs)

**Overlay filesystem setup:**

```rust
pub struct OverlayConfig {
    pub lower_dirs: Vec<PathBuf>,  // Image layers
    pub upper_dir: PathBuf,         // Container changes
    pub work_dir: PathBuf,          // Overlay work
    pub merged_dir: PathBuf,        // Mount point
}

pub fn setup_overlay(config: &OverlayConfig) -> Result<()> {
    // Create directories
    for dir in &[&config.upper_dir, &config.work_dir, &config.merged_dir] {
        std::fs::create_dir_all(dir)?;
    }

    // Build lowerdir option (colon-separated)
    let lowerdir = config.lower_dirs
        .iter()
        .map(|p| p.to_string_lossy())
        .collect::<Vec<_>>()
        .join(":");

    // Mount options
    let options = format!(
        "lowerdir={},upperdir={},workdir={}",
        lowerdir,
        config.upper_dir.display(),
        config.work_dir.display()
    );

    // Mount overlay
    mount_overlay(&config.merged_dir, &options)?;

    Ok(())
}

fn mount_overlay(target: &Path, options: &str) -> Result<()> {
    let c_target = CString::new(target.to_string_lossy().as_ref())?;
    let c_fstype = CString::new("overlay")?;
    let c_source = CString::new("overlay")?;
    let c_options = CString::new(options)?;

    let ret = unsafe {
        libc::mount(
            c_source.as_ptr(),
            c_target.as_ptr(),
            c_fstype.as_ptr(),
            0,
            c_options.as_ptr() as *const c_void,
        )
    };

    if ret != 0 {
        return Err(std::io::Error::last_os_error());
    }

    Ok(())
}
```

**pivot_root implementation:**

```rust
pub fn pivot_root(new_root: &Path) -> Result<()> {
    // Change to new root
    std::env::set_current_dir(new_root)?;

    // Create old_root directory
    let old_root = new_root.join(".old_root");
    std::fs::create_dir_all(&old_root)?;

    // pivot_root syscall
    let c_new = CString::new(".")?;
    let c_old = CString::new(".old_root")?;

    let ret = unsafe {
        libc::syscall(
            libc::SYS_pivot_root,
            c_new.as_ptr(),
            c_old.as_ptr(),
        )
    };

    if ret != 0 {
        return Err(std::io::Error::last_os_error());
    }

    // Change to new root
    std::env::set_current_dir("/")?;

    // Unmount old root
    let c_old_root = CString::new("/.old_root")?;
    unsafe {
        libc::umount2(
            c_old_root.as_ptr(),
            libc::MNT_DETACH,
        );
    }

    // Remove old_root directory
    std::fs::remove_dir("/.old_root")?;

    Ok(())
}
```

**Mount /proc in container:**

```rust
pub fn mount_proc() -> Result<()> {
    let proc_dir = PathBuf::from("/proc");
    std::fs::create_dir_all(&proc_dir)?;

    let c_source = CString::new("proc")?;
    let c_target = CString::new("/proc")?;
    let c_fstype = CString::new("proc")?;

    let ret = unsafe {
        libc::mount(
            c_source.as_ptr(),
            c_target.as_ptr(),
            c_fstype.as_ptr(),
            0,
            std::ptr::null(),
        )
    };

    if ret != 0 {
        return Err(std::io::Error::last_os_error());
    }

    Ok(())
}
```

## Daemon Architecture

### Request Handling Flow

**Request types (protocol.rs):**

```rust
#[derive(Serialize, Deserialize)]
pub enum DaemonRequest {
    Run {
        image: String,
        command: Vec<String>,
        memory_mb: Option<u64>,
        cpu_weight: Option<u64>,
    },
    Stop {
        container_id: String,
    },
    Remove {
        container_id: String,
    },
    List,
}

#[derive(Serialize, Deserialize)]
pub enum DaemonResponse {
    Ok {
        message: String,
        data: Option<serde_json::Value>,
    },
    Error {
        message: String,
    },
}
```

### Async/Sync Bridging

**Pattern used for blocking operations:**

```rust
// In daemon handler (async context)
async fn handle_run(request: RunRequest) -> Result<String> {
    // Async operations (image pull, etc.)
    pull_image(&request.image).await?;

    // Blocking operations wrapped with spawn_blocking
    let container_id = tokio::task::spawn_blocking(move || {
        // Synchronous container setup
        setup_overlay()?;
        create_cgroup()?;

        // clone() is inherently blocking
        let pid = spawn_container_process()?;

        Ok(pid)
    }).await??;

    // Back to async for state updates
    state.add_container(container_id.clone()).await;

    Ok(container_id)
}
```

### State Management

**Container state (state.rs):**

```rust
pub struct DaemonState {
    containers: Arc<RwLock<HashMap<String, ContainerInfo>>>,
}

#[derive(Clone)]
pub struct ContainerInfo {
    pub id: String,
    pub image: String,
    pub pid: pid_t,
    pub status: ContainerStatus,
    pub created_at: SystemTime,
}

#[derive(Clone)]
pub enum ContainerStatus {
    Running,
    Stopped,
    Exited(i32),
}

impl DaemonState {
    pub async fn add_container(&self, info: ContainerInfo) {
        let mut containers = self.containers.write().await;
        containers.insert(info.id.clone(), info);
    }

    pub async fn update_status(&self, id: &str, status: ContainerStatus) {
        let mut containers = self.containers.write().await;
        if let Some(info) = containers.get_mut(id) {
            info.status = status;
        }
    }

    pub async fn remove_container(&self, id: &str) {
        let mut containers = self.containers.write().await;
        containers.remove(id);
    }
}
```

## Error Handling Patterns

**Daemon error handling:**

```rust
pub async fn handle_request(
    request: DaemonRequest,
    state: Arc<DaemonState>,
) -> DaemonResponse {
    match dispatch_request(request, state).await {
        Ok(result) => DaemonResponse::Ok {
            message: "Success".to_string(),
            data: Some(result),
        },
        Err(e) => {
            error!("Request failed: {}", e);
            DaemonResponse::Error {
                message: format!("{}", e),
            }
        }
    }
}
```

**Never panic in daemon:**
- All errors converted to `DaemonResponse::Error`
- Daemon continues running even on request failures
- Individual container failures don't crash daemon

## Performance Considerations

**Process spawning:**
- `clone()` is synchronous, wrapped in `spawn_blocking`
- Daemon doesn't block other requests during container spawn

**State access:**
- `RwLock` allows concurrent reads
- Writes lock briefly for updates

**Overlay mounting:**
- Synchronous mount syscalls
- Wrapped in `spawn_blocking` to avoid blocking daemon

**Image pulling:**
- Async HTTP client (tokio-based)
- Streams layer downloads
- Can handle multiple pulls concurrently
