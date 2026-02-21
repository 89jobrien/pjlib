---
allowed-tools: Bash(joedb:*)
argument-hint: " [--status pending|in_progress|completed] [--project <name>] [--limit N]"
description: List todos from SQLite DB using joedb CLI.
---

# List Todos

Display todos from the SQLite database: $ARGUMENTS

!`joedb todo list $ARGUMENTS`

## Examples

```bash
joedb todo list                              # All active todos
joedb todo list --status pending             # Pending only
joedb todo list --status completed --limit 10 # Last 10 completed
joedb todo list --project odk                # Project-specific
```

## Options

- `--status <pending|in_progress|completed>`: Filter by status
- `--project <name>`: Filter by project
- `--limit <N>`: Limit number of results
- `--archived`: Include archived todos
