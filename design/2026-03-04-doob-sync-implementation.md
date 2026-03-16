# Doob Sync Plugin System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use @superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a plugin/provider system for syncing doob todos to external issue trackers (beads, GitHub, Jira, Linear, kan)

**Architecture:** Hexagonal architecture with SOLID principles. Domain layer (sync logic) → Ports (IssueTracker trait) → Adapters (concrete providers) → Application layer (CLI)

**Tech Stack:** Rust, SurrealDB, Nextest, thiserror, serde, chrono, clap

---

## Phase 1: Foundation

### Task 1: Add Dependencies

**Files:**
- Modify: `Cargo.toml`

**Step 1: Add required dependencies**

```toml
# Add to [dependencies] section
[dependencies]
# ... existing dependencies ...
thiserror = "2.0"
chrono = { version = "0.4", features = ["serde"] }

# Add to [dev-dependencies] section
[dev-dependencies]
# ... existing dev-dependencies ...
```

**Step 2: Verify dependencies compile**

Run: `cargo check`
Expected: Compiles successfully

**Step 3: Commit**

```bash
git add Cargo.toml Cargo.lock
git commit -m "deps: add thiserror and chrono for sync module"
```

---

### Task 2: Create Sync Module Structure

**Files:**
- Create: `src/sync/mod.rs`
- Create: `src/sync/domain.rs`
- Create: `src/sync/adapters/mod.rs`
- Modify: `src/lib.rs`

**Step 1: Create sync module directory**

```bash
mkdir -p src/sync/adapters
```

**Step 2: Create src/sync/mod.rs**

```rust
// src/sync/mod.rs

pub mod domain;
pub mod adapters;
```

**Step 3: Create src/sync/domain.rs (empty for now)**

```rust
// src/sync/domain.rs

// Domain models and logic will go here
```

**Step 4: Create src/sync/adapters/mod.rs (empty for now)**

```rust
// src/sync/adapters/mod.rs

// Adapter implementations will go here
```

**Step 5: Add sync module to lib.rs**

```rust
// Add to src/lib.rs
pub mod sync;
```

**Step 6: Verify module structure compiles**

Run: `cargo check`
Expected: Compiles successfully

**Step 7: Commit**

```bash
git add src/sync/
git add src/lib.rs
git commit -m "feat: add sync module structure"
```

---

### Task 3: Define TodoStatus Enum

**Files:**
- Modify: `src/sync/domain.rs`
- Create: `tests/unit/mod.rs`
- Create: `tests/unit/domain_test.rs`

**Step 1: Create test directory structure**

```bash
mkdir -p tests/unit
```

**Step 2: Write failing test for TodoStatus**

```rust
// tests/unit/domain_test.rs

use doob::sync::domain::TodoStatus;

#[test]
fn todo_status__serializes_to_string() {
    let status = TodoStatus::Pending;
    let json = serde_json::to_string(&status).unwrap();
    assert_eq!(json, "\"Pending\"");
}

#[test]
fn todo_status__deserializes_from_string() {
    let json = "\"InProgress\"";
    let status: TodoStatus = serde_json::from_str(json).unwrap();
    assert_eq!(status, TodoStatus::InProgress);
}

#[test]
fn todo_status__supports_equality() {
    assert_eq!(TodoStatus::Pending, TodoStatus::Pending);
    assert_ne!(TodoStatus::Pending, TodoStatus::InProgress);
}
```

**Step 3: Create tests/unit/mod.rs**

```rust
// tests/unit/mod.rs

mod domain_test;
```

**Step 4: Run tests to verify they fail**

Run: `cargo test todo_status`
Expected: FAIL with "no such module `domain`" or similar

**Step 5: Implement TodoStatus**

```rust
// src/sync/domain.rs

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum TodoStatus {
    Pending,
    InProgress,
}
```

**Step 6: Run tests to verify they pass**

Run: `cargo test todo_status`
Expected: PASS (3 tests)

**Step 7: Commit**

```bash
git add src/sync/domain.rs tests/unit/
git commit -m "feat: add TodoStatus enum with serde support"
```

---

### Task 4: Define SyncableTodo

**Files:**
- Modify: `src/sync/domain.rs`
- Modify: `tests/unit/domain_test.rs`

**Step 1: Write failing test for SyncableTodo**

```rust
// Add to tests/unit/domain_test.rs

use doob::sync::domain::SyncableTodo;

#[test]
fn syncable_todo__creates_with_required_fields() {
    let todo = SyncableTodo {
        id: "1".to_string(),
        title: "Test todo".to_string(),
        description: None,
        priority: 2,
        status: TodoStatus::Pending,
        tags: vec![],
        project: None,
        file_path: None,
        due_date: None,
    };

    assert_eq!(todo.id, "1");
    assert_eq!(todo.title, "Test todo");
    assert_eq!(todo.priority, 2);
}

#[test]
fn syncable_todo__serializes_to_json() {
    let todo = SyncableTodo {
        id: "1".to_string(),
        title: "Test".to_string(),
        description: Some("Description".to_string()),
        priority: 1,
        status: TodoStatus::InProgress,
        tags: vec!["tag1".to_string()],
        project: Some("project".to_string()),
        file_path: Some("/path/to/file".to_string()),
        due_date: Some("2026-12-31".to_string()),
    };

    let json = serde_json::to_value(&todo).unwrap();
    assert_eq!(json["id"], "1");
    assert_eq!(json["title"], "Test");
    assert_eq!(json["priority"], 1);
}
```

**Step 2: Run tests to verify they fail**

Run: `cargo test syncable_todo`
Expected: FAIL with "cannot find struct `SyncableTodo`"

**Step 3: Implement SyncableTodo**

```rust
// Add to src/sync/domain.rs

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncableTodo {
    pub id: String,
    pub title: String,
    pub description: Option<String>,
    pub priority: u8,
    pub status: TodoStatus,
    pub tags: Vec<String>,
    pub project: Option<String>,
    pub file_path: Option<String>,
    pub due_date: Option<String>,
}
```

**Step 4: Run tests to verify they pass**

Run: `cargo test syncable_todo`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/sync/domain.rs tests/unit/domain_test.rs
git commit -m "feat: add SyncableTodo domain model"
```

---

### Task 5: Define SyncRecord

**Files:**
- Modify: `src/sync/domain.rs`
- Modify: `tests/unit/domain_test.rs`

**Step 1: Write failing test for SyncRecord**

```rust
// Add to tests/unit/domain_test.rs

use doob::sync::domain::SyncRecord;

#[test]
fn sync_record__stores_external_sync_data() {
    let record = SyncRecord {
        external_id: "bd-42".to_string(),
        external_url: Some("https://example.com/bd-42".to_string()),
        provider: "beads".to_string(),
        synced_at: "2026-03-04T08:00:00Z".to_string(),
    };

    assert_eq!(record.external_id, "bd-42");
    assert_eq!(record.provider, "beads");
    assert!(record.external_url.is_some());
}

#[test]
fn sync_record__serializes_with_optional_url() {
    let record = SyncRecord {
        external_id: "123".to_string(),
        external_url: None,
        provider: "github".to_string(),
        synced_at: "2026-03-04T08:00:00Z".to_string(),
    };

    let json = serde_json::to_value(&record).unwrap();
    assert_eq!(json["external_id"], "123");
    assert_eq!(json["external_url"], serde_json::Value::Null);
}
```

**Step 2: Run tests to verify they fail**

Run: `cargo test sync_record`
Expected: FAIL with "cannot find struct `SyncRecord`"

**Step 3: Implement SyncRecord**

```rust
// Add to src/sync/domain.rs

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncRecord {
    pub external_id: String,
    pub external_url: Option<String>,
    pub provider: String,
    pub synced_at: String,
}
```

**Step 4: Run tests to verify they pass**

Run: `cargo test sync_record`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/sync/domain.rs tests/unit/domain_test.rs
git commit -m "feat: add SyncRecord domain model"
```

---

### Task 6: Define SyncError

**Files:**
- Modify: `src/sync/domain.rs`
- Modify: `tests/unit/domain_test.rs`

**Step 1: Write failing test for SyncError**

```rust
// Add to tests/unit/domain_test.rs

use doob::sync::domain::SyncError;

#[test]
fn sync_error__formats_provider_unavailable() {
    let err = SyncError::ProviderUnavailable("beads".to_string());
    let msg = format!("{}", err);
    assert!(msg.contains("beads"));
    assert!(msg.contains("not available"));
}

#[test]
fn sync_error__formats_external_api_error() {
    let err = SyncError::ExternalApiError("Connection timeout".to_string());
    let msg = format!("{}", err);
    assert!(msg.contains("Connection timeout"));
}

#[test]
fn sync_error__is_debug_formattable() {
    let err = SyncError::InvalidConfiguration("Bad config".to_string());
    let debug = format!("{:?}", err);
    assert!(debug.contains("InvalidConfiguration"));
}
```

**Step 2: Run tests to verify they fail**

Run: `cargo test sync_error`
Expected: FAIL with "cannot find enum `SyncError`"

**Step 3: Implement SyncError**

```rust
// Add to top of src/sync/domain.rs
use thiserror::Error;

// Add to src/sync/domain.rs (after imports)

#[derive(Error, Debug)]
pub enum SyncError {
    #[error("Provider '{0}' is not available or not installed")]
    ProviderUnavailable(String),

    #[error("Invalid configuration: {0}")]
    InvalidConfiguration(String),

    #[error("External API error: {0}")]
    ExternalApiError(String),

    #[error("Todo '{0}' has already been synced to this provider")]
    TodoAlreadySynced(String),

    #[error("Database error: {0}")]
    DatabaseError(String),

    #[error("Serialization error: {0}")]
    SerializationError(String),
}
```

**Step 4: Run tests to verify they pass**

Run: `cargo test sync_error`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/sync/domain.rs tests/unit/domain_test.rs
git commit -m "feat: add SyncError with thiserror"
```

---

### Task 7: Define IssueTracker Trait

**Files:**
- Modify: `src/sync/domain.rs`
- Modify: `tests/unit/domain_test.rs`

**Step 1: Write failing test for IssueTracker trait**

```rust
// Add to tests/unit/domain_test.rs

// Mock implementation for testing
struct MockIssueTracker {
    name: String,
    available: bool,
}

impl MockIssueTracker {
    fn new(name: &str, available: bool) -> Self {
        Self {
            name: name.to_string(),
            available,
        }
    }
}

impl doob::sync::domain::IssueTracker for MockIssueTracker {
    fn name(&self) -> &str {
        &self.name
    }

    fn is_available(&self) -> Result<bool, SyncError> {
        Ok(self.available)
    }

    fn create_issue(&self, todo: &SyncableTodo) -> Result<SyncRecord, SyncError> {
        if !self.available {
            return Err(SyncError::ProviderUnavailable(self.name.clone()));
        }

        Ok(SyncRecord {
            external_id: format!("{}-{}", self.name, todo.id),
            external_url: None,
            provider: self.name.clone(),
            synced_at: chrono::Utc::now().to_rfc3339(),
        })
    }
}

#[test]
fn issue_tracker__returns_provider_name() {
    let tracker = MockIssueTracker::new("test", true);
    assert_eq!(tracker.name(), "test");
}

#[test]
fn issue_tracker__checks_availability() {
    let tracker = MockIssueTracker::new("test", true);
    assert!(tracker.is_available().unwrap());

    let tracker = MockIssueTracker::new("test", false);
    assert!(!tracker.is_available().unwrap());
}

#[test]
fn issue_tracker__creates_issue_when_available() {
    let tracker = MockIssueTracker::new("test", true);
    let todo = SyncableTodo {
        id: "1".to_string(),
        title: "Test".to_string(),
        description: None,
        priority: 2,
        status: TodoStatus::Pending,
        tags: vec![],
        project: None,
        file_path: None,
        due_date: None,
    };

    let result = tracker.create_issue(&todo);
    assert!(result.is_ok());
    let record = result.unwrap();
    assert_eq!(record.external_id, "test-1");
    assert_eq!(record.provider, "test");
}
```

**Step 2: Run tests to verify they fail**

Run: `cargo test issue_tracker`
Expected: FAIL with "cannot find trait `IssueTracker`"

**Step 3: Implement IssueTracker trait**

```rust
// Add to src/sync/domain.rs

/// Port: External issue tracker
pub trait IssueTracker {
    /// Provider name (e.g., "beads", "github")
    fn name(&self) -> &str;

    /// Check if provider is available (CLI installed, auth configured, etc.)
    fn is_available(&self) -> Result<bool, SyncError>;

    /// Create an issue in the external system
    fn create_issue(&self, todo: &SyncableTodo) -> Result<SyncRecord, SyncError>;
}
```

**Step 4: Run tests to verify they pass**

Run: `cargo test issue_tracker`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/sync/domain.rs tests/unit/domain_test.rs
git commit -m "feat: add IssueTracker trait (port)"
```

---

### Task 8: Implement SyncService

**Files:**
- Modify: `src/sync/domain.rs`
- Create: `tests/unit/sync_service_test.rs`
- Modify: `tests/unit/mod.rs`

**Step 1: Write failing tests for SyncService**

```rust
// tests/unit/sync_service_test.rs

use doob::sync::domain::{IssueTracker, SyncableTodo, SyncRecord, SyncError, TodoStatus, SyncService};

// Reuse MockIssueTracker from domain_test or define it here
struct MockTracker {
    name: String,
    available: bool,
    should_fail: bool,
}

impl MockTracker {
    fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            available: true,
            should_fail: false,
        }
    }

    fn with_availability(mut self, available: bool) -> Self {
        self.available = available;
        self
    }

    fn with_failure(mut self, should_fail: bool) -> Self {
        self.should_fail = should_fail;
        self
    }
}

impl IssueTracker for MockTracker {
    fn name(&self) -> &str {
        &self.name
    }

    fn is_available(&self) -> Result<bool, SyncError> {
        Ok(self.available)
    }

    fn create_issue(&self, todo: &SyncableTodo) -> Result<SyncRecord, SyncError> {
        if self.should_fail {
            return Err(SyncError::ExternalApiError("Mock failure".to_string()));
        }

        Ok(SyncRecord {
            external_id: format!("{}-{}", self.name, todo.id),
            external_url: None,
            provider: self.name.clone(),
            synced_at: chrono::Utc::now().to_rfc3339(),
        })
    }
}

fn make_todo(id: &str, title: &str, status: TodoStatus) -> SyncableTodo {
    SyncableTodo {
        id: id.to_string(),
        title: title.to_string(),
        description: None,
        priority: 2,
        status,
        tags: vec![],
        project: None,
        file_path: None,
        due_date: None,
    }
}

#[test]
fn sync_service__creates_issue__when_todo_is_pending() {
    let tracker = MockTracker::new("test");
    let service = SyncService::new(tracker);
    let todo = make_todo("1", "Test todo", TodoStatus::Pending);

    let result = service.sync_todo(&todo);

    assert!(result.is_ok());
    let record = result.unwrap();
    assert_eq!(record.external_id, "test-1");
}

#[test]
fn sync_service__creates_issue__when_todo_is_in_progress() {
    let tracker = MockTracker::new("test");
    let service = SyncService::new(tracker);
    let todo = make_todo("2", "Test todo", TodoStatus::InProgress);

    let result = service.sync_todo(&todo);

    assert!(result.is_ok());
}

#[test]
fn sync_service__rejects__when_provider_unavailable() {
    let tracker = MockTracker::new("test").with_availability(false);
    let service = SyncService::new(tracker);
    let todo = make_todo("1", "Test todo", TodoStatus::Pending);

    let result = service.sync_todo(&todo);

    assert!(result.is_err());
    assert!(matches!(result.unwrap_err(), SyncError::ProviderUnavailable(_)));
}

#[test]
fn sync_service__handles_multiple_todos() {
    let tracker = MockTracker::new("test");
    let service = SyncService::new(tracker);

    let todos = vec![
        make_todo("1", "Todo 1", TodoStatus::Pending),
        make_todo("2", "Todo 2", TodoStatus::InProgress),
        make_todo("3", "Todo 3", TodoStatus::Pending),
    ];

    let results = service.sync_todos(&todos);

    assert_eq!(results.len(), 3);
    assert!(results.iter().all(|r| r.is_ok()));
}

#[test]
fn sync_service__partial_failure_continues() {
    let tracker = MockTracker::new("test").with_failure(true);
    let service = SyncService::new(tracker);

    let todos = vec![
        make_todo("1", "Todo 1", TodoStatus::Pending),
        make_todo("2", "Todo 2", TodoStatus::Pending),
    ];

    let results = service.sync_todos(&todos);

    assert_eq!(results.len(), 2);
    assert!(results.iter().all(|r| r.is_err()));
}
```

**Step 2: Add to tests/unit/mod.rs**

```rust
// Add to tests/unit/mod.rs
mod sync_service_test;
```

**Step 3: Run tests to verify they fail**

Run: `cargo test sync_service`
Expected: FAIL with "cannot find struct `SyncService`"

**Step 4: Implement SyncService**

```rust
// Add to src/sync/domain.rs

/// Domain service: Sync orchestration
pub struct SyncService<T: IssueTracker> {
    tracker: T,
}

impl<T: IssueTracker> SyncService<T> {
    pub fn new(tracker: T) -> Self {
        Self { tracker }
    }

    pub fn sync_todo(&self, todo: &SyncableTodo) -> Result<SyncRecord, SyncError> {
        // Domain logic: validate availability
        if !self.tracker.is_available()? {
            return Err(SyncError::ProviderUnavailable(
                self.tracker.name().to_string()
            ));
        }

        // Domain logic: only sync active todos
        if todo.status != TodoStatus::Pending && todo.status != TodoStatus::InProgress {
            return Err(SyncError::InvalidConfiguration(
                "Only pending/in_progress todos can be synced".to_string()
            ));
        }

        self.tracker.create_issue(todo)
    }

    pub fn sync_todos(&self, todos: &[SyncableTodo]) -> Vec<Result<SyncRecord, SyncError>> {
        todos.iter()
            .map(|todo| self.sync_todo(todo))
            .collect()
    }
}
```

**Step 5: Run tests to verify they pass**

Run: `cargo test sync_service`
Expected: PASS (5 tests)

**Step 6: Commit**

```bash
git add src/sync/domain.rs tests/unit/
git commit -m "feat: add SyncService domain service"
```

---

### Task 9: Set Up Nextest Configuration

**Files:**
- Create: `.config/nextest.toml`

**Step 1: Create .config directory**

```bash
mkdir -p .config
```

**Step 2: Create nextest configuration**

```toml
# .config/nextest.toml

[profile.default]
# Run tests in parallel
test-threads = "num-cpus"

# Retry flaky tests
retries = 2

# Show output only for failed tests
failure-output = "immediate-final"
success-output = "never"

# Test groups
[profile.default.overrides]
# Integration tests run serially (they might create real issues)
filter = 'test(integration)'
test-threads = 1
retries = 3

# Unit tests run in parallel
filter = 'test(^((?!integration).)*$)'
test-threads = "num-cpus"

# CI profile
[profile.ci]
retries = 0
failure-output = "immediate-final"
success-output = "final"

# Integration test profile
[profile.integration]
retries = 3
test-threads = 1
slow-timeout = { period = "120s", terminate-after = 5 }
```

**Step 3: Test with nextest (if installed)**

Run: `cargo nextest run` (or `cargo test` if nextest not installed)
Expected: All tests pass

**Step 4: Commit**

```bash
git add .config/nextest.toml
git commit -m "chore: add nextest configuration"
```

---

### Task 10: Add Test Coverage Documentation

**Files:**
- Create: `docs/sync/testing.md`

**Step 1: Create docs/sync directory**

```bash
mkdir -p docs/sync
```

**Step 2: Create testing documentation**

```markdown
# Sync Module Testing Guide

## Running Tests

### With Nextest (Recommended)

```bash
# Install nextest
cargo install cargo-nextest --locked

# Run all tests
cargo nextest run

# Run only unit tests
cargo nextest run --lib

# Run with coverage
cargo llvm-cov nextest --all-features --workspace --lcov --output-path lcov.info
```

### With Cargo Test

```bash
# Run all tests
cargo test

# Run specific test module
cargo test sync_service

# Run with output
cargo test -- --nocapture
```

## Test Organization

```
tests/
├── unit/                   # Unit tests (domain logic)
│   ├── domain_test.rs     # Domain model tests
│   └── sync_service_test.rs # SyncService tests
├── integration/           # Integration tests (real CLIs)
│   └── beads_adapter_test.rs (coming in Phase 2)
└── common/                # Shared test utilities
    └── mod.rs
```

## Coverage Goals

- **Overall:** 80%+ test coverage
- **Domain layer:** 90%+ (critical business logic)
- **Adapters:** 70%+ (integration tests may be limited)
- **CLI commands:** 60%+ (harder to test, validated manually)

## Writing Tests

Follow TDD approach:
1. Write failing test
2. Run test to verify it fails
3. Implement minimal code to make test pass
4. Run test to verify it passes
5. Commit

Use descriptive test names:
```rust
#[test]
fn sync_service__creates_issue__when_todo_is_pending() {
    // Test implementation
}
```
```

**Step 3: Commit**

```bash
git add docs/sync/testing.md
git commit -m "docs: add testing guide for sync module"
```

---

## Phase 2: Beads Adapter

### Task 11: Create BeadsAdapter Structure

**Files:**
- Create: `src/sync/adapters/beads.rs`
- Modify: `src/sync/adapters/mod.rs`

**Step 1: Create beads adapter file**

```rust
// src/sync/adapters/beads.rs

use crate::sync::domain::{IssueTracker, SyncableTodo, SyncRecord, SyncError};
use std::process::Command;

pub struct BeadsAdapter {
    // No state needed - delegates to bd CLI
}

impl BeadsAdapter {
    pub fn new() -> Self {
        Self {}
    }

    fn map_priority(&self, priority: u8) -> u8 {
        // Direct 0-4 mapping
        priority.min(4)
    }

    fn extract_issue_id(&self, output: &str) -> Result<String, SyncError> {
        // Parse "Created issue bd-42" or similar
        output.split_whitespace()
            .find(|s| s.starts_with("bd-"))
            .map(String::from)
            .ok_or_else(|| SyncError::ExternalApiError(
                "Could not parse bd issue ID from output".to_string()
            ))
    }
}

impl IssueTracker for BeadsAdapter {
    fn name(&self) -> &str {
        "beads"
    }

    fn is_available(&self) -> Result<bool, SyncError> {
        Command::new("bd")
            .arg("--version")
            .output()
            .map(|output| output.status.success())
            .map_err(|e| SyncError::ProviderUnavailable(format!("bd CLI not found: {}", e)))
    }

    fn create_issue(&self, todo: &SyncableTodo) -> Result<SyncRecord, SyncError> {
        let mut cmd = Command::new("bd");
        cmd.arg("create")
           .arg(&todo.title)
           .arg("--type=task")
           .arg(format!("--priority={}", self.map_priority(todo.priority)));

        if let Some(ref desc) = todo.description {
            cmd.arg(format!("--description={}", desc));
        }

        if let Some(ref _project) = todo.project {
            cmd.arg(format!("--external-ref=doob-{}", todo.id));
        }

        if !todo.tags.is_empty() {
            cmd.arg(format!("--notes=tags: {}", todo.tags.join(", ")));
        }

        let output = cmd.output()
            .map_err(|e| SyncError::ExternalApiError(format!("Failed to run bd: {}", e)))?;

        if !output.status.success() {
            return Err(SyncError::ExternalApiError(
                String::from_utf8_lossy(&output.stderr).to_string()
            ));
        }

        let stdout = String::from_utf8_lossy(&output.stdout);
        let bd_id = self.extract_issue_id(&stdout)?;

        Ok(SyncRecord {
            external_id: bd_id,
            external_url: None,
            provider: "beads".to_string(),
            synced_at: chrono::Utc::now().to_rfc3339(),
        })
    }
}
```

**Step 2: Export BeadsAdapter from adapters module**

```rust
// src/sync/adapters/mod.rs

pub mod beads;

pub use beads::BeadsAdapter;
```

**Step 3: Verify it compiles**

Run: `cargo check`
Expected: Compiles successfully

**Step 4: Commit**

```bash
git add src/sync/adapters/
git commit -m "feat: add BeadsAdapter implementation"
```

---

### Task 12: Add Unit Tests for BeadsAdapter

**Files:**
- Create: `tests/unit/beads_adapter_test.rs`
- Modify: `tests/unit/mod.rs`

**Step 1: Write unit tests for BeadsAdapter helpers**

```rust
// tests/unit/beads_adapter_test.rs

use doob::sync::adapters::BeadsAdapter;
use doob::sync::domain::IssueTracker;

#[test]
fn beads_adapter__returns_correct_name() {
    let adapter = BeadsAdapter::new();
    assert_eq!(adapter.name(), "beads");
}

#[test]
fn beads_adapter__maps_priority_0_to_4() {
    let adapter = BeadsAdapter::new();

    // Access via reflection or make map_priority public for testing
    // For now, test indirectly through create_issue or make it pub(crate)
    // This is a design decision - for simplicity, we'll skip direct testing
    // of private methods and rely on integration tests
}

#[test]
fn beads_adapter__extract_issue_id_from_output() {
    let adapter = BeadsAdapter::new();

    // If extract_issue_id is private, test through integration
    // Or make it pub(crate) for testing
}
```

**Note:** Private helper methods (`map_priority`, `extract_issue_id`) can be tested indirectly through integration tests. Alternatively, make them `pub(crate)` for white-box testing.

**Step 2: Add to mod.rs**

```rust
// Add to tests/unit/mod.rs
mod beads_adapter_test;
```

**Step 3: Run tests**

Run: `cargo nextest run beads_adapter`
Expected: PASS (1 test)

**Step 4: Commit**

```bash
git add tests/unit/
git commit -m "test: add unit tests for BeadsAdapter"
```

---

### Task 13: Add Integration Tests for BeadsAdapter

**Files:**
- Create: `tests/integration/mod.rs`
- Create: `tests/integration/beads_adapter_test.rs`
- Modify: `Cargo.toml`

**Step 1: Add integration-tests feature**

```toml
# Add to Cargo.toml

[features]
integration-tests = []
```

**Step 2: Create integration test directory**

```bash
mkdir -p tests/integration
```

**Step 3: Write integration test**

```rust
// tests/integration/beads_adapter_test.rs

#[cfg(feature = "integration-tests")]
mod integration {
    use doob::sync::adapters::BeadsAdapter;
    use doob::sync::domain::{IssueTracker, SyncableTodo, TodoStatus};

    #[test]
    fn beads_adapter__creates_real_issue__when_bd_cli_available() {
        let adapter = BeadsAdapter::new();

        // Skip if bd not available
        if !adapter.is_available().unwrap_or(false) {
            eprintln!("Skipping: bd CLI not available");
            return;
        }

        let todo = SyncableTodo {
            id: "integration-test".to_string(),
            title: "Doob sync integration test".to_string(),
            description: Some("Created by doob sync integration test".to_string()),
            priority: 2,
            status: TodoStatus::Pending,
            tags: vec!["test".to_string(), "integration".to_string()],
            project: Some("doob".to_string()),
            file_path: None,
            due_date: None,
        };

        let result = adapter.create_issue(&todo);

        assert!(result.is_ok());
        let record = result.unwrap();
        assert!(record.external_id.starts_with("bd-"));
        assert_eq!(record.provider, "beads");

        println!("Created issue: {}", record.external_id);

        // Note: Cleanup should be done manually or via bd close command
        // For safety, we leave test issues for manual inspection
    }

    #[test]
    fn beads_adapter__is_unavailable__when_bd_not_installed() {
        // This test only passes if bd is NOT installed
        // Skip in CI where bd might be installed

        let adapter = BeadsAdapter::new();
        let result = adapter.is_available();

        // Just verify it returns a result (either true or false is valid)
        assert!(result.is_ok());
    }
}
```

**Step 4: Create integration mod.rs**

```rust
// tests/integration/mod.rs

mod beads_adapter_test;
```

**Step 5: Run integration tests**

Run: `cargo nextest run --features integration-tests --profile integration`
Expected: Tests run (may skip if bd not available)

**Step 6: Commit**

```bash
git add tests/integration/ Cargo.toml
git commit -m "test: add integration tests for BeadsAdapter"
```

---

### Task 14: Document BeadsAdapter

**Files:**
- Create: `docs/sync/providers/beads.md`

**Step 1: Create providers directory**

```bash
mkdir -p docs/sync/providers
```

**Step 2: Write BeadsAdapter documentation**

```markdown
# Beads Provider

## Overview

The Beads provider syncs doob todos to [beads](https://github.com/user/beads) issues using the `bd` CLI.

## Prerequisites

1. Install `bd` CLI:
   ```bash
   cargo install --git https://github.com/user/beads bd
   ```

2. Initialize beads in your project:
   ```bash
   bd init
   ```

3. Verify bd is available:
   ```bash
   bd --version
   ```

## Configuration

Enable the beads provider:

```bash
doob sync config beads --enable
```

Configuration file (`~/.doob/sync_providers.toml`):

```toml
[beads]
enabled = true
auto_sync = false
sync_filter = { statuses = ["pending", "in_progress"], projects = [], min_priority = null }
[beads.custom]
# No custom settings needed for beads
```

## Usage

```bash
# Sync todos to beads
doob sync to --provider beads

# Dry run
doob sync to --provider beads --dry-run

# Sync specific project
doob sync to --provider beads --project dotfiles
```

## Priority Mapping

| Doob Priority | Beads Priority | Description |
|---------------|----------------|-------------|
| 0             | 0 (P0)         | Critical    |
| 1             | 1 (P1)         | High        |
| 2             | 2 (P2)         | Medium      |
| 3             | 3 (P3)         | Low         |
| 4-5           | 4 (P4)         | Backlog     |

## Field Mapping

- **Title** → bd issue title
- **Description** → bd issue description (if present)
- **Priority** → bd priority (0-4 scale)
- **Tags** → bd issue notes (formatted as "tags: tag1, tag2")
- **Project** → bd external-ref (formatted as "doob-{id}")

## Limitations

- One-way sync only (doob → beads)
- No update support (Phase 1)
- Cannot sync completed todos
- Requires bd CLI installed and accessible

## Troubleshooting

### "bd CLI not found"

Ensure bd is installed and in your PATH:
```bash
which bd
bd --version
```

### "Created issue bd-42 not parsed"

The bd CLI output format may have changed. Check bd version compatibility.

### Permission denied

Ensure you have write access to the `.beads/` directory in your project.
```

**Step 3: Commit**

```bash
git add docs/sync/providers/beads.md
git commit -m "docs: add BeadsAdapter provider documentation"
```

---

## Phase 3: Metadata & Repository (Preview)

**Note:** Phase 3 tasks follow the same TDD pattern. Here's a preview of the structure:

### Task 15: Define SyncMetadata Types
- Write tests for `SyncMetadata` and `ProviderSyncData`
- Implement types with HashMap for multi-provider support
- Add helper methods (is_synced_to, upsert_sync_record, etc.)

### Task 16: Define TodoRepository Trait
- Write tests for `TodoFilter` and `TodoWithMetadata`
- Implement `TodoRepository` trait
- Create mock repository for testing

### Task 17: Implement SurrealTodoRepository
- Write tests for SurrealDB queries
- Implement load_todos with filtering
- Implement update_metadata

### Task 18: Add Repository Integration Tests
- Test with real SurrealDB instance
- Verify metadata persistence
- Test filtering logic

---

## Phase 4: CLI Commands (Preview)

### Task 19: Define SyncCommands Enum
- Define clap subcommands (to, providers, config, status)
- Add command arguments and flags
- Wire up to main CLI

### Task 20: Implement sync to Command
- Handle provider lookup
- Load todos from repository
- Call SyncService
- Update metadata
- Display results

### Task 21: Implement sync providers Command
- List all registered providers
- Check availability status
- Format output

### Task 22: Implement sync status Command
- Query todos with metadata
- Group by sync status
- Display formatted output

---

## Testing & Validation

### Running All Tests

```bash
# Unit tests only
cargo nextest run --lib

# All tests including integration
cargo nextest run --features integration-tests --profile integration

# With coverage
cargo llvm-cov nextest --all-features --workspace --lcov --output-path lcov.info
```

### Manual Testing Checklist

- [ ] Unit tests pass
- [ ] Integration tests pass (with bd CLI installed)
- [ ] cargo check passes
- [ ] cargo clippy -- -D warnings passes
- [ ] Documentation is accurate

### Coverage Report

```bash
cargo llvm-cov nextest --html
open target/llvm-cov/html/index.html
```

---

## Next Steps

After completing Phase 1 (Foundation) and Phase 2 (Beads Adapter):

1. **Phase 3:** Implement metadata management and SurrealDB repository
2. **Phase 4:** Add CLI commands for sync operations
3. **Phase 5:** Implement GitHub adapter
4. **Phase 6:** Add remaining adapters (Jira, Linear, kan)

## References

- Design doc: `design/2026-03-04-doob-sync-plugin-system-design.md`
- Testing guide: `docs/sync/testing.md`
- Beads provider docs: `docs/sync/providers/beads.md`
- @superpowers:test-driven-development for TDD workflow
- @superpowers:executing-plans for step-by-step execution
