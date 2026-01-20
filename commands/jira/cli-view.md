---
description: View Jira issue details using jira-cli
allowed-tools: Bash
argument-hint: [issue-key] e.g., PROJ-123
---

# View Jira Issue via CLI

View detailed issue information using `jira-cli`.

## Arguments

- `$1` - Issue key (required)

## Instructions

### Basic View

```bash
jira issue view $1
```

### With Comments

```bash
jira issue view $1 --comments
```

### JSON Output (for parsing)

```bash
jira issue view $1 --output json
```

### Open in Browser

```bash
jira open $1
```

### Information Displayed

- Issue key and summary
- Status, priority, type
- Assignee and reporter
- Description
- Labels and components
- Sprint (if applicable)
- Created/updated dates
- Comments (with `--comments` flag)
