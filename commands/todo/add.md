---
allowed-tools: Bash(doob:*)
argument-hint: " <description> [--priority 0-5] [--project <project>] [--tags <tags>]"
description: Add a todo to SQLite DB using doob CLI.
---

# Add Todo

Add a new todo to the SQLite database: $ARGUMENTS

!`doob todo add $ARGUMENTS`

## Examples

```bash
doob todo add "Fix SetLevel() losing JSON config in logging.go" --priority 1 --project gaw --tags bug,logging
```

```bash
doob todo add "Add security tests for ValidatePathWithin()" --priority 1 --project gaw --tags critical,testing,security
```

## Options

- `--priority <0-5>`: Priority level (0=highest, 5=lowest)
- `--project <name>`: Associate with project
- `--file <path>`: Associate with file
- `--due <YYYY-MM-DD>`: Set due date
- `--tags <tag1,tag2>`: Comma-separated tags
