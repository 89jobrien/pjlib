---
description: Create a new Rust project with hexagonal architecture and best practices
allowed-tools: Bash, Read
argument-hint: '[project-name] [--workspace]'
---

# Create New Rust Project

Create a new Rust project in `~/dev/` with standard structure, hexagonal architecture, and best practices configured.

## Usage

```bash
# Simple library project
~/.claude/scripts/new-rust-project.sh myproject

# Binary project
~/.claude/scripts/new-rust-project.sh myapp --bin

# Workspace with hexagonal architecture (recommended)
~/.claude/scripts/new-rust-project.sh myapp --workspace
```

## What Gets Created

### Standard Project

- Cargo.toml with metadata
- src/lib.rs or src/main.rs
- README.md with setup instructions
- CLAUDE.md with project-specific guidelines
- .gitignore for Rust projects
- rust-toolchain.toml
- .github/workflows/ci.yml for CI/CD
- Git repository with initial commit

### Workspace Project (--workspace)

Creates hexagonal architecture with three crates:

```text
myapp/
├── Cargo.toml (workspace root)
├── crates/
│   ├── core/       # Domain layer (entities, ports)
│   ├── app/        # Application layer (use cases)
│   └── infra/      # Infrastructure layer (adapters)
├── tests/          # Integration tests
├── benches/        # Benchmarks
├── examples/       # Example code
└── CLAUDE.md       # Project instructions
```

## Workspace Configuration

The workspace includes:

- Shared dependencies (tokio, serde, thiserror, etc.)
- Workspace lints (forbid unsafe, clippy warnings)
- Standard dev dependencies (proptest)
- CI/CD workflow
- Pre-configured profiles (dev, release, release-with-debug)

## After Creation

```bash
cd ~/dev/myproject

# Verify setup
cargo check

# Run tests
cargo test

# Build
cargo build
```

## Cargo Aliases Available

From `~/.cargo/config.toml`:

```bash
cargo c          # check
cargo ca         # check --all-features
cargo t          # test
cargo qa         # format + clippy + test
cargo doc        # build and open docs
cargo lint       # clippy with warnings as errors
```

## Architecture

Projects follow hexagonal architecture (ports & adapters):

**Core (crates/core)**:
- Domain entities
- Port trait definitions
- Business logic (dependency-free)

**App (crates/app)**:
- Use cases
- Application services
- Orchestration logic

**Infra (crates/infra)**:
- Database adapters
- HTTP adapters
- External service adapters
- Implementation of core ports

## Dependencies Included

### Production

- `tokio` - Async runtime
- `serde` + `serde_json` - Serialization
- `thiserror` - Error types
- `anyhow` - Error handling
- `tracing` - Logging

### Development

- `proptest` - Property-based testing

Add more as needed with:

```bash
cargo add package
cargo add --dev package
```

## Next Steps

1. Update CLAUDE.md with project-specific details
2. Define domain entities in `crates/core/src/domain/`
3. Define ports in `crates/core/src/ports/`
4. Implement use cases in `crates/app/src/use_cases/`
5. Implement adapters in `crates/infra/src/adapters/`
6. Write tests

## See Also

- [Rust Guidelines](~/.claude/rules/rust.md)
- [Rust Patterns](~/.claude/projects/-Users-joe--claude/memory/rust-patterns.md)
- [CLAUDE.md Template](~/.claude/templates/rust-project-CLAUDE.md)
