---
description: Add a comment to a Jira issue
allowed-tools: Bash, mcp__plugin_atlassian_atlassian__addCommentToJiraIssue, mcp__plugin_atlassian_atlassian__getJiraIssue
argument-hint: [issue-key] [comment-text]
---

Add a comment to Jira issue **$1**.

## Current State

- Jira CLI: !`jira --version 2>/dev/null || echo "jira-cli not installed"`
- Current user: !`jira me 2>/dev/null || echo "Not authenticated"`

## Arguments

- `$1` - Issue key (required)
- `$2+` - Comment text (optional, will prompt or use context)

## Instructions

### Step 1: Verify Issue Exists

Fetch issue to confirm it exists and show current title/status.

### Step 2: Get Comment Content

If comment text provided as argument, use that.

Otherwise:
1. Check if there's relevant context from the conversation
2. Ask user what they want to comment

### Step 3: Format and Post Comment

**For plain text comments:**
Use MCP `addCommentToJiraIssue` with markdown format.

**For rich text (code blocks, lists, etc.):**
Use REST API with ADF format:

```bash
python ~/.claude/skills/jira/scripts/jira_api.py POST "/issue/$1/comment" --data '{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [{ "type": "text", "text": "Comment text here" }]
      }
    ]
  }
}'
```

### ADF Formatting Reference

**Code block:**
```json
{
  "type": "codeBlock",
  "attrs": { "language": "python" },
  "content": [{ "type": "text", "text": "code here" }]
}
```

**Bullet list:**
```json
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [
        { "type": "paragraph", "content": [{ "type": "text", "text": "Item" }] }
      ]
    }
  ]
}
```

### Step 4: Confirm

Display:
- Comment added successfully
- Link to issue
- Preview of comment
