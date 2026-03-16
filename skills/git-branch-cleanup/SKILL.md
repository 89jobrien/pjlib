---
name: git-branch-cleanup
description: Automatically clean up merged branches, stale remotes, and organize repository structure. Use this skill when you notice merged branches, stale remote-tracking branches, cluttered branch lists, or when completing feature work. Trigger for phrases like "clean up branches", "delete merged branches", "prune remotes", "organize git", or when branch count exceeds 10-15 active branches. Also activate proactively after PR merges or when git branch output shows many [gone] references.
allowed-tools: [Bash, Read]
---

# Git Branch Cleanup

You are an expert at Git branch management, specializing in safe cleanup of merged branches and repository organization.

## When to Use This Skill

Use this skill whenever:
- You notice many merged branches in `git branch` output
- Remote-tracking branches show `[gone]` status
- The repository has more than 10-15 active branches
- After completing and merging a pull request
- The user mentions "cleanup", "organize", or "delete branches"
- Git operations are slow due to too many branch references

## Safety Principles

**Never delete:**
- Main branches: `main`, `master`, `develop`, `staging`, `production`
- Release branches: `release/*` patterns
- The current branch (always check `git branch --show-current`)
- Branches with unmerged work (unless explicitly requested)

**Always:**
- Verify branch merge status before deletion
- Keep backup references via reflog (30-day recovery window)
- Show dry-run output before destructive operations
- Confirm with user for force deletions

## Core Workflow

### Step 1: Analyze Current State

First, gather repository information:

```bash
# Show current branch
git branch --show-current

# List all branches with tracking info
git branch -vv

# Show recent branches by activity
git for-each-ref --sort=-committerdate refs/heads/ --format='%(refname:short)|%(committerdate:relative)|%(upstream:track)' | head -20 | column -t -s '|'

# Identify merged branches
git branch --merged main 2>/dev/null || git branch --merged master 2>/dev/null
```

Present a summary to the user:
- Total branches: local and remote
- Merged branches (safe to delete)
- Stale branches (no activity in 30+ days)
- Gone branches (remote deleted but local remains)

### Step 2: Categorize Branches

**Safe to delete (merged):**

```bash
# Find merged feature branches
git branch --merged main | grep -v "^\*\|main\|master\|develop"
```

**Gone branches (remote deleted):**

```bash
# Find branches tracking deleted remotes
git branch -vv | grep ': gone]'
```

**Stale branches (old but not merged):**

```bash
# Find branches with no activity in 90 days
git for-each-ref --sort=committerdate refs/heads/ --format='%(refname:short)|%(committerdate:relative)' | grep -E 'months|years' ago
```

### Step 3: Present Cleanup Plan

Before making changes, show the user:

```markdown
Branch Cleanup Plan
-------------------
Safe to delete (merged): 8 branches
  - feature/user-auth (merged 2 weeks ago)
  - bugfix/login-error (merged 1 month ago)
  - ...

Gone remotes: 3 branches
  - feature/old-feature (remote deleted)
  - ...

Stale branches: 2 branches (require confirmation)
  - experiment/new-ui (6 months old, not merged)
  - ...

Protected: main, develop, staging (kept)
```

Ask: "Should I proceed with cleanup? (safe only / all / cancel)"

### Step 4: Execute Cleanup

**Delete merged branches:**

```bash
# Delete local merged branches (safe)
git branch --merged main | grep -v "^\*\|main\|master\|develop" | xargs -n 1 git branch -d

# Also delete remote branches if requested
git branch -r --merged main | grep -v "main\|master\|develop\|HEAD" | sed 's/origin\///' | xargs -n 1 git push origin --delete
```

**Clean gone branches:**

```bash
# Delete branches whose remotes are gone
git branch -vv | grep ': gone]' | awk '{print $1}' | xargs -n 1 git branch -D
```

**Prune remote references:**

```bash
# Remove stale remote-tracking branches
git remote prune origin

# Or for all remotes
git remote | xargs -n 1 git remote prune
```

### Step 5: Verify and Report

After cleanup:

```bash
# Show current state
git branch -a

# Show reflog for recovery
git reflog --no-merges --since="1 week ago" | head -20
```

Generate a report:

```markdown
Branch Cleanup Complete
-----------------------
Deleted 8 merged local branches
Removed 3 gone tracking branches
Pruned 5 stale remote references

Before: 23 branches
After: 10 branches

Recovery available via reflog for 30 days.
Run `git reflog` to see recent deletions.
```

## Advanced Operations

### Delete Unmerged Branches (Risky)

Only with explicit user confirmation:

```bash
# Force delete unmerged branch (DESTRUCTIVE)
git branch -D branch-name

# Before deletion, save the commit hash
git rev-parse branch-name
# Outputs: abc123def456...

# Recovery command (save this for user):
echo "To recover: git checkout -b branch-name abc123def456"
```

### Bulk Remote Cleanup

```bash
# List merged remote branches
git branch -r --merged main | grep origin | grep -v 'main\|master\|develop\|HEAD'

# Delete them (requires push access)
git branch -r --merged main | grep origin | grep -v 'main\|master\|develop\|HEAD' | sed 's/origin\///' | xargs -n 1 git push origin --delete
```

### Sync with GitHub PR Status

If `gh` CLI is available:

```bash
# Check if branch has merged PR
gh pr list --state merged --json headRefName --jq '.[].headRefName'

# Safe delete only branches with merged PRs
gh pr list --state merged --json headRefName --jq '.[].headRefName' | xargs -n 1 git branch -d
```

## Recovery Procedures

### Recover Recently Deleted Branch

```bash
# Find the commit in reflog
git reflog --no-merges --since="2 weeks ago" | grep -i "branch-name"

# Recreate branch at that commit
git checkout -b branch-name <commit-hash>
```

### Restore All Recent Deletions

```bash
# Show all branch deletions in last 30 days
git reflog --date=relative | grep 'moving from' | head -20

# Interactive restore (user picks what to recover)
git reflog | grep 'branch:' | head -20
```

## Command Modes

### Dry Run (default)

Show what would be deleted without making changes:

```bash
# Just list, don't delete
git branch --merged main | grep -v "^\*\|main\|master\|develop"
```

### Interactive Mode

Confirm each deletion:

```bash
# Loop with confirmation
git branch --merged main | grep -v "^\*\|main\|master\|develop" | while read branch; do
  echo "Delete $branch? (y/n)"
  read answer
  if [ "$answer" = "y" ]; then
    git branch -d "$branch"
  fi
done
```

### Force Mode

Delete without confirmation (use carefully):

```bash
# Batch delete merged branches
git branch --merged main | grep -v "^\*\|main\|master\|develop" | xargs -n 1 git branch -d
```

## Best Practices

1. **Run git fetch before cleanup** - Ensure branch merge status is current
2. **Check git status** - No uncommitted changes in the current branch
3. **Use -d (lowercase) for merged** - Safer than -D (force)
4. **Keep reflog accessible** - Don't run git gc during cleanup
5. **Document large cleanups** - Note what was deleted and why
6. **Test in dry-run first** - Always preview before executing

## Common Patterns

**Weekly Maintenance:**

```bash
# Standard weekly cleanup routine
git fetch --all --prune
git branch --merged main | grep -v "^\*\|main\|master\|develop" | xargs -n 1 git branch -d
git remote prune origin
```

**Post-Release Cleanup:**

```bash
# Clean up release branches after successful deploy
git branch | grep 'release/' | grep -v "$(git branch --show-current)" | xargs -n 1 git branch -d
```

**Pre-PR Review:**

```bash
# Clean workspace before creating new feature
git fetch origin main:main
git branch --merged main | grep -v "^\*\|main" | xargs -n 1 git branch -d
```

## Output Format

Always provide a structured summary:

```markdown
Git Branch Cleanup Report
=========================
Date: YYYY-MM-DD HH:MM

Summary
-------
Action: [Dry Run / Cleanup Executed]
Branches analyzed: N
Branches deleted: N
Remote references pruned: N

Details
-------
Deleted merged branches:
- feature/user-auth (merged 2024-02-15)
- bugfix/login-fix (merged 2024-02-20)

Gone tracking branches removed:
- feature/experiment (remote deleted)

Protected (kept):
- main
- develop
- current-feature

Recovery
--------
All deletions are recoverable via reflog for 30 days.
To see recent changes: git reflog --date=relative | head -20
To recover a branch: git checkout -b <branch-name> <commit-hash>

Next Steps
----------
Repository is now organized with N active branches.
Consider running this cleanup monthly or after major releases.
```

## Remember

The goal is to maintain a clean, organized repository without losing work. Always err on the side of caution - it's better to keep an extra branch than to lose important work. Recovery via reflog is possible but prevention is better.
