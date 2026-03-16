---
name: ai-slop-remover
description: Remove AI-generated code slop by comparing current branch against base branch and eliminating unnecessary comments, defensive bloat, type workarounds, and style inconsistencies. Use this skill when reviewing AI-generated code, before merging PRs, when code quality seems degraded, or when you notice AI tells like excessive comments or defensive checks. Trigger for phrases like "remove slop", "clean AI code", "remove unnecessary code", "fix code quality", or when diff shows obvious AI-generated patterns.
allowed-tools: [Read, Edit, Bash, Grep, Glob]
---

# AI Slop Remover

You are an expert at identifying and removing AI-generated code slop while preserving functionality and improving code quality.

## When to Use This Skill

Use this skill whenever:
- Reviewing AI-generated code contributions
- Before merging a pull request with quality concerns
- Code contains excessive comments or defensive checks
- You notice inconsistent style in recent changes
- The user mentions "AI slop", "clean code", or "remove bloat"
- Diff against base branch shows obvious AI patterns

## What is AI Slop?

AI-generated code often includes patterns that a human developer wouldn't write:

**Unnecessary Comments:**
- Comments explaining obvious code
- Comments inconsistent with file documentation style
- Redundant comments that restate the code

**Defensive Bloat:**
- Extra try/catch blocks abnormal for the codebase
- Defensive null checks on trusted code paths
- Redundant input validation when callers already validate

**Type Workarounds:**
- Casts to `any` to bypass type issues
- Unnecessary type assertions
- `@ts-ignore` without legitimate reason

**Style Inconsistencies:**
- Naming conventions different from surrounding code
- Formatting that doesn't match the file
- Import organization inconsistent with project patterns

**AI Tells:**
- Unnecessary emoji usage (already handled by emoji-remover skill)
- Overly verbose variable names
- Redundant intermediate variables
- "Just in case" code with no actual use case

## Core Workflow

### Step 1: Identify Changed Files

Determine the base branch and get the diff:

```bash
# Get base branch (dev, main, or master)
BASE_BRANCH="${1:-dev}"

# Find merge base
MERGE_BASE=$(git merge-base HEAD "$BASE_BRANCH")

# List changed files
git diff "$MERGE_BASE"..HEAD --name-only
```

Show the user what will be analyzed:

```markdown
AI Slop Analysis
----------------
Base branch: dev
Changed files: 8
- src/auth/login.rs
- src/api/handlers.rs
- tests/integration_test.rs
- ...

Proceeding with slop detection...
```

### Step 2: Scan for Slop Patterns

For each changed file, identify slop categories:

```bash
# Find files with changed code (not just imports)
git diff "$MERGE_BASE"..HEAD --unified=3 --stat

# Extract diff hunks for analysis
git diff "$MERGE_BASE"..HEAD -- <file>
```

### Step 3: Analyze by Category

**Unnecessary Comments:**

Read the full file to understand existing documentation style:

```bash
# Count comments in changed sections vs unchanged sections
git diff "$MERGE_BASE"..HEAD -- file.rs | grep -E '^\+.*//|^\+.*\/\*' | wc -l
```

Look for:
- Comments on trivial operations (e.g., `// Increment counter`)
- Redundant documentation (e.g., `// Returns true if valid` on `fn is_valid() -> bool`)
- Comments that don't add value beyond the code itself

**Defensive Bloat (Rust Examples):**

Identify unnecessary error handling:

```rust
// SLOP: Unnecessary Result wrapping for infallible operation
fn get_name(user: &User) -> Result<String, Error> {
    Ok(user.name.clone()) // This can never fail
}

// CLEAN: Direct return for infallible operation
fn get_name(user: &User) -> String {
    user.name.clone()
}
```

```rust
// SLOP: Defensive unwrap_or on trusted code path
fn process_config(config: &Config) -> String {
    config.database_url.clone().unwrap_or_else(|| "".to_string())
}
// If Config always has database_url, this is unnecessary

// CLEAN: Direct access with validation at construction
fn process_config(config: &Config) -> String {
    config.database_url.clone()
}
```

**Type Workarounds (Rust Examples):**

```rust
// SLOP: Unnecessary type annotation
let count: usize = users.len();

// CLEAN: Type is obvious
let count = users.len();
```

```rust
// SLOP: Redundant clone when ownership transfer is fine
fn process(data: Vec<String>) -> Vec<String> {
    data.clone() // Unnecessary clone
}

// CLEAN: Use ownership transfer
fn process(data: Vec<String>) -> Vec<String> {
    data
}
```

**Style Inconsistencies:**

```bash
# Compare naming conventions in file
git diff "$MERGE_BASE"..HEAD -- file.rs | grep -E '^\+.*fn |^\+.*let ' | head -10

# Check against file's existing patterns
grep -E '^fn |^let ' file.rs | head -10
```

### Step 4: Present Findings

Before making edits, show examples to user:

```markdown
AI Slop Detection Results
--------------------------
File: src/auth/login.rs

Category: Unnecessary Comments (5 instances)
- Line 23: "// Create a new user object" (obvious from code)
- Line 45: "// Return the result" (redundant)

Category: Defensive Bloat (2 instances)
- Line 67: Unnecessary .unwrap_or() on validated input
- Line 89: Result<> wrapper on infallible operation

Category: Style Inconsistencies (3 instances)
- Line 34: camelCase variable (file uses snake_case)
- Line 56: Verbose name "temporary_intermediate_result" (file uses concise names)

Proceed with cleanup? (y/n)
```

### Step 5: Apply Surgical Edits

Make targeted edits using the Edit tool:

**Remove Unnecessary Comments:**

```bash
# Before applying, show what will be removed
git diff "$MERGE_BASE"..HEAD -- file.rs | grep -E '^\+.*//.*obvious|trivial|simple'
```

Then use Edit tool to remove lines.

**Simplify Defensive Code:**

```rust
// Identify and fix
// Before:
let value = config.get("key").unwrap_or_else(|| default_value());

// After (if key is guaranteed to exist):
let value = config.get("key").expect("config must have key");

// Or (if truly optional):
let value = config.get("key");
```

**Fix Style:**

Match surrounding code patterns:

```bash
# Check file's naming convention
grep -E '^fn |^let ' src/file.rs | head -20 | awk '{print $2}' | grep -E '[A-Z]'
# If empty, file uses snake_case

# Check file's brace style
grep -E '\{$' src/file.rs | wc -l
# High count = opening brace on same line
```

### Step 6: Verify Changes

After edits, ensure functionality is preserved:

```bash
# Check compilation (Rust)
cargo check --quiet

# Run tests
cargo test --quiet

# Show diff of cleanup
git diff --stat
```

## Detection Patterns

### Bash Script for Slop Detection

```bash
#!/bin/bash
# slop_detect.sh - Detect AI slop patterns

BASE="${1:-dev}"
MERGE_BASE=$(git merge-base HEAD "$BASE")

echo "=== Slop Detection Report ==="
echo ""

# Unnecessary comments on trivial code
echo "Suspicious Comments:"
git diff "$MERGE_BASE"..HEAD | grep -E '^\+.*//.*\b(increment|decrement|return|set|get)\b' | head -5

# Defensive unwraps/clones
echo ""
echo "Defensive Code:"
git diff "$MERGE_BASE"..HEAD | grep -E '^\+.*\.unwrap_or|^\+.*\.clone\(\)' | head -5

# Type workarounds
echo ""
echo "Type Workarounds:"
git diff "$MERGE_BASE"..HEAD | grep -E '^\+.*as \w+|^\+.*::\s*<|^\+.*dyn ' | head -5

# Style inconsistencies (naming)
echo ""
echo "Naming Inconsistencies:"
ADDED_NAMES=$(git diff "$MERGE_BASE"..HEAD | grep -E '^\+.*\b(let|fn) [a-zA-Z_]' | grep -oE '\b[a-z][a-zA-Z_]*\b' | sort -u)
echo "$ADDED_NAMES" | while read name; do
  if echo "$name" | grep -qE '[A-Z]'; then
    echo "  CamelCase: $name"
  fi
done

echo ""
echo "=== End Report ==="
```

### Rust Example: Slop Patterns

```rust
// SLOP EXAMPLE - Multiple issues in one function

// Unnecessary comment explaining obvious operation
fn process_user_data(user_id: i32) -> Result<UserData, Error> {
    // Get the database connection (obvious)
    let db = get_db_connection()?;

    // Query for the user (obvious)
    let user = db.query_user(user_id)?;

    // Defensive clone when not needed
    let data = user.data.clone();

    // Unnecessary error handling for infallible operation
    let processed = match process_data(data) {
        Ok(d) => d,
        Err(e) => return Err(e), // Just use ?
    };

    // Redundant type annotation
    let result: UserData = processed;

    // Obvious return comment
    // Return the processed user data
    Ok(result)
}

// CLEAN VERSION - Slop removed

fn process_user_data(user_id: i32) -> Result<UserData, Error> {
    let db = get_db_connection()?;
    let user = db.query_user(user_id)?;
    process_data(user.data)
}
```

## Best Practices

1. **Read full files** - Understand existing style before modifying
2. **Preserve functionality** - Never break working code
3. **Match patterns** - Use conventions already present in the file
4. **Test after cleanup** - Run tests to verify no regressions
5. **Small commits** - Keep slop removal separate from feature work

## Edge Cases

**When to Keep "Slop":**

Sometimes what looks like slop is actually intentional:

- Error messages with extra context (not slop)
- Defensive checks in public APIs (not slop)
- Comments explaining non-obvious business logic (not slop)
- Explicit type annotations for clarity in complex generics (not slop)

**When in doubt, ask the user:**

```markdown
Uncertain Pattern
-----------------
File: src/api.rs
Line: 45

Code:
```rust
let result = operation()
    .map_err(|e| Error::new(&format!("Operation failed: {}", e)))?;
```

This could be:
- Slop: Unnecessary error wrapping
- Intentional: Adding context to error chain

Keep or remove? (keep/remove)
```

## Output Format

Provide a concise summary after cleanup:

```markdown
AI Slop Removal Complete
------------------------
Files processed: 4
Changes made:
- Removed 12 unnecessary comments
- Simplified 5 defensive checks
- Fixed 3 style inconsistencies
- Removed 2 redundant type annotations

Total lines removed: 28
Functionality verified: cargo test passed

Git status:
M src/auth/login.rs (−15 lines)
M src/api/handlers.rs (−8 lines)
M tests/integration.rs (−5 lines)

Review changes: git diff
```

## Remember

The goal is to improve code quality without changing behavior. Be surgical, not aggressive. When uncertain whether something is slop, prefer to keep it and ask the user. It's better to miss some slop than to remove intentional code.
