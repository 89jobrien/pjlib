---
description: List Jira issues assigned to current user
allowed-tools: Bash, mcp__plugin_atlassian_atlassian__searchJiraIssuesUsingJql, mcp__plugin_atlassian_atlassian__search
argument-hint: [--all | --sprint | --overdue]
---

List my Jira issues.

## Options

- `--all` or no args: All my open issues
- `--sprint`: Only issues in current sprint
- `--overdue`: Only overdue issues
- `--recent`: Issues I updated in last 7 days

## Instructions

### Build JQL Based on Option

**Default (--all or empty):**
```
assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC, updated DESC
```

**--sprint:**
```
assignee = currentUser() AND sprint in openSprints() ORDER BY rank ASC
```

**--overdue:**
```
assignee = currentUser() AND duedate < now() AND resolution = Unresolved ORDER BY duedate ASC
```

**--recent:**
```
assignee = currentUser() AND updated >= -7d ORDER BY updated DESC
```

### Execute and Display

1. Use MCP `searchJiraIssuesUsingJql` or REST API fallback
2. Group results by status:

## In Progress (3)
| Key | Summary | Priority | Due |
|-----|---------|----------|-----|

## To Do (5)
| Key | Summary | Priority | Due |
|-----|---------|----------|-----|

## In Review (2)
| Key | Summary | Priority | Due |
|-----|---------|----------|-----|

Include summary stats:
- Total open issues
- Overdue count (if any)
- Due this week count
