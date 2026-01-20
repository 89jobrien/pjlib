---
description: Create a new Jira issue with guided workflow
allowed-tools: Bash, mcp__plugin_atlassian_atlassian__createJiraIssue, mcp__plugin_atlassian_atlassian__getVisibleJiraProjects, mcp__plugin_atlassian_atlassian__getJiraProjectIssueTypesMetadata, AskUserQuestion
argument-hint: [project] [summary] e.g., PROJ "Fix login bug"
---

Create a new Jira issue.

## Arguments

- `$1` - Project key (optional, will prompt if missing)
- `$2+` - Summary/title (optional, will prompt if missing)

## Instructions

### Step 1: Gather Required Information

**If project not provided:**
1. Use `getVisibleJiraProjects` to list available projects
2. Ask user to select or specify project key

**If summary not provided:**
1. Ask user for issue summary
2. Can also derive from conversation context if relevant

### Step 2: Determine Issue Type

1. Use `getJiraProjectIssueTypesMetadata` to get available types for project
2. Default to "Task" unless user specifies otherwise
3. Common types: Task, Bug, Story, Epic, Sub-task

### Step 3: Gather Optional Fields

Ask user if they want to specify:
- **Description**: Detailed explanation (will be converted to ADF)
- **Priority**: Highest, High, Medium, Low, Lowest
- **Assignee**: User to assign (default: unassigned)
- **Labels**: Comma-separated labels
- **Sprint**: Add to current sprint?

### Step 4: Create Issue

Use MCP `createJiraIssue` or REST API:

```bash
python ~/.claude/skills/jira/scripts/jira_api.py POST /issue --data '{
  "fields": {
    "project": { "key": "PROJECT_KEY" },
    "issuetype": { "name": "Task" },
    "summary": "Issue summary",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "paragraph",
          "content": [{ "type": "text", "text": "Description here" }]
        }
      ]
    }
  }
}'
```

### Step 5: Confirm Creation

Display:
- Created issue key and link
- Summary of fields set
- Offer to open in browser or add more details
