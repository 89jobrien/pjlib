---
description: Create Jira issue using jira-cli
allowed-tools: Bash, AskUserQuestion
argument-hint: [-t Type] [-s "Summary"] [-b "Description"]
---

# Create Jira Issue via CLI

Create a new issue using `jira-cli` command-line tool.

## Current State

- Jira CLI: !`jira --version 2>/dev/null || echo "jira-cli not installed"`
- Current user: !`jira me 2>/dev/null || echo "Not authenticated"`

## Arguments

- `-t` - Issue type (Bug, Task, Story, Epic)
- `-s` - Summary/title
- `-b` - Description/body
- `-y` - Priority (Highest, High, Medium, Low, Lowest)
- `-a` - Assignee
- `-l` - Labels (comma-separated)

## Instructions

### Interactive Mode

```bash
jira issue create
```

Opens interactive prompts for all fields.

### Non-Interactive Mode

```bash
# Basic task
jira issue create -tTask -s"Task summary"

# Bug with details
jira issue create -tBug -s"Bug summary" \
  -b"Steps to reproduce:\n1. Step one\n2. Step two" \
  -yHigh

# Story with labels
jira issue create -tStory -s"User story" \
  -b"As a user, I want to..." \
  -l"frontend,feature"

# Assign to self
jira issue create -tTask -s"My task" -a$(jira me)

# Sub-task under parent
jira issue create -tSubtask -s"Sub-task summary" --parent PROJ-123
```

### Field Options

| Flag | Field | Example |
|------|-------|---------|
| `-t` | Type | `-tBug`, `-tTask`, `-tStory` |
| `-s` | Summary | `-s"Fix login bug"` |
| `-b` | Description | `-b"Detailed description"` |
| `-y` | Priority | `-yHigh`, `-yCritical` |
| `-a` | Assignee | `-a$(jira me)`, `-ajohn.doe` |
| `-l` | Labels | `-l"bug,urgent"` |
| `-C` | Component | `-CBackend` |
| `--parent` | Parent issue | `--parent PROJ-100` |

### Markdown in Description

The `-b` flag supports markdown:

```bash
jira issue create -tBug -s"Login fails" -b"## Steps
1. Go to login page
2. Enter credentials
3. Click submit

## Expected
User logged in

## Actual
Error message shown"
```

### After Creation

The CLI outputs the created issue key. Offer to:

1. View the issue: `jira issue view PROJ-XXX`
2. Open in browser: `jira open PROJ-XXX`
3. Assign it: `jira issue assign PROJ-XXX $(jira me)`
