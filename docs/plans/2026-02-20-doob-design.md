# Doob: Rust + SurrealDB Todo System Design

**Date:** 2026-02-20
**Status:** Design
**Type:** New Project - Rust Rewrite

## Overview

`doob` is a modern todo management CLI built in Rust with SurrealDB, replacing the current Python-based `joedb`.
Designed for speed, reliability, and advanced features like graph-based task dependencies.

## Goals

1. **Drop-in replacement** for joedb with identical CLI interface
2. **SurrealDB benefits**: Real-time subscriptions, graph relations, better JSON support
3. **Single binary**: No Python/uv dependencies, faster execution
4. **Enhanced features**: Task dependencies, subtasks, graph queries
5. **Migration path**: Import existing 204 todos from SQLite export

## Non-Goals

- Web UI (CLI-only for now)
- Cloud sync (local-first, optional sync later)
- Mobile apps (desktop focus)
- Replacing Valerie agent (agent stays, just uses new CLI)

## Architecture

### Tech Stack

```
doob (Rust binary)
├── clap (CLI framework)
├── surrealdb (embedded database)
├── tokio (async runtime)
├── serde (JSON serialization)
├── chrono (date/time handling)
└── anyhow (error handling)
```

### Database: SurrealDB Embedded

**Why SurrealDB over SQLite:**

| Feature | SQLite (joedb) | SurrealDB (doob) |
|---------|----------------|------------------|
| Relations | Manual joins | Native graph edges |
| JSON | Limited | First-class |
| Real-time | Polling | Live queries |
| Dependencies | Requires junction table | Native RELATE |
| Subtasks | parent_id column | Graph traversal |
| Queries | SQL only | SQL + GraphQL-like |

**Database location**: `~/.claude/data/doob.db` (SurrealDB embedded file)

### Data Model

```surrealql
DEFINE TABLE todo SCHEMAFUL;
DEFINE FIELD uuid ON TABLE todo TYPE string;
DEFINE FIELD content ON TABLE todo TYPE string ASSERT $value != NONE;
DEFINE FIELD status ON TABLE todo TYPE string
  ASSERT $value INSIDE ["pending", "in_progress", "completed", "cancelled"];
DEFINE FIELD priority ON TABLE todo TYPE int DEFAULT 0 ASSERT $value >= 0 AND $value <= 5;
DEFINE FIELD due_date ON TABLE todo TYPE option<datetime>;
DEFINE FIELD created_at ON TABLE todo TYPE datetime DEFAULT time::now();
DEFINE FIELD completed_at ON TABLE todo TYPE option<datetime>;
DEFINE FIELD updated_at ON TABLE todo TYPE datetime DEFAULT time::now();
DEFINE FIELD archived_at ON TABLE todo TYPE option<datetime>;
DEFINE FIELD project ON TABLE todo TYPE option<string>;
DEFINE FIELD project_path ON TABLE todo TYPE option<string>;
DEFINE FIELD file_path ON TABLE todo TYPE option<string>;
DEFINE FIELD session_id ON TABLE todo TYPE option<string>;
DEFINE FIELD source ON TABLE todo TYPE string DEFAULT "manual";
DEFINE FIELD tags ON TABLE todo TYPE array<string> DEFAULT [];
DEFINE FIELD metadata ON TABLE todo TYPE option<object> DEFAULT {};

-- Graph relations for dependencies
DEFINE TABLE blocks SCHEMAFULL TYPE RELATION IN todo OUT todo;
DEFINE TABLE subtask_of SCHEMAFULL TYPE RELATION IN todo OUT todo;

-- Indexes for performance
DEFINE INDEX idx_todo_status ON TABLE todo COLUMNS status;
DEFINE INDEX idx_todo_project ON TABLE todo COLUMNS project;
DEFINE INDEX idx_todo_due_date ON TABLE todo COLUMNS due_date;
DEFINE INDEX idx_todo_tags ON TABLE todo COLUMNS tags;
```

**Key improvements:**
- **tags**: Native array instead of junction table
- **metadata**: Flexible JSON for future extensions
- **Graph relations**: `blocks` and `subtask_of` as first-class edges
- **Validation**: Schema enforcement at database level

## CLI Interface

### Command Structure

```bash
doob [OPTIONS] <COMMAND>

Commands:
  todo       Manage todos (list, add, update, complete, delete)
  deps       Manage task dependencies (add, remove, graph)
  query      Run custom SurrealDB queries
  import     Import from joedb export
  export     Export to JSON
  sync       Sync with external systems
  config     Manage configuration

Options:
  --db <PATH>    Database path (default: ~/.claude/data/doob.db)
  --json         Output in JSON format
  -h, --help     Print help
  -V, --version  Print version
```

### Todo Subcommands

**Maintaining joedb compatibility:**

```bash
# List todos (identical to joedb)
doob todo list                              # All active
doob todo list --status pending             # Filtered
doob todo list --project odk                # Project-specific
doob todo list --limit 10                   # Limited

# Add todo (enhanced with graph support)
doob todo add "Task description" \
  --priority 1 \
  --project odk \
  --file src/main.rs \
  --tags bug,urgent \
  --due 2026-03-01 \
  --blocks 42                                # NEW: Blocks todo #42
  --subtask-of 10                            # NEW: Subtask of #10

# Update todo (identical to joedb)
doob todo update 42 --status completed
doob todo update 42 --priority 2
doob todo update 42 --due 2026-12-31
doob todo update 42 --due clear

# Complete/delete (identical to joedb)
doob todo complete 42
doob todo delete 42
```

### New Features: Dependencies

```bash
# Add dependency relationships
doob deps add 42 --blocks 43              # 42 blocks 43 (43 can't start until 42 done)
doob deps add 42 --subtask-of 10          # 42 is subtask of 10

# Remove dependencies
doob deps remove 42 --blocks 43
doob deps remove 42 --subtask-of 10

# Visualize dependency graph
doob deps graph                           # ASCII tree view
doob deps graph --dot                     # Graphviz DOT format
doob deps graph --from 42                 # From specific todo

# Find blocked tasks
doob deps blocked                         # All blocked todos
doob deps blocking 42                     # What 42 is blocking
```

### Migration Command

```bash
# Import from joedb export
doob import joedb ~/.claude/data/exports/todos-complete-export.json

# Preview import
doob import joedb --dry-run export.json

# Export for backup
doob export --output backup.json
```

## Implementation Plan

### Phase 1: Core CLI (Week 1)

**Tasks:**
1. Project setup with Cargo.toml
2. CLI structure with clap
3. SurrealDB embedded setup
4. Schema definition
5. Basic CRUD operations (add, list, update, delete, complete)
6. Test suite (integration tests with temp DB)

**Deliverable:** Working `doob todo` commands with joedb compatibility

### Phase 2: Migration (Week 1)

**Tasks:**
1. JSON import logic
2. joedb export parser
3. Data validation
4. Migration tests
5. Migration documentation

**Deliverable:** Successful import of 204 existing todos

### Phase 3: Dependencies (Week 2)

**Tasks:**
1. Graph relation setup (blocks, subtask_of)
2. `doob deps` subcommands
3. Graph traversal queries
4. Cycle detection
5. Visualization (ASCII tree)
6. Dependency tests

**Deliverable:** Full dependency management

### Phase 4: Integration (Week 2)

**Tasks:**
1. Update Valerie agent to use `doob`
2. Update `/todo:*` commands to use `doob`
3. Performance benchmarks (doob vs joedb)
4. Documentation
5. Migration guide for users

**Deliverable:** Production-ready `doob` replacing `joedb`

## File Structure

```
doob/
├── Cargo.toml                 # Rust dependencies
├── README.md                  # Project documentation
├── src/
│   ├── main.rs                # CLI entry point
│   ├── cli/
│   │   ├── mod.rs             # CLI module
│   │   ├── todo.rs            # Todo subcommands
│   │   ├── deps.rs            # Dependency subcommands
│   │   ├── import.rs          # Import commands
│   │   └── export.rs          # Export commands
│   ├── db/
│   │   ├── mod.rs             # Database module
│   │   ├── schema.rs          # SurrealDB schema
│   │   ├── queries.rs         # Query builders
│   │   └── migrations.rs      # Migration logic
│   ├── models/
│   │   ├── mod.rs             # Data models
│   │   ├── todo.rs            # Todo struct
│   │   └── dependency.rs      # Dependency types
│   └── utils/
│       ├── mod.rs             # Utilities
│       ├── date.rs            # Date parsing
│       └── output.rs          # Output formatting
├── tests/
│   ├── integration/           # Integration tests
│   │   ├── todo_crud.rs
│   │   ├── dependencies.rs
│   │   └── import.rs
│   └── fixtures/              # Test data
│       └── sample_export.json
└── migrations/                # Database migrations
    └── initial_schema.surql
```

## Data Migration Strategy

### Step 1: Export from joedb (DONE ✅)

- Exported 204 todos to `~/.claude/data/exports/todos-complete-export.json`
- Includes all fields: uuid, content, status, priority, tags, etc.

### Step 2: Import to doob

```bash
doob import joedb ~/.claude/data/exports/todos-complete-export.json
```

**Import logic:**
1. Read JSON export
2. Validate schema
3. Create todos in SurrealDB
4. Map old IDs to new record IDs
5. Preserve UUIDs for cross-reference
6. Import tags as arrays
7. Create projects if needed
8. Report success/failures

**Validation:**
- Check UUID uniqueness
- Validate status values
- Validate priority range (0-5)
- Check file paths exist
- Validate date formats

### Step 3: Verification

```bash
# Compare counts
joedb todo list --status pending | wc -l   # 183
doob todo list --status pending | wc -l    # Should be 183

# Spot check
joedb todo list --limit 5
doob todo list --limit 5

# Check specific todo
joedb todo list | grep "Document security boundaries"
doob todo list | grep "Document security boundaries"
```

### Step 4: Cutover

1. Stop using joedb commands
2. Update Valerie agent to use doob
3. Update todo commands to use doob
4. Backup joedb SQLite file
5. Optional: Keep joedb as fallback for 1 week

## Valerie Agent Integration

**Minimal changes needed:**

```diff
# agents/core/valerie.md

-All task management uses the `joedb` CLI backed by SQLite
+All task management uses the `doob` CLI backed by SurrealDB

 ```bash
-joedb todo list
-joedb todo add "Task" --priority 1
-joedb todo update ID --status completed
+doob todo list
+doob todo add "Task" --priority 1
+doob todo update ID --status completed
 ```
```

Agent behavior stays identical - just calls `doob` instead of `joedb`.

## Commands Integration

**Already fixed!** Commands now use joedb interface, which doob will match:

```markdown
# commands/todo/list.md
!`doob todo list $ARGUMENTS`  # Just change joedb -> doob

# commands/todo/add.md
!`doob todo add $ARGUMENTS`

# commands/todo/complete.md
!`doob todo complete $ARGUMENTS`
```

Simple find/replace in 6 files.

## Performance Targets

| Operation | joedb (Python) | doob (Rust) Target |
|-----------|----------------|---------------------|
| `list` 200 todos | ~100ms | < 10ms |
| `add` todo | ~80ms | < 5ms |
| `update` status | ~70ms | < 5ms |
| `query` with tags | ~120ms | < 15ms |
| Startup time | ~200ms | < 2ms |

**Why faster:**
- Compiled binary (no Python interpreter)
- SurrealDB embedded (no process spawn)
- Optimized queries (native graph traversal)
- Zero network latency (embedded DB)

## Testing Strategy

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_add_todo() {
        let db = setup_test_db().await;
        let todo = create_todo("Test task", 1).await;
        assert_eq!(todo.content, "Test task");
        assert_eq!(todo.priority, 1);
    }

    #[tokio::test]
    async fn test_dependency_cycle_detection() {
        let db = setup_test_db().await;
        let todo1 = create_todo("Task 1", 1).await;
        let todo2 = create_todo("Task 2", 1).await;

        // Create cycle: 1 -> 2 -> 1
        add_dependency(todo1, todo2, "blocks").await;
        let result = add_dependency(todo2, todo1, "blocks").await;

        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("cycle"));
    }
}
```

### Integration Tests

```rust
#[tokio::test]
async fn test_full_workflow() {
    // Setup
    let db_path = temp_dir().join("test.db");
    let cli = DoobCli::new(&db_path);

    // Add todos
    cli.run(&["todo", "add", "Parent task"]).await?;
    cli.run(&["todo", "add", "Subtask 1", "--subtask-of", "1"]).await?;
    cli.run(&["todo", "add", "Subtask 2", "--subtask-of", "1"]).await?;

    // List subtasks
    let output = cli.run(&["todo", "list", "--parent", "1"]).await?;
    assert!(output.contains("Subtask 1"));
    assert!(output.contains("Subtask 2"));

    // Complete parent (should affect subtasks)
    cli.run(&["todo", "complete", "1"]).await?;

    // Verify
    let output = cli.run(&["todo", "list", "--status", "completed"]).await?;
    assert!(output.contains("Parent task"));
}
```

### Migration Tests

```rust
#[tokio::test]
async fn test_import_joedb_export() {
    let export_path = "tests/fixtures/todos-complete-export.json";
    let db_path = temp_dir().join("imported.db");

    // Import
    let result = import_joedb(export_path, &db_path).await;
    assert!(result.is_ok());

    // Verify counts
    let todos = list_todos(&db_path, None).await?;
    assert_eq!(todos.len(), 204);

    // Verify specific todo
    let todo = find_by_uuid(&db_path, "da23f906-20bd-4c04-9762-61855be341db").await?;
    assert_eq!(todo.content, "build n8n sandbox coder module");
    assert_eq!(todo.tags, vec!["test", "cli"]);
}
```

## Error Handling

```rust
#[derive(Debug, thiserror::Error)]
pub enum DoobError {
    #[error("Database error: {0}")]
    Database(#[from] surrealdb::Error),

    #[error("Todo not found: {0}")]
    TodoNotFound(String),

    #[error("Dependency cycle detected: {0}")]
    DependencyCycle(String),

    #[error("Invalid status: {0}. Must be: pending, in_progress, completed, cancelled")]
    InvalidStatus(String),

    #[error("Invalid priority: {0}. Must be 0-5")]
    InvalidPriority(u8),

    #[error("Invalid date format: {0}")]
    InvalidDate(String),

    #[error("Import error: {0}")]
    Import(String),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
}

pub type Result<T> = std::result::Result<T, DoobError>;
```

## Configuration

```toml
# ~/.config/doob/config.toml

[database]
path = "~/.claude/data/doob.db"
backup_on_startup = true
backup_retention_days = 30

[display]
default_limit = 50
date_format = "%Y-%m-%d"
show_tags = true
show_project = true

[behavior]
auto_archive_completed = false
archive_after_days = 90
warn_on_cycles = true
```

## Deployment

### Installation

```bash
# From source
git clone https://github.com/yourusername/doob.git
cd doob
cargo build --release
cp target/release/doob ~/.local/bin/

# Verify
doob --version

# Import existing todos
doob import joedb ~/.claude/data/exports/todos-complete-export.json

# Test
doob todo list --limit 5
```

### Release Binary

```bash
# Build for current platform
cargo build --release

# Cross-compile for Linux (from macOS)
cargo build --release --target x86_64-unknown-linux-gnu

# Create distribution
tar -czf doob-v1.0.0-macos-arm64.tar.gz -C target/release doob
```

## Success Criteria

- [ ] All 204 todos imported successfully
- [ ] joedb CLI interface 100% compatible
- [ ] All existing `/todo:*` commands work with doob
- [ ] Valerie agent works with doob
- [ ] Performance targets met (>10x faster than joedb)
- [ ] Dependency graph features working
- [ ] Test coverage > 80%
- [ ] Documentation complete
- [ ] Zero data loss during migration

## Future Enhancements

**Post-v1.0:**
- [ ] Web UI (Tauri or Leptos)
- [ ] Real-time sync across devices
- [ ] Markdown export/import
- [ ] Integration with Linear/Jira
- [ ] AI-powered task suggestions
- [ ] Calendar view
- [ ] Pomodoro timer integration
- [ ] Mobile apps (via Tauri)

## Timeline

**Week 1:**
- Day 1-2: Project setup, core CRUD
- Day 3-4: Migration logic
- Day 5-7: Testing, bugfixes

**Week 2:**
- Day 8-10: Dependency system
- Day 11-12: Integration with Valerie/commands
- Day 13-14: Documentation, release

**Total: 2 weeks to production-ready v1.0**

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| SurrealDB instability | High | Use stable embedded version, extensive testing |
| Migration data loss | Critical | Dry-run mode, keep joedb backup, verification |
| Performance regression | Medium | Benchmark suite, optimize queries |
| Breaking Valerie | High | Maintain CLI compatibility, integration tests |
| User adoption | Low | Identical interface, clear migration guide |

## Appendices

### Appendix A: SurrealDB Queries

**List todos with subtasks:**
```surrealql
SELECT *, ->subtask_of<-todo.* as subtasks
FROM todo
WHERE status = "pending"
ORDER BY priority ASC, created_at DESC
LIMIT 50;
```

**Find blocking chain:**
```surrealql
SELECT *,
  ->blocks->todo.* as blocks_directly,
  ->blocks->todo->blocks->todo.* as blocks_transitively
FROM todo:42;
```

**Dependency graph:**
```surrealql
SELECT id, content,
  count(->blocks->todo) as blocking_count,
  count(<-blocks<-todo) as blocked_by_count
FROM todo
WHERE status != "completed";
```

### Appendix B: Migration Checklist

- [ ] Export joedb to JSON (DONE ✅)
- [ ] Backup SQLite database
- [ ] Build doob binary
- [ ] Run import --dry-run
- [ ] Fix any validation errors
- [ ] Run actual import
- [ ] Verify counts match
- [ ] Spot-check 10 random todos
- [ ] Update Valerie agent
- [ ] Update todo commands
- [ ] Test full workflow with commands
- [ ] Archive joedb (keep for 1 week)
- [ ] Announce migration complete

### Appendix C: Compatibility Matrix

| joedb Command | doob Equivalent | Status |
|---------------|-----------------|--------|
| `joedb todo list` | `doob todo list` | ✅ Compatible |
| `joedb todo add` | `doob todo add` | ✅ Enhanced (deps) |
| `joedb todo update` | `doob todo update` | ✅ Compatible |
| `joedb todo complete` | `doob todo complete` | ✅ Compatible |
| `joedb todo delete` | `doob todo delete` | ✅ Compatible |
| `joedb note` | N/A | ⚠️ Not in v1.0 |
| `joedb sync` | N/A | ⚠️ Not in v1.0 |

---

**Author:** Claude Sonnet 4.5
**Date:** 2026-02-20
**Status:** Ready for Implementation
