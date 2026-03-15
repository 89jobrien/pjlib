---
name: rust-test-fix
description: Automated Rust testing workflow that runs tests, analyzes failures using pattern matching, suggests fixes based on common Rust idioms, and re-runs to verify. Use after writing new Rust code, when fixing failing tests in CI/CD, during TDD cycles, debugging async/tokio runtime issues, or fixing type mismatches and borrow checker errors. Detects patterns like missing tokio test attributes, type mismatches, borrow checker conflicts, and assertion failures.
allowed-tools: [Read, Edit, Bash, Grep, Glob]
skills: tdd:tdd-cycle, dev:review-code, test-automation
---

# Rust Test-Fix-Cycle Skill

Automated Rust testing workflow that runs tests, analyzes failures, suggests fixes, and re-runs to verify.

## Overview

This skill streamlines the Rust testing workflow by automating the red-green-refactor cycle:

1. **Run tests** in a specific crate or workspace
2. **Analyze failures** using Rust-specific pattern matching
3. **Suggest fixes** based on common Rust idioms and error patterns
4. **Apply fixes** automatically or with confirmation
5. **Re-run tests** to verify the fix
6. **Report results** with before/after comparison

## When to Use

- After writing new Rust code that needs testing
- When fixing failing tests in CI/CD
- During TDD red-green-refactor cycles
- Debugging async/tokio runtime issues
- Fixing type mismatches and borrow checker errors

## Usage

```bash
# Run in current crate
/rust-test-fix

# Specify crate
/rust-test-fix components

# Specific test
/rust-test-fix components::test_pipeline_integration

# Workspace-wide
/rust-test-fix --workspace

# Auto-fix mode (applies fixes without confirmation)
/rust-test-fix --auto-fix

# Dry run (show fixes but don't apply)
/rust-test-fix --dry-run
```

## Common Patterns Detected

### 1. **Runtime Issues**
- Missing `#[tokio::test]` attribute
- Attempting async operations without runtime
- Fix: Add `#[tokio::test]` or wrap in `tokio::runtime::Runtime`

### 2. **Type Mismatches**
- `std::time::Duration` vs `chrono::Duration`
- Comparing incompatible types
- Fix: Extract to variable with correct type, use proper conversion

### 3. **Borrow Checker**
- Mutable reference conflicts
- Moving values in closures
- Fix: Use `Arc<Mutex<T>>` or `Arc<AtomicT>` for shared mutable state

### 4. **Environment Variables**
- Unsafe `std::env::set_var` in tests
- Fix: Use `temp_env` crate or fixture isolation

### 5. **Assertion Failures**
- Logic errors in test expectations
- Wrong assertion type
- Fix: Correct assertion logic or use appropriate assertion macro

## Example Output

```
=== Rust Test-Fix Cycle ===
Crate: components
Running tests...

❌ FAILED: test_retry_with_mutable_state
Error: cannot assign to immutable variable `counter`

Analysis:
- Pattern: Shared mutable state in async test
- Cause: Variable `counter` needs to be mutable across spawned tasks
- Solution: Use Arc<AtomicUsize> for thread-safe mutable counter

Suggested Fix:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-  let counter = 0;
+  let counter = Arc::new(AtomicUsize::new(0));

-  counter += 1;
+  counter.fetch_add(1, Ordering::SeqCst);
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Apply fix? [Y/n]: y

Applying fix... ✓
Re-running tests...

✅ PASSED: test_retry_with_mutable_state

Summary:
- Tests run: 1
- Failures fixed: 1
- Success rate: 100%
```

## Integration

### With DevLoop Pipeline
- Automatically detects which crates have recent changes
- Prioritizes tests for modified code
- Uses pipeline metrics to guide test selection

### With TDD Workflow
- Integrates with `/tdd:tdd-cycle` for full TDD workflow
- Supports red-green-refactor phases
- Tracks test coverage improvements

### With CI/CD
- Can be run in CI pipeline for automated fixes
- Generates fix reports for PR reviews
- Exports metrics for test quality tracking

## Configuration

Set environment variables to customize:

```bash
# Test timeout (seconds)
TEST_TIMEOUT=300

# Auto-fix mode (skip confirmation)
AUTO_FIX=true

# Verbosity
RUST_TEST_FIX_VERBOSE=true

# Test arguments
CARGO_TEST_ARGS="--no-fail-fast"
```

## Advanced Features

### Pattern Learning
The skill learns from your fixes and suggests similar patterns:

```bash
# Save a fix pattern
/rust-test-fix --save-pattern

# List saved patterns
/rust-test-fix --list-patterns

# Apply custom pattern
/rust-test-fix --pattern=tokio-runtime-missing
```

### Batch Mode
Fix multiple test failures in one run:

```bash
# Fix all failing tests in crate
/rust-test-fix components --batch

# Fix up to N tests
/rust-test-fix --batch --limit=5
```

### Report Generation
Generate detailed fix reports:

```bash
# Markdown report
/rust-test-fix --report=markdown > test-fixes.md

# JSON for CI
/rust-test-fix --report=json > test-fixes.json
```

## Tips

- Run after pulling changes to catch integration issues
- Use `--dry-run` first to preview fixes
- Combine with `/dev:review-code` for comprehensive quality check
- Save common patterns for your project
- Review auto-fixes before committing

## Examples

### Pipeline Test Fixes (Recent Session)
Based on your recent work fixing pipeline tests:

```bash
# Fix the retry test with atomic counter
/rust-test-fix eddos::test_retry_with_mutable_state
→ Detected: Mutable state in async context
→ Applied: Arc<AtomicUsize> pattern
→ ✅ Test passed

# Fix git watcher test isolation
/rust-test-fix components::test_git_watcher_creation
→ Detected: Environment assumption
→ Applied: Temp directory pattern
→ ✅ Test passed

# Fix integration test duration types
/rust-test-fix components::test_pipeline_partial_batch_flush
→ Detected: std::time::Duration vs chrono::Duration mismatch
→ Applied: Explicit chrono::Duration usage
→ ✅ Test passed
```
