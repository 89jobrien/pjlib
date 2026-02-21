---
name: rust-testing-strategies
description: Comprehensive Rust testing strategies with cargo nextest, proptest, insta, mockall/mockito, and testing decision framework by project type
---

# Rust Testing Strategies

Use this skill when writing tests for Rust projects, setting up testing infrastructure, or improving test coverage.

## When to Use This Skill

**Use PROACTIVELY when:**
- Writing tests for new code
- Setting up CI/CD test pipelines
- Reviewing test coverage
- Implementing TDD workflows
- Choosing testing approaches

**Use when users request:**
- Help with test organization
- Property-based testing guidance
- Mocking strategies
- Testing framework selection
- Test coverage improvement

## Quick Decision Tree

```
What are you testing?
│
├─ Pure function → Unit test
├─ Complex algorithm → Unit test + Property test (proptest)
├─ Public API → Doc test + Unit test
├─ HTTP client/server → Mock test (mockito)
├─ Trait-based dependency → Mock test (mockall)
├─ CLI application → Integration test (assert_cmd)
├─ Complex output → Snapshot test (insta)
├─ Async code → #[tokio::test] or #[async_std::test]
└─ Database → Integration test (testcontainers)
```

## Modern Testing Stack (2026)

**Essential Tools:**
- **cargo nextest** - 3x faster test runner (industry standard)
- **proptest** - Property-based testing
- **insta** - Snapshot testing
- **mockall** - Trait mocking
- **mockito** - HTTP mocking
- **cargo-llvm-cov** - Code coverage (more accurate than tarpaulin)

**Install:**
```bash
cargo install cargo-nextest cargo-llvm-cov
```

## Testing Strategy by Project Type

### Library Crate

**Mix**: 70% unit, 15% doc, 10% integration, 5% property

```rust
// Unit test
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculation() {
        assert_eq!(calculate(2, 3), 5);
    }
}

// Doc test
/// Calculates the sum of two numbers.
///
/// # Examples
///
/// ```
/// use mylib::calculate;
/// assert_eq!(calculate(2, 3), 5);
/// ```
pub fn calculate(a: i32, b: i32) -> i32 {
    a + b
}

// Property test
#[cfg(test)]
mod proptests {
    use proptest::prelude::*;

    proptest! {
        #[test]
        fn test_commutative(a: i32, b: i32) {
            prop_assert_eq!(calculate(a, b), calculate(b, a));
        }
    }
}
```

### CLI Application

**Mix**: 50% integration, 40% unit, 10% snapshot

```rust
// Integration test using assert_cmd
#[test]
fn test_cli_help() {
    let mut cmd = Command::cargo_bin("mycli").unwrap();
    cmd.arg("--help")
        .assert()
        .success()
        .stdout(predicate::str::contains("Usage:"));
}

// Snapshot test for output
#[test]
fn test_cli_output() {
    let output = run_cli(&["list", "--format", "json"]);
    insta::assert_snapshot!(output);
}
```

### Web API

**Mix**: 45% unit, 35% integration, 15% mock, 5% property

```rust
// Integration test for API endpoint
#[tokio::test]
async fn test_create_user() {
    let app = create_test_app().await;

    let response = app
        .post("/users")
        .json(&json!({"name": "Alice", "email": "alice@example.com"}))
        .send()
        .await;

    assert_eq!(response.status(), 201);
}

// Mock external HTTP service
#[tokio::test]
async fn test_external_api() {
    let mut server = mockito::Server::new_async().await;
    let mock = server.mock("GET", "/data")
        .with_status(200)
        .with_body(r#"{"result": "success"}"#)
        .create_async()
        .await;

    let result = fetch_data(&server.url()).await;
    assert_eq!(result.unwrap(), "success");
    mock.assert_async().await;
}
```

### Database Application

**Mix**: 40% integration, 35% unit, 20% property, 5% bench

```rust
// Integration test with testcontainers
#[tokio::test]
async fn test_user_repository() {
    let postgres = testcontainers::GenericImage::new("postgres", "16")
        .with_env_var("POSTGRES_PASSWORD", "password");

    let container = postgres.start().await;
    let port = container.get_host_port_ipv4(5432).await;

    let pool = create_pool(&format!("postgres://postgres:password@localhost:{port}")).await;
    let repo = UserRepository::new(pool);

    let user = repo.create("Alice").await.unwrap();
    assert_eq!(user.name, "Alice");
}
```

## Property-Based Testing

Use proptest for testing invariants:

```rust
use proptest::prelude::*;

proptest! {
    // Test that encoding and decoding are inverses
    #[test]
    fn test_roundtrip(data: Vec<u8>) {
        let encoded = encode(&data);
        let decoded = decode(&encoded).unwrap();
        prop_assert_eq!(data, decoded);
    }

    // Test that function preserves property
    #[test]
    fn test_sorted_output(mut input: Vec<i32>) {
        let output = sort_and_deduplicate(&input);
        prop_assert!(output.windows(2).all(|w| w[0] <= w[1]));
    }
}
```

## Snapshot Testing

Use insta for testing complex output:

```rust
#[test]
fn test_json_serialization() {
    let config = Config {
        host: "localhost".into(),
        port: 8080,
        features: vec!["auth".into(), "api".into()],
    };

    let json = serde_json::to_string_pretty(&config).unwrap();
    insta::assert_snapshot!(json);
}

// Review snapshots
// cargo insta review
```

## Mocking Strategies

### Trait-Based Mocking (mockall)

```rust
use mockall::*;

#[automock]
trait UserService {
    fn get_user(&self, id: u64) -> Result<User, Error>;
}

#[test]
fn test_with_mock() {
    let mut mock = MockUserService::new();
    mock.expect_get_user()
        .with(eq(1))
        .returning(|_| Ok(User { id: 1, name: "Alice".into() }));

    let result = process_user(&mock, 1).unwrap();
    assert_eq!(result.name, "Alice");
}
```

### HTTP Mocking (mockito)

```rust
#[tokio::test]
async fn test_api_client() {
    let mut server = mockito::Server::new_async().await;

    let mock = server.mock("GET", "/users/1")
        .match_header("authorization", "Bearer token")
        .with_status(200)
        .with_json_body(json!({"id": 1, "name": "Alice"}))
        .create_async()
        .await;

    let client = ApiClient::new(&server.url());
    let user = client.get_user(1).await.unwrap();

    assert_eq!(user.name, "Alice");
    mock.assert_async().await;
}
```

## Test Organization

```
src/
├── lib.rs
└── user.rs
tests/
├── integration_test.rs     # Integration tests
└── common/
    └── mod.rs              # Shared test utilities
benches/
└── benchmark.rs            # Benchmarks
```

## Coverage Measurement

```bash
# Generate coverage report
cargo llvm-cov --html

# Check coverage threshold
cargo llvm-cov --fail-under-lines 80
```

## CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Run tests with nextest
  run: cargo nextest run --all-features

- name: Run doc tests
  run: cargo test --doc

- name: Check coverage
  run: |
    cargo llvm-cov --all-features --html
    cargo llvm-cov --fail-under-lines 80
```

## Reference Files

This skill includes detailed references:

- **`references/testing-patterns.md`** - Unit, integration, doc test patterns
- **`references/property-testing-guide.md`** - Proptest strategies, generators, shrinking
- **`references/snapshot-testing-guide.md`** - Insta patterns, review workflows
- **`references/mocking-strategies.md`** - mockall and mockito patterns
- **`references/test-organization.md`** - Project structure, common utilities
- **`references/ci-cd-testing.md`** - GitHub Actions, GitLab CI configurations

Load these files when you need detailed implementation guidance.

## Quality Metrics

### Coverage Targets

| Project Type | Minimum Coverage | Target Coverage |
|--------------|------------------|-----------------|
| Library | 80% | 90%+ |
| CLI | 70% | 85% |
| Web API | 75% | 85% |
| Critical Systems | 90% | 95%+ |

### Test Mix Guidelines

- **Unit tests**: 40-70% (higher for libraries)
- **Integration tests**: 20-50% (higher for CLIs/APIs)
- **Doc tests**: 5-15% (higher for libraries)
- **Property tests**: 5-20% (higher for algorithms)

## Best Practices

1. **Test naming**: Use descriptive names (`test_calculate_returns_sum_of_two_numbers`)
2. **Arrange-Act-Assert**: Structure tests clearly
3. **One assertion per test**: Focus tests on single behaviors
4. **Use helpers**: Extract common setup to helper functions
5. **Test errors**: Don't just test happy paths
6. **Run tests in CI/CD**: Automate with cargo nextest
7. **Review snapshots**: Use `cargo insta review` workflow
8. **Monitor coverage**: Fail CI if coverage drops

## Success Criteria

- All tests passing
- Coverage >80%
- cargo nextest configured
- Property tests for core algorithms
- Mocks for external dependencies
- Snapshot tests for complex output
- Tests run in <30 seconds (use nextest)
- CI/CD integrated
