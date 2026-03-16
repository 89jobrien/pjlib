---
allowed-tools: Read, Write, Bash
argument-hint: [--bin] | [--lib] | [--workspace]
description: Scaffold new Rust project with cargo initialization and project structure
---

# Scaffold Project

Initialize new Rust project with cargo scaffolding: **$ARGUMENTS**

## Current Directory State

Check if directory is suitable for project initialization.

!`pwd`
!`ls -A | wc -l | xargs echo "Files in directory:"`

## Task

Scaffold new Rust project using cargo initialization commands and create project structure.

**Project Type**: Use `--bin` for binary application, `--lib` for library crate, or `--workspace` for multi-crate workspace

**Scaffolding Framework**:

1. **Project Type Detection** - Binary, library, or workspace project
2. **Tool Validation** - Ensure cargo and rustup are installed
3. **Directory Check** - Verify directory is empty or suitable for initialization
4. **Cargo Initialization** - Run cargo new/init commands
5. **Additional Configuration** - Create Cargo.toml profiles, clippy.toml, rustfmt.toml

**Supported Project Types**:

### Binary Application (`--bin`)

Create an executable Rust application:

```bash
# In new directory
cargo new my-app

# In existing directory
cargo init --bin
```

Generates:
```
my-app/
├── Cargo.toml
├── .gitignore
└── src/
    └── main.rs
```

### Library Crate (`--lib`)

Create a Rust library:

```bash
# In new directory
cargo new --lib my-lib

# In existing directory
cargo init --lib
```

Generates:
```
my-lib/
├── Cargo.toml
├── .gitignore
└── src/
    └── lib.rs
```

### Cargo Workspace (`--workspace`)

Create a multi-crate workspace (like the Maestro project):

```bash
# Create workspace directory
mkdir my-workspace
cd my-workspace

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
tracing = "0.1"
EOF

# Create crates directory
mkdir -p crates

# Create first crate (library)
cargo new --lib crates/core

# Create second crate (binary)
cargo new crates/cli
```

Generates:
```
my-workspace/
├── Cargo.toml            # Workspace manifest
├── Cargo.lock
├── .gitignore
└── crates/
    ├── core/
    │   ├── Cargo.toml
    │   └── src/
    │       └── lib.rs
    └── cli/
        ├── Cargo.toml
        └── src/
            └── main.rs
```

**Enhanced Cargo.toml Configuration**:

For binary projects, add profiles and metadata:

```toml
[package]
name = "my-app"
version = "0.1.0"
edition = "2024"
rust-version = "1.75.0"
authors = ["Your Name <your.email@example.com>"]
description = "A Rust application"
license = "MIT OR Apache-2.0"
repository = "https://github.com/username/my-app"

[dependencies]
tokio = { version = "1.48", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
anyhow = "1.0"
tracing = "0.1"

[dev-dependencies]
criterion = "0.5"

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
```

**Workspace Cargo.toml Example** (from Maestro project):

```toml
[workspace]
resolver = "2"
members = [
    "crates/core",
    "crates/cli",
    "crates/api"
]

[workspace.dependencies]
# Async runtime
tokio = { version = "1.48", features = ["full"] }

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Error handling
anyhow = "1.0"
thiserror = "2.0"

# HTTP and web
axum = "0.8"
tower = "0.5"
tower-http = { version = "0.6", features = ["trace", "cors"] }
reqwest = { version = "0.12", default-features = false, features = ["rustls-tls", "json"] }

# Observability
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter", "json"] }

# Testing
tokio-test = "0.4"
mockito = "1.6"
wiremock = "0.6"

[profile.dev]
opt-level = 0

[profile.release]
opt-level = 3
lto = true
codegen-units = 1

[profile.dist]
inherits = "release"
lto = "fat"
panic = "abort"
```

**Additional Configuration Files**:

Create `rustfmt.toml`:

```toml
edition = "2024"
max_width = 100
use_small_heuristics = "Default"
```

Create `clippy.toml`:

```toml
# Disallow unsafe patterns
[[disallowed-methods]]
path = "std::env::set_var"
reason = "Use dependency injection for testability"

[[disallowed-methods]]
path = "std::thread::sleep"
reason = "Use tokio::time::sleep in async contexts"
```

Create `.gitignore`:

```
# Rust
/target/
**/*.rs.bk
Cargo.lock  # Remove this line for applications

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
```

**Binary + Library Structure**:

For projects that provide both a library and binary:

```toml
# Cargo.toml
[package]
name = "my-project"
version = "0.1.0"
edition = "2024"

[lib]
name = "my_project"
path = "src/lib.rs"

[[bin]]
name = "my-project"
path = "src/main.rs"

[dependencies]
# Dependencies
```

Directory structure:
```
my-project/
├── Cargo.toml
├── src/
│   ├── lib.rs       # Library code
│   ├── main.rs      # Binary entrypoint
│   └── bin/
│       └── tool.rs  # Additional binaries
└── tests/
    └── integration.rs
```

**Project Structure Best Practices**:

```
my-project/
├── Cargo.toml
├── Cargo.lock
├── README.md
├── LICENSE
├── .gitignore
├── rustfmt.toml
├── clippy.toml
├── src/
│   ├── main.rs or lib.rs
│   ├── lib.rs (if both bin and lib)
│   └── bin/          # Additional binaries
├── tests/            # Integration tests
│   └── integration.rs
├── benches/          # Benchmarks
│   └── bench.rs
├── examples/         # Example programs
│   └── example.rs
└── docs/             # Documentation
```

**Post-Scaffolding**:

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Build project
cargo build

# Run tests
cargo test

# Check for errors
cargo check

# Format code
cargo fmt

# Run lints
cargo clippy

# Generate documentation
cargo doc --open
```

**Workspace Member Configuration**:

For workspace members, reference workspace dependencies:

```toml
# crates/my-crate/Cargo.toml
[package]
name = "my-crate"
version = "0.1.0"
edition.workspace = true  # Inherit from workspace

[dependencies]
tokio = { workspace = true }
serde = { workspace = true }

# Crate-specific dependencies
uuid = { version = "1.11", features = ["v4", "serde"] }
```

**Common Scaffolding Patterns**:

1. **Web API Service**: axum + tower + tokio + tracing
2. **CLI Application**: clap + anyhow + tokio
3. **Library Crate**: serde + thiserror
4. **Async Service**: tokio + tracing + anyhow

**Validation**:

```bash
# Verify project builds
cargo check

# Verify tests pass
cargo test

# Verify no clippy warnings
cargo clippy -- -D warnings

# Verify formatting
cargo fmt --check
```

**Output**: Complete Rust project structure with Cargo.toml configuration, additional config files (rustfmt.toml, clippy.toml), proper directory structure, and git initialization for immediate development.
