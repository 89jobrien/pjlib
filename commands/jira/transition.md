---
description: Transition a Jira issue to a new status
allowed-tools: Bash, mcp__plugin_atlassian_atlassian__getJiraIssue, mcp__plugin_atlassian_atlassian__transitionJiraIssue, mcp__plugin_atlassian_atlassian__getTransitionsForJiraIssue
argument-hint: [issue-key] [status] e.g., PROJ-123 "In Progress"
---

Transition Jira issue **$1** to status: **$2**

## Instructions

### Step 1: Get Current State

1. Fetch issue details to show current status
2. Get available transitions using `getTransitionsForJiraIssue`

### Step 2: Find Target Transition

Match the requested status to available transitions:
- Match is case-insensitive
- Support common aliases:
  - "start" / "begin" -> "In Progress"
  - "done" / "complete" / "close" -> "Done"
  - "review" / "pr" -> "In Review" or "Code Review"
  - "todo" / "backlog" -> "To Do"
  - "reopen" -> "Reopen" or "To Do"

### Step 3: Execute Transition

If status not provided or ambiguous:
1. List available transitions
2. Ask user to select

Use MCP `transitionJiraIssue` or REST API:

```bash
# Get transitions
python ~/.claude/skills/jira/scripts/jira_api.py GET "/issue/$1/transitions"

# Execute transition
python ~/.claude/skills/jira/scripts/jira_api.py POST "/issue/$1/transitions" --data '{
  "transition": { "id": "TRANSITION_ID" }
}'
```

### Step 4: Confirm

Display:
- Previous status -> New status
- Link to issue
- Offer to add a comment about the transition
