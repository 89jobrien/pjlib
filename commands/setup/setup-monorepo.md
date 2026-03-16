---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [--workspace] | [--nx-cargo]
description: Configure Rust Cargo workspace (monorepo) with comprehensive build orchestration and dependency management
---

# Setup Monorepo

Configure comprehensive Rust Cargo workspace with advanced dependency management: **$ARGUMENTS**

## Current Project State

- Repository structure: !`find . -maxdepth 2 -type d | head -10`
- Existing workspace: @Cargo.toml with [workspace] section
- Crate count: !`find . -name "Cargo.toml" -not -path "./target/*" | wc -l`
- Rust version: !`rustc --version 2>/dev/null || echo "Rust not installed"`

## Task

Implement production-ready Cargo workspace (Rust's native monorepo solution) with advanced build orchestration:

**Workspace Configuration**: Use `--workspace` for standard Cargo workspace or `--nx-cargo` for Nx-based Cargo orchestration (experimental)

**Cargo Workspace Architecture**:

Cargo provides native monorepo support through workspaces, eliminating the need for external tools like Nx, Lerna, or Turborepo used in JavaScript ecosystems.

1. **Workspace Structure** - Member crates organization, shared dependencies, virtual manifests
2. **Dependency Management** - Workspace dependencies, version unification, dependency resolution
3. **Build Orchestration** - Parallel builds, incremental compilation, build caching
4. **Development Workflow** - Hot reloading, testing strategies, documentation generation
5. **CI/CD Integration** - Build pipelines, test sharding, caching strategies
6. **Shared Configuration** - Rustfmt, clippy, edition settings, profiles

**Workspace Cargo.toml Structure**:

```toml
[workspace]
resolver = "2"
members = [
    "crates/*",
    "examples/*",
]
exclude = [
    "crates/experimental",
    "target",
]

# Default members (built when running `cargo build` at workspace root)
default-members = ["crates/core", "crates/cli"]

[workspace.dependencies]
# Centralized dependency management - all versions defined once
# Async runtime
tokio = { version = "1.48", features = ["full"] }
tokio-test = "0.4"
tokio-stream = "0.1"

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Error handling
anyhow = "1.0"
thiserror = "2.0"

# Web framework
axum = { version = "0.8", features = ["macros"] }
tower = "0.5"
tower-http = { version = "0.6", features = ["trace", "cors"] }

# HTTP client
reqwest = { version = "0.12", default-features = false, features = ["rustls-tls", "json"] }

# Observability
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter", "json"] }

# Testing
mockito = "1.6"
wiremock = "0.6"
criterion = "0.5"

# Common workspace package settings
[workspace.package]
version = "0.1.0"
edition = "2024"
rust-version = "1.75.0"
license = "MIT OR Apache-2.0"
authors = ["Your Name <email@example.com>"]
repository = "https://github.com/username/project"

# Workspace-wide profile configuration
[profile.dev]
opt-level = 0
debug = true
incremental = true

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true
debug = false

[profile.dist]
inherits = "release"
lto = "fat"
panic = "abort"

# Development profile with some optimizations
[profile.dev-opt]
inherits = "dev"
opt-level = 1

# CI profile - faster builds, some optimization
[profile.ci]
inherits = "dev"
debug = false
incremental = false
```

**Workspace Directory Structure** (Maestro-style):

```
workspace-root/
├── Cargo.toml              # Workspace manifest
├── Cargo.lock              # Unified dependency lockfile
├── .gitignore
├── README.md
├── rustfmt.toml            # Shared formatting
├── clippy.toml             # Shared lints
├── crates/
│   ├── core/               # Core library
│   │   ├── Cargo.toml
│   │   ├── src/
│   │   │   └── lib.rs
│   │   └── tests/
│   ├── api/                # API server
│   │   ├── Cargo.toml
│   │   ├── src/
│   │   │   └── main.rs
│   │   └── tests/
│   └── cli/                # CLI tool
│       ├── Cargo.toml
│       ├── src/
│       │   └── main.rs
│       └── tests/
├── tests/                  # Workspace-level integration tests
│   └── integration.rs
├── benches/                # Workspace-level benchmarks
│   └── bench.rs
├── examples/               # Workspace examples
│   └── example.rs
├── docs/                   # Documentation
└── .github/
    └── workflows/
        └── ci.yml
```

**Member Crate Configuration**:

```toml
# crates/core/Cargo.toml
[package]
name = "core"
version.workspace = true
edition.workspace = true
rust-version.workspace = true
license.workspace = true
authors.workspace = true

[dependencies]
# Use workspace dependencies
tokio = { workspace = true }
serde = { workspace = true }
anyhow = { workspace = true }
thiserror = { workspace = true }

# Crate-specific dependencies
uuid = { version = "1.11", features = ["v4", "serde"] }

# Inter-workspace dependencies
# (automatically uses workspace version)
# other-crate = { path = "../other-crate" }

[dev-dependencies]
tokio-test = { workspace = true }
mockito = { workspace = true }
```

**Inter-Crate Dependencies**:

```toml
# crates/cli/Cargo.toml
[package]
name = "cli"
version.workspace = true
edition.workspace = true

[dependencies]
# Reference other workspace members
core = { path = "../core" }
api = { path = "../api" }

# Workspace dependencies
tokio = { workspace = true }
clap = { version = "4.5", features = ["derive"] }
```

**Build Orchestration**:

Cargo automatically handles:
- **Parallel builds** - Multiple crates built in parallel
- **Incremental compilation** - Only rebuild changed code
- **Dependency ordering** - Builds crates in correct order
- **Shared build artifacts** - Single `target/` directory for all crates

```bash
# Build entire workspace
cargo build --workspace

# Build specific crate
cargo build -p core

# Build with all features
cargo build --workspace --all-features

# Build in release mode
cargo build --workspace --release

# Clean all build artifacts
cargo clean
```

**Testing Strategies**:

```bash
# Run all tests in workspace
cargo test --workspace

# Run tests for specific crate
cargo test -p core

# Run tests with nextest (faster)
cargo nextest run --workspace

# Run tests with all features
cargo nextest run --workspace --all-features

# Run integration tests only
cargo test --workspace --test '*'

# Run doc tests
cargo test --workspace --doc
```

**Development Workflow**:

```bash
# Watch for changes and rebuild
cargo watch -x check -x test

# Check all crates (faster than build)
cargo check --workspace

# Format all code
cargo fmt --workspace

# Lint all code
cargo clippy --workspace --all-targets -- -D warnings

# Generate documentation for all crates
cargo doc --workspace --no-deps --open

# Update dependencies
cargo update

# Check for outdated dependencies
cargo outdated --workspace
```

**CI/CD Integration** (GitHub Actions):

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy
      - uses: Swatinem/rust-cache@v2

      - name: Format check
        run: cargo fmt --all -- --check

      - name: Clippy
        run: cargo clippy --workspace --all-targets --all-features --locked -- -D warnings

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - uses: taiki-e/install-action@nextest

      - name: Run tests
        run: cargo nextest run --workspace --all-features --locked

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2

      - name: Build workspace
        run: cargo build --workspace --locked --release

  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - uses: taiki-e/install-action@cargo-llvm-cov

      - name: Generate coverage
        run: cargo llvm-cov --workspace --all-features --lcov --output-path lcov.info

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: lcov.info
```

**Shared Configuration Files**:

All workspace members inherit these configurations:

`rustfmt.toml`:
```toml
edition = "2024"
max_width = 100
use_small_heuristics = "Default"
imports_granularity = "Crate"
group_imports = "StdExternalCrate"
```

`clippy.toml`:
```toml
[[disallowed-methods]]
path = "std::env::set_var"
reason = "Use dependency injection for testability"

[[disallowed-methods]]
path = "std::thread::sleep"
reason = "Use tokio::time::sleep in async contexts"

cognitive-complexity-threshold = 15
```

**Dependency Management Best Practices**:

1. **Version Unification**: Define all versions in `[workspace.dependencies]`
2. **Feature Flags**: Use workspace features for consistent builds
3. **Path Dependencies**: Reference local crates with `{ path = "../crate" }`
4. **Locked Builds**: Always use `--locked` in CI for reproducible builds

**Advanced Features**:

### Task Caching

Cargo automatically caches:
- Compiled dependencies (in `target/`)
- Incremental compilation artifacts
- Test results (with cargo-nextest)

### Virtual Manifests

For workspaces without a root package:

```toml
# Cargo.toml (virtual manifest)
[workspace]
resolver = "2"
members = ["crates/*"]

# No [package] section - workspace has no root package
```

### Feature Unification

```toml
[workspace.dependencies]
tokio = { version = "1.48", features = ["full"] }

# Member crate can use subset of features
# crates/member/Cargo.toml
[dependencies]
tokio = { workspace = true, features = ["rt-multi-thread"] }
```

**Performance Optimization**:

```bash
# Use sccache for shared compilation cache
export RUSTC_WRAPPER=sccache

# Use mold linker for faster linking
export RUSTFLAGS="-C link-arg=-fuse-ld=mold"

# Parallel jobs
cargo build --workspace -j8
```

**Workspace Commands Reference**:

```bash
# Metadata
cargo metadata --no-deps              # View workspace structure

# Building
cargo build --workspace               # Build all crates
cargo build -p crate-name             # Build specific crate
cargo build --workspace --release     # Release build

# Testing
cargo test --workspace                # Run all tests
cargo nextest run --workspace         # Run with nextest

# Documentation
cargo doc --workspace --no-deps       # Generate docs
cargo doc --workspace --open          # Open docs in browser

# Maintenance
cargo update                          # Update dependencies
cargo clean                           # Clean build artifacts
cargo tree -p crate-name              # View dependency tree
```

**Output**: Complete Cargo workspace (monorepo) with optimized build system, dependency management, CI/CD integration, and comprehensive tooling for productive multi-crate Rust development.

**Note**: Unlike JavaScript/TypeScript monorepos which require tools like Nx, Lerna, or Turborepo, Rust's Cargo has built-in workspace support that provides equivalent functionality natively.
