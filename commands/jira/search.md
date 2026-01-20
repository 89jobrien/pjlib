---
description: Search Jira issues using JQL or natural language
allowed-tools: Bash, mcp__plugin_atlassian_atlassian__searchJiraIssuesUsingJql, mcp__plugin_atlassian_atlassian__search
argument-hint: [query] e.g., "my open bugs" or "project=AOP AND status='In Progress'"
---

Search Jira for issues matching: **$ARGUMENTS**

## Instructions

### Step 1: Determine Query Type

If the query looks like natural language, translate to JQL first using these patterns:

| Natural Language | JQL Translation |
|-----------------|-----------------|
| my issues | `assignee = currentUser()` |
| my open issues | `assignee = currentUser() AND resolution = Unresolved` |
| my bugs | `assignee = currentUser() AND issuetype = Bug` |
| open bugs | `issuetype = Bug AND resolution = Unresolved` |
| high priority | `priority >= High` |
| in sprint / current sprint | `sprint in openSprints()` |
| updated today | `updated >= startOfDay()` |
| updated this week | `updated >= startOfWeek()` |
| created today | `created >= startOfDay()` |
| due this week | `duedate >= startOfWeek() AND duedate <= endOfWeek()` |
| overdue | `duedate < now() AND resolution = Unresolved` |
| unassigned | `assignee IS EMPTY` |
| blockers | `priority = Highest OR priority = Blocker` |

Combine patterns as needed. Add `ORDER BY updated DESC` for recency.

If the query already contains JQL operators (=, IN, AND, OR, ~), use it directly.

### Step 2: Execute Search

1. Try MCP tool `searchJiraIssuesUsingJql` first
2. If MCP fails, use REST API:
   ```bash
   python ~/.claude/skills/jira/scripts/jira_api.py GET /search --query "jql=<JQL>&maxResults=20"
   ```

### Step 3: Display Results

Present results in a table:

| Key | Summary | Status | Assignee | Priority | Updated |
|-----|---------|--------|----------|----------|---------|
| PROJ-123 | Fix login bug | In Progress | @user | High | 2h ago |

Include:
- Total count of matching issues
- The JQL query used (so user can refine)
- Pagination info if more results exist
