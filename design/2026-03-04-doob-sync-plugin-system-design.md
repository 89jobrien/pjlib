# Doob Sync Plugin System Design

**Date:** 2026-03-04
**Author:** Design Session with User
**Status:** Approved

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Provider Interface](#provider-interface)
4. [Sync Metadata & Repository](#sync-metadata--repository)
5. [CLI Interface](#cli-interface)
6. [Error Handling & Retry Logic](#error-handling--retry-logic)
7. [Testing Strategy](#testing-strategy)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Future Enhancements](#future-enhancements)

## Overview

### Problem Statement

Doob users need to sync their todos with external issue tracking systems (beads, GitHub Issues, Jira, Linear, and
custom kan system). This sync should be:

- **Extensible** - Easy to add new providers
- **One-way** - Doob → external systems (bidirectional in future)
- **Manual** - User-triggered via `doob sync` command
- **Tracked** - Store sync metadata to prevent duplicates
- **Filtered** - Only sync pending/in_progress todos

### Solution Approach

Implement a plugin/provider system using hexagonal architecture and SOLID principles:

- **Domain layer** - Core sync logic independent of external systems
- **Ports** - `IssueTracker` trait defining provider interface
- **Adapters** - Concrete implementations for each provider (beads, GitHub, etc.)
- **Application layer** - CLI commands and orchestration
- **Repository layer** - SurrealDB integration for metadata persistence

### Key Design Decisions

1. **Plugin architecture** - Chosen over direct CLI integration or shared database to support multiple providers
2. **CLI delegation** - Providers shell out to existing CLIs (bd, gh, jira) rather than reimplementing APIs
3. **Metadata storage** - Use todo.metadata JSON field to track sync records per provider
4. **SOLID principles** - Clean separation between domain, ports, and adapters
5. **Nextest** - Modern test runner with parallel execution and retry support

## Architecture

### Directory Structure

```
doob/
├── src/
│   ├── cli.rs                    # Main CLI entry point
│   ├── commands/
│   │   ├── todo.rs              # Existing todo commands
│   │   └── sync.rs              # New sync command
│   ├── sync/
│   │   ├── mod.rs               # Sync module public interface
│   │   ├── domain.rs            # Core domain models (no external deps)
│   │   ├── registry.rs          # Provider registry/discovery
│   │   ├── metadata.rs          # Sync metadata tracking
│   │   ├── repository.rs        # SurrealDB integration
│   │   ├── retry.rs             # Retry logic for network failures
│   │   └── adapters/
│   │       ├── mod.rs           # Adapters module
│   │       ├── beads.rs         # bd (beads) provider
│   │       ├── github.rs        # GitHub Issues provider
│   │       ├── jira.rs          # Jira provider
│   │       ├── linear.rs        # Linear provider
│   │       └── kan.rs           # kan provider
│   └── lib.rs
├── tests/
│   ├── unit/
│   │   ├── sync_service_test.rs
│   │   ├── metadata_test.rs
│   │   └── retry_test.rs
│   ├── integration/
│   │   ├── beads_adapter_test.rs
│   │   ├── github_adapter_test.rs
│   │   └── repository_test.rs
│   └── common/
│       └── mod.rs               # Shared test utilities
├── .config/
│   └── nextest.toml             # Nextest configuration
└── docs/
    └── sync/
        ├── providers/
        │   ├── beads.md
        │   ├── github.md
        │   ├── jira.md
        │   ├── linear.md
        │   └── kan.md
        └── user-guide.md
```

### Configuration Files

**~/.doob/sync_providers.toml** - Per-provider configuration:

```toml
[beads]
enabled = true
auto_sync = false
sync_filter = { statuses = ["pending", "in_progress"], projects = [], min_priority = null }
[beads.custom]
# bd-specific settings

[github]
enabled = true
auto_sync = false
sync_filter = { statuses = ["pending", "in_progress"], projects = ["myproject"], min_priority = 2 }
[github.custom]
repo = "user/repo"
label = "from-doob"

[jira]
enabled = false
auto_sync = false
sync_filter = { statuses = ["pending", "in_progress"], projects = [], min_priority = null }
[jira.custom]
project_key = "PROJ"
issue_type = "Task"

[linear]
enabled = false
auto_sync = false
sync_filter = { statuses = ["pending"], projects = [], min_priority = null }
[linear.custom]
team_id = "abc123"

[kan]
enabled = true
auto_sync = true
sync_filter = { statuses = ["pending", "in_progress"], projects = [], min_priority = null }
[kan.custom]
# kan-specific settings
```

### Data Flow

```
┌─────────────┐
│  User CLI   │
│  doob sync  │
└──────┬──────┘
       │
       v
┌──────────────────┐
│  Sync Command    │
│  (Application)   │
└──────┬───────────┘
       │
       v
┌──────────────────┐      ┌────────────────┐
│ Provider Registry│─────>│  IssueTracker  │ (Port)
└──────┬───────────┘      └────────┬───────┘
       │                           │
       v                           v
┌──────────────────┐      ┌────────────────┐
│  SyncService     │─────>│  Concrete      │
│  (Domain Logic)  │      │  Adapters      │
└──────┬───────────┘      │  - BeadsAdapter│
       │                  │  - GitHubAdapter│
       │                  │  - JiraAdapter │
       v                  │  - LinearAdapter│
┌──────────────────┐      │  - KanAdapter  │
│ TodoRepository   │      └────────────────┘
│ (SurrealDB)      │
└──────────────────┘
```

**Sequence Diagram:**

```
User          CLI          SyncService    Provider      Repository
 |             |                |             |              |
 |─sync to bd─>|                |             |              |
 |             |─get tracker───>|             |              |
 |             |                |             |              |
 |             |─load todos────────────────────────────────>|
 |             |<───────────────────────────────────────────|
 |             |                |             |              |
 |             |─sync_todo()───>|             |              |
 |             |                |─is_available()─>          |
 |             |                |<────────────|              |
 |             |                |─create_issue()─>          |
 |             |                |<────────────|              |
 |             |<───────────────|             |              |
 |             |                |             |              |
 |             |─update_metadata────────────────────────────>|
 |             |<───────────────────────────────────────────|
 |<─success───|                |             |              |
```

## Provider Interface

### Core Domain Models

```rust
// src/sync/domain.rs

use serde::{Deserialize, Serialize};
use thiserror::Error;

/// Domain model: A todo that needs to be synced
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncableTodo {
    pub id: String,
    pub title: String,
    pub description: Option<String>,
    pub priority: u8,              // 0-5 scale
    pub status: TodoStatus,
    pub tags: Vec<String>,
    pub project: Option<String>,
    pub file_path: Option<String>,
    pub due_date: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum TodoStatus {
    Pending,
    InProgress,
}

/// Result of syncing to external system
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncRecord {
    pub external_id: String,        // e.g., "bd-42", "123"
    pub external_url: Option<String>, // e.g., GitHub issue URL
    pub provider: String,            // "beads", "github", etc.
    pub synced_at: String,          // ISO 8601 timestamp
}

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

### Port: IssueTracker Trait

```rust
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

**Design Rationale:**

- **Simple trait** - Only 3 methods: name, availability check, create issue
- **No async** - Adapters use sync subprocess calls (simpler, easier to test)
- **Error type** - Domain-specific SyncError for clear error handling
- **Stateless** - Trait doesn't require mutable state

### Domain Service: SyncService

```rust
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

**SOLID Principles Applied:**

1. **Single Responsibility** - SyncService only orchestrates sync logic
2. **Open/Closed** - Add new providers without modifying SyncService
3. **Dependency Inversion** - SyncService depends on IssueTracker abstraction, not concrete adapters

### Adapter Example: BeadsAdapter

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

        if let Some(ref project) = todo.project {
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

**Priority Mapping:**

| Doob Priority | Beads Priority | Description |
|---------------|----------------|-------------|
| 0             | 0 (P0)         | Critical    |
| 1             | 1 (P1)         | High        |
| 2             | 2 (P2)         | Medium      |
| 3             | 3 (P3)         | Low         |
| 4-5           | 4 (P4)         | Backlog     |

## Sync Metadata & Repository

### Metadata Schema

Sync metadata is stored in the `todo.metadata` JSON field:

```json
{
  "sync": {
    "beads": {
      "id": "bd-42",
      "synced_at": "2026-03-04T08:00:00Z"
    },
    "github": {
      "id": "123",
      "url": "https://github.com/user/repo/issues/123",
      "synced_at": "2026-03-04T08:01:00Z"
    }
  }
}
```

### Metadata Management

```rust
// src/sync/metadata.rs

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct SyncMetadata {
    #[serde(default)]
    pub sync: HashMap<String, ProviderSyncData>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProviderSyncData {
    pub id: String,
    pub url: Option<String>,
    pub synced_at: String,
}

impl SyncMetadata {
    pub fn is_synced_to(&self, provider: &str) -> bool {
        self.sync.contains_key(provider)
    }

    pub fn get_sync_record(&self, provider: &str) -> Option<&ProviderSyncData> {
        self.sync.get(provider)
    }

    pub fn upsert_sync_record(&mut self, provider: String, data: ProviderSyncData) {
        self.sync.insert(provider, data);
    }

    pub fn synced_providers(&self) -> Vec<String> {
        self.sync.keys().cloned().collect()
    }
}
```

### Repository Interface

```rust
pub trait TodoRepository {
    fn load_todos(&self, filter: &TodoFilter) -> Result<Vec<TodoWithMetadata>>;
    fn update_metadata(&self, todo_id: &str, metadata: &SyncMetadata) -> Result<()>;
}

#[derive(Debug, Clone)]
pub struct TodoFilter {
    pub statuses: Vec<String>,
    pub projects: Option<Vec<String>>,
    pub not_synced_to: Option<String>,  // Filter out already-synced todos
}

#[derive(Debug, Clone)]
pub struct TodoWithMetadata {
    pub todo: SyncableTodo,
    pub metadata: SyncMetadata,
}
```

### SurrealDB Implementation

```rust
// src/sync/repository.rs

pub struct SurrealTodoRepository {
    db: Surreal<Db>,
}

impl TodoRepository for SurrealTodoRepository {
    fn load_todos(&self, filter: &TodoFilter) -> Result<Vec<TodoWithMetadata>> {
        let mut query = "SELECT * FROM todo WHERE 1=1".to_string();

        // Filter by status
        if !filter.statuses.is_empty() {
            let statuses = filter.statuses
                .iter()
                .map(|s| format!("'{}'", s))
                .collect::<Vec<_>>()
                .join(", ");
            query.push_str(&format!(" AND status IN [{}]", statuses));
        }

        // Filter by project
        if let Some(ref projects) = filter.projects {
            if !projects.is_empty() {
                let projects_str = projects
                    .iter()
                    .map(|p| format!("'{}'", p))
                    .collect::<Vec<_>>()
                    .join(", ");
                query.push_str(&format!(" AND project IN [{}]", projects_str));
            }
        }

        // Filter out already-synced
        if let Some(ref provider) = filter.not_synced_to {
            query.push_str(&format!(" AND !meta::exists(metadata.sync.{})", provider));
        }

        // Execute query and map results
        // ... implementation details
    }

    fn update_metadata(&self, todo_id: &str, metadata: &SyncMetadata) -> Result<()> {
        let metadata_json = serde_json::to_value(metadata)?;

        self.db.query("UPDATE $id SET metadata = $metadata")
            .bind(("id", format!("todo:{}", todo_id)))
            .bind(("metadata", metadata_json))
            .await?;

        Ok(())
    }
}
```

## CLI Interface

### Command Structure

```rust
#[derive(Debug, Subcommand)]
pub enum SyncCommands {
    /// Sync todos to external issue tracker
    #[command(name = "to")]
    SyncTo {
        #[arg(short, long)]
        provider: String,

        #[arg(long)]
        dry_run: bool,

        #[arg(short = 'p', long)]
        project: Option<String>,

        #[arg(long)]
        force: bool,
    },

    /// List available sync providers
    #[command(name = "providers")]
    ListProviders,

    /// Configure a sync provider
    #[command(name = "config")]
    ConfigureProvider {
        provider: String,

        #[arg(long)]
        enable: bool,

        #[arg(long)]
        disable: bool,
    },

    /// Show sync status for todos
    #[command(name = "status")]
    SyncStatus {
        #[arg(long)]
        synced: bool,

        #[arg(long)]
        unsynced: bool,
    },
}
```

### Example Usage

```bash
# List available providers
doob sync providers
# Output:
# 📋 Available sync providers:
#   • beads - ✓ available
#   • github - ✓ available
#   • jira - ✗ unavailable
#   • linear - ✗ unavailable
#   • kan - ✓ available

# Sync to beads
doob sync to --provider beads
# Output:
# 📤 Syncing 5 todos to beads...
#   ✓ Implement feature X → bd-42
#   ✓ Fix bug in auth → bd-43
#   ✓ Write tests → bd-44
#   ✓ Update docs → bd-45
#   ✓ Refactor module → bd-46
# ✨ Synced 5 todos (5 succeeded, 0 failed)

# Dry run to preview
doob sync to --provider github --dry-run
# Output:
# 🔍 Dry run: would sync 3 todos to github
#   • Implement feature X
#   • Fix bug in auth
#   • Write tests

# Sync specific project
doob sync to --provider beads --project dotfiles

# Force re-sync already synced todos
doob sync to --provider beads --force

# Show sync status
doob sync status
# Output:
# 📊 Sync Status:
#
# Synced to multiple providers (2 todos):
#   • Implement feature X (beads: bd-42, github: #123)
#   • Fix bug in auth (beads: bd-43)
#
# Synced to beads only (3 todos):
#   • Write tests (beads: bd-44)
#   • Update docs (beads: bd-45)
#   • Refactor module (beads: bd-46)
#
# Not synced (2 todos):
#   • New todo 1
#   • New todo 2

# Configure provider
doob sync config beads --enable
doob sync config github --disable
```

## Error Handling & Retry Logic

### Error Types

```rust
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

### Retry Policy

```rust
// src/sync/retry.rs

pub struct RetryPolicy {
    pub max_attempts: u32,
    pub base_delay_ms: u64,
    pub max_delay_ms: u64,
}

impl Default for RetryPolicy {
    fn default() -> Self {
        Self {
            max_attempts: 3,
            base_delay_ms: 1000,
            max_delay_ms: 10000,
        }
    }
}

impl RetryPolicy {
    pub fn execute<F, T>(&self, mut f: F) -> Result<T, SyncError>
    where
        F: FnMut() -> Result<T, SyncError>,
    {
        let mut last_error = None;

        for attempt in 0..self.max_attempts {
            match f() {
                Ok(result) => return Ok(result),
                Err(e) => {
                    if !self.is_retryable(&e) {
                        return Err(e);
                    }

                    last_error = Some(e);

                    if attempt + 1 < self.max_attempts {
                        let delay = self.calculate_delay(attempt);
                        std::thread::sleep(Duration::from_millis(delay));
                    }
                }
            }
        }

        Err(last_error.unwrap())
    }

    fn is_retryable(&self, error: &SyncError) -> bool {
        matches!(error,
            SyncError::ExternalApiError(_) |
            SyncError::ProviderUnavailable(_)
        )
    }

    fn calculate_delay(&self, attempt: u32) -> u64 {
        // Exponential backoff: base_delay * 2^attempt, capped at max_delay
        let delay = self.base_delay_ms * 2_u64.pow(attempt);
        delay.min(self.max_delay_ms)
    }
}
```

**Retry Behavior:**

- Attempt 1: Immediate
- Attempt 2: 1s delay
- Attempt 3: 2s delay
- Only retries transient errors (API failures, provider unavailable)
- Does not retry configuration errors or already-synced errors

## Testing Strategy

### Nextest Configuration

**.config/nextest.toml:**

```toml
[profile.default]
test-threads = "num-cpus"
retries = 2
failure-output = "immediate-final"
success-output = "never"

[profile.default.overrides]
# Integration tests run serially
filter = 'test(integration)'
test-threads = 1
retries = 3

# Unit tests run in parallel
filter = 'test(^((?!integration).)*$)'
test-threads = "num-cpus"

[profile.ci]
retries = 0
failure-output = "immediate-final"
success-output = "final"

[profile.integration]
retries = 3
test-threads = 1
slow-timeout = { period = "120s", terminate-after = 5 }
```

### Test Organization

```
tests/
├── unit/
│   ├── sync_service_test.rs      # Domain logic tests
│   ├── metadata_test.rs           # Metadata management tests
│   └── retry_test.rs              # Retry logic tests
├── integration/
│   ├── beads_adapter_test.rs      # Real bd CLI tests
│   ├── github_adapter_test.rs     # Real gh CLI tests
│   └── repository_test.rs         # SurrealDB integration tests
└── common/
    └── mod.rs                      # Shared test utilities
```

### Test Commands

```bash
# Install nextest
cargo install cargo-nextest --locked

# Run all tests
cargo nextest run

# Run only unit tests
cargo nextest run --lib

# Run integration tests (requires bd, gh CLIs)
cargo nextest run --features integration-tests --profile integration

# Run with coverage
cargo llvm-cov nextest --all-features --workspace --lcov --output-path lcov.info

# Run specific test
cargo nextest run sync_service__creates_issue

# List all tests
cargo nextest list

# Retry failed tests
cargo nextest run --failed
```

### Test Examples

```rust
#[test]
fn sync_service__creates_issue__when_todo_is_pending() {
    // Arrange
    let tracker = MockTracker::new("test");
    let service = SyncService::new(tracker.clone());
    let todo = make_todo("1", "Test todo", TodoStatus::Pending);

    // Act
    let result = service.sync_todo(&todo);

    // Assert
    assert!(result.is_ok());
    let record = result.unwrap();
    assert_eq!(record.external_id, "test-1");
}

#[test]
#[cfg(feature = "integration-tests")]
fn beads_adapter__creates_real_issue__when_bd_cli_available() {
    let adapter = BeadsAdapter::new();

    if !adapter.is_available().unwrap_or(false) {
        return; // Skip if bd not available
    }

    let todo = make_todo("integration-test", "Nextest integration test", TodoStatus::Pending);
    let result = adapter.create_issue(&todo);

    assert!(result.is_ok());
    assert!(result.unwrap().external_id.starts_with("bd-"));
}
```

### Coverage Goals

- **Overall:** 80%+ test coverage
- **Domain layer:** 90%+ (critical business logic)
- **Adapters:** 70%+ (integration tests may be limited)
- **CLI commands:** 60%+ (harder to test, but validated manually)

## Implementation Roadmap

### Phase 1: Foundation (Week 1)

**Goals:**
- Core domain models and traits
- Basic sync service
- Test infrastructure

**Deliverables:**
- `src/sync/domain.rs` with SyncableTodo, SyncRecord, SyncError, IssueTracker trait
- `SyncService` with sync_todo() and sync_todos()
- Unit test suite with MockTracker
- Nextest configuration

**Success Criteria:**
- All unit tests passing
- 90%+ coverage on domain code
- Clear separation of concerns (no external dependencies in domain)

### Phase 2: Beads Adapter (Week 1-2)

**Goals:**
- First concrete adapter implementation
- Integration with bd CLI
- Priority mapping

**Deliverables:**
- `src/sync/adapters/beads.rs`
- Integration tests with real bd CLI
- Documentation in `docs/sync/providers/beads.md`

**Success Criteria:**
- Can create bd issues from doob todos
- Priority mapping works correctly (0-4 scale)
- External ID extraction works
- Integration tests pass (when bd available)

### Phase 3: Repository & CLI (Week 2)

**Goals:**
- SurrealDB integration
- CLI commands
- Metadata persistence

**Deliverables:**
- `src/sync/repository.rs` with SurrealTodoRepository
- `src/sync/metadata.rs` with SyncMetadata types
- `src/commands/sync.rs` with CLI subcommands
- `doob sync to` command working end-to-end

**Success Criteria:**
- Can filter todos by status, project, sync status
- Metadata persists in SurrealDB
- Dry-run mode works
- User-friendly CLI output

### Phase 4: GitHub Adapter (Week 3)

**Goals:**
- Second adapter to validate extensibility
- GitHub Issues integration

**Deliverables:**
- `src/sync/adapters/github.rs`
- GitHub-specific configuration (repo, labels)
- Integration tests
- Documentation

**Success Criteria:**
- Can create GitHub issues from doob todos
- Issue URLs stored in metadata
- Labels applied correctly
- Works with both public and private repos

### Phase 5: Configuration System (Week 3)

**Goals:**
- Provider configuration
- Enable/disable providers
- Per-provider settings

**Deliverables:**
- `src/sync/registry.rs` with ProviderRegistry
- `~/.doob/sync_providers.toml` config file
- `doob sync config` command
- `doob sync providers` list command

**Success Criteria:**
- Providers can be enabled/disabled
- Custom settings per provider
- Config validation works
- Clear error messages

### Phase 6: Additional Adapters (Week 4+)

**Goals:**
- Complete provider ecosystem
- Full feature parity

**Deliverables:**
- `src/sync/adapters/kan.rs`
- `src/sync/adapters/jira.rs`
- `src/sync/adapters/linear.rs`
- Documentation for each provider

**Success Criteria:**
- All 5 providers working
- Consistent CLI interface
- Complete documentation
- Production-ready

## Future Enhancements

### Phase 7: Bidirectional Sync

**Goal:** Sync changes from external systems back to doob

**Changes:**
- Add `read_issue()` method to IssueTracker trait
- Implement conflict detection and resolution
- Add `doob sync from` command
- Periodic polling or webhook support

**Use Cases:**
- Issue closed in GitHub → mark todo complete in doob
- Issue title changed → update todo title
- New comment added → add note to todo

### Phase 8: Batch Optimization

**Goal:** Improve performance for large sync operations

**Changes:**
- Override `sync_todos()` in adapters with batch APIs
- Parallel syncing with rayon
- Progress bars (indicatif)
- Transaction support

**Benefits:**
- Faster sync for 100+ todos
- Better user feedback
- Atomic operations

### Phase 9: Advanced Filtering

**Goal:** More granular control over what gets synced

**Features:**
- Tag-based filtering
- Due date filtering
- Custom sync rules per provider
- Project-specific provider mappings

**Example:**
```toml
[github.custom]
repo = "user/repo"
filter = { tags = ["bug", "feature"], min_priority = 1 }
```

### Phase 10: Auto-sync Hooks

**Goal:** Automatic syncing on todo operations

**Features:**
- Hook into `doob todo add` to auto-sync
- Hook into `doob todo complete` to close external issues
- Background sync daemon
- Configurable triggers

**Example:**
```bash
doob todo add "Fix bug" --auto-sync beads,github
# Automatically creates bd issue and GitHub issue
```

### Future: Web Dashboard

**Goal:** Visual interface for sync management

**Features:**
- Sync status overview
- Manual conflict resolution
- Provider health monitoring
- Sync history and analytics
- Batch operations UI

## Migration Path

### For Existing Doob Users

**No Breaking Changes:**
- Sync is purely additive functionality
- Existing todos work unchanged
- Metadata field is optional

**Upgrade Steps:**

```bash
# 1. Update doob
cargo install --path . --force

# 2. Verify installation
doob sync providers

# 3. (Optional) Enable providers
doob sync config beads --enable

# 4. Sync when ready
doob sync to --provider beads --dry-run  # Preview
doob sync to --provider beads             # Sync
```

### Rollback Plan

If issues arise:
1. Sync metadata is non-destructive - todos unchanged
2. Can disable providers: `doob sync config <provider> --disable`
3. Can clear metadata if needed (manual SurrealDB update)

## Performance Considerations

### Database Optimization

**Indexes:**
```sql
-- SurrealDB indexes for faster filtering
DEFINE INDEX status_idx ON todo FIELDS status;
DEFINE INDEX project_idx ON todo FIELDS project;
DEFINE INDEX metadata_sync_idx ON todo FIELDS metadata.sync;
```

**Query Optimization:**
- Batch load todos (avoid N+1)
- Filter at database level, not in application
- Use prepared statements

### CLI Subprocess Management

**Best Practices:**
- Timeout handling (prevent hung processes)
- stderr/stdout buffering limits
- Process cleanup on error

### Metadata Size

**Constraints:**
- Limit sync metadata to essential fields only
- No redundant data storage
- Consider cleanup of old sync records (optional future feature)

## Security Considerations

### Credential Management

**Principles:**
- Never store credentials in doob database
- Rely on provider CLIs for authentication
- Use system keychain where possible

**Provider Auth:**
- **beads:** File system permissions on `.beads/`
- **GitHub:** `gh auth login` (OAuth token)
- **Jira:** `jira login` (API token)
- **Linear:** API key in config
- **kan:** Custom auth mechanism

### Input Validation

**Protection Against:**
- CLI injection in titles/descriptions
- Malformed external IDs
- Invalid JSON in metadata

**Mitigation:**
- Escape shell arguments
- Validate external ID formats
- JSON schema validation

### Provider Permissions

**Minimum Required:**
- **GitHub:** `repo` scope (or `public_repo` for public only)
- **Jira:** Create issue permission in project
- **Linear:** Team member with write access
- **beads:** Write access to `.beads/` directory

## Appendix

### References

- **SOLID Principles in Rust:** [tuttlem.github.io](http://tuttlem.github.io/2025/08/31/hexagonal-architecture-in-rust.html)
- **Hexagonal Architecture:** [github.com/antoinecarton/hexagonal-rust](https://github.com/antoinecarton/hexagonal-rust)
- **Dependency Inversion:** [antoniodiaz.me](https://www.antoniodiaz.me/en/blog/dependency-inversion-in-rust-6)
- **Nextest:** [nexte.st](https://nexte.st)

### Glossary

- **Adapter:** Concrete implementation of a port (e.g., BeadsAdapter implements IssueTracker)
- **Port:** Interface/trait defining external system contract (e.g., IssueTracker)
- **Provider:** External issue tracking system (beads, GitHub, Jira, Linear, kan)
- **Sync Record:** Metadata about a sync operation (external ID, URL, timestamp)
- **SyncableTodo:** Domain model representing a todo ready to be synced

### Open Questions

1. **Bulk updates:** Should we support updating many existing bd issues when re-syncing with `--force`?
   - **Decision:** Phase 1 focuses on create-only. Updates in Phase 7 (bidirectional sync)

2. **Conflict resolution:** How to handle when a todo is synced to multiple providers and they diverge?
   - **Decision:** Phase 1 is one-way only. Conflicts deferred to Phase 7

3. **Provider priority:** If auto-sync is enabled for multiple providers, what order?
   - **Decision:** Phase 1 manual sync only. Auto-sync order TBD in Phase 10

4. **Webhook support:** Should providers support webhooks for real-time updates?
   - **Decision:** Phase 1 CLI-based polling. Webhooks deferred to Phase 7+

---

**Design Approved:** 2026-03-04
**Next Step:** Invoke writing-plans skill for implementation plan
