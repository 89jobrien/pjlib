---
name: minibox:build-test
description: Build, test, and debug workflows for minibox container runtime
---

# Minibox Build & Test

Build, test, and debug the minibox container runtime with project-specific workflows.

## When to Use

Use this skill when:
- Building the minibox daemon or CLI
- Running or writing tests for container primitives
- Debugging build failures or test issues
- Checking code quality and formatting
- Understanding build configuration

## Quick Commands

### Build Commands

**Build all components:**
```bash
cargo build --all
```

**Build specific components:**
```bash
cargo build -p minibox        # Core library
cargo build -p miniboxd       # Daemon
cargo build -p minibox-cli    # CLI tool
```

**Release build:**
```bash
cargo build --release --all
```

### Test Commands

**Run all tests:**
```bash
cargo test --all
```

**Run tests for specific component:**
```bash
cargo test -p minibox
cargo test -p miniboxd
```

**Run specific test:**
```bash
cargo test test_name
```

**Run with output:**
```bash
cargo test -- --nocapture
```

### Quality Checks

**Format code:**
```bash
cargo fmt --all
```

**Check formatting:**
```bash
cargo fmt --all -- --check
```

**Run clippy:**
```bash
cargo clippy --all -- -D warnings
```

**Check without building:**
```bash
cargo check --all
```

## Development Workflow

### Before Committing

1. Format code: `cargo fmt --all`
2. Run clippy: `cargo clippy --all -- -D warnings`
3. Run tests: `cargo test --all`
4. Build release: `cargo build --release --all`

### Debugging Build Issues

**Check dependencies:**
```bash
cargo tree
```

**Clean build:**
```bash
cargo clean
cargo build --all
```

**Verbose build:**
```bash
cargo build --all --verbose
```

### Test Development

Currently minibox has no test coverage. When adding tests:

**Create test module in source file:**
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_namespace_creation() {
        // Test code
    }
}
```

**Create integration tests:**
```bash
mkdir -p tests
# Create tests/integration_test.rs
```

## Project Structure

Key directories:
- `minibox/` - Core library with container primitives
- `miniboxd/` - Daemon implementation
- `minibox-cli/` - Command-line interface
- `Cargo.toml` - Workspace configuration

## Bundled Scripts

**Build helper:**
```bash
./skills/minibox/build-test/scripts/build.sh
```
Builds all minibox components with progress output.

**Test runner:**
```bash
./skills/minibox/build-test/scripts/test.sh
```
Runs all tests with proper output formatting.

**Quality checker:**
```bash
./skills/minibox/build-test/scripts/check.sh
```
Runs all quality checks (fmt, clippy, tests, compile).

## Common Issues

**Missing dependencies:**
- Ensure Linux development headers are installed
- Check libc version compatibility

**Test failures:**
- Verify running on Linux (required for namespaces/cgroups)
- Check for required kernel features
- Run as root for namespace operations

**Build performance:**
- Use `cargo build --release` for optimized builds
- Use `sccache` for faster recompilation
- Check `target/` directory size with `du -sh target/`

## Detailed References

For comprehensive testing guidance, load `references/testing-guide.md` which covers:
- Test strategy (unit, integration, property-based)
- Testing challenges (Linux-only, root-required, cleanup)
- Test utilities and helpers
- Priority test coverage areas
- CI/CD configuration
