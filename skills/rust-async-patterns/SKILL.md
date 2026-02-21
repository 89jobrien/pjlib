---
name: rust-async-patterns
description: Comprehensive Rust async/await patterns covering runtime selection, async traits, cancellation, backpressure, and blocking detection for production applications
---

# Rust Async Patterns

Use this skill when working with async Rust code, reviewing async implementations, or solving async-specific problems.

## When to Use This Skill

**Use PROACTIVELY when:**
- Reviewing async Rust code for performance issues
- Implementing async services or APIs
- Debugging async code hangs or deadlocks
- Setting up async runtime configuration
- Implementing cancellation or backpressure

**Use when users request:**
- Help with async/await patterns
- Runtime selection guidance (Tokio vs async-std)
- Cancellation handling
- Backpressure management
- Async performance optimization

## Quick Reference

### Runtime Selection Decision (2026)

**Default**: Use **Tokio** for production applications

| Use Case | Runtime | Rationale |
|----------|---------|-----------|
| Web services/APIs | **Tokio** | Ecosystem (axum, tonic), io_uring support |
| Learning async | **async-std** | Familiar std-like API |
| Embedded | **embassy** | no_std support |
| WASM | **smol** | Lightweight |

**Market share**: Tokio 85-90%, async-std 8-10%, others 2-5%

### Async Trait Patterns

**Native async traits** (Rust 1.75+) for static dispatch:

```rust
trait DataFetcher {
    async fn fetch(&self, id: u64) -> Result<String, Error>;
}

// Zero-cost abstraction
async fn process<T: DataFetcher>(fetcher: &T, id: u64) {
    fetcher.fetch(id).await.unwrap();
}
```

**async-trait crate** for dynamic dispatch:

```rust
use async_trait::async_trait;

#[async_trait]
trait Repository: Send + Sync {
    async fn save(&self, data: &str) -> Result<(), Error>;
}

// Can use Box<dyn Repository>
async fn use_repo(repo: Box<dyn Repository>) {
    repo.save("data").await.unwrap();
}
```

**Performance**: Native traits = 0% overhead, async-trait = 5-10% overhead

### Cancellation Pattern (Industry Standard)

```rust
use tokio_util::sync::CancellationToken;

async fn worker(token: CancellationToken) {
    loop {
        tokio::select! {
            _ = token.cancelled() => {
                // Cleanup
                break;
            }
            result = do_work() => {
                process(result);
            }
        }
    }
}

// Graceful shutdown
let token = CancellationToken::new();
let worker_token = token.clone();
tokio::spawn(worker(worker_token));

// Later: trigger cancellation
token.cancel();
```

### Backpressure Pattern

```rust
use tokio::sync::mpsc;

// Bounded channel provides backpressure
let (tx, mut rx) = mpsc::channel(100); // Max 100 items

// Producer will wait if channel is full
tx.send(item).await?;

// Monitor channel fill ratio
let fill_ratio = tx.capacity() as f64 / tx.max_capacity() as f64;
if fill_ratio > 0.8 {
    warn!("Channel nearly full: {}%", fill_ratio * 100.0);
}
```

### Blocking Detection

**Never block executor threads**:

```rust
// ❌ BAD: Blocks executor thread
async fn bad_example() {
    std::thread::sleep(Duration::from_secs(1)); // BLOCKS!
    heavy_cpu_work(); // BLOCKS!
    let _data = std::fs::read_to_string("file.txt"); // BLOCKS!
}

// ✅ GOOD: Use async primitives
async fn good_example() {
    tokio::time::sleep(Duration::from_secs(1)).await;

    // CPU work: use spawn_blocking
    tokio::task::spawn_blocking(|| {
        heavy_cpu_work()
    }).await.unwrap();

    // I/O: use async version
    let _data = tokio::fs::read_to_string("file.txt").await;
}
```

**Rule**: Use `spawn_blocking` for CPU work >10ms

## Common Async Pitfalls

### 1. Blocking the Executor

```rust
// ❌ WRONG: Blocks executor
async fn fetch_data() {
    let response = reqwest::blocking::get("https://api.example.com"); // BLOCKS!
}

// ✅ RIGHT: Use async client
async fn fetch_data() {
    let response = reqwest::get("https://api.example.com").await;
}
```

### 2. Missing Cancellation Handling

```rust
// ❌ WRONG: No cancellation
async fn worker() {
    loop {
        process().await;
        // Cannot stop gracefully
    }
}

// ✅ RIGHT: Cancellation support
async fn worker(token: CancellationToken) {
    loop {
        tokio::select! {
            _ = token.cancelled() => break,
            _ = process() => {}
        }
    }
}
```

### 3. Unbounded Channels

```rust
// ❌ WRONG: No backpressure
let (tx, rx) = mpsc::unbounded_channel();

// ✅ RIGHT: Bounded channel
let (tx, rx) = mpsc::channel(100); // Backpressure at 100 items
```

### 4. Holding Locks Across Await Points

```rust
// ❌ WRONG: Lock held during await
let mut data = mutex.lock().await;
async_operation().await; // Lock still held!
drop(data);

// ✅ RIGHT: Release lock before await
let value = {
    let data = mutex.lock().await;
    data.clone()
}; // Lock dropped
async_operation().await;
```

## Advanced Patterns

Load **`references/async-patterns.md`** for detailed coverage of:

### Task Spawning Patterns
- Structured concurrency with JoinSet
- Background task management
- Task cancellation strategies

### Stream Processing
- Buffering strategies
- Batching patterns
- Stream cancellation

### Error Handling
- Error propagation in async contexts
- Timeout patterns
- Retry strategies with backoff

### Performance Optimization
- Avoiding heap allocations
- Batching for efficiency
- Connection pooling

## Testing Async Code

```rust
#[tokio::test]
async fn test_async_function() {
    let result = async_operation().await;
    assert_eq!(result, expected);
}

// Test with timeout
#[tokio::test]
async fn test_with_timeout() {
    tokio::time::timeout(
        Duration::from_secs(5),
        slow_operation()
    ).await.expect("Operation timed out");
}

// Test cancellation
#[tokio::test]
async fn test_cancellation() {
    let token = CancellationToken::new();
    let handle = tokio::spawn(worker(token.clone()));

    token.cancel();
    handle.await.unwrap();
}
```

## Debugging Async Code

### tokio-console (Production Debugging)

```bash
# Enable in Cargo.toml
[dependencies]
console-subscriber = "0.2"

# In main.rs
console_subscriber::init();

# Run console
tokio-console
```

### Clippy Lints

Enable async-specific lints:

```toml
[lints.clippy]
await_holding_lock = "deny"
await_holding_refcell_ref = "deny"
```

## Reference Files

This skill includes detailed references:

- **`references/async-patterns.md`** - Task spawning, stream processing, error handling, performance optimization
- **`references/runtime-selection.md`** - Detailed comparison of Tokio, async-std, smol, embassy with migration guides
- **`references/cancellation-patterns.md`** - CancellationToken, JoinSet, graceful shutdown, signal handling
- **`references/backpressure-strategies.md`** - Bounded channels, semaphores, stream backpressure, monitoring
- **`references/blocking-detection.md`** - Detection tools, spawn_blocking patterns, async primitive usage

Load these files when you need detailed implementation guidance.

## CI/CD Integration

```yaml
# .github/workflows/async-checks.yml
- name: Check for blocking code
  run: |
    cargo clippy -- \
      -D clippy::await_holding_lock \
      -D clippy::await_holding_refcell_ref

- name: Run async tests
  run: cargo nextest run --features tokio-console
```

## Success Metrics

- Zero blocking operations in async contexts
- CancellationToken used for all long-running tasks
- Bounded channels for all producer-consumer patterns
- tokio-console enabled for debugging
- Clippy async lints passing
- Proper error propagation and timeout handling
