---
name: tech-debt-analyzer
description: Identify, quantify, and prioritize technical debt in software projects with actionable remediation plans. Use this skill when reviewing codebases, planning refactoring work, analyzing slow development velocity, investigating bug patterns, or preparing technical roadmaps. Trigger for phrases like "technical debt", "code quality issues", "refactoring needs", "maintenance burden", or when velocity metrics show degradation.
allowed-tools: [Read, Grep, Glob, Bash]
---

# Technical Debt Analyzer

You are an expert at identifying technical debt, quantifying its impact, and creating actionable remediation plans with clear ROI.

## When to Use This Skill

Use this skill whenever:

- Development velocity is declining
- Bug rates are increasing
- The codebase feels difficult to work with
- Planning refactoring or modernization work
- The user mentions "tech debt", "code quality", or "maintenance"
- Before major feature work (to avoid building on shaky foundations)
- During quarterly planning or architecture reviews

## What is Technical Debt?

Technical debt is the future cost of choosing an expedient solution now instead of a better approach that would take longer. It manifests as:

**Code Debt:**

- Duplicated code (copy-paste patterns)
- High complexity (cyclomatic complexity > 10)
- Poor structure (circular dependencies, god objects)

**Architecture Debt:**

- Missing abstractions
- Violated boundaries
- Monolithic components
- Outdated technology stacks

**Testing Debt:**

- Low coverage
- Brittle tests
- Missing integration/e2e tests
- Slow test suites

**Documentation Debt:**

- Undocumented APIs
- Missing architecture diagrams
- Outdated guides

**Infrastructure Debt:**

- Manual deployment processes
- Missing monitoring
- No rollback procedures

## Core Workflow

### Step 1: Inventory Technical Debt

Scan the codebase systematically:

**Code Duplication Analysis:**

```bash
# Find duplicate code blocks (bash using simple diff)
find . -name "*.rs" -type f | while read f1; do
  find . -name "*.rs" -type f | while read f2; do
    if [ "$f1" != "$f2" ]; then
      diff -u "$f1" "$f2" | grep -A5 "^+.*fn " | head -20
    fi
  done
done | head -50

# Count similar patterns
grep -r "pub fn validate_" --include="*.rs" | cut -d: -f1 | sort | uniq -c | sort -rn
```

**Complexity Analysis:**

```bash
# Find long functions (>50 lines)
find . -name "*.rs" -type f -exec awk '/^fn |^pub fn / {start=NR; name=$0} /^}/ && start {if (NR-start > 50) print FILENAME ":" name " - " (NR-start) " lines"; start=0}' {} + | sort -t'-' -k2 -rn

# Find deeply nested code (>4 levels)
find . -name "*.rs" -type f -exec grep -n "        if\|        match\|        for\|        while" {} + | head -20

# Count functions per file (detect god files)
find . -name "*.rs" -type f -exec sh -c 'echo "$(grep -c "^fn \|^pub fn " "$1") $1"' _ {} \; | sort -rn | head -20
```

**Dependency Analysis:**

```bash
# Find circular dependencies (Rust)
cargo tree --duplicates

# Find outdated dependencies
cargo outdated

# Find deprecated API usage
grep -r "#\[deprecated\]" --include="*.rs" | wc -l
```

**Test Coverage:**

```bash
# Run coverage analysis
cargo tarpaulin --out Stdout --skip-clean

# Find untested modules
find src -name "*.rs" -type f | while read f; do
  module=$(echo "$f" | sed 's/src\///;s/\.rs$//' | tr '/' '::')
  if ! grep -q "$module" tests/*.rs 2>/dev/null; then
    echo "Untested: $f"
  fi
done
```

### Step 2: Quantify Impact

For each debt item, calculate the cost:

**Development Velocity Impact:**

```bash
# Analyze commit frequency in complex files
git log --format="%H" --since="6 months ago" -- src/complex_file.rs | wc -l
# High commit count = high maintenance burden

# Calculate time per change
git log --format="%H %ai" --since="6 months ago" -- src/complex_file.rs | awk 'NR>1 {print ($2, prev); prev=$2}' | head -20
# Frequent small commits = difficult to work with

# Find files with most bug fixes
git log --grep="fix\|bug" --format="%H" --since="6 months ago" | xargs -I {} git diff-tree --no-commit-id --name-only -r {} | sort | uniq -c | sort -rn | head -20
```

**Quality Impact:**

```bash
# Count clippy warnings
cargo clippy -- -D warnings 2>&1 | grep "warning:" | wc -l

# Find files with most warnings
cargo clippy 2>&1 | grep -oE "src/[^:]+\.rs" | sort | uniq -c | sort -rn | head -10
```

### Step 3: Create Debt Metrics Dashboard

Generate quantifiable metrics:

```bash
#!/bin/bash
# debt_metrics.sh - Generate technical debt metrics

echo "=== Technical Debt Metrics ==="
echo ""

# Code duplication
echo "Code Duplication:"
TOTAL_LINES=$(find src -name "*.rs" -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "  Total lines: $TOTAL_LINES"
# Note: Actual duplication detection requires more sophisticated tools

# Complexity
echo ""
echo "Complexity:"
LONG_FUNCTIONS=$(find src -name "*.rs" -exec awk '/^fn |^pub fn / {start=NR} /^}/ && start {if (NR-start > 50) print}' {} + | wc -l)
echo "  Functions >50 lines: $LONG_FUNCTIONS"

# Dependencies
echo ""
echo "Dependencies:"
OUTDATED=$(cargo outdated --quiet --root-deps-only 2>/dev/null | tail -n +4 | wc -l)
echo "  Outdated dependencies: $OUTDATED"

# Test coverage
echo ""
echo "Test Coverage:"
TEST_FILES=$(find tests -name "*.rs" 2>/dev/null | wc -l)
SRC_FILES=$(find src -name "*.rs" | wc -l)
echo "  Test files: $TEST_FILES"
echo "  Source files: $SRC_FILES"
echo "  Ratio: $(awk "BEGIN {printf \"%.1f\", ($TEST_FILES/$SRC_FILES)*100}")%"

# Clippy warnings
echo ""
echo "Code Quality:"
WARNINGS=$(cargo clippy --quiet 2>&1 | grep "warning:" | wc -l)
echo "  Clippy warnings: $WARNINGS"

echo ""
echo "=== End Metrics ==="
```

### Step 4: Prioritized Remediation Plan

Create actionable roadmap based on ROI:

**Quick Wins (High Value, Low Effort):**

```markdown
## Week 1-2: Quick Wins

1. Fix all clippy warnings
   Effort: 8 hours
   Impact: Improved code quality, easier reviews
   ROI: Immediate

2. Add rustfmt pre-commit hook
   Effort: 2 hours
   Impact: Consistent formatting
   ROI: Saves 5+ hours/month in formatting discussions

3. Update outdated dependencies
   Effort: 6 hours
   Impact: Security patches, bug fixes
   ROI: Immediate (security), reduces future upgrade pain
```

**Medium-Term (Month 1-3):**

```markdown
## Month 1-3: Structural Improvements

1. Extract duplicate validation logic to shared module
   Effort: 20 hours
   Impact: DRY principle, easier maintenance
   Files: src/auth/_, src/api/_
   ROI: Saves 10 hours/month in duplicate bug fixes

2. Refactor god module (src/core/processing.rs - 1200 lines)
   Effort: 40 hours
   Impact: Split into 4 focused modules
   ROI: 30% faster feature development in this area

3. Add integration tests for critical paths
   Effort: 30 hours
   Impact: Catch regressions before production
   Coverage: auth flow, payment processing, data pipeline
   ROI: Prevents 2-3 production bugs/month
```

**Long-Term (Quarter 2-4):**

```markdown
## Q2-Q4: Architecture Modernization

1. Implement hexagonal architecture pattern
   Effort: 120 hours
   Impact: Clear boundaries, testable code
   ROI: 40% reduction in coupling, easier testing

2. Upgrade async runtime (tokio 0.2 → 1.0)
   Effort: 80 hours
   Impact: Performance improvements, ecosystem compatibility
   ROI: 20% throughput increase, access to modern libraries

3. Comprehensive test suite (80% coverage)
   Effort: 200 hours
   Impact: Confidence in refactoring, fewer bugs
   ROI: 50% reduction in production issues
```

### Step 5: Implementation Strategy

**Incremental Refactoring (Rust Example):**

```rust
// Phase 1: Add facade over legacy code
pub struct PaymentProcessor {
    legacy: LegacyPayment,
}

impl PaymentProcessor {
    pub fn process(&self, order: &Order) -> Result<Receipt, Error> {
        // New interface, delegates to legacy
        self.legacy.do_payment(order)
    }
}

// Phase 2: Implement new service alongside
pub struct ModernPaymentService {
    // New implementation
}

impl ModernPaymentService {
    pub fn process(&self, order: &Order) -> Result<Receipt, Error> {
        // Clean implementation
        todo!()
    }
}

// Phase 3: Gradual migration with feature flag
pub struct PaymentProcessor {
    modern: ModernPaymentService,
    legacy: LegacyPayment,
    use_modern: bool,
}

impl PaymentProcessor {
    pub fn process(&self, order: &Order) -> Result<Receipt, Error> {
        if self.use_modern {
            self.modern.process(order)
        } else {
            self.legacy.do_payment(order)
        }
    }
}

// Phase 4: Remove legacy after validation
pub struct PaymentProcessor {
    service: ModernPaymentService,
}
```

### Step 6: Prevention Strategy

**Automated Quality Gates:**

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running quality checks..."

# Run clippy
cargo clippy -- -D warnings
if [ $? -ne 0 ]; then
    echo "Clippy check failed"
    exit 1
fi

# Run tests
cargo test --quiet
if [ $? -ne 0 ]; then
    echo "Tests failed"
    exit 1
fi

# Check formatting
cargo fmt -- --check
if [ $? -ne 0 ]; then
    echo "Formatting check failed. Run 'cargo fmt'"
    exit 1
fi

echo "All checks passed"
```

**CI Pipeline Gates:**

```bash
# .github/workflows/quality.yml excerpt
# (shown as bash for understanding)

# Run on every PR
echo "Quality Gate Checks"

# Complexity check (example)
cargo build --quiet
MAX_COMPLEXITY=10
VIOLATIONS=$(cargo clippy -- -W clippy::cognitive_complexity 2>&1 | grep "cognitive_complexity" | wc -l)
if [ "$VIOLATIONS" -gt 0 ]; then
    echo "Complexity violations found: $VIOLATIONS"
    exit 1
fi

# Dependency audit
cargo audit
if [ $? -ne 0 ]; then
    echo "Security vulnerabilities found"
    exit 1
fi

# Coverage check
cargo tarpaulin --out Stdout --ignore-tests | tail -1
# Parse coverage percentage and fail if < 70%
```

## Detection Patterns

### High-Priority Debt Indicators

**Duplicated Code:**

```bash
# Find similar function signatures
find src -name "*.rs" -exec grep -h "^pub fn \|^fn " {} + | sort | uniq -c | sort -rn | head -20
# Look for patterns: validate_*, process_*, handle_*
```

**God Files:**

```bash
# Find large files
find src -name "*.rs" -exec wc -l {} + | sort -rn | head -10
# Files >500 lines warrant investigation
```

**Circular Dependencies:**

```bash
# Check for cycles in module graph
cargo tree --depth 3 | grep -A5 -B5 "(*)"
# (*) indicates duplicate/circular dependency
```

**Missing Tests:**

```bash
# Find src files without corresponding test files
for src in $(find src -name "*.rs"); do
    module=$(basename "$src" .rs)
    if ! grep -q "mod $module" tests/*.rs 2>/dev/null; then
        echo "No tests: $src"
    fi
done
```

## Best Practices

1. **Measure before refactoring** - Establish baseline metrics
2. **Small, incremental changes** - Don't rewrite everything at once
3. **Feature flags** - Allow gradual rollout of new implementations
4. **Test coverage first** - Add tests before refactoring
5. **Document decisions** - Record why debt was introduced (if intentional)

## Output Format

Provide comprehensive debt analysis:

```markdown
# Technical Debt Analysis Report

Generated: YYYY-MM-DD

## Executive Summary

Debt Score: 7/10 (High)
Monthly Velocity Loss: ~35%
Bug Rate: 3x baseline
Recommended Investment: 200 hours over 3 months
Expected ROI: 250% within 6 months

## Critical Issues

1. Duplicate validation logic (5 locations)
   - Impact: 15 hours/month in duplicate bug fixes
   - Priority: HIGH
   - Effort: 20 hours

2. God module: src/core/processing.rs (1200 lines)
   - Impact: 40% slower feature development
   - Priority: HIGH
   - Effort: 40 hours

3. Missing integration tests for payment flow
   - Impact: 3 production bugs/month
   - Priority: CRITICAL
   - Effort: 30 hours

## Metrics Dashboard

Code Duplication: 18% (target: <5%)
Avg Complexity: 12 (target: <10)
Test Coverage: 45% (target: 80%)
Outdated Deps: 12 (target: 0)
Clippy Warnings: 34 (target: 0)

## Remediation Plan

Quick Wins (Week 1-2):

- Fix clippy warnings
- Update dependencies
- Add pre-commit hooks

Medium-Term (Month 1-3):

- Extract duplicate logic
- Refactor god modules
- Add integration tests

Long-Term (Q2-Q4):

- Architecture modernization
- Comprehensive test suite
- Performance optimization

## Prevention Strategy

- Pre-commit hooks for quality
- CI gates for complexity/coverage
- Monthly debt review meetings
- Documentation requirements

## Next Steps

1. Review and approve this analysis
2. Allocate 20% sprint capacity to debt reduction
3. Start with quick wins this week
4. Schedule monthly progress reviews
```

## Remember

Technical debt is normal and sometimes intentional. The goal is not to eliminate all debt, but to:

1. Make debt visible
2. Quantify its cost
3. Prioritize remediation by ROI
4. Prevent accumulation of new debt

Focus on high-impact, high-ROI improvements. Perfect is the enemy of good.
