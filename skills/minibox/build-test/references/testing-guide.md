# Testing Guide for Minibox

Comprehensive guide for adding test coverage to minibox container runtime.

## Current State

Minibox currently has **no test coverage**. This guide helps you add tests systematically.

## Test Strategy

### Unit Tests

Test individual functions and modules in isolation.

**Location:** In the same file as the code being tested

**Example - Testing namespace flags:**

```rust
// minibox/src/container/namespace.rs

#[cfg(test)]
mod tests {
    use super::*;
    use libc::{CLONE_NEWPID, CLONE_NEWNS, CLONE_NEWNET};

    #[test]
    fn test_namespace_flags_combination() {
        let flags = CLONE_NEWPID | CLONE_NEWNS | CLONE_NEWNET;
        assert!(flags & CLONE_NEWPID != 0);
        assert!(flags & CLONE_NEWNS != 0);
        assert!(flags & CLONE_NEWNET != 0);
    }
}
```

**Example - Testing cgroup path generation:**

```rust
// minibox/src/container/cgroups.rs

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cgroup_path_generation() {
        let container_id = "abc123";
        let expected = "/sys/fs/cgroup/minibox/abc123";
        let path = CgroupManager::cgroup_path(container_id);
        assert_eq!(path, expected);
    }

    #[test]
    fn test_memory_limit_formatting() {
        let limit_mb = 512;
        let expected = "536870912"; // 512 * 1024 * 1024
        let formatted = CgroupManager::format_memory_limit(limit_mb);
        assert_eq!(formatted, expected);
    }
}
```

### Integration Tests

Test component interactions and end-to-end workflows.

**Location:** `tests/` directory in workspace root

**Example - Container lifecycle test:**

```rust
// tests/container_lifecycle.rs

use minibox::container::*;
use std::process::Command;

#[test]
#[ignore] // Requires root and Linux
fn test_container_run_and_stop() {
    // This test requires:
    // - Running on Linux
    // - Root permissions
    // - Daemon running

    let container_id = "test-container";

    // Run container
    let output = Command::new("./target/debug/minibox-cli")
        .args(&["run", "ubuntu:latest", "echo", "hello"])
        .output()
        .expect("Failed to run container");

    assert!(output.status.success());

    // Verify output
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("hello"));
}
```

### Property-Based Tests

Use `proptest` or `quickcheck` for property testing.

**Add to Cargo.toml:**

```toml
[dev-dependencies]
proptest = "1.0"
```

**Example - Testing overlay path combinations:**

```rust
// minibox/src/container/rootfs.rs

#[cfg(test)]
mod tests {
    use super::*;
    use proptest::prelude::*;

    proptest! {
        #[test]
        fn test_overlay_paths_always_absolute(container_id in "[a-z0-9]{12}") {
            let paths = OverlayPaths::new(&container_id);
            assert!(paths.lower.starts_with('/'));
            assert!(paths.upper.starts_with('/'));
            assert!(paths.work.starts_with('/'));
            assert!(paths.merged.starts_with('/'));
        }
    }
}
```

## Test Organization

### Per-Component Testing

**minibox (core library):**
- Unit tests for namespace, cgroup, process, rootfs modules
- Mock filesystem operations where possible
- Test error handling paths

**miniboxd (daemon):**
- Unit tests for protocol serialization
- Mock request handling
- State management tests

**minibox-cli (CLI):**
- Argument parsing tests
- Client communication tests

### Testing Challenges

**Requires Linux:**
- Many tests require Linux kernel features
- Use `#[cfg(target_os = "linux")]` to skip on other platforms

```rust
#[test]
#[cfg(target_os = "linux")]
fn test_namespace_isolation() {
    // Test code
}
```

**Requires Root:**
- Namespace/cgroup operations need CAP_SYS_ADMIN
- Use `#[ignore]` and run with `cargo test -- --ignored --test-threads=1`

```rust
#[test]
#[ignore]
fn test_cgroup_creation() {
    // Must run with: sudo -E cargo test -- --ignored
}
```

**Cleanup Required:**
- Tests must clean up cgroups, mounts, processes
- Use `Drop` implementations or `defer` patterns

```rust
struct TestCleanup {
    container_id: String,
}

impl Drop for TestCleanup {
    fn drop(&mut self) {
        // Cleanup cgroups, mounts, etc.
        let _ = std::fs::remove_dir_all(
            format!("/sys/fs/cgroup/minibox/{}", self.container_id)
        );
    }
}

#[test]
fn test_with_cleanup() {
    let _cleanup = TestCleanup {
        container_id: "test123".to_string(),
    };

    // Test code - cleanup happens automatically
}
```

## Running Tests

**All tests:**
```bash
cargo test --all
```

**Specific module:**
```bash
cargo test -p minibox cgroups
```

**With output:**
```bash
cargo test -- --nocapture
```

**Ignored tests (requires root):**
```bash
sudo -E cargo test -- --ignored --test-threads=1
```

**Integration tests only:**
```bash
cargo test --test container_lifecycle
```

## Test Utilities

Create test helpers in `minibox/src/testing.rs`:

```rust
// minibox/src/testing.rs

#![cfg(test)]

use std::process::Command;
use std::sync::Once;

static INIT: Once = Once::new();

/// Initialize test environment (run once)
pub fn init_test_env() {
    INIT.call_once(|| {
        // Setup test directories
        let _ = std::fs::create_dir_all("/tmp/minibox-test");
    });
}

/// Generate unique container ID for tests
pub fn test_container_id() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let ts = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis();
    format!("test-{}", ts)
}

/// Check if running as root
pub fn is_root() -> bool {
    unsafe { libc::geteuid() == 0 }
}

/// Check if running on Linux
pub fn is_linux() -> bool {
    cfg!(target_os = "linux")
}

/// Skip test if not root
macro_rules! require_root {
    () => {
        if !is_root() {
            eprintln!("Skipping test: requires root");
            return;
        }
    };
}

/// Skip test if not Linux
macro_rules! require_linux {
    () => {
        if !is_linux() {
            eprintln!("Skipping test: requires Linux");
            return;
        }
    };
}
```

## Priority Test Coverage

### High Priority

1. **Cgroup operations** - Resource limiting is critical
2. **Overlay filesystem** - Data persistence and isolation
3. **Error handling** - Daemon stability
4. **Protocol serialization** - Client/daemon communication

### Medium Priority

1. **Process spawning** - Already well-tested via integration
2. **Image pulling** - Depends on external registry
3. **State management** - Relatively simple logic

### Low Priority

1. **CLI parsing** - Straightforward logic
2. **Logging** - Visual verification sufficient

## Continuous Integration

Add to `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - name: Run tests
        run: cargo test --all
      - name: Run clippy
        run: cargo clippy --all -- -D warnings
      - name: Check formatting
        run: cargo fmt --all -- --check
```

## References

- [Rust Testing Documentation](https://doc.rust-lang.org/book/ch11-00-testing.html)
- [proptest Documentation](https://docs.rs/proptest/)
- [Testing async code](https://tokio.rs/tokio/tutorial/testing)
