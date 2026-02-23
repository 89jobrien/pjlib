# Claude Workspace Cleanup Script

Reclaims disk space from `~/.claude` by archiving old session data to iCloud Drive and deleting temporary files.

## Usage

### Preview (Dry-Run Mode - Default)

See what would be cleaned up without making changes:

```bash
uv run python scripts/cleanup_claude_data.py
```

### Execute Cleanup

Actually perform the cleanup:

```bash
uv run python scripts/cleanup_claude_data.py --execute
```

### Custom Retention Period

Keep last 14 days instead of default 7:

```bash
uv run python scripts/cleanup_claude_data.py --days 14 --execute
```

## What Gets Cleaned

### Archived to iCloud (`~/Documents/claude-archives/YYYY-MM-DD/`)

- `projects/` - Session project contexts
- `transcripts/` - Session transcripts

Files older than retention period are copied to iCloud Drive, then deleted locally.

### Deleted Without Archive

- `plugins/` - Marketplace plugins (re-downloadable)
- `debug/` - Debug logs
- `shell-snapshots/` - Shell state captures
- `file-history/` - File version tracking
- `logs/` - Application logs

Files older than retention period are deleted directly.

### Deleted Entirely

- `paste-cache/` - All temporary clipboard data
- `*.backup*` - Backup files
- `.DS_Store` - macOS metadata files

## Safety Features

- **Dry-run by default** - Must use `--execute` to make changes
- **Archive verification** - Ensures copies succeeded before deleting
- **Detailed logging** - All operations logged to `logs/cleanup-YYYY-MM-DD-HHMMSS.log`
- **Error handling** - Continues on permission errors, reports failures

## Expected Results

Initial cleanup typically reclaims **~750MB** (varies based on usage).

## Logs

Detailed logs written to:

```text
~/.claude/logs/cleanup-YYYY-MM-DD-HHMMSS.log
```

## Running Periodically

Recommended frequency: weekly or monthly

Each run creates a new timestamped archive in:

```text
~/Documents/claude-archives/YYYY-MM-DD/
```

iCloud Drive automatically syncs these to the cloud.
