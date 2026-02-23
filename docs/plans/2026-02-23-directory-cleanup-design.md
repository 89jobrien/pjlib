# Claude Workspace Cleanup Design

**Date:** 2026-02-23
**Objective:** Reclaim disk space (~1.3GB) by archiving old session data to iCloud and deleting temporary files

## Problem Statement

The `~/.claude` workspace has accumulated ~1.3GB of auto-generated data across multiple directories:
- `projects/` (505M) - session project contexts
- `plugins/` (279M) - downloaded marketplace plugins
- `transcripts/` (247M) - session transcripts
- `debug/` (245M) - debug logs and diagnostics
- `shell-snapshots/` (34M) - shell state captures
- `file-history/` (19M) - file version tracking
- `logs/` (8.1M) - application logs
- `paste-cache/` (500K) - temporary clipboard data
- Backup files (settings.json.backup, etc.)

## User Requirements

1. **Primary goal:** Reclaim disk space
2. **Retention policy:** Keep last 7 days of data locally, archive/delete older content
3. **Archive strategy:** Archive valuable session data to iCloud Drive (`~/Documents/`), delete regenerable data
4. **Safety:** Preview changes before execution (dry-run mode)
5. **Simplicity:** Manual script execution (no automation initially)

## Solution Architecture

### Script: `scripts/cleanup_claude_data.py`

**Technology stack:**
- Python 3.12+ (using type hints, dataclasses, pathlib)
- Standard library only (no external dependencies)
- Compatible with uv for package management

**CLI interface:**
```bash
# Preview what will happen (default, safe)
python scripts/cleanup_claude_data.py

# Execute cleanup
python scripts/cleanup_claude_data.py --execute

# Custom retention period
python scripts/cleanup_claude_data.py --days 14 --execute
```

**Modes:**
- `--dry-run` (default): Preview actions without making changes
- `--execute`: Perform actual cleanup operations
- `--days N`: Set retention period (default: 7)

## Data Classification & Handling

### Category A: Archive to iCloud, then delete locally

**Directories:**
- `projects/` (505M)
- `transcripts/` (247M)

**Process:**
1. Identify files/directories older than 7 days (based on mtime)
2. Copy to `~/Documents/claude-archives/YYYY-MM-DD/` preserving directory structure
3. Verify copy succeeded (compare file counts and total size)
4. Delete local copy after successful archive
5. iCloud Drive automatically syncs archived data to cloud

**Archive structure:**
```
~/Documents/claude-archives/2026-02-23/
├── projects/
│   ├── old-project-1/
│   └── old-project-2/
└── transcripts/
    ├── session-abc/
    └── session-xyz/
```

### Category B: Delete old files only (no archival)

**Directories:**
- `plugins/` (279M)
- `debug/` (245M)
- `shell-snapshots/` (34M)
- `file-history/` (19M)
- `logs/` (8.1M)

**Process:**
1. Identify files/directories older than 7 days
2. Delete directly (these are regenerable/low-value)
3. Claude Code will recreate as needed

**Rationale:** These directories contain auto-generated data:
- `plugins/` can be re-downloaded from marketplace
- `debug/logs/` are diagnostic data rarely needed
- `shell-snapshots/file-history/` are session recovery data with diminishing value over time

### Category C: Delete entirely (temp/backup files)

**Targets:**
- `paste-cache/` - all files regardless of age
- `*.backup*` files (e.g., `settings.json.backup.20260222_065209`)
- `.DS_Store` files

**Process:**
- Delete immediately without age checking
- These are temporary/redundant files with no archival value

## Age Determination Logic

**Method:** File modification time (`stat().st_mtime`)
**Cutoff:** `datetime.now() - timedelta(days=7)`
**Scope:** For directories, check the directory's own mtime (not recursive contents)

Files newer than cutoff remain untouched in `~/.claude` for instant access.

## Safety Mechanisms

### Pre-flight Checks
1. Verify `~/.claude` exists and is accessible
2. Verify `~/Documents/` exists for archival
3. Create archive directory: `~/Documents/claude-archives/YYYY-MM-DD/`
4. Check available disk space (warn if archive size > available space)

### Archive Verification
1. Copy files to archive location
2. Verify copy succeeded:
   - Compare file counts (source vs destination)
   - Compare total sizes
3. Only delete source after successful verification
4. Abort on verification failure (leave source intact)

### Error Handling

**Permission errors:**
- Log warning with file path
- Skip file and continue processing
- Report in summary

**IO errors during copy:**
- Abort operation immediately
- Leave source files intact
- Report failure and exit with error code

**Missing directories:**
- Log info message (already clean)
- Continue processing other directories

**Partial failures:**
- Complete all operations that can succeed
- Report what succeeded vs failed in summary
- Exit with error code if any failures occurred

### File Safety
- Never delete files newer than cutoff date
- Skip files currently locked or in use (catch OSError)
- Preserve directory structure in archives (no flattening)

## Output & Reporting

### Dry-Run Mode Output

```
Claude Data Cleanup - DRY RUN MODE
==================================
Cutoff date: 2026-02-16 (7 days ago)

WILL ARCHIVE TO: ~/Documents/claude-archives/2026-02-23/
  projects/old-project-1/ (120MB, modified 2026-02-10)
  projects/old-project-2/ (85MB, modified 2026-02-12)
  transcripts/session-abc/ (15MB, modified 2026-02-14)
  ... (15 more items)

WILL DELETE (no archive):
  debug/session-xyz/ (50MB, modified 2026-02-09)
  logs/old.log (2MB, modified 2026-02-11)
  paste-cache/0b29cbf8ea1ac9b9.txt (11KB)
  ... (42 more items)

SUMMARY:
  Archive: 452MB (18 items)
  Delete: 298MB (45 items)
  Total space to reclaim: 750MB

Run with --execute to perform cleanup.
```

### Execute Mode Output

Same format with additions:
- Progress indicators during operations
- Live updates: "Archiving projects/ ... done (452MB copied)"
- Verification status: "Verifying archive integrity ... OK"
- Final summary with actual results

### Detailed Logging

**Log file:** `logs/cleanup-YYYY-MM-DD-HHMMSS.log`

**Contents:**
- Timestamp for operation start/end
- Complete list of archived files with paths and sizes
- Complete list of deleted files with paths and sizes
- Any errors or warnings encountered
- Final summary statistics

## Expected Outcomes

### Immediate Results
- **Space reclaimed:** ~750MB locally (varies based on 7-day cutoff)
- **Archive created:** `~/Documents/claude-archives/2026-02-23/` with old session data
- **Workspace cleaned:** Only recent files (< 7 days) remain in `~/.claude`
- **Functionality preserved:** Claude Code continues working normally

### Post-Cleanup State

**Local (`~/.claude`):**
- Recent projects/transcripts (last 7 days)
- Recent debug/logs/snapshots (last 7 days)
- All core configuration (agents/, commands/, skills/, settings.json)
- No temp files or backups

**Archived (`~/Documents/claude-archives/`):**
- Timestamped snapshots of old session data
- Automatically synced to iCloud Drive
- Available for retrieval if needed
- Can be deleted from iCloud later if never accessed

### Re-usability

Script can be run periodically:
- Weekly/monthly cleanup recommended
- Each run creates new timestamped archive
- Idempotent - safe to run multiple times
- No interference with Claude Code operation

## Future Enhancements

If automation is desired later, this manual script provides the foundation for:
- **Approach 2:** Scheduled execution via macOS launchd (weekly cleanup)
- **Approach 3:** Hybrid manual archive + auto-cleanup for regenerable data

Current design prioritizes safety and transparency for initial cleanup.

## Implementation Notes

**Dependencies:** None beyond Python 3.12+ standard library

**Modules to use:**
- `pathlib` for path operations
- `shutil` for file/directory copying and deletion
- `datetime` for age calculations
- `dataclasses` for configuration
- `argparse` for CLI interface
- `logging` for detailed logs

**Type safety:** Full type hints throughout for maintainability

**Testing considerations:**
- Test dry-run mode doesn't modify filesystem
- Test archive verification catches corruption
- Test partial failure handling
- Test with various edge cases (empty dirs, locked files, etc.)
