---
name: git-bisect-guide
description: Guide automated git bisect sessions to find regression commits with smart test execution and commit analysis. Use this skill when tracking down bugs introduced by specific commits, finding when tests started failing, debugging performance regressions, or investigating when features broke. Trigger for phrases like "find the bad commit", "when did this break", "bisect", "regression hunt", or when the user needs to identify which commit introduced an issue.
allowed-tools: [Bash, Read]
---

# Git Bisect Guide

You are an expert at using git bisect to systematically find regression commits through binary search and automated testing.

## When to Use This Skill

Use this skill whenever:
- A bug exists but the commit that introduced it is unknown
- Tests are failing but worked previously
- Performance has degraded and you need to find the cause
- A feature broke but the timeline is unclear
- The user mentions "bisect", "find bad commit", or "when did this break"
- Debugging requires identifying the exact change that caused an issue

## What is Git Bisect?

Git bisect uses binary search to efficiently find the commit that introduced a regression:
- Marks a known good commit (working state)
- Marks a known bad commit (broken state)
- Binary searches the commit range
- Identifies the first bad commit in O(log n) time

## Core Workflow

### Step 1: Analyze Repository State

Gather information for bisect session:

```bash
# Show current state
git branch --show-current

# Show recent commits
git log --oneline -20

# Check for active bisect
git bisect log 2>/dev/null

# Show available tags
git tag --sort=-version:refname | head -10

# Check status
git status --porcelain
```

Present to user:

```markdown
Bisect Session Analysis
-----------------------
Current branch: feature/auth
Recent activity: 156 commits since last tag
Suggested good commit: v1.2.0 (2 months ago)
Suggested bad commit: HEAD (current)
Commit range: ~156 commits → ~8 bisect steps

Ready to start? (y/n)
```

### Step 2: Initialize Bisect Session

**Create backup first:**

```bash
# Backup current state
BACKUP_BRANCH="bisect-backup-$(date +%Y%m%d-%H%M%S)"
git branch "$BACKUP_BRANCH"
echo "Backup created: $BACKUP_BRANCH"

# Start bisect
git bisect start

# Mark bad commit (usually HEAD)
git bisect bad HEAD

# Mark good commit (known working state)
git bisect good v1.2.0
```

**Git outputs:**

```bash
Bisecting: 78 revisions left to test after this (roughly 7 steps)
[abc123def456] commit message here
```

### Step 3: Test Current Commit

For each bisect checkpoint, test and mark:

**Automatic mode (with test command):**

```bash
# Rust example - run tests automatically
git bisect run cargo test --quiet --test regression_test

# Bash script example
git bisect run bash -c "cargo build --quiet && ./target/debug/app --check"

# Performance test example
git bisect run bash -c "cargo bench --bench perf_test | grep -q 'time:.*[0-9]ms'"
```

**Manual mode:**

```bash
# Build and test at current commit
cargo build --quiet
cargo test --quiet

# If tests pass
git bisect good

# If tests fail
git bisect bad

# If cannot determine (build fails, etc)
git bisect skip
```

### Step 4: Analyze Current Commit

At each bisect point, show relevant information:

```bash
# Show current commit details
echo "=== Current Bisect Commit ==="
git log -1 --pretty=format:"%H%nAuthor: %an%nDate: %ar%nMessage: %s%n"

# Show files changed
echo ""
echo "Files changed:"
git show --name-status --pretty="" HEAD

# Show actual changes (first 50 lines)
echo ""
echo "Changes preview:"
git show --stat HEAD
```

**Example output:**

```markdown
Current Bisect Commit
---------------------
Commit: abc123def456
Author: Jane Developer
Date: 3 weeks ago
Message: Refactor authentication middleware

Files changed:
M src/auth/middleware.rs
M src/api/handlers.rs
A tests/auth_test.rs

Test this commit:
Run: cargo test
Then: git bisect good/bad
```

### Step 5: Handle Test Results

**For automatic bisect:**

```bash
# Git bisect run will automatically complete
# When done, show results
git bisect log > /tmp/bisect-results.log
```

**For manual bisect:**

After each test:

```bash
# User reports: "Tests pass"
git bisect good

# Git automatically checks out next commit
# Outputs: Bisecting: 39 revisions left (roughly 6 steps)
```

### Step 6: Complete and Report

When bisect finds the bad commit:

```bash
# Git outputs:
# abc123def456 is the first bad commit
# commit abc123def456
# Author: John Developer
# Date: Wed Jan 15 14:30:00 2024
#
#     optimize database queries
#
# :100644 100644 abc123 def456 M  src/auth/database.rs

# Show detailed analysis
echo "=== First Bad Commit Found ==="
git show abc123def456 --stat

# Save bisect log
git bisect log > bisect-$(date +%Y%m%d).log

# End bisect session
git bisect reset

# Return to original branch
git checkout -
```

## Bisect Modes

### Automatic with Test Command

Best for: Automated test suites

```bash
#!/bin/bash
# bisect_auto.sh - Automatic bisect script

git bisect start
git bisect bad HEAD
git bisect good v1.2.0

# Run bisect with test command
git bisect run cargo test --test auth_regression

# Capture result
RESULT=$?

# Cleanup and report
git bisect log > bisect-results.log
git bisect reset

echo "Bisect complete. Results in bisect-results.log"
exit $RESULT
```

### Manual with Guidance

Best for: Complex issues needing human judgment

```bash
#!/bin/bash
# bisect_manual.sh - Guided manual bisect

git bisect start
git bisect bad HEAD
git bisect good v1.2.0

while true; do
    # Show current commit
    echo "=== Testing Commit ==="
    git log -1 --oneline
    git show --stat --pretty=""

    # Wait for user input
    echo ""
    echo "Test this commit, then enter:"
    echo "  g = good"
    echo "  b = bad"
    echo "  s = skip (cannot determine)"
    echo "  q = quit"
    read -p "> " choice

    case "$choice" in
        g) git bisect good || break ;;
        b) git bisect bad || break ;;
        s) git bisect skip || break ;;
        q) git bisect reset; exit 0 ;;
        *) echo "Invalid choice" ;;
    esac
done

# Show results
git bisect log
git bisect reset
```

### Performance Regression Bisect

Best for: Finding performance degradation

```bash
#!/bin/bash
# bisect_perf.sh - Performance bisect

# Threshold: 100ms
THRESHOLD_MS=100

git bisect start
git bisect bad HEAD
git bisect good v1.2.0

git bisect run bash -c '
    cargo build --release --quiet || exit 125

    # Run benchmark 3 times, take average
    total=0
    for i in 1 2 3; do
        time_ms=$(cargo bench --bench perf | grep -oE "[0-9]+ ms" | grep -oE "[0-9]+")
        total=$((total + time_ms))
    done
    avg=$((total / 3))

    echo "Average time: ${avg}ms (threshold: '"$THRESHOLD_MS"'ms)"

    if [ $avg -gt '"$THRESHOLD_MS"' ]; then
        exit 1  # Bad (slow)
    else
        exit 0  # Good (fast)
    fi
'

git bisect log
git bisect reset
```

## Advanced Techniques

### Skip Unbuildable Commits

```bash
# Bisect run script that skips build failures
git bisect run bash -c '
    cargo build --quiet 2>/dev/null || exit 125  # 125 = skip
    cargo test --quiet || exit 1                  # 1 = bad
    exit 0                                         # 0 = good
'
```

Exit codes:
- 0 = good commit
- 1-127 (except 125) = bad commit
- 125 = skip commit

### Multi-Criteria Bisect

```bash
# Test multiple conditions
git bisect run bash -c '
    # Must build
    cargo build --quiet || exit 125

    # Must pass tests
    cargo test --quiet || exit 1

    # Must meet performance threshold
    cargo bench --bench critical | grep -q "time.*[0-9][0-9]ms" || exit 1

    exit 0
'
```

### Bisect with Environment Setup

```bash
# Bisect script with dependency management
git bisect run bash -c '
    # Install dependencies for this commit
    cargo clean --quiet 2>/dev/null
    cargo fetch --quiet 2>/dev/null || exit 125

    # Build
    cargo build --quiet || exit 125

    # Test
    cargo test --quiet test_name || exit 1

    exit 0
'
```

## Recovery and Safety

### Interrupt and Resume

```bash
# If bisect is interrupted, check status
git bisect log

# Resume with manual marking
git bisect good  # or bad

# Or reset and restart
git bisect reset
```

### Recover from Mistakes

```bash
# View bisect log
git bisect log

# Undo last marking (no direct command, but can reset and restart)
git bisect reset
git bisect replay bisect-log-file

# Or use reflog
git reflog
git checkout <previous-state>
```

### Backup and Restore

```bash
# Before starting
git branch bisect-backup-$(date +%Y%m%d)

# Save bisect state
git bisect log > bisect-state.log

# Restore if needed
git bisect replay bisect-state.log
```

## Common Patterns

### Find When Tests Started Failing

```bash
git bisect start
git bisect bad HEAD
git bisect good $(git describe --tags --abbrev=0)
git bisect run cargo test --test failing_test
git bisect reset
```

### Find Performance Regression

```bash
git bisect start
git bisect bad HEAD
git bisect good last-release
git bisect run bash -c 'time timeout 10s cargo run | grep -q "Expected output"'
git bisect reset
```

### Find Build Break

```bash
git bisect start
git bisect bad HEAD
git bisect good working-commit
git bisect run cargo build --quiet
git bisect reset
```

## Best Practices

1. **Use tags for good commits** - Known releases are reliable good points
2. **Test the range first** - Verify good is actually good, bad is actually bad
3. **Backup before bisecting** - Create a branch pointing to current state
4. **Keep test focused** - Test only the specific regression
5. **Use cargo clean between tests** - Avoid stale build artifacts
6. **Document findings** - Save bisect log for reference

## Output Format

Provide clear bisect reports:

```markdown
Git Bisect Results
==================
Date: YYYY-MM-DD HH:MM

Session Summary
---------------
Good commit: v1.2.0 (abc123)
Bad commit: HEAD (def456)
Total commits in range: 156
Bisect steps required: 8
Duration: 12 minutes

First Bad Commit
----------------
Commit: 789abc
Author: Developer Name
Date: 2024-01-15 14:30:00
Message: Optimize database queries

Files Changed
-------------
M src/auth/database.rs (45 lines changed)
M src/middleware/auth.rs (12 lines changed)
A tests/auth_test.rs (89 lines added)

Impact
------
This commit introduced the authentication regression
affecting user login for admin accounts.

Recommended Actions
-------------------
1. Review commit: git show 789abc
2. Revert: git revert 789abc
3. Create issue: Document findings
4. Add test: Prevent future regressions

Recovery Commands
-----------------
git checkout main
git revert 789abc
git push origin main

Bisect Log
----------
Saved to: bisect-20240315.log
```

## Remember

Git bisect is powerful but requires:
- Clear definition of good vs bad
- Reproducible test
- Clean repository state
- Patience for the process

The goal is to find the exact commit that introduced the issue, not to fix it during bisect. Stay focused on testing and marking commits correctly.
