---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [--full] | [--minimal] | [--nightly]
description: Setup comprehensive Rust development environment with toolchain, tools, and IDE configuration
---

# Setup Development Environment

Setup comprehensive Rust development environment with modern tooling: **$ARGUMENTS**

## Current Environment State

- Operating system: !`uname -s` (!`uname -m` architecture)
- Rust toolchain: !`rustc --version 2>/dev/null || echo "Rust not installed"`
- Cargo version: !`cargo --version 2>/dev/null`
- Rustup status: !`rustup show 2>/dev/null || echo "rustup not installed"`
- IDE/Editor: Check for VS Code, RustRover, or other development environments

## Task

Configure complete Rust development environment with modern tools and best practices:

**Setup Mode**: Use `--full` for complete tooling, `--minimal` for basic setup, or `--nightly` for nightly toolchain

**Core Rust Installation**:

1. **Install Rustup** (Rust toolchain manager):
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Configure Default Toolchain**:
   ```bash
   # Install stable toolchain (recommended)
   rustup default stable

   # Optional: Install nightly for advanced features
   rustup toolchain install nightly

   # Verify installation
   rustc --version
   cargo --version
   ```

**Essential Components**:

Install required Rust components:

```bash
# Code formatting
rustup component add rustfmt

# Code linting
rustup component add clippy

# IDE integration (LSP)
rustup component add rust-analyzer

# Source code for standard library (for IDE navigation)
rustup component add rust-src
```

**Development Tools**:

1. **Cargo Extensions**:
   ```bash
   # Improved test runner with parallel execution
   cargo install cargo-nextest

   # Dependency management
   cargo install cargo-edit        # cargo add, cargo rm, cargo upgrade
   cargo install cargo-outdated    # Check for outdated dependencies

   # Code coverage
   cargo install cargo-llvm-cov

   # Watch for file changes and rebuild
   cargo install cargo-watch

   # Security auditing
   cargo install cargo-audit

   # Binary installation from crates.io
   cargo install cargo-binstall    # Faster than cargo install
   ```

2. **Performance & Profiling Tools**:
   ```bash
   # Benchmarking
   # (criterion is added as dev-dependency, not installed globally)

   # Build time analysis
   cargo install cargo-bloat       # Find what takes up space in binary
   cargo install cargo-udeps       # Find unused dependencies
   ```

3. **Documentation Tools**:
   ```bash
   # Generate and open docs
   cargo doc --open
   ```

**IDE Configuration**:

### VS Code Setup

1. **Install Extensions**:
   - rust-analyzer (Official Rust LSP)
   - CodeLLDB (Debugger)
   - crates (Dependency version management)
   - Better TOML (TOML syntax highlighting)

2. **Configure Settings** (`.vscode/settings.json`):
   ```json
   {
     "rust-analyzer.check.command": "clippy",
     "rust-analyzer.check.allTargets": true,
     "rust-analyzer.check.extraArgs": [
       "--all-features",
       "--",
       "-D",
       "warnings"
     ],
     "rust-analyzer.cargo.features": "all",
     "rust-analyzer.rustfmt.extraArgs": ["+nightly"],
     "editor.formatOnSave": true,
     "editor.defaultFormatter": "rust-lang.rust-analyzer",
     "[rust]": {
       "editor.formatOnSave": true,
       "editor.defaultFormatter": "rust-lang.rust-analyzer"
     },
     "rust-analyzer.inlayHints.chainingHints.enable": true,
     "rust-analyzer.inlayHints.parameterHints.enable": true,
     "rust-analyzer.lens.enable": true
   }
   ```

3. **Debug Configuration** (`.vscode/launch.json`):
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "type": "lldb",
         "request": "launch",
         "name": "Debug executable",
         "cargo": {
           "args": ["build", "--bin=your-binary-name", "--package=your-package-name"],
           "filter": {
             "name": "your-binary-name",
             "kind": "bin"
           }
         },
         "args": [],
         "cwd": "${workspaceFolder}"
       },
       {
         "type": "lldb",
         "request": "launch",
         "name": "Debug unit tests",
         "cargo": {
           "args": ["test", "--no-run", "--lib", "--package=your-package-name"],
           "filter": {
             "name": "your-package-name",
             "kind": "lib"
           }
         },
         "args": [],
         "cwd": "${workspaceFolder}"
       }
     ]
   }
   ```

**Workspace vs Single-Crate Projects**:

### Cargo Workspace (Monorepo)
For projects with multiple related crates:

```toml
# Workspace Cargo.toml
[workspace]
resolver = "2"
members = ["crate-a", "crate-b", "crate-c"]

[workspace.dependencies]
tokio = { version = "1.48", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
anyhow = "1.0"
```

Member crates inherit workspace dependencies:

```toml
# crate-a/Cargo.toml
[dependencies]
tokio = { workspace = true }
serde = { workspace = true }
```

### Single-Crate Project
Standard project structure:

```bash
cargo new my-project
cd my-project
```

**Environment Configuration**:

1. **Environment Variables**:
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export RUST_BACKTRACE=1              # Show backtraces on panic
   export CARGO_INCREMENTAL=1           # Enable incremental compilation (default)
   export RUSTFLAGS="-C link-arg=-fuse-ld=lld"  # Faster linking (if lld installed)
   ```

2. **Cargo Configuration** (`~/.cargo/config.toml`):
   ```toml
   [build]
   jobs = 8                    # Parallel build jobs

   [term]
   color = "auto"              # Colored output

   [alias]
   b = "build"
   t = "nextest run"
   c = "clippy --all-targets -- -D warnings"
   f = "fmt --all"
   ```

**Project-Specific Configuration**:

Create `.cargo/config.toml` in project root:

```toml
[build]
target-dir = "target"

[alias]
# Project-specific aliases
check-all = "clippy --all-targets --all-features --locked -- -D warnings"
test-all = "nextest run --all-features --locked"

[env]
# Environment variables for builds
DATABASE_URL = { value = "postgres://localhost/dev", relative = true }
```

**Testing Setup**:

```bash
# Install nextest (preferred test runner)
cargo install cargo-nextest

# Configure nextest
cargo nextest --version

# Run tests
cargo nextest run
```

**Async Development (Tokio)**:

For async projects, configure Cargo.toml:

```toml
[dependencies]
tokio = { version = "1.48", features = ["full"] }

[dev-dependencies]
tokio-test = "0.4"
```

**Common Development Workflow**:

```bash
# Check compilation without building
cargo check

# Build project
cargo build

# Run project (if binary)
cargo run

# Run tests
cargo nextest run

# Run specific test
cargo nextest run test_name

# Format code
cargo fmt

# Lint code
cargo clippy

# Generate and open documentation
cargo doc --open

# Update dependencies
cargo update

# Watch for changes and rebuild
cargo watch -x check -x test
```

**EditorConfig** (`.editorconfig`):

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.rs]
indent_style = space
indent_size = 4

[*.toml]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

**Team Synchronization**:

- Commit `.vscode/settings.json` for team consistency
- Document required components in README.md
- Create setup script (`scripts/setup-dev.sh`):
  ```bash
  #!/bin/bash
  # Install required components
  rustup component add rustfmt clippy rust-analyzer rust-src

  # Install cargo extensions
  cargo install cargo-nextest cargo-watch cargo-edit

  echo "Development environment setup complete!"
  ```

**Advanced Features**:

- **Hot Reloading**: Use `cargo watch -x run` for automatic rebuilds
- **Performance Profiling**: Install `perf`, `valgrind`, or `cargo-flamegraph`
- **Cross-Compilation**: Add targets with `rustup target add x86_64-unknown-linux-musl`
- **Conditional Compilation**: Use `#[cfg(target_os = "linux")]` for platform-specific code

**Verification**:

```bash
# Verify Rust installation
rustc --version
cargo --version
rustup show

# Verify components
rustup component list --installed

# Verify cargo extensions
cargo nextest --version
cargo clippy --version
rustfmt --version
```

**Output**: Complete Rust development environment with toolchain configuration, IDE setup, essential tools, workspace support, and team synchronization for productive Rust development.
