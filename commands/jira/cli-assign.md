---
description: Assign Jira issue using jira-cli
allowed-tools: Bash
argument-hint: [issue-key] [assignee|me|x]
---

# Assign Jira Issue via CLI

Assign or unassign issues using `jira-cli`.

## Arguments

- `$1` - Issue key (required)
- `$2` - Assignee (username, "me", or "x" to unassign)

## Instructions

### Assign to Yourself

```bash
jira issue assign $1 $(jira me)
```

### Assign to Specific User

```bash
jira issue assign $1 john.doe
```

### Unassign

```bash
jira issue assign $1 x
```

### Get Current User

```bash
jira me
```

### Examples

```bash
# Assign to self
jira issue assign PROJ-123 $(jira me)

# Assign to teammate
jira issue assign PROJ-123 jane.smith

# Unassign
jira issue assign PROJ-123 x
```

### Bulk Assign

```bash
# Assign all "To Do" issues to yourself
jira issue list --jql "status = 'To Do' AND project = PROJ" --plain \
  | awk '{print $1}' \
  | xargs -I {} jira issue assign {} $(jira me)
```
