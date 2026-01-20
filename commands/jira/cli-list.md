---
description: List Jira issues using jira-cli with filters
allowed-tools: Bash
argument-hint: [--mine|--jql "query"|--status "In Progress"]
---

# List Jira Issues via CLI

List issues using `jira-cli` command-line tool.

## Arguments

- `$ARGUMENTS` - Filters or JQL query

## Instructions

### Parse Arguments

Translate natural language or flags to jira-cli options:

| User Input | jira-cli Command |
|------------|------------------|
| (no args) | `jira issue list` |
| `--mine` / `my issues` | `jira issue list -a$(jira me)` |
| `--status "X"` | `jira issue list -s"X"` |
| `--priority High` | `jira issue list -yHigh` |
| `--jql "query"` | `jira issue list --jql "query"` |
| `bugs` | `jira issue list --jql "issuetype = Bug"` |
| `in progress` | `jira issue list -s"In Progress"` |
| `sprint` | `jira issue list --jql "sprint in openSprints()"` |

### Execute Command

```bash
# Default: list recent issues
jira issue list --paginate 20

# Assigned to current user
jira issue list -a$(jira me) --paginate 20

# By status
jira issue list -s"In Progress" --paginate 20

# By priority
jira issue list -yHigh --paginate 20

# Combined filters
jira issue list -a$(jira me) -s"To Do" -yHigh

# Custom JQL
jira issue list --jql "project = PROJ AND created >= -7d"

# JSON output for parsing
jira issue list --output json
```

### Output Formats

- Default: Interactive table
- `--output json` - JSON for parsing
- `--output csv` - CSV export
- `--plain` - Plain text

### Common JQL Patterns

```bash
# My open issues
jira issue list --jql "assignee = currentUser() AND resolution = Unresolved"

# Sprint issues
jira issue list --jql "sprint in openSprints()"

# High priority bugs
jira issue list --jql "issuetype = Bug AND priority >= High AND resolution = Unresolved"

# Updated this week
jira issue list --jql "updated >= startOfWeek()"

# Overdue
jira issue list --jql "duedate < now() AND resolution = Unresolved"
```
