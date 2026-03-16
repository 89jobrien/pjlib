---
paths: ["**/*.rs", "**/Cargo.toml"]
---

# Rust Rules

## Project Structure

```text
project/
├── Cargo.toml              # Project manifest
├── Cargo.lock             # Dependency lock (commit this)
├── README.md
├── src/
│   ├── lib.rs             # Library root
│   ├── main.rs            # Binary root
│   ├── bin/               # Additional binaries
│   │   └── tool.rs
│   └── modules/
│       ├── mod.rs
│       └── core.rs
├── tests/                 # Integration tests
│   └── integration_test.rs
├── benches/               # Benchmarks
│   └── benchmark.rs
└── examples/              # Example code
    └── basic.rs
```

**Projects location**: `~/dev/`

## Cargo Commands

```bash
# Build
cargo build                # Debug build
cargo build --release      # Release build

# Run
cargo run                  # Run main binary
cargo run --bin tool       # Run specific binary
cargo run --example basic  # Run example

# Test
cargo test                 # Run all tests
cargo test --lib           # Library tests only
cargo test integration     # Specific test
cargo nextest run          # Use nextest if available

# Check & Lint
cargo check                # Type check without building
cargo clippy               # Linting
cargo clippy -- -D warnings  # Deny warnings
cargo fmt                  # Format code

# Dependencies
cargo add package          # Add dependency
cargo add --dev package    # Add dev dependency
cargo update              # Update dependencies
cargo tree                # Show dependency tree
```

## Code Style

### Naming Conventions

```rust
// Modules, types, traits: PascalCase
mod my_module;
struct UserAccount;
enum Status;
trait Validate;

// Functions, variables: snake_case
fn process_data() {}
let user_count = 0;
const MAX_SIZE: usize = 100;

// Type parameters: Single capital letter or PascalCase
fn generic<T>(item: T) {}
fn convert<Input, Output>(input: Input) -> Output {}

// Lifetimes: short, lowercase
fn parse<'a>(input: &'a str) -> &'a str {}
```

### Module Organization

```rust
// lib.rs or main.rs
mod config;
mod database;
mod handlers;
mod models;
mod utils;

pub use config::Config;
pub use models::{User, Post};

// Re-export commonly used items
pub mod prelude {
    pub use crate::config::Config;
    pub use crate::models::*;
}
```

### Error Handling

**Use Result<T, E> for recoverable errors:**

```rust
use std::fs;
use std::io;

// Good - explicit error types
fn load_config(path: &str) -> Result<String, io::Error> {
    fs::read_to_string(path)
}

// Better - custom error type
#[derive(Debug, thiserror::Error)]
enum ConfigError {
    #[error("IO error: {0}")]
    Io(#[from] io::Error),
    #[error("Parse error: {0}")]
    Parse(String),
}

fn parse_config(path: &str) -> Result<Config, ConfigError> {
    let content = fs::read_to_string(path)?;
    serde_yaml::from_str(&content)
        .map_err(|e| ConfigError::Parse(e.to_string()))
}
```

**Use Option<T> for absence:**

```rust
// Good - explicit about absence
fn find_user(id: u64) -> Option<User> {
    users.iter().find(|u| u.id == id).cloned()
}

// Pattern matching
match find_user(123) {
    Some(user) => println!("Found: {}", user.name),
    None => println!("User not found"),
}

// Or use combinators
let name = find_user(123)
    .map(|u| u.name.clone())
    .unwrap_or_else(|| "Unknown".to_string());
```

**Never use unwrap() in production code:**

```rust
// Bad - will panic
let config = load_config("config.yaml").unwrap();

// Good - handle errors
let config = load_config("config.yaml")
    .expect("Failed to load config: config.yaml must exist");

// Better - propagate errors
let config = load_config("config.yaml")?;

// Best - provide context
let config = load_config("config.yaml")
    .context("Loading application configuration")?;
```

## Type Safety

### Use the Type System

```rust
// Bad - stringly typed
fn process_user(role: &str) -> bool {
    role == "admin" || role == "moderator"
}

// Good - strong types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Role {
    User,
    Moderator,
    Admin,
}

fn process_user(role: Role) -> bool {
    matches!(role, Role::Admin | Role::Moderator)
}
```

### Newtype Pattern

```rust
// Prevent mixing up similar types
struct UserId(u64);
struct PostId(u64);
struct Timestamp(i64);

// Can't accidentally use PostId where UserId expected
fn get_user(id: UserId) -> Option<User> {
    // ...
}

// Call with
get_user(UserId(123));
// get_user(PostId(456));  // Compile error!
```

### Builder Pattern

```rust
#[derive(Debug)]
struct Config {
    host: String,
    port: u16,
    timeout: u64,
}

impl Config {
    fn builder() -> ConfigBuilder {
        ConfigBuilder::default()
    }
}

#[derive(Default)]
struct ConfigBuilder {
    host: Option<String>,
    port: Option<u16>,
    timeout: Option<u64>,
}

impl ConfigBuilder {
    fn host(mut self, host: impl Into<String>) -> Self {
        self.host = Some(host.into());
        self
    }

    fn port(mut self, port: u16) -> Self {
        self.port = Some(port);
        self
    }

    fn build(self) -> Result<Config, String> {
        Ok(Config {
            host: self.host.ok_or("host is required")?,
            port: self.port.unwrap_or(8080),
            timeout: self.timeout.unwrap_or(30),
        })
    }
}

// Usage
let config = Config::builder()
    .host("localhost")
    .port(3000)
    .build()?;
```

## SOLID Principles in Rust

### Single Responsibility

```rust
// Bad - multiple responsibilities
struct UserManager {
    users: Vec<User>,
    db: Database,
}

impl UserManager {
    fn save_user(&mut self, user: User) { /* ... */ }
    fn send_email(&self, user: &User) { /* ... */ }
    fn log_activity(&self, msg: &str) { /* ... */ }
}

// Good - separated concerns
struct UserRepository {
    db: Database,
}

impl UserRepository {
    fn save(&self, user: &User) -> Result<(), Error> { /* ... */ }
    fn find(&self, id: UserId) -> Result<Option<User>, Error> { /* ... */ }
}

struct EmailService {
    smtp: SmtpClient,
}

impl EmailService {
    fn send(&self, to: &str, subject: &str, body: &str) -> Result<(), Error> {
        /* ... */
    }
}
```

### Dependency Inversion (Traits)

```rust
// Define trait for abstraction
trait UserRepository {
    fn find(&self, id: UserId) -> Result<Option<User>, Error>;
    fn save(&self, user: &User) -> Result<(), Error>;
}

// Concrete implementations
struct PostgresUserRepository {
    pool: PgPool,
}

impl UserRepository for PostgresUserRepository {
    fn find(&self, id: UserId) -> Result<Option<User>, Error> {
        // PostgreSQL implementation
    }

    fn save(&self, user: &User) -> Result<(), Error> {
        // PostgreSQL implementation
    }
}

// Depend on trait, not concrete type
struct UserService<R: UserRepository> {
    repo: R,
}

impl<R: UserRepository> UserService<R> {
    fn new(repo: R) -> Self {
        Self { repo }
    }

    fn get_user(&self, id: UserId) -> Result<Option<User>, Error> {
        self.repo.find(id)
    }
}
```

## Async/Await with Tokio

```rust
use tokio;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let result = fetch_data("https://api.example.com").await?;
    println!("Result: {}", result);
    Ok(())
}

async fn fetch_data(url: &str) -> Result<String, reqwest::Error> {
    let response = reqwest::get(url).await?;
    let body = response.text().await?;
    Ok(body)
}

// Concurrent operations
async fn fetch_multiple() -> Result<(), Error> {
    let (result1, result2, result3) = tokio::join!(
        fetch_data("url1"),
        fetch_data("url2"),
        fetch_data("url3"),
    );

    // Handle results
    Ok(())
}

// Spawning tasks
async fn background_work() {
    let handle = tokio::spawn(async {
        // Background task
        process_data().await
    });

    // Wait for completion
    let result = handle.await.unwrap();
}
```

## Testing

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_user_creation() {
        let user = User::new("alice", "alice@example.com");
        assert_eq!(user.name, "alice");
        assert_eq!(user.email, "alice@example.com");
    }

    #[test]
    #[should_panic(expected = "email is required")]
    fn test_invalid_email() {
        User::new("alice", "");
    }

    #[tokio::test]
    async fn test_async_operation() {
        let result = fetch_data("url").await;
        assert!(result.is_ok());
    }
}
```

### Property-Based Testing (proptest)

```rust
#[cfg(test)]
mod tests {
    use proptest::prelude::*;

    proptest! {
        #[test]
        fn test_roundtrip(s in "\\PC*") {
            let encoded = encode(&s);
            let decoded = decode(&encoded)?;
            prop_assert_eq!(s, decoded);
        }

        #[test]
        fn test_sorting(mut vec in prop::collection::vec(any::<i32>(), 0..100)) {
            vec.sort();
            // Check sorted property
            for i in 1..vec.len() {
                prop_assert!(vec[i-1] <= vec[i]);
            }
        }
    }
}
```

### Integration Tests

```rust
// tests/integration_test.rs
use my_crate::*;

#[tokio::test]
async fn test_full_workflow() {
    let config = Config::from_env().expect("config");
    let service = UserService::new(config);

    let user = service.create_user("alice").await.unwrap();
    assert_eq!(user.name, "alice");

    let found = service.find_user(user.id).await.unwrap();
    assert!(found.is_some());
}
```

## Common Patterns

### Option/Result Combinators

```rust
// map, and_then, or_else
let result = find_user(123)
    .map(|u| u.email.clone())
    .ok_or("User not found")?;

// unwrap_or, unwrap_or_else, unwrap_or_default
let name = user.name.unwrap_or_default();
let count = cache.get("count").unwrap_or_else(|| fetch_count());

// ?operator for early return
fn process() -> Result<(), Error> {
    let config = load_config()?;
    let db = connect_db(&config)?;
    Ok(())
}
```

### Iterator Patterns

```rust
// Prefer iterators over loops
let sum: i32 = numbers.iter().sum();
let doubled: Vec<i32> = numbers.iter().map(|x| x * 2).collect();
let evens: Vec<i32> = numbers.iter().filter(|x| x % 2 == 0).collect();

// Chain operations
let result = users
    .iter()
    .filter(|u| u.active)
    .map(|u| &u.email)
    .collect::<Vec<_>>();

// find, any, all
let admin = users.iter().find(|u| u.role == Role::Admin);
let has_admin = users.iter().any(|u| u.role == Role::Admin);
let all_active = users.iter().all(|u| u.active);
```

### Ownership Patterns

```rust
// Borrow when you don't need ownership
fn print_user(user: &User) {
    println!("{}", user.name);
}

// Take ownership when transferring
fn consume_user(user: User) {
    // user is moved here
}

// Clone when you need an independent copy
let user_copy = user.clone();

// Use Cow for conditionally owned data
use std::borrow::Cow;

fn process_text(input: &str) -> Cow<str> {
    if input.contains("old") {
        Cow::Owned(input.replace("old", "new"))
    } else {
        Cow::Borrowed(input)
    }
}
```

## Performance

### Avoid Unnecessary Allocations

```rust
// Bad - allocates string
fn get_greeting(name: String) -> String {
    format!("Hello, {}!", name)
}

// Good - borrow
fn get_greeting(name: &str) -> String {
    format!("Hello, {}!", name)
}

// Better - return Cow when sometimes borrowed
fn get_greeting(name: &str) -> Cow<str> {
    if name.is_empty() {
        Cow::Borrowed("Hello, stranger!")
    } else {
        Cow::Owned(format!("Hello, {}!", name))
    }
}
```

### Use References

```rust
// Bad - cloning in loop
for user in &users {
    process_user(user.clone());
}

// Good - pass reference
for user in &users {
    process_user(user);
}

fn process_user(user: &User) {
    // ...
}
```

## Essential Crates

### Must-Have

```toml
[dependencies]
# Error handling
thiserror = "1.0"          # Derive error types
anyhow = "1.0"             # Flexible error handling

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Async runtime
tokio = { version = "1.36", features = ["full"] }

# Logging
tracing = "0.1"
tracing-subscriber = "0.3"

[dev-dependencies]
# Testing
proptest = "1.4"           # Property-based testing
```

### Common Tools

```toml
# HTTP client
reqwest = { version = "0.11", features = ["json"] }

# HTTP server
axum = "0.7"

# Database
sqlx = { version = "0.7", features = ["postgres", "runtime-tokio"] }

# CLI
clap = { version = "4.5", features = ["derive"] }

# Time
chrono = "0.4"
```

## Best Practices

### DO

- Use `cargo clippy` before every commit
- Run `cargo fmt` to format code
- Write doc comments for public APIs
- Use `Result<T, E>` for errors, `Option<T>` for absence
- Prefer borrowing over cloning
- Use `#[derive]` for common traits
- Make fields private by default
- Use type aliases for complex types

### DON'T

- Use `unwrap()` or `expect()` in production (except for `Mutex` poisoning)
- Clone unnecessarily
- Use `panic!()` for expected errors
- Ignore Clippy warnings without good reason
- Make everything public
- Use `unsafe` without documentation
- Mutate through `Arc` without proper synchronization

## Documentation

```rust
/// Represents a user in the system.
///
/// # Examples
///
/// ```
/// use myapp::User;
///
/// let user = User::new("alice", "alice@example.com");
/// assert_eq!(user.name, "alice");
/// ```
pub struct User {
    /// The user's unique identifier
    pub id: UserId,
    /// The user's display name
    pub name: String,
}

impl User {
    /// Creates a new user with the given name and email.
    ///
    /// # Arguments
    ///
    /// * `name` - The user's display name
    /// * `email` - The user's email address
    ///
    /// # Returns
    ///
    /// Returns a new `User` instance
    ///
    /// # Panics
    ///
    /// Panics if the email is empty
    pub fn new(name: impl Into<String>, email: impl Into<String>) -> Self {
        // ...
    }
}
```

## Project Setup Checklist

- [ ] Run `cargo init` or `cargo new project-name`
- [ ] Set up `.gitignore` (include `target/`, `Cargo.lock` for libraries)
- [ ] Configure `Cargo.toml` with metadata
- [ ] Set up CI/CD with `cargo test` and `cargo clippy`
- [ ] Add `rust-toolchain.toml` for consistent toolchain version
- [ ] Configure pre-commit hooks for `fmt` and `clippy`
- [ ] Add README with build instructions
- [ ] Set up logging with `tracing`
