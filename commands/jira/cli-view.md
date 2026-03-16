---
description: View Jira issue details using jira-cli
allowed-tools: Bash
argument-hint: [issue-key] e.g., PROJ-123
---

# View Jira Issue via CLI

View detailed issue information using `jira-cli`.

## Current State

- Jira CLI: !`jira --version 2>/dev/null || echo "jira-cli not installed"`
- Current user: !`jira me 2>/dev/null || echo "Not authenticated"`

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
