# Doob Phase 1 MVP Implementation Plan

**Date:** 2026-02-20
**Status:** Ready for Implementation
**Type:** Rust CLI - Public GitHub Repository

## Overview

Phase 1 MVP of `doob` - a modern, agent-first todo CLI built with Rust and SurrealDB. This plan covers the minimal viable product: three core commands (`add`, `list`, `complete`) with first-class support for coding agents and Claude Code CLI.

**Repository:** https://github.com/yourusername/doob (public)
**Location:** `~/dev/doob/`

## Goals

1. **MVP with 3 commands:** `add`, `list`, `complete`
2. **Agent-first design:** JSON output, batch operations, context detection, proper exit codes
3. **TDD implementation:** Tests first, vertical slices
4. **Public GitHub repo:** Open source, documented, ready for community

## Architecture

### Tech Stack

```
doob (Rust CLI)
├── clap 4          # CLI framework with derive macros
├── surrealdb 2     # Embedded database (file + in-memory for tests)
├── tokio 1         # Async runtime
├── serde           # JSON serialization
├── serde_json      # JSON output
├── chrono          # Date/time handling
├── anyhow          # Error handling
└── git2            # Git context detection
```

### Project Structure

```
doob/
├── .github/
│   └── workflows/
│       ├── ci.yml          # Run tests on PR
│       └── release.yml     # Build binaries on tag
├── Cargo.toml
├── README.md               # Usage examples, installation
├── LICENSE                 # MIT or Apache-2.0
├── src/
│   ├── main.rs             # CLI entry point + error handling
│   ├── db/
│   │   ├── mod.rs          # Database module exports
│   │   └── schema.rs       # SurrealDB schema + connection
│   ├── models/
│   │   └── todo.rs         # Todo struct with serde
│   ├── context/
│   │   ├── mod.rs          # Context detection module
│   │   ├── git.rs          # Git repo/project detection
│   │   └── project.rs      # Project path inference
│   ├── output/
│   │   ├── mod.rs          # Output formatting
│   │   ├── json.rs         # JSON formatter for agents
│   │   └── human.rs        # Human-readable formatter
│   └── commands/
│       ├── mod.rs          # Command module
│       ├── add.rs          # `doob todo add` (batch + context)
│       ├── list.rs         # `doob todo list` (JSON output)
│       └── complete.rs     # `doob todo complete` (batch)
└── tests/
    ├── common/
    │   └── mod.rs          # Test helpers (setup_test_db, etc.)
    └── integration/
        ├── add_test.rs
        ├── list_test.rs
        ├── complete_test.rs
        ├── json_output_test.rs
        ├── batch_test.rs
        └── context_test.rs
```

## Data Model

### Todo Struct (Rust)

```rust
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Todo {
    pub id: Option<String>,        // SurrealDB record ID
    pub uuid: String,               // Portable UUID
    pub content: String,            // Task description
    pub status: TodoStatus,         // Status enum
    pub priority: u8,               // 0-5 (0=highest)
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub completed_at: Option<DateTime<Utc>>,
    pub project: Option<String>,    // Auto-detected or manual
    pub project_path: Option<String>,
    pub file_path: Option<String>,  // Relative to project
    pub tags: Vec<String>,          // Native array
    pub metadata: Option<serde_json::Value>, // Flexible JSON
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TodoStatus {
    Pending,
    InProgress,
    Completed,
    Cancelled,
}
```

### SurrealDB Schema

```surrealql
DEFINE TABLE todo SCHEMAFULL;
DEFINE FIELD uuid ON TABLE todo TYPE string ASSERT $value != NONE;
DEFINE FIELD content ON TABLE todo TYPE string ASSERT $value != NONE;
DEFINE FIELD status ON TABLE todo TYPE string
  ASSERT $value INSIDE ["pending", "in_progress", "completed", "cancelled"];
DEFINE FIELD priority ON TABLE todo TYPE int DEFAULT 0
  ASSERT $value >= 0 AND $value <= 5;
DEFINE FIELD created_at ON TABLE todo TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON TABLE todo TYPE datetime DEFAULT time::now();
DEFINE FIELD completed_at ON TABLE todo TYPE option<datetime>;
DEFINE FIELD project ON TABLE todo TYPE option<string>;
DEFINE FIELD project_path ON TABLE todo TYPE option<string>;
DEFINE FIELD file_path ON TABLE todo TYPE option<string>;
DEFINE FIELD tags ON TABLE todo TYPE array<string> DEFAULT [];
DEFINE FIELD metadata ON TABLE todo TYPE option<object>;

DEFINE INDEX idx_todo_status ON TABLE todo COLUMNS status;
DEFINE INDEX idx_todo_project ON TABLE todo COLUMNS project;
```

**Database Location:** `~/.claude/data/doob.db`

## CLI Interface

### Command Structure

```rust
#[derive(Parser)]
#[command(name = "doob")]
#[command(about = "Modern todo management for coding agents")]
pub struct Cli {
    /// Output in JSON format (machine-readable)
    #[arg(long, global = true)]
    pub json: bool,

    /// Database path (default: ~/.claude/data/doob.db)
    #[arg(long, global = true)]
    pub db: Option<String>,

    #[command(subcommand)]
    pub command: Commands,
}
```

### Commands (Phase 1 MVP)

**1. Add Todo(s)**
```bash
# Single add with context detection
doob todo add "Fix auth bug"
# → Auto-detects: project=repo-name, file_path=relative/path

# Batch add
doob todo add "Task 1" "Task 2" "Task 3" --priority 1 --tags urgent,bug

# Manual context override
doob todo add "Task" --project myproject --file src/main.rs
```

**2. List Todos**
```bash
# List all
doob todo list

# Filter by status
doob todo list --status pending

# Filter by project
doob todo list --project myproject

# Limit results
doob todo list --limit 10

# JSON output for agents
doob --json todo list --status pending
```

**3. Complete Todo(s)**
```bash
# Single complete
doob todo complete 42

# Batch complete
doob todo complete 1 2 3
```

## Agent Integration Features

### 1. JSON Output Mode

**Flag:** `--json` (global)

**Example:**
```bash
doob --json todo list --status pending
```

**Output:**
```json
{
  "todos": [
    {
      "id": "todo:abc123",
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "content": "Fix auth bug",
      "status": "pending",
      "priority": 1,
      "created_at": "2026-02-20T10:30:00Z",
      "updated_at": "2026-02-20T10:30:00Z",
      "completed_at": null,
      "project": "doob",
      "project_path": "/Users/joe/dev/doob",
      "file_path": "src/main.rs",
      "tags": ["bug", "urgent"],
      "metadata": null
    }
  ],
  "count": 1
}
```

### 2. Context Detection

**Git-based detection:**
```rust
// Detect project from git remote
fn detect_project() -> Option<String> {
    // 1. Check git remote URL → extract repo name
    // 2. Fallback to directory name
    // Examples:
    //   git@github.com:user/doob.git → "doob"
    //   /Users/joe/dev/myproject → "myproject"
}

// Detect file path relative to project root
fn detect_file_path() -> Option<String> {
    // 1. Find git repo root
    // 2. Get current working directory
    // 3. Return relative path from root to cwd
    // Example: cwd=/Users/joe/dev/doob/src → "src"
}
```

**Behavior:**
- Auto-detect if not specified by user
- User-provided values override detection
- Detection failure is non-fatal (project=None, file_path=None)

### 3. Batch Operations

**Add multiple:**
```bash
doob todo add "Task 1" "Task 2" "Task 3"
# Creates 3 separate todos with same priority/tags
```

**Complete multiple:**
```bash
doob todo complete 42 43 44
# Marks all 3 as completed
```

**Implementation:**
- Accept `Vec<String>` for content/IDs
- Single database transaction for atomicity
- Report success count + any failures

### 4. Exit Codes

```rust
pub enum ExitCode {
    Success = 0,          // Operation completed successfully
    TodoNotFound = 1,     // Todo ID not found in database
    InvalidInput = 2,     // Invalid arguments (priority > 5, bad status)
    DatabaseError = 3,    // Database connection/query error
    ContextError = 4,     // Git context detection failed (non-fatal)
}
```

**Usage in agents:**
```bash
doob todo complete 999
echo $?  # Returns 1 (not found)

if doob --json todo list --status pending; then
  # Success, parse JSON
else
  # Handle error based on exit code
fi
```

## Implementation Approach: Vertical Slices (TDD)

### Slice 1: `doob todo add` (Days 1-2)

**TDD Red-Green-Refactor:**

1. **RED - Write failing tests:**
```rust
#[tokio::test]
async fn test_add_single_todo() {
    let db = setup_test_db().await;
    let result = run_cli(&["todo", "add", "Test task"], &db).await;

    assert!(result.is_ok());
    let todos = query_all_todos(&db).await;
    assert_eq!(todos.len(), 1);
    assert_eq!(todos[0].content, "Test task");
    assert_eq!(todos[0].status, TodoStatus::Pending);
}

#[tokio::test]
async fn test_add_batch_todos() {
    let db = setup_test_db().await;
    let result = run_cli(&["todo", "add", "T1", "T2", "T3"], &db).await;

    assert!(result.is_ok());
    let todos = query_all_todos(&db).await;
    assert_eq!(todos.len(), 3);
}

#[tokio::test]
async fn test_add_with_context_detection() {
    let temp_repo = setup_test_git_repo("test-repo").await;
    std::env::set_current_dir(&temp_repo);

    let db = setup_test_db().await;
    let result = run_cli(&["todo", "add", "Test"], &db).await;

    let todos = query_all_todos(&db).await;
    assert_eq!(todos[0].project, Some("test-repo".to_string()));
}
```

2. **GREEN - Minimal implementation:**
   - Parse CLI args with clap
   - Connect to SurrealDB
   - Detect context (git repo, file path)
   - Generate UUID
   - INSERT into database
   - Handle batch with loop

3. **REFACTOR - Extract modules:**
   - Move context detection to `context/` module
   - Extract DB connection setup
   - Create reusable query helpers

**Deliverable:** `doob todo add` works with single/batch and context detection

---

### Slice 2: `doob todo list` (Days 3-4)

**TDD Red-Green-Refactor:**

1. **RED - Write failing tests:**
```rust
#[tokio::test]
async fn test_list_all_todos() {
    let db = setup_test_db().await;
    seed_todos(&db, 5).await;

    let result = run_cli(&["todo", "list"], &db).await;
    assert!(result.is_ok());

    let todos = parse_output(&result.unwrap());
    assert_eq!(todos.len(), 5);
}

#[tokio::test]
async fn test_list_json_output() {
    let db = setup_test_db().await;
    seed_todos(&db, 3).await;

    let result = run_cli(&["--json", "todo", "list"], &db).await;
    let json: serde_json::Value = serde_json::from_str(&result.unwrap()).unwrap();

    assert_eq!(json["count"], 3);
    assert_eq!(json["todos"].as_array().unwrap().len(), 3);
}

#[tokio::test]
async fn test_list_filter_status() {
    let db = setup_test_db().await;
    seed_todos_with_status(&db, 3, TodoStatus::Pending).await;
    seed_todos_with_status(&db, 2, TodoStatus::Completed).await;

    let result = run_cli(&["todo", "list", "--status", "pending"], &db).await;
    let todos = parse_output(&result.unwrap());
    assert_eq!(todos.len(), 3);
}
```

2. **GREEN - Implement queries:**
   - SELECT query with filters
   - JSON formatter (serde_json)
   - Human-readable formatter
   - Status/project filtering

3. **REFACTOR - Output module:**
   - Create `output/json.rs` and `output/human.rs`
   - Reusable formatters for all commands
   - Consistent styling

**Deliverable:** `doob todo list` with filters and JSON output

---

### Slice 3: `doob todo complete` (Days 5-6)

**TDD Red-Green-Refactor:**

1. **RED - Write failing tests:**
```rust
#[tokio::test]
async fn test_complete_single_todo() {
    let db = setup_test_db().await;
    let todo = create_todo(&db, "Test").await;

    let result = run_cli(&["todo", "complete", &todo.id], &db).await;
    assert!(result.is_ok());

    let updated = get_todo(&db, &todo.id).await;
    assert_eq!(updated.status, TodoStatus::Completed);
    assert!(updated.completed_at.is_some());
}

#[tokio::test]
async fn test_complete_batch_todos() {
    let db = setup_test_db().await;
    let ids = create_todos(&db, 3).await;

    let result = run_cli(&["todo", "complete", &ids.join(" ")], &db).await;
    assert!(result.is_ok());

    for id in &ids {
        let todo = get_todo(&db, id).await;
        assert_eq!(todo.status, TodoStatus::Completed);
    }
}

#[tokio::test]
async fn test_complete_not_found_exit_code() {
    let db = setup_test_db().await;

    let result = run_cli(&["todo", "complete", "999"], &db).await;
    assert!(result.is_err());

    let exit_code = get_exit_code(&result.unwrap_err());
    assert_eq!(exit_code, ExitCode::TodoNotFound as i32);
}
```

2. **GREEN - Implement updates:**
   - UPDATE query to set status=completed
   - Set completed_at timestamp
   - Batch operation support
   - Proper exit codes

3. **REFACTOR - Error handling:**
   - Extract error handling patterns
   - Consistent exit code mapping
   - Reusable query builders

**Deliverable:** `doob todo complete` with batch and exit codes

---

### After Each Slice

- ✅ Run full test suite: `cargo test`
- ✅ Manual smoke test with real DB
- ✅ Git commit with descriptive message
- ✅ Update README with working examples

## Error Handling

```rust
use anyhow::{Context, Result};
use std::process;

#[derive(Debug)]
pub enum ExitCode {
    Success = 0,
    TodoNotFound = 1,
    InvalidInput = 2,
    DatabaseError = 3,
    ContextError = 4,
}

pub fn handle_error(err: anyhow::Error) -> ! {
    let exit_code = determine_exit_code(&err);
    eprintln!("Error: {}", err);
    process::exit(exit_code as i32);
}

fn determine_exit_code(err: &anyhow::Error) -> ExitCode {
    let msg = err.to_string();
    if msg.contains("not found") {
        ExitCode::TodoNotFound
    } else if msg.contains("invalid") {
        ExitCode::InvalidInput
    } else if msg.contains("database") {
        ExitCode::DatabaseError
    } else {
        ExitCode::DatabaseError
    }
}
```

## Testing Strategy

### Integration Tests (Primary)

**Setup Helper:**
```rust
// tests/common/mod.rs
pub async fn setup_test_db() -> Surreal<Client> {
    let db = Surreal::new::<Mem>(()).await.unwrap();
    db.use_ns("test").use_db("test").await.unwrap();

    // Load schema
    db.query(include_str!("../src/db/schema.surql"))
        .await
        .unwrap();

    db
}

pub async fn setup_test_git_repo(name: &str) -> TempDir {
    let dir = TempDir::new().unwrap();
    Repository::init(&dir).unwrap();

    // Add remote
    let mut remote = repo.remote("origin", &format!("git@github.com:test/{}.git", name)).unwrap();

    dir
}
```

**Test Categories:**
1. Command parsing tests
2. Database operations tests
3. Context detection tests
4. JSON output tests
5. Batch operations tests
6. Exit code tests

### Unit Tests (Supporting)

- Context detection logic (`context/git.rs`)
- Output formatters (`output/json.rs`, `output/human.rs`)
- Status enum conversions
- Date parsing

**Coverage Target:** > 80%

## GitHub Repository Setup

### Repository Details

- **Name:** `doob`
- **Description:** Modern, agent-first todo CLI built with Rust and SurrealDB
- **Visibility:** Public
- **License:** MIT
- **Topics:** rust, cli, todo, surrealdb, agents, productivity

### README.md Structure

```markdown
# doob

Modern todo management CLI built for coding agents and developers.

## Features

- 🚀 **Fast** - Written in Rust, SurrealDB embedded
- 🤖 **Agent-First** - JSON output, batch operations, context detection
- 📦 **Single Binary** - No dependencies, just works
- 🔍 **Context-Aware** - Auto-detects project and file from git

## Installation

### From Binary
Download from [releases](https://github.com/yourusername/doob/releases)

### From Source
```bash
cargo install --git https://github.com/yourusername/doob
```

## Quick Start

```bash
# Add a todo (auto-detects project/file)
doob todo add "Fix auth bug"

# Add with tags and priority
doob todo add "Refactor code" --priority 1 --tags refactor,urgent

# List todos
doob todo list

# List as JSON (for agents)
doob --json todo list --status pending

# Complete a todo
doob todo complete 42

# Batch operations
doob todo add "Task 1" "Task 2" "Task 3"
doob todo complete 1 2 3
```

## Agent Integration

Perfect for Claude Code, Cursor, Aider, and other AI coding assistants.

### JSON Output
```bash
doob --json todo list
```

### Exit Codes
- 0: Success
- 1: Todo not found
- 2: Invalid input
- 3: Database error

### Context Detection
Automatically detects project and file from git repository.

## Development

```bash
# Run tests
cargo test

# Build
cargo build --release

# Install locally
cargo install --path .
```

## License

MIT
```

### GitHub Actions Workflows

**CI Workflow (`.github/workflows/ci.yml`):**
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo test --all-features
      - run: cargo clippy -- -D warnings
      - run: cargo fmt -- --check
```

**Release Workflow (`.github/workflows/release.yml`):**
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo build --release
      - uses: actions/upload-artifact@v4
        with:
          name: doob-${{ matrix.os }}
          path: target/release/doob
```

## Success Criteria

### Functional Requirements

- [ ] `doob todo add "Task"` creates todo with auto-detected context
- [ ] `doob todo add "T1" "T2" "T3"` batch creates 3 todos
- [ ] `doob todo list` shows all todos in human-readable format
- [ ] `doob --json todo list` outputs valid JSON
- [ ] `doob todo list --status pending` filters correctly
- [ ] `doob todo list --project myproject` filters by project
- [ ] `doob todo complete 42` marks as completed with timestamp
- [ ] `doob todo complete 1 2 3` batch completes
- [ ] Exit code 1 when todo not found
- [ ] Exit code 2 for invalid input
- [ ] Context detection extracts project from git remote
- [ ] Context detection extracts file path relative to repo root
- [ ] User-provided context overrides auto-detection

### Quality Requirements

- [ ] All tests pass: `cargo test`
- [ ] Test coverage > 80%
- [ ] No clippy warnings: `cargo clippy`
- [ ] Code formatted: `cargo fmt`
- [ ] Binary builds: `cargo build --release`
- [ ] Database persists at `~/.claude/data/doob.db`
- [ ] README with clear examples
- [ ] GitHub repo created and public
- [ ] CI workflow running

### Performance Targets

- [ ] List 200 todos: < 10ms
- [ ] Add todo: < 5ms
- [ ] Binary startup: < 2ms
- [ ] JSON output parses with jq

## Timeline

**6 Days for MVP:**

- **Days 1-2:** Slice 1 - `doob todo add`
  - Project setup, Cargo.toml
  - TDD: tests → implementation → refactor
  - Context detection
  - Batch support

- **Days 3-4:** Slice 2 - `doob todo list`
  - Query implementation
  - JSON output formatter
  - Human output formatter
  - Filtering (status, project, limit)

- **Days 5-6:** Slice 3 - `doob todo complete`
  - Update queries
  - Batch complete
  - Exit code handling
  - Final integration tests

**Post-MVP:**
- GitHub repo setup
- CI/CD workflows
- README documentation
- Release v0.1.0

## Next Steps (After Phase 1)

**Phase 2:** Migration & Integration
- Import command for joedb export
- Update Valerie agent
- Update `/todo:*` commands
- Performance benchmarks

**Phase 3:** Dependencies (Future)
- Graph relations (blocks, subtasks)
- Dependency visualization
- Advanced queries

## Appendix: Cargo.toml

```toml
[package]
name = "doob"
version = "0.1.0"
edition = "2021"
authors = ["Your Name <you@example.com>"]
license = "MIT"
description = "Modern, agent-first todo CLI"
repository = "https://github.com/yourusername/doob"

[dependencies]
clap = { version = "4", features = ["derive"] }
surrealdb = { version = "2", features = ["kv-rocksdb"] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
chrono = { version = "0.4", features = ["serde"] }
anyhow = "1"
git2 = "0.19"
uuid = { version = "1", features = ["v4", "serde"] }

[dev-dependencies]
tempfile = "3"
assert_cmd = "2"
predicates = "3"
