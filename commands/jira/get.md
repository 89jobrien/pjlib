---
description: Get details for a Jira issue by key
allowed-tools: Bash, mcp__plugin_atlassian_atlassian__getJiraIssue, mcp__plugin_atlassian_atlassian__search
argument-hint: [issue-key] e.g., PROJ-123
---

Get full details for Jira issue: **$1**

## Instructions

1. First, try using the MCP Atlassian tool `getJiraIssue` with the issue key
2. If MCP times out or fails, fall back to the REST API skill:
   ```bash
   python ~/.claude/skills/jira/scripts/jira_api.py GET "/issue/$1"
   ```

## Display Format

Present the issue information in a clear, readable format:

### Issue Header
- **Key**: [PROJ-123]
- **Summary**: [Title]
- **Status**: [Status] | **Priority**: [Priority]
- **Type**: [Issue Type]

### People
- **Assignee**: [Name or Unassigned]
- **Reporter**: [Name]

### Details
- **Labels**: [label1, label2]
- **Components**: [component1]
- **Sprint**: [Sprint name if applicable]
- **Due Date**: [Date if set]

### Description
[Render the description, converting ADF to readable markdown]

### Recent Activity
[Show last 3 comments if available]

### Links
- **Blocks**: [linked issues]
- **Blocked by**: [linked issues]
- **Related**: [linked issues]
