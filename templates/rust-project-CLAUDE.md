# [Project Name] - Claude Instructions

> Project-specific instructions for Claude Code. READ THIS FIRST when working on this project.

## Quick Reference Card

```bash
# Quality checks (run before every commit)
cargo qa              # Format + clippy + test

# Development cycle
cargo c              # Type check only (fast)
cargo t              # Run tests
cargo r              # Run application

# Build
cargo b              # Debug build
cargo br             # Release build
```

## Project Context

**Purpose**: [One sentence: what this project does]

**Architecture**: Hexagonal (Ports & Adapters) - STRICTLY ENFORCED
```
core/   → Domain logic (no external dependencies)
app/    → Use cases (orchestrates domain)
infra/  → Adapters (DB, HTTP, external services)
```

**Critical Constraints**:
- NO `.unwrap()` in production code
- ALL services use trait-based dependency injection
- ALL errors use custom `AppError` type
- ALL public APIs have doc comments

## Project Structure

```text
project/
├── Cargo.toml              # Workspace root
├── crates/
│   ├── core/              # Domain layer
│   │   ├── src/
│   │   │   ├── domain/    # Business entities & traits
│   │   │   ├── ports/     # Interface definitions
│   │   │   └── lib.rs
│   │   └── Cargo.toml
│   ├── app/               # Application layer
│   │   ├── src/
│   │   │   ├── use_cases/ # Business logic
│   │   │   └── lib.rs
│   │   └── Cargo.toml
│   └── infra/             # Infrastructure layer
│       ├── src/
│       │   ├── adapters/  # DB, HTTP, etc.
│       │   └── lib.rs
│       └── Cargo.toml
├── tests/                 # Integration tests
└── benches/               # Benchmarks
```

## Key Conventions

### Error Handling

```rust
// Use project-specific error type
#[derive(Debug, thiserror::Error)]
pub enum AppError {
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
    #[error("Not found: {resource}")]
    NotFound { resource: String },
    #[error("Validation failed: {0}")]
    Validation(String),
}

pub type Result<T> = std::result::Result<T, AppError>;
```

### Dependency Injection

All services receive dependencies via traits:

```rust
pub struct UserService<R: UserRepository> {
    repo: R,
}

impl<R: UserRepository> UserService<R> {
    pub fn new(repo: R) -> Self {
        Self { repo }
    }
}
```

### Testing Strategy

- **Unit tests**: In each module (`#[cfg(test)]`)
- **Integration tests**: In `tests/` directory
- **Property-based**: For data transformations (proptest)
- **Async tests**: Use `#[tokio::test]`

## Dependencies

### Core Dependencies

```toml
[workspace.dependencies]
# Async runtime
tokio = { version = "1.36", features = ["full"] }

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Error handling
thiserror = "1.0"
anyhow = "1.0"

# HTTP (if needed)
axum = "0.7"
tower = "0.4"

# Database (if needed)
sqlx = { version = "0.7", features = ["postgres", "runtime-tokio"] }

# Logging
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

[workspace.dev-dependencies]
proptest = "1.4"
tokio-test = "0.4"
```

## Development Workflow

### Before Committing

```bash
# Format code
cargo fmt

# Lint
cargo clippy -- -D warnings

# Type check
cargo check --all-features

# Run tests
cargo test
# or with nextest (faster)
cargo nextest run

# Build
cargo build --release
```

### Running the Project

```bash
# Development
cargo run

# With environment variables
DATABASE_URL=postgres://... cargo run

# Specific binary
cargo run --bin server
```

## Architecture Principles

1. **Domain-Driven Design**: Core domain is dependency-free
2. **Dependency Inversion**: High-level modules don't depend on low-level
3. **Interface Segregation**: Small, focused traits
4. **No unwrap()**: Always handle errors explicitly
5. **Async by default**: Use tokio for I/O operations

## Code Style

- **No emojis** in code or comments
- **No AI slop** (empty TODOs, placeholder comments)
- **Delete unused code** completely
- **Type hints everywhere** (let bindings can infer)
- **Document public APIs** with doc comments

## Testing Requirements

### Unit Tests

Every public function should have tests:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_user_validation() {
        let user = User::new("alice", "alice@example.com");
        assert!(user.is_valid());
    }
}
```

### Integration Tests

Test the full stack:

```rust
// tests/integration_test.rs
#[tokio::test]
async fn test_create_user_flow() {
    let app = test_app().await;
    let response = app.create_user("alice").await;
    assert!(response.is_ok());
}
```

## Performance Considerations

- Avoid cloning in hot paths
- Use `&str` over `String` for function parameters
- Prefer iterators over collecting to Vec
- Use `Cow<str>` for conditional ownership
- Profile before optimizing

## Security

- Never commit secrets to git
- Use environment variables for config
- Validate all external input
- Use prepared statements for SQL
- Keep dependencies updated

## Common Tasks

### Add New Feature

1. Define trait in `core/src/ports/`
2. Implement use case in `app/src/use_cases/`
3. Implement adapter in `infra/src/adapters/`
4. Write tests (unit + integration)
5. Update documentation

### Add New Dependency

```bash
# From workspace root
cargo add package --package crate-name

# Or edit Cargo.toml and run
cargo update
```

### Database Migrations

```bash
# Create migration (with sqlx)
sqlx migrate add migration_name

# Run migrations
sqlx migrate run

# Revert last migration
sqlx migrate revert
```

## Troubleshooting

### Build Issues

```bash
# Clean and rebuild
cargo clean
cargo build

# Check for outdated dependencies
cargo outdated

# Update dependencies
cargo update
```

### Test Failures

```bash
# Run specific test
cargo test test_name

# Run with output
cargo test -- --nocapture

# Run single-threaded
cargo test -- --test-threads=1
```

## Decision Log

**Keep this updated with architectural decisions:**

| Date | Decision | Rationale |
|------|----------|-----------|
| YYYY-MM-DD | Chose axum over actix-web | Better type safety, simpler API |
| YYYY-MM-DD | Using sqlx with compile-time queries | Catch SQL errors at build time |

## Related Documentation

- [Rust Guidelines](~/.claude/rules/rust.md)
- [SOLID Patterns](~/.claude/projects/-Users-joe--claude/memory/rust-patterns.md)
- [Core Environment](~/.claude/projects/-Users-joe--claude/memory/MEMORY.md)
- Project README: `README.md`
- API Documentation: Run `cargo doc --open`

## Context for Claude

When working on this project:
1. Read this file FIRST (especially Quick Reference and Critical Constraints)
2. Check Decision Log for architectural context
3. Follow hexagonal architecture strictly
4. Run `cargo qa` before finishing any work
5. Update Decision Log when making architectural choices
