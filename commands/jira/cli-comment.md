---
description: Add comment to Jira issue using jira-cli
allowed-tools: Bash
argument-hint: [issue-key] [-m "comment text"]
---

# Add Comment to Jira Issue via CLI

Add a comment using `jira-cli`.

## Arguments

- `$1` - Issue key (required)
- `-m` - Comment text (optional, opens editor if omitted)

## Instructions

### With Inline Comment

```bash
jira issue comment $1 -m"Comment text here"
```

### Open Editor for Comment

```bash
jira issue comment $1
```

Opens default editor for longer comments.

### Markdown Support

```bash
jira issue comment $1 -m"## Update

- Fixed the bug
- Added tests
- Ready for review

See PR #456"
```

### View Comments

```bash
jira issue view $1 --comments
```

### Examples

```bash
# Simple comment
jira issue comment PROJ-123 -m"Working on this now"

# Status update
jira issue comment PROJ-123 -m"Blocked waiting for API access"

# PR reference
jira issue comment PROJ-123 -m"PR submitted: https://github.com/org/repo/pull/456"

# Resolution note
jira issue comment PROJ-123 -m"Fixed in commit abc123. Root cause was null check missing."
```
