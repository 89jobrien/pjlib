#!/usr/bin/env bash
set -euo pipefail

# Create new Rust project with standard structure and configuration
# Usage: new-rust-project.sh project-name [--lib|--bin]

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

function log_info() {
    echo -e "${GREEN}[INFO]${NC} $*" >&2
}

function log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

function log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*" >&2
}

function show_usage() {
    cat <<EOF
Usage: $(basename "$0") PROJECT_NAME [OPTIONS]

Create a new Rust project with hexagonal architecture setup.

Options:
    --lib       Create library project (default)
    --bin       Create binary project
    --workspace Create cargo workspace with core/app/infra crates
    -h, --help  Show this help

Examples:
    $(basename "$0") myapp
    $(basename "$0") myapp --workspace
    $(basename "$0") mylib --lib
EOF
}

# Parse arguments
project_name=""
project_type="lib"
use_workspace=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        --lib)
            project_type="lib"
            shift
            ;;
        --bin)
            project_type="bin"
            shift
            ;;
        --workspace)
            use_workspace=true
            shift
            ;;
        *)
            if [[ -z "$project_name" ]]; then
                project_name="$1"
            else
                log_error "Unknown argument: $1"
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$project_name" ]]; then
    log_error "Project name is required"
    show_usage
    exit 1
fi

# Validate project name
if [[ ! "$project_name" =~ ^[a-z][a-z0-9_-]*$ ]]; then
    log_error "Project name must start with lowercase letter and contain only lowercase, numbers, hyphens, and underscores"
    exit 1
fi

# Check if cargo is available
if ! command -v cargo &>/dev/null; then
    log_error "cargo not found. Install Rust: https://rustup.rs/"
    exit 1
fi

# Project directory
readonly PROJECT_DIR="$HOME/dev/$project_name"

if [[ -d "$PROJECT_DIR" ]]; then
    log_error "Project directory already exists: $PROJECT_DIR"
    exit 1
fi

log_info "Creating Rust project: $project_name"
log_info "Location: $PROJECT_DIR"
log_info "Type: $project_type"
log_info "Workspace: $use_workspace"

# Create project directory
mkdir -p "$HOME/dev"
cd "$HOME/dev"

if [[ "$use_workspace" == true ]]; then
    # Create workspace structure
    log_info "Creating workspace structure..."

    cargo new "$project_name" --lib
    cd "$project_name"

    # Create workspace Cargo.toml
    cat > Cargo.toml <<'WORKSPACE_TOML'
[workspace]
members = [
    "crates/core",
    "crates/app",
    "crates/infra",
]
resolver = "2"

[workspace.package]
version = "0.1.0"
edition = "2021"
authors = ["Your Name <your.email@example.com>"]

[workspace.dependencies]
# Async runtime
tokio = { version = "1.36", features = ["full"] }

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Error handling
thiserror = "1.0"
anyhow = "1.0"

# Logging
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

[workspace.dev-dependencies]
proptest = "1.4"

[workspace.lints.rust]
unsafe_code = "forbid"

[workspace.lints.clippy]
all = "warn"
pedantic = "warn"
WORKSPACE_TOML

    # Create crate directories
    mkdir -p crates/{core,app,infra}/src

    # Core crate
    cat > crates/core/Cargo.toml <<CORE_TOML
[package]
name = "${project_name}-core"
version.workspace = true
edition.workspace = true

[dependencies]
serde.workspace = true
thiserror.workspace = true

[dev-dependencies]
proptest.workspace = true
CORE_TOML

    cat > crates/core/src/lib.rs <<'CORE_LIB'
//! Core domain layer
//!
//! Contains business entities, domain logic, and port definitions.

pub mod domain;
pub mod ports;

pub use domain::*;
pub use ports::*;
CORE_LIB

    mkdir -p crates/core/src/{domain,ports}
    touch crates/core/src/domain/mod.rs
    touch crates/core/src/ports/mod.rs

    # App crate
    cat > crates/app/Cargo.toml <<APP_TOML
[package]
name = "${project_name}-app"
version.workspace = true
edition.workspace = true

[dependencies]
${project_name}-core = { path = "../core" }
thiserror.workspace = true
anyhow.workspace = true
tokio.workspace = true
tracing.workspace = true

[dev-dependencies]
proptest.workspace = true
APP_TOML

    cat > crates/app/src/lib.rs <<'APP_LIB'
//! Application layer
//!
//! Contains use cases and application services.

pub mod use_cases;

pub use use_cases::*;
APP_LIB

    mkdir -p crates/app/src/use_cases
    touch crates/app/src/use_cases/mod.rs

    # Infra crate
    cat > crates/infra/Cargo.toml <<INFRA_TOML
[package]
name = "${project_name}-infra"
version.workspace = true
edition.workspace = true

[dependencies]
${project_name}-core = { path = "../core" }
${project_name}-app = { path = "../app" }
tokio.workspace = true
tracing.workspace = true
serde.workspace = true
serde_json.workspace = true

[dev-dependencies]
proptest.workspace = true
INFRA_TOML

    cat > crates/infra/src/lib.rs <<'INFRA_LIB'
//! Infrastructure layer
//!
//! Contains adapters for external services (DB, HTTP, etc.)

pub mod adapters;

pub use adapters::*;
INFRA_LIB

    mkdir -p crates/infra/src/adapters
    touch crates/infra/src/adapters/mod.rs

    # Remove default src/ directory
    rm -rf src

else
    # Create simple project
    if [[ "$project_type" == "bin" ]]; then
        cargo new "$project_name"
    else
        cargo new "$project_name" --lib
    fi

    cd "$project_name"
fi

# Create standard directories
mkdir -p tests benches examples .github/workflows

# Create README
cat > README.md <<README
# $project_name

[Brief description of what this project does]

## Setup

\`\`\`bash
# Build
cargo build

# Run tests
cargo test

# Run (if binary)
cargo run
\`\`\`

## Development

\`\`\`bash
# Format code
cargo fmt

# Lint
cargo clippy -- -D warnings

# Check types
cargo check --all-features

# Build release
cargo build --release
\`\`\`

## Architecture

This project follows hexagonal architecture (ports & adapters):

- **Domain**: Core business logic (dependency-free)
- **Application**: Use cases and orchestration
- **Infrastructure**: External adapters (DB, HTTP, etc.)

## License

[Your license here]
README

# Create CLAUDE.md from template
if [[ -f "$HOME/.claude/templates/rust-project-CLAUDE.md" ]]; then
    cp "$HOME/.claude/templates/rust-project-CLAUDE.md" CLAUDE.md
    # Replace placeholder with project name
    sed -i '' "s/\[Project Name\]/$project_name/g" CLAUDE.md
fi

# Create .gitignore
cat > .gitignore <<'GITIGNORE'
# Rust
/target
Cargo.lock

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Local files
*.local.md
.env
GITIGNORE

# Create rust-toolchain.toml
cat > rust-toolchain.toml <<'TOOLCHAIN'
[toolchain]
channel = "stable"
components = ["rustfmt", "clippy"]
TOOLCHAIN

# Create GitHub Actions workflow
cat > .github/workflows/ci.yml <<'WORKFLOW'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  CARGO_TERM_COLOR: always

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2

      - name: Check formatting
        run: cargo fmt --all -- --check

      - name: Clippy
        run: cargo clippy --all-targets --all-features -- -D warnings

      - name: Build
        run: cargo build --verbose

      - name: Run tests
        run: cargo test --verbose
WORKFLOW

# Initialize git repository
git init
git add .
git commit -m "chore: initial project setup

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

log_info "Project created successfully!"
echo ""
log_info "Next steps:"
echo "  cd $PROJECT_DIR"
echo "  cargo build"
echo "  cargo test"
echo ""
log_info "Project structure:"
tree -L 2 -I target 2>/dev/null || ls -la
