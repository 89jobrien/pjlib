---
allowed-tools: Bash(joedb:*)
argument-hint: " <id>"
description: Mark todo <id> as completed in SQLite DB.
---

# Complete Todo

Mark a todo as completed in the SQLite database: $ARGUMENTS

!`joedb todo complete $ARGUMENTS`

## Example

```bash
joedb todo complete 42
```
