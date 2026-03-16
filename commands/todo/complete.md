---
allowed-tools: Bash(doob:*)
argument-hint: " <id>"
description: Mark todo <id> as completed in SQLite DB.
---

# Complete Todo

Mark a todo as completed in the SQLite database: $ARGUMENTS

!`doob todo complete $ARGUMENTS`

## Example

```bash
doob todo complete 42
```
