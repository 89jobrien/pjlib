---
allowed-tools: Read, Write, Bash
argument-hint: [--single-crate] | [--workspace]
description: Initialize Rust workspace with standard directory structure and Cargo configuration
---

# Initialize Workspace

Initialize Rust workspace with standard structure: **$ARGUMENTS**

## Current Workspace State

Check current directory contents before initialization.

!`pwd`
!`ls -la | head -20`

## Task

Create standard Rust workspace or single-crate project structure with configuration files.

**Workspace Type**: Use `--single-crate` for standalone project or `--workspace` for multi-crate workspace

**Initialization Framework**:

1. **Directory Creation** - Standard Rust project directories (src/, tests/, benches/, examples/)
2. **Cargo Configuration** - Generate Cargo.toml with appropriate structure
3. **Git Initialization** - Initialize git repository with Rust .gitignore
4. **Configuration Files** - Create rustfmt.toml, clippy.toml, and other configs
5. **README Generation** - Create basic README.md with project structure

**Single-Crate Project** (`--single-crate`):

Initialize a standard Rust project:

```bash
cargo init
```

Creates:
```
project/
├── Cargo.toml
├── .gitignore
├── src/
│   └── main.rs (or lib.rs)
└── target/ (after building)
```

Enhanced structure:
```
project/
├── Cargo.toml
├── Cargo.lock
├── .gitignore
├── README.md
├── LICENSE
├── rustfmt.toml
├── clippy.toml
├── src/
│   ├── main.rs or lib.rs
│   └── lib/ or bin/
├── tests/
│   └── integration.rs
├── benches/
│   └── bench.rs
├── examples/
│   └── example.rs
└── docs/
```

**Cargo Workspace** (`--workspace`):

Initialize a multi-crate workspace (recommended for larger projects):

```bash
# Create workspace root
mkdir -p crates
touch Cargo.toml

# Create workspace Cargo.toml
cat > Cargo.toml << 'EOF'
[workspace]
resolver = "2"
members = ["crates/*"]

[workspace.dependencies]
tokio = { version = "1.48", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
anyhow = "1.0"
thiserror = "2.0"
EOF

# Create first crate
cargo new --lib crates/core
```

Workspace structure:
```
workspace/
├── Cargo.toml          # Workspace manifest
├── Cargo.lock
├── .gitignore
├── README.md
├── rustfmt.toml        # Shared formatting
├── clippy.toml         # Shared lints
├── crates/
│   ├── core/           # Core library
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── lib.rs
│   ├── cli/            # CLI binary
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── main.rs
│   └── api/            # API server
│       ├── Cargo.toml
│       └── src/
│           └── main.rs
├── tests/              # Workspace-level integration tests
└── docs/
```

**Workspace Cargo.toml Template**:

```toml
[workspace]
resolver = "2"
members = [
    "crates/*",
]
exclude = [
    "crates/experimental",  # Optional: exclude specific crates
]

[workspace.dependencies]
# Async runtime
tokio = { version = "1.48", features = ["full"] }
tokio-test = "0.4"

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Error handling
anyhow = "1.0"
thiserror = "2.0"

# Web frameworks
axum = "0.8"
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

# Common workspace settings
[workspace.package]
edition = "2024"
rust-version = "1.75.0"
license = "MIT OR Apache-2.0"

# Optimized profiles
[profile.dev]
opt-level = 0
debug = true

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true

[profile.dist]
inherits = "release"
lto = "fat"
panic = "abort"
```

**Member Crate Cargo.toml**:

```toml
# crates/core/Cargo.toml
[package]
name = "core"
version.workspace = true
edition.workspace = true
rust-version.workspace = true
license.workspace = true

[dependencies]
# Use workspace dependencies
tokio = { workspace = true }
serde = { workspace = true }
anyhow = { workspace = true }

# Crate-specific dependencies
uuid = { version = "1.11", features = ["v4", "serde"] }

[dev-dependencies]
tokio-test = { workspace = true }
```

**Configuration Files**:

Create `rustfmt.toml`:

```toml
edition = "2024"
max_width = 100
use_small_heuristics = "Default"
imports_granularity = "Crate"
group_imports = "StdExternalCrate"
```

Create `clippy.toml`:

```toml
# Enforce best practices
[[disallowed-methods]]
path = "std::env::set_var"
reason = "Use dependency injection for testability; not thread-safe"

[[disallowed-methods]]
path = "std::thread::sleep"
reason = "Use tokio::time::sleep in async contexts"

[[disallowed-methods]]
path = "std::env::var"
reason = "Prefer explicit configuration structs"

# Complexity thresholds
cognitive-complexity-threshold = 15
```

Create `.gitignore`:

```
# Rust
/target/
**/*.rs.bk
*.pdb

# Cargo.lock should be committed for binaries, ignored for libraries
# Uncomment the following line for library projects:
# Cargo.lock

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
*.profraw
*.profdata

# Documentation
/target/doc/

# Environment
.env
.env.local
```

Create `README.md`:

```markdown
# Project Name

Description of your Rust project.

## Project Structure

This is a Cargo workspace with the following crates:

- `crates/core` - Core library
- `crates/cli` - Command-line interface
- `crates/api` - API server

## Getting Started

### Prerequisites

- Rust 1.75.0 or later
- Cargo (comes with Rust)

### Building

```bash
cargo build
```

### Running Tests

```bash
cargo test
```

### Running

```bash
cargo run -p cli
```

## Development

### Code Formatting

```bash
cargo fmt
```

### Linting

```bash
cargo clippy
```

## License

MIT OR Apache-2.0
```

**Directory Creation Script**:

```bash
#!/bin/bash
# init-rust-workspace.sh

# Create workspace structure
mkdir -p crates
mkdir -p tests
mkdir -p docs
mkdir -p .github/workflows

# Create workspace Cargo.toml
cat > Cargo.toml << 'EOF'
[workspace]
resolver = "2"
members = ["crates/*"]

[workspace.dependencies]
tokio = { version = "1.48", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
anyhow = "1.0"

[profile.release]
opt-level = 3
lto = true
EOF

# Create first crate
cargo new --lib crates/core

# Create configuration files
cat > rustfmt.toml << 'EOF'
edition = "2024"
max_width = 100
EOF

cat > clippy.toml << 'EOF'
[[disallowed-methods]]
path = "std::env::set_var"
reason = "Use dependency injection"
EOF

# Initialize git
git init
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Rust.gitignore

echo "Rust workspace initialized!"
```

**VS Code Workspace Configuration**:

Create `.vscode/settings.json`:

```json
{
  "rust-analyzer.check.command": "clippy",
  "rust-analyzer.check.allTargets": true,
  "rust-analyzer.cargo.features": "all",
  "editor.formatOnSave": true,
  "[rust]": {
    "editor.defaultFormatter": "rust-lang.rust-analyzer"
  }
}
```

**GitHub Actions Workflow**:

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --all-features --locked
```

**Post-Initialization**:

```bash
# Verify workspace structure
cargo metadata --no-deps

# Build all crates
cargo build --workspace

# Test all crates
cargo test --workspace

# Check formatting
cargo fmt --check

# Run clippy
cargo clippy --workspace -- -D warnings
```

**Workspace Commands**:

```bash
# Build specific crate
cargo build -p core

# Test specific crate
cargo test -p cli

# Run binary from specific crate
cargo run -p cli

# Update dependencies
cargo update

# Check all crates
cargo check --workspace

# Build all crates in release mode
cargo build --workspace --release
```

**Output**: Complete Rust workspace with Cargo.toml configuration, member crates structure, shared configuration files (rustfmt.toml, clippy.toml), git initialization, and VS Code integration for productive multi-crate development.
