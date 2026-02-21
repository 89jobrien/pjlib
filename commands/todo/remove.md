---
allowed-tools: Bash(joedb:*)
argument-hint: " <id>"
description: Remove todo <id> entirely from SQLite DB.
---

# Remove Todo

Remove a todo entirely from the SQLite database: $ARGUMENTS

!`joedb todo delete $ARGUMENTS`

## Example

```bash
joedb todo delete 42
```
