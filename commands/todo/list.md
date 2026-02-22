---
allowed-tools: Bash(doob:*)
argument-hint: " [--status pending|in_progress|completed] [--project <name>] [--limit N]"
description: List todos from SQLite DB using doob CLI.
---

# List Todos

Display todos from the SQLite database: $ARGUMENTS

!`doob todo list $ARGUMENTS`

## Examples

```bash
doob todo list                              # All active todos
doob todo list --status pending             # Pending only
doob todo list --status completed --limit 10 # Last 10 completed
doob todo list --project odk                # Project-specific
```

## Options

- `--status <pending|in_progress|completed>`: Filter by status
- `--project <name>`: Filter by project
- `--limit <N>`: Limit number of results
- `--archived`: Include archived todos
