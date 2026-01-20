---
description: Transition/move Jira issue to new status using jira-cli
allowed-tools: Bash
argument-hint: [issue-key] [status] e.g., PROJ-123 "In Progress"
---

# Move/Transition Jira Issue via CLI

Change issue status using `jira-cli`.

## Arguments

- `$1` - Issue key (required)
- `$2` - Target status (optional, interactive if omitted)

## Instructions

### Interactive Mode

```bash
jira issue move $1
```

Shows available transitions and prompts for selection.

### Direct Transition

```bash
# Start work
jira issue move $1 "In Progress"

# Complete
jira issue move $1 "Done"

# Move to review
jira issue move $1 "In Review"
```

### With Comment

```bash
jira issue move $1 "Done" -m"Fixed in PR #123"
```

### With Resolution (for closing)

```bash
jira issue move $1 "Done" --resolution "Fixed"
jira issue move $1 "Done" --resolution "Won't Fix"
```

### Common Status Aliases

| User Says | Likely Status |
|-----------|---------------|
| start, begin | In Progress |
| done, complete, close | Done |
| review, pr | In Review / Code Review |
| todo, backlog | To Do |
| reopen | Reopen / To Do |

### Workflow

1. If status not provided, run interactive: `jira issue move $1`
2. If status provided, run direct: `jira issue move $1 "$2"`
3. If transition fails, show available transitions
4. Confirm the new status after transition
