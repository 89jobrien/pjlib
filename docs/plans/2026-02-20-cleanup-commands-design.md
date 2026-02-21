# Storage Cleanup Commands Design

**Date:** 2026-02-20
**Status:** Approved
**Type:** New Feature - Utility Commands

## Overview

Design for a suite of specialized cleanup commands to help manage disk storage in `~/dev/` and `~/Documents/`
directories by safely removing regenerable artifacts (dependencies, build outputs, git caches, application caches).

## Goals

1. Provide granular control over different types of cleanup operations
2. Maximize safety through interactive confirmations and dry-run modes
3. Give clear visibility into storage usage and reclaimable space
4. Follow existing Claude Code command patterns and conventions
5. Enable quick recovery with restoration commands

## Non-Goals

- Automated cleanup without user intervention
- Cleaning system-level caches or directories
- Managing cloud storage or remote resources
- Optimization or defragmentation of filesystems

## Architecture

### Command Suite (5 commands)

All commands placed in `/util/` category:

1. **`/util:analyze-storage`** - Storage analysis and discovery
2. **`/util:cleanup-deps`** - Dependency cleanup (node_modules, .venv, __pycache__)
3. **`/util:cleanup-builds`** - Build artifact cleanup (.next, dist, build, target)
4. **`/util:cleanup-git`** - Git maintenance (packed objects, worktrees, gc)
5. **`/util:cleanup-caches`** - Application cache analysis and cleanup

### Design Principles

- **Focused responsibility:** Each command handles one type of cleanup
- **Interactive by default:** Require confirmation before deletion
- **Transparent:** Show what will be deleted and how to restore it
- **Fail-safe:** Dry-run mode, protected paths, recovery information
- **Discoverable:** Consistent naming (`/util:cleanup-*`) and argument patterns

## Command Specifications

### 1. /util:analyze-storage

**Purpose:** Non-destructive storage analysis to guide cleanup decisions.

**Arguments:**
- `[path]` - Directory to analyze (default: `~/dev/` and `~/Documents/`)

**Behavior:**
- Run `du -h -d 1 <path>` to get directory sizes
- Identify cleanup opportunities:
  - Count of `node_modules/` directories and total size
  - Count of `.venv/` directories and total size
  - Count of build directories (`.next/`, `dist/`, etc.) and total size
  - Git repository sizes and packed object sizes
  - Cache directories and sizes
- Display sorted by size (largest first)
- Estimate total reclaimable space
- Suggest which cleanup commands to run

**Output Format:**
```
STORAGE ANALYSIS: /Users/joe/dev/
Total: 15 GB

Top Directories by Size:
  maestro/           10 GB
  kan/               3.0 GB
  logwatcher/        1.8 GB

Cleanup Opportunities:
  Dependencies:      2.5 GB (3 directories)
    - Run: /util:cleanup-deps --path=~/dev/
  Build Artifacts:   1.2 GB (5 directories)
    - Run: /util:cleanup-builds --path=~/dev/
  Git Objects:       450 MB (packed objects, reflog)
    - Run: /util:cleanup-git --path=~/dev/
  Caches:           320 MB (needs analysis)
    - Run: /util:cleanup-caches --path=~/dev/

Total Reclaimable: ~4.4 GB
```

### 2. /util:cleanup-deps

**Purpose:** Clean dependency directories that can be regenerated.

**Targets:**
- `node_modules/` (npm/yarn/pnpm)
- `.venv/`, `venv/` (Python virtual environments)
- `__pycache__/`, `.pytest_cache/` (Python caches)
- `vendor/` (Go, PHP dependencies)

**Arguments:**
- `--path=DIR` - Directory to scan (default: `~/dev/` and `~/Documents/`)
- `--dry-run` - Show what would be deleted without deleting
- `--yes` - Skip confirmations (use carefully)

**Behavior:**
1. Find all dependency directories recursively
2. Calculate size and last modified time for each
3. Check for protected markers (`.keep`, local packages)
4. Display sorted list with sizes
5. Prompt for confirmation per directory
6. Delete confirmed directories
7. Display restoration commands

**Safety Checks:**
- Skip if directory contains `.keep` file
- Skip if `node_modules/` contains local packages (check for `file:` in package.json)
- Skip if `.venv/` contains editable installs (check for `.egg-link` files)
- Never delete if path is current working directory

**Restoration Commands:**
- `node_modules/` → `npm install` or `yarn install` or `pnpm install`
- `.venv/` → `uv sync` or `python -m venv .venv && pip install -r requirements.txt`
- `__pycache__/` → Auto-regenerated on next run

### 3. /util:cleanup-builds

**Purpose:** Clean build artifacts that can be rebuilt.

**Targets:**
- `.next/` (Next.js)
- `dist/`, `build/` (Vite, CRA, generic builds)
- `target/` (Rust, Java)
- `.turbo/` (Turborepo cache)
- `out/` (Next.js static export)
- `.nuxt/`, `.output/` (Nuxt.js)

**Arguments:**
- `--path=DIR` - Directory to scan (default: `~/dev/` and `~/Documents/`)
- `--dry-run` - Show what would be deleted without deleting
- `--yes` - Skip confirmations

**Behavior:**
- Same flow as cleanup-deps but targeting build directories
- Detect framework from nearby files (package.json, Cargo.toml, etc.)
- Show framework-specific rebuild commands

**Restoration Commands:**
- `.next/` → `npm run build` or `next build`
- `dist/` → `npm run build` or `vite build`
- `target/` → `cargo build`

### 4. /util:cleanup-git

**Purpose:** Git repository maintenance and cache cleanup.

**Targets:**
- Packed objects (`.git/objects/pack/`)
- Orphaned worktrees
- Reflog entries older than 30 days
- Dangling commits

**Arguments:**
- `--path=DIR` - Directory to scan (default: `~/dev/` and `~/Documents/`)
- `--dry-run` - Show what would be done without doing it
- `--yes` - Skip confirmations

**Behavior:**
1. Find all `.git/` directories
2. Run `git gc --aggressive` to repack objects
3. List orphaned worktrees with `git worktree list`
4. Prune reflog older than 30 days
5. Show space savings

**Safety Checks:**
- Never delete `.git/` directory itself
- Check for unpushed commits before pruning
- Warn if reflog contains recent activity

**Commands Used:**
```bash
git gc --aggressive
git worktree prune
git reflog expire --expire=30.days.ago --all
git prune
```

### 5. /util:cleanup-caches

**Purpose:** Analyze and clean application caches with safety categorization.

**Targets:**
- `.cache/` directories
- Temporary files (`/tmp/`, `*.tmp`)
- Log files (`*.log`, `logs/`)
- Application-specific caches (browser caches, build tool caches)

**Arguments:**
- `--path=DIR` - Directory to scan (default: `~/dev/` and `~/Documents/`)
- `--dry-run` - Show what would be deleted without deleting
- `--category=LEVEL` - Filter by safety level (safe|review|danger)

**Behavior:**
1. Deep scan for cache directories and files
2. Categorize by safety level:
   - **SAFE:** Package manager caches, browser caches (can regenerate)
   - **REVIEW:** Application data caches (might contain state)
   - **DANGER:** Databases, credential stores (never auto-delete)
3. Show age, size, and contents summary
4. Require explicit opt-in per category
5. Never delete DANGER category without manual review

**Safety Categories:**

SAFE (auto-suggest for deletion):
- `~/.npm/`, `~/.cache/yarn/`, `~/.cache/pip/`
- Browser caches (Chrome, Firefox cache dirs)
- Build tool caches (`.turbo/`, `.next/cache/`)

REVIEW (show but require confirmation):
- Application-specific `.cache/` directories
- Log files older than 30 days
- Temporary files

DANGER (show but don't suggest deletion):
- SQLite databases (`.db`, `.sqlite`)
- Credential stores (`.config/`, `.credentials/`)
- Any cache with "auth", "token", "session" in path

## Safety Mechanisms

### Protected Paths

Never delete:
- `.git/` directories themselves (only clean contents)
- Directories with `.keep` or `DO_NOT_DELETE` markers
- Current working directory
- System directories (`/`, `/usr/`, `/etc/`, etc.)
- Home directory itself

### Interactive Confirmation

Default confirmation flow:
```
Delete item [1] (maestro/node_modules/)? [y/N/all/quit]:
  y     - Delete this item
  N     - Skip this item (default)
  all   - Delete all remaining items
  quit  - Stop and exit
```

### Dry-Run Mode

`--dry-run` flag shows exactly what would be deleted:
```
[DRY RUN] Would delete: ~/dev/maestro/node_modules/ (2.1 GB)
[DRY RUN] Would delete: ~/dev/kan/.venv/ (456 MB)
[DRY RUN] Total space to reclaim: 2.5 GB
[DRY RUN] No changes made.
```

### Recovery Information

After deletion, show:
- What was deleted and when
- Commands to restore each deleted item
- Estimated time to rebuild
- Log saved to `~/.claude/cleanup-history.log`

### Deletion Log

Append to `~/.claude/cleanup-history.log`:
```
2026-02-20 15:30:45 | DELETED | ~/dev/maestro/node_modules/ | 2.1GB | npm install
2026-02-20 15:31:02 | DELETED | ~/dev/kan/__pycache__/ | 12MB | (auto-regenerated)
```

## Technical Implementation

### Command Format

Standard Claude Code markdown with YAML frontmatter:

```yaml
---
allowed-tools: Bash(find:*), Bash(du:*), Bash(rm:*), Bash(stat:*), Read, Grep, AskUserQuestion
argument-hint: [--path=DIR] [--dry-run] [--yes]
description: Clean up [type] artifacts interactively with safety checks
---
```

### Discovery Phase (Bash)

```bash
# Find all node_modules directories
find ~/dev -type d -name "node_modules" -prune 2>/dev/null

# Calculate sizes
du -sh ~/dev/maestro/node_modules 2>/dev/null

# Get modification times (macOS)
stat -f "%Sm" ~/dev/maestro/node_modules 2>/dev/null

# Get modification times (Linux)
stat -c "%y" ~/dev/maestro/node_modules 2>/dev/null
```

### Analysis Phase

- Parse find/du output into structured list
- Sort by size (largest first)
- Calculate total reclaimable space
- Detect restoration commands based on nearby files

### Confirmation Phase

Use AskUserQuestion tool for interactive prompts:
- Present each item with size and path
- Offer y/N/all/quit options
- Track user choices

### Execution Phase

```bash
# Safe deletion with verification
if [ -d "/path/to/node_modules" ]; then
  rm -rf "/path/to/node_modules" && echo "✓ Success" || echo "✗ Failed"
else
  echo "⊘ Already removed or doesn't exist"
fi
```

### Dynamic Content

Use `!` syntax for live data in command output:
```markdown
Current storage: !`du -sh ~/dev/ | cut -f1`
Available space: !`df -h ~ | tail -1 | awk '{print $4}'`
Last cleanup: !`tail -1 ~/.claude/cleanup-history.log | cut -d'|' -f1 || echo "Never"`
```

### Error Handling

- Check if target path exists before scanning
- Handle permission errors gracefully
- Validate paths before `rm` commands
- Provide meaningful error messages
- Never fail silently

## User Experience

### Typical Workflow

```bash
# 1. Analyze storage to understand opportunities
/util:analyze-storage ~/dev/

# 2. Preview what would be deleted
/util:cleanup-deps --path=~/dev/ --dry-run

# 3. Actually clean dependencies (interactive)
/util:cleanup-deps --path=~/dev/

# 4. Clean build artifacts
/util:cleanup-builds --path=~/dev/

# 5. Optional: Git maintenance
/util:cleanup-git --path=~/dev/
```

### Example Session

```
> /util:cleanup-deps --path=~/dev/

STORAGE CLEANUP: Dependencies
=============================
Scanning: /Users/joe/dev/

Found 3 dependency directories:
  [1] maestro/node_modules/     2.1 GB   (last modified: 45 days ago)
  [2] kan/.venv/                456 MB   (last modified: 12 days ago)
  [3] logwatcher/__pycache__/   12 MB    (last modified: 3 days ago)

Total reclaimable: 2.5 GB

Delete item [1] (maestro/node_modules/)? [y/N/all/quit]: y
✓ Deleted maestro/node_modules/ (2.1 GB freed)
  To restore: cd ~/dev/maestro && npm install

Delete item [2] (kan/.venv/)? [y/N/all/quit]: n
⊘ Skipped kan/.venv/

Delete item [3] (logwatcher/__pycache__)? [y/N/all/quit]: y
✓ Deleted logwatcher/__pycache__/ (12 MB freed)

SUMMARY
=======
Deleted: 2 items
Freed: 2.1 GB
Skipped: 1 item

RESTORATION COMMANDS
====================
cd ~/dev/maestro && npm install
# __pycache__ will auto-regenerate

Log saved to: ~/.claude/cleanup-history.log
```

## Edge Cases

### Empty Directories
- Skip directories that are already empty
- Show message: "⊘ Already empty"

### Permission Errors
- Catch permission denied errors
- Show message: "✗ Permission denied: <path>"
- Continue with remaining items

### Concurrent Modifications
- Check if directory still exists before deleting
- Handle race conditions gracefully

### Very Large Directories
- Show progress indicator for deletions > 1GB
- Allow cancellation with Ctrl+C

### Symlinks
- Don't follow symlinks during find
- Show warning if symlink target would be deleted

## Testing Strategy

### Manual Testing
1. Test each command with `--dry-run` flag
2. Test on sample directories with known content
3. Verify restoration commands work correctly
4. Test error handling (permission denied, missing paths)
5. Verify cleanup history log is written correctly

### Validation Checks
- [ ] Commands follow standard frontmatter format
- [ ] All Bash commands are properly escaped
- [ ] Dynamic content (`!` syntax) works correctly
- [ ] Confirmation prompts function as expected
- [ ] Dry-run mode never deletes anything
- [ ] Protected paths are never deleted
- [ ] Recovery commands are accurate

## Future Enhancements

- Add `--recursive-limit` to control scan depth
- Support `--older-than=DAYS` to filter by age
- Add `--min-size=SIZE` to only show large targets
- Create scheduled cleanup suggestions
- Integration with disk space alerts
- Export cleanup report to CSV/JSON
- Add undo functionality (move to trash instead of rm)

## Open Questions

None - design is complete and approved.

## Approval

- [x] Architecture approved
- [x] Safety mechanisms approved
- [x] Command format approved
- [x] Technical implementation approved
- [x] Ready for implementation
