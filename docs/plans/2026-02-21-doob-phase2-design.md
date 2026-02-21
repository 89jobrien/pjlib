# Doob Phase 2: Migration & Integration - Design Document

**Date:** 2026-02-21
**Status:** Design Approved
**Phase:** 2 (Migration & Integration)
**Dependencies:** Phase 1 MVP (Complete)

## Overview

Phase 2 migrates from the Python-based `joedb` system to the Rust-based `doob` CLI. This includes importing 204 existing todos, updating the Valerie agent, updating `/todo:*` commands, and updating the TodoWrite sync hook.

## Goals

1. **Import existing data** - Migrate 204 todos from joedb SQLite export to doob
2. **System-wide integration** - Update all commands, agents, and hooks to use doob
3. **Safe migration** - Dry-run preview, automatic backup, verification
4. **Clean transition** - Complete switch to doob, remove joedb dependencies

## Migration Strategy

### Approach: Clean Migration with Backup

**Implementation:**
- Add `doob import joedb` command with `--dry-run` flag
- Import preserves all data, sets `archived_at` for completed todos
- Automatic backup of joedb database before import
- Update Valerie agent to use doob commands
- Update all 6 `/todo:*` commands to use doob
- Update TodoWrite sync hook to call doob
- Remove joedb references after successful migration

**Why this approach:**
- doob Phase 1 is production-ready with all features working
- Dry-run preview mitigates risk
- Automatic backup provides safety net
- Clean break simplifies long-term maintenance
- Foundation for Phase 3 (graph-based dependencies)

## Architecture

### Section 1: Import Command

**Command Structure:**
```bash
doob import joedb <export-file> [--dry-run] [--backup]
```

**Import Logic Flow:**
1. **Validate export file**
   - Check JSON structure
   - Verify schema version: "joedb-sqlite"
   - Ensure required fields exist

2. **Backup joedb database** (if `--backup` or joedb DB detected)
   - Copy `~/.claude/data/claude.db` → `~/.claude/data/backups/claude.db.backup.TIMESTAMP`
   - Print backup location for user
   - Abort if backup fails

3. **Dry-run mode** (if `--dry-run` flag)
   - Parse all todos
   - Show counts: total, pending, completed, with tags
   - Display sample todos (first 3)
   - Show what would be imported/archived
   - Exit without modifying database

4. **Import todos** (actual import)
   - For each todo in export:
     - Map joedb fields to doob schema
     - Set `archived_at = completed_at` for completed todos
     - Preserve: uuid, content, status, priority, tags, dates, project, file_path
     - Generate new doob IDs (SurrealDB record format)
   - Report progress every 50 todos
   - Handle errors gracefully (skip with warning)

5. **Verification**
   - Compare counts (imported vs export)
   - List sample imported todos
   - Report success/warnings

**Field Mapping:**

| joedb Field | doob Field | Notes |
|------------|-----------|-------|
| `id` | (ignore) | doob generates new SurrealDB IDs |
| `uuid` | `uuid` | Preserve original UUID |
| `content` | `content` | Direct mapping |
| `status` | `status` | pending/in_progress/completed |
| `priority` | `priority` | 0-5 scale |
| `tags[]` | `tags[]` | Native array (no junction table) |
| `completed_at` | `completed_at` | Preserve timestamp |
| `completed_at` | `archived_at` | If status=completed, set archived_at |
| `created_at` | `created_at` | Preserve timestamp |
| `updated_at` | `updated_at` | Preserve timestamp |
| `due_date` | (skip) | Not in Phase 1 schema, add in Phase 3 |
| `project` | `project` | Direct mapping |
| `project_path` | `project_path` | Direct mapping |
| `file_path` | `file_path` | Direct mapping |
| `session_id` | (skip) | Not needed in doob |
| `source` | (skip) | All imports marked as source="import" |
| `parent_id` | (skip) | Phase 3 feature (subtasks/dependencies) |
| `archived_at` | (skip from import) | Set by import logic for completed |

**Error Handling:**
- Invalid JSON → Abort with clear error message and line number
- Missing required fields (uuid, content) → Skip todo with warning
- Database connection fails → Abort with helpful message
- Backup fails → Abort (don't import without backup)
- Duplicate UUID → Skip with warning (shouldn't happen)

**Example Output:**

Dry-run:
```
Analyzing export: /Users/joe/.claude/data/exports/todos-complete-export.json
✓ Valid joedb export (schema: joedb-sqlite)

Import Summary:
  Total todos: 204
  Pending: 183 (will be active)
  Completed: 21 (will be archived)
  With tags: 178

Sample todos to import:
  1. [pending] "build n8n sandbox coder module" [tags: test, cli]
  2. [pending] "New todo item"
  3. [completed] "Fix authentication bug" → will be archived

Run without --dry-run to import.
```

Actual import:
```
Creating backup: /Users/joe/.claude/data/backups/claude.db.backup.20260221-120000
✓ Backup created successfully

Importing todos from joedb export...
Progress: 50/204 (24%)
Progress: 100/204 (49%)
Progress: 150/204 (73%)
Progress: 200/204 (98%)

Import complete!
  ✓ Imported: 204 todos
  ✓ Active: 183
  ✓ Archived: 21
  ✓ Warnings: 0
  ✓ Errors: 0

Verification:
  Sample active todos:
    - todo:abc123 | "build n8n sandbox coder module"
    - todo:def456 | "New todo item"

  Sample archived todos:
    - todo:ghi789 | "Fix authentication bug" [completed: 2025-12-13]

Run 'doob todo list' to see active todos.
Run 'doob todo list --archived' to see archived todos.
```

### Section 2: System-Wide Updates

**Files Requiring Updates (9 total):**

#### Commands (6 files)
All in `/commands/todo/`:
- `add.md` - Update `Bash(joedb:*)` → `Bash(doob:*)`, update examples
- `list.md` - Update CLI calls and examples
- `complete.md` - Update to use `doob todo complete`
- `remove.md` - Update CLI calls
- `due.md` - Update CLI calls (note: Phase 3 feature)
- `undo.md` - Update CLI calls

**Changes:**
```diff
- allowed-tools: Bash(joedb:*)
+ allowed-tools: Bash(doob:*)

- !`joedb todo add $ARGUMENTS`
+ !`doob todo add $ARGUMENTS`
```

#### Agent (1 file)
`/agents/core/valerie.md`:
- Update "Core System" section: joedb → doob, SQLite → SurrealDB
- Update all command examples
- Update database location: `claude.db` → `doob.db`
- Keep personality, workflow, interaction style unchanged

**Command Mapping:**
```bash
# OLD (joedb)                              # NEW (doob)
joedb todo list                            → doob todo list
joedb todo list --status pending           → doob todo list --status pending
joedb todo add "Task" --priority 1         → doob todo add "Task" --priority 1
joedb todo update ID --status completed    → doob todo complete ID
joedb todo update ID --status pending      → doob todo update ID --status pending
joedb todo delete ID                       → (Phase 3: doob todo delete ID)
```

**Key Differences to Document:**
- `doob todo complete <id>` - Dedicated complete command (simpler than update)
- `doob --json todo list` - Global JSON flag (better for agents)
- Context auto-detection - doob auto-fills project from git

#### Hooks (2 files)

**`/hooks/workflows/todo_sync_workflow.py`:**
Update subprocess call to use doob:
```python
# OLD
cmd = [
    "joedb", "todo", "add",
    content,
    "--project", "claude-session",
    "--tags", f"claude,{status}"
]

# NEW
cmd = [
    "doob", "todo", "add",
    content,
    "--project", "claude-session",
    "--tags", f"claude,{status}"
]
```

**`/hooks/tests/test_todo_sync.py`:**
Update test to verify doob integration instead of joedb.

**Files to Skip:**
- `archived/agents/utilitarian/migration-auditor.md` - Archived, not active
- `commands/research-*.md` - Just examples mentioning joedb as a project name
- `tasks/*/` - Old session data, not active code

### Section 3: Testing & Verification

**Import Testing:**

1. **Unit Tests** (`tests/import_test.rs`):
   - Valid JSON parsing
   - Field mapping (joedb → doob schema)
   - Archive logic (completed → archived_at)
   - Tag array conversion
   - Error handling (invalid JSON, missing fields)
   - Dry-run mode (no DB modification)

2. **Integration Tests**:
   - Import small dataset (5-10 todos) to test DB
   - Verify counts match
   - Check archived todos excluded from default list
   - Verify tags imported correctly
   - Test progress reporting

3. **Full Migration Test**:
   - Import real 204-todo export to test database
   - Verify counts: 204 total, 183 pending, 21 archived
   - Spot-check 5 random todos (content, tags, dates match)
   - Test query performance with full dataset

**System Integration Testing:**

1. **Command Verification** - Run each updated `/todo:*` command, verify output
2. **Valerie Verification** - Test Valerie with sample tasks
3. **Hook Verification** - Test TodoWrite → doob sync
4. **End-to-end Workflow**:
   ```bash
   /todo:add "Test task" --priority 1
   /todo:list
   /todo:complete <id>
   ```

**Rollback Plan:**
- Original `claude.db` backed up at `~/.claude/data/backups/claude.db.backup.TIMESTAMP`
- If import fails or data issues found:
  1. Stop using doob
  2. Restore joedb backup: `cp backup.TIMESTAMP claude.db`
  3. Continue with joedb while fixing doob issues
- Export file (`todos-complete-export.json`) preserved as source of truth
- Can re-run import after fixes

### Section 4: Implementation Plan

**Phase 2A: Import Command** (4 tasks)
- Task 1: Import command structure with CLI parsing and dry-run mode
- Task 2: JSON parsing and field mapping logic
- Task 3: Archive logic for completed todos
- Task 4: Backup mechanism and verification output

**Phase 2B: System Integration** (4 tasks)
- Task 5: Update 6 `/todo:*` commands (add, list, complete, remove, due, undo)
- Task 6: Update Valerie agent markdown
- Task 7: Update todo_sync_workflow.py hook
- Task 8: Update test_todo_sync.py

**Phase 2C: Migration & Verification** (2 tasks)
- Task 9: Run dry-run import, review output, fix issues
- Task 10: Execute actual import, verify data integrity

**Implementation Order:**
1. Build import command with tests (TDD)
2. Test import with export file (dry-run)
3. Update all commands/agents/hooks
4. Run actual import
5. Verify end-to-end workflow
6. Document migration completion

## Success Criteria

- ✅ All 204 todos imported (183 active, 21 archived)
- ✅ `doob todo list` shows only pending/in_progress (no completed)
- ✅ `doob todo list --archived --status completed` shows 21 archived todos
- ✅ Tags preserved correctly (178 todos with tags)
- ✅ `/todo:add` creates new todos in doob
- ✅ `/todo:list` displays todos from doob
- ✅ `/todo:complete` marks todos complete in doob
- ✅ Valerie uses doob for all task operations
- ✅ TodoWrite hook syncs to doob successfully
- ✅ joedb backup created before import with timestamp
- ✅ All tests passing (import tests, integration tests)
- ✅ No regression in functionality

## Migration Checklist

**Pre-Migration:**
- [ ] Phase 1 MVP complete and verified
- [ ] Export file exists: `~/.claude/data/exports/todos-complete-export.json`
- [ ] Backup directory exists: `~/.claude/data/backups/`

**Migration:**
- [ ] Build and test import command
- [ ] Run dry-run: `doob import joedb export.json --dry-run`
- [ ] Review dry-run output
- [ ] Run actual import: `doob import joedb export.json`
- [ ] Verify backup created
- [ ] Verify counts match (204 total, 183 active, 21 archived)
- [ ] Spot-check sample todos

**Integration:**
- [ ] Update 6 `/todo:*` commands
- [ ] Update Valerie agent
- [ ] Update todo_sync hook
- [ ] Test `/todo:add`, `/todo:list`, `/todo:complete`
- [ ] Test Valerie task management
- [ ] Test TodoWrite sync

**Post-Migration:**
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Rollback plan documented
- [ ] joedb can be deprecated

## Next Steps (Phase 3)

After Phase 2 completes:
- Due dates support
- Task dependencies (graph relations)
- Subtasks (parent_id → subtask_of edges)
- Delete/archive commands
- Performance benchmarks vs joedb

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Data loss during import | Critical | Automatic backup, dry-run preview, verification |
| Import failures | High | Error handling, skip with warning, clear error messages |
| Performance issues | Medium | Test with full dataset, optimize queries if needed |
| Integration bugs | Medium | Comprehensive testing, rollback plan |
| User confusion | Low | Clear documentation, command examples |

## Technical Notes

**Database Compatibility:**
- joedb: SQLite with junction tables for tags
- doob: SurrealDB with native array support
- No schema conflicts (separate databases)

**Import Performance:**
- 204 todos should import in < 1 second
- Progress reporting every 50 todos
- Batch insert for efficiency

**Archive Strategy:**
- Completed todos get `archived_at = completed_at`
- Default queries exclude archived (WHERE archived_at IS NULL)
- Use `--archived` flag to include in queries

**UUID Preservation:**
- Original joedb UUIDs preserved in doob
- Enables future data correlation if needed
- No UUID conflicts (globally unique)
