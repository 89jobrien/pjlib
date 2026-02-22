---
allowed-tools: Bash(doob:*)
argument-hint: " <id>"
description: Mark completed todo <id> as incomplete in SQLite DB.
---

# Undo Todo Completion

Mark a completed todo as incomplete (pending) in the SQLite database.

## Usage

```bash
/todo:undo <id>
```

## Instructions

1. Parse the todo ID from arguments
2. Run the update command to change status back to "pending"
3. Confirm the change to the user

## Command

!`doob todo undo $ARGUMENTS`

## Examples

```bash
# Mark todo #42 as incomplete (back to pending)
doob todo undo 42
```

## Status Options

- `pending` - Not started (default for undo)
- `in_progress` - Currently working on
- `completed` - Done

## Feedback

After updating, show:

```
Undid completion for todo #<id> - status changed to pending
```

## Notes

- The `completed_at` timestamp is preserved for historical record
- Use `/todo:list` to see all todos and their current status
