---
name: devloop
description: Comprehensive helper for working with the DevLoop development observability tool - both using it to analyze development patterns and contributing to its development. Use when running DevLoop commands, interpreting council mode analysis, understanding git activity patterns, reviewing Claude Code sessions, or working on DevLoop's hexagonal architecture codebase. Trigger for phrases like "run devloop", "analyze branch", "council mode", "development patterns", or when working on the DevLoop Rust codebase itself.
allowed-tools: [Read, Bash, Grep, Glob]
skills: baml, writing-solid-rust
---

# DevLoop Development Observability Skill

A comprehensive helper for working with the DevLoop development observability tool - both using it to analyze development patterns and contributing to its development.

## Overview

DevLoop is a Rust-based development observability tool that provides a TUI for visualizing git activity and Claude AI sessions. This skill helps you:

1. **Run DevLoop commands** - Quick access to analysis, logs, export, and TUI
2. **Interpret analysis results** - Understand council mode insights and health scores
3. **Analyze development patterns** - Review git activity and Claude session metadata
4. **Develop DevLoop itself** - Navigate hexagonal architecture and BAML schemas

## When to Use This Skill

Use this skill when you need to:

- Run DevLoop analysis on a branch and interpret the results
- Understand council mode perspectives (Strict Critic, Creative Explorer, etc.)
- Review Claude Code session transcripts and development patterns
- Work on DevLoop's codebase (architecture, BAML, GKG integration)
- Debug or extend DevLoop features
- Generate development observability insights

## Prerequisites

**For using DevLoop:**
- DevLoop installed and built (`just run` works)
- Git repository to analyze
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (for AI analysis)

**For DevLoop development:**
- Rust toolchain (edition 2024)
- `just` command runner
- Optional: GKG server for code structure integration

## Core Capabilities

### 1. DevLoop Commands Wrapper

Quick access to common DevLoop commands with context about when and how to use them.

**Available Commands:**

```bash
# AI branch analysis (single perspective)
just analyze [BRANCH]

# AI branch analysis (multi-role council mode)
just analyze --council [BRANCH]

# View Claude Code session transcripts
just logs [SESSION]

# Export timeline data as JSON
just export

# Start the interactive TUI
just run

# Development commands
just dev        # Debug mode
just test       # Run tests
just fmt        # Format code
just check      # Quick compile check
just relay      # WebSocket relay server
```

**When to use each command:**
- `analyze` - Quick health check on a branch before merging
- `analyze --council` - Deep analysis from multiple AI perspectives (security, performance, creativity, etc.)
- `logs` - Review past Claude Code sessions and development history
- `export` - Get structured data for custom analysis or reporting
- `run` - Interactive exploration of git activity and timeline

### 2. Branch Analysis Helper

**Council Mode Perspectives:**

DevLoop's council analysis provides insights from 5 different AI roles:

1. **Strict Critic** - Conservative risk assessment, focuses on potential issues
2. **Creative Explorer** - Innovation opportunities, creative solutions
3. **General Analyst** - Balanced view, overall health assessment
4. **Security Reviewer** - Security concerns, vulnerability detection
5. **Performance Analyst** - Performance implications, optimization opportunities

**Interpreting Results:**

Health scores range from 0.0 to 1.0:
- **0.8-1.0** - Excellent, ready to merge
- **0.6-0.8** - Good, minor improvements suggested
- **0.4-0.6** - Fair, address recommendations before merging
- **0.0-0.4** - Poor, significant issues need attention

Each analyst provides:
- `health_score` - Numeric assessment
- `risk_level` - "low" | "medium" | "high"
- `insights` - Array of specific observations
- `recommendations` - Actionable suggestions

**Example workflow:**

```bash
# Run council analysis on current branch
just analyze --council

# Review different perspectives
# - Check Strict Critic for blockers
# - Review Security Reviewer for vulnerabilities
# - Consider Creative Explorer for enhancements
# - Use General Analyst for overall decision

# If health score < 0.6, address recommendations
# Then re-run analysis before merging
```

### 3. Development Observability

**Git Activity Analysis:**

DevLoop tracks:
- Branch lifetime and activity patterns
- Commit frequency and timing
- Session correlation with commits
- Development rhythm and focus areas

**Claude Session Metadata:**

Located in:
- `~/.claude/projects/` - Project configurations
- `~/.claude/transcripts/` - Session transcripts

DevLoop correlates sessions with git activity to:
- Identify which sessions led to which commits
- Detect context switches and multitasking
- Measure time between planning (sessions) and implementation (commits)
- Surface productivity patterns

**Productivity Insights:**

- **Session-to-commit lag** - Time between AI assistance and implementation
- **Branch focus** - Single vs. multi-branch development patterns
- **Commit batching** - Small frequent commits vs. large batches
- **AI reliance** - Correlation between session frequency and code quality

### 4. DevLoop Development

**Architecture Overview:**

DevLoop uses **hexagonal (ports-and-adapters) architecture**:

```
┌─────────────────────────────────────────┐
│  TUI Layer (crates/cli)                 │
│  - Ratatui UI components                │
│  - App<T, B, I> generic over adapters   │
└───────────────┬─────────────────────────┘
                │ Trait boundaries
┌───────────────▼─────────────────────────┐
│  Domain Layer (crates/components)       │
│  - Pure domain models (zero deps)       │
│  - Trait-based ports:                   │
│    • TimelineProvider                   │
│    • BranchAggregator                   │
│    • InsightProvider                    │
└───────────────┬─────────────────────────┘
                │ Trait implementations
┌───────────────▼─────────────────────────┐
│  Adapter Layer (crates/cli/adapters)    │
│  - GitAdapter (git2-based)              │
│  - BamlAdapter (AI analysis)            │
│  - GkgAdapter (code structure)          │
│  - UnifiedAdapter (composition)         │
│  - CouncilAdapter (multi-role AI)       │
└─────────────────────────────────────────┘
```

**Key Design Principles:**

1. **Domain purity** - `components/src/domain.rs` has zero external dependencies
2. **Dependency injection** - `App` receives trait objects, not concrete types
3. **Testability** - Trait boundaries enable test doubles without mocking
4. **Serializable schema** - `components/src/schema.rs` for cross-runtime rendering

**Workspace Crates:**

- **`crates/cli`** - Main TUI application (ratatui), entry point, adapters
- **`crates/components`** - Domain models, ports (traits), git adapter
- **`crates/baml`** - AI analysis schemas and generated client
- **`crates/slides`** - BAML-powered slide generation with ppt-rs
- **`crates/devloop-cli`** - Non-interactive CLI for agents/scripting
- **`crates/relay`** - WebSocket broadcast server for events

**BAML Development:**

BAML files define AI analysis functions in `crates/baml/baml_src/`:

```baml
// Function definition
function AnalyzeBranch_StrictCritic(
  branch_name: string
  commits: string
  sessions: string
  commit_count: int
  session_count: int
) -> BranchInsight {
  client CustomGPT5Mini
  prompt #"
    You are a STRICT CRITIC reviewing a development branch.

    Branch: {{ branch_name }}
    Commits: {{ commit_count }}
    Sessions: {{ session_count }}

    Recent commits:
    {{ commits }}

    Recent sessions:
    {{ sessions }}

    Focus on risks, issues, and conservative assessment.

    {{ ctx.output_format }}
  "#
}
```

**BAML Best Practices (from rules/baml.md):**

- Classes use PascalCase, fields use snake_case
- All fields need `@description` annotations
- Always end prompts with `{{ ctx.output_format }}`
- Use Mini models for simple extraction, full models for reasoning
- Define clients in `clients.baml` for reusability
- Descriptive test names: `test analyze_active_feature_branch`

**GKG Integration:**

GitLab Knowledge Graph provides code structure:

```rust
// Fetch code definitions
let definitions = gkg_adapter.get_definitions("src/main.rs").await?;

// Fetch code references
let references = gkg_adapter.get_references("function_name").await?;

// Get repository map
let repo_map = gkg_adapter.get_repo_map().await?;
```

**GKG Setup (v0.25.0+):**

```bash
# Stop server before indexing
gkg server stop

# Index project
gkg index .

# Start server
gkg server start
```

**Important:** v0.25.0+ removed HTTP indexing API - use CLI directly.

**Common Development Tasks:**

```bash
# Run tests
just test

# Run specific package tests
cargo test -p devloop-cli

# Format all code
just fmt

# Lint
cargo clippy --workspace

# Quick compile check
just check

# Clean build artifacts
just clean

# Simultaneous relay + TUI dev
zellij --layout devloop-layout.kdl
```

## Workflow Examples

### Example 1: Pre-merge Branch Analysis

```bash
# Scenario: About to merge feature/auth branch
# Goal: Ensure branch is ready for merge

# Step 1: Run council analysis
just analyze --council feature/auth

# Step 2: Review health scores
# - All analysts > 0.6? Proceed
# - Any analyst < 0.6? Address recommendations

# Step 3: Check specific concerns
# - Security Reviewer: Any vulnerabilities?
# - Performance Analyst: Any bottlenecks?
# - Strict Critic: Any blockers?

# Step 4: If issues found, fix and re-analyze
# ... make fixes ...
just analyze --council feature/auth

# Step 5: Merge when all green
```

### Example 2: Development Pattern Analysis

```bash
# Scenario: Want to understand my development rhythm
# Goal: Identify productivity patterns

# Step 1: Start TUI to explore timeline
just run

# Step 2: Navigate to BranchList view
# - See all branches with activity
# - Note branch lifetimes and commit counts

# Step 3: Drill into specific branch
# - View timeline of commits and sessions
# - Identify session-to-commit lag
# - Detect context switches

# Step 4: Export data for custom analysis
just export > timeline.json

# Step 5: Analyze patterns
# - How often do I switch branches?
# - What's my session-to-commit lag?
# - Do I batch commits or commit frequently?
```

### Example 3: Adding a New BAML Analyst

```bash
# Scenario: Want to add "Documentation Reviewer" role
# Goal: Extend council with docs-focused perspective

# Step 1: Create BAML function
# Edit crates/baml/baml_src/analysis.baml

function AnalyzeBranch_DocsReviewer(
  branch_name: string
  commits: string
  sessions: string
  commit_count: int
  session_count: int
) -> BranchInsight {
  client CustomGPT5Mini
  prompt #"
    You are a DOCUMENTATION REVIEWER.

    Focus on:
    - README updates
    - Code comments
    - API documentation
    - User-facing docs

    Branch: {{ branch_name }}
    {{ commits }}
    {{ sessions }}

    {{ ctx.output_format }}
  "#
}

# Step 2: Add test case
test analyze_docs_heavy_branch {
  functions [AnalyzeBranch_DocsReviewer]
  args {
    branch_name "feature/docs"
    commits "Add API docs\nUpdate README"
    sessions "Planning docs structure"
    commit_count 3
    session_count 1
  }
}

# Step 3: Regenerate BAML client
cd crates/baml
baml-cli generate

# Step 4: Update CouncilAdapter
# Edit crates/cli/src/adapters/council.rs
# Add DocsReviewer to council members

# Step 5: Test
just test-pkg devloop-cli
just analyze --council
```

### Example 4: Debugging GKG Integration

```bash
# Scenario: GKG integration not working
# Goal: Diagnose and fix GKG connectivity

# Step 1: Check GKG server status
gkg server status

# If stopped, start it:
gkg server start

# Step 2: Verify indexing
gkg server stop
gkg index .
gkg server start

# Step 3: Test GKG connectivity
curl http://localhost:27495/health

# Step 4: Check environment variables
echo $GKG_SERVER_URL
# Should be http://localhost:27495 or unset (uses default)

# Step 5: Run DevLoop with GKG debug
RUST_LOG=devloop_cli::adapters::gkg=debug just run

# Step 6: Verify graceful degradation
# UnifiedAdapter should work even if GKG unavailable
# Check logs for "GKG unavailable" warnings vs errors
```

## Tips and Best Practices

**For Using DevLoop:**

1. **Run council mode for important branches** - Single analyst is quick but may miss insights
2. **Export data regularly** - Build historical analysis of development patterns
3. **Review session transcripts** - Learn from past AI interactions
4. **Use health scores as guidelines** - Not absolute truth, but useful signals

**For DevLoop Development:**

1. **Keep domain pure** - Never add external deps to `components/src/domain.rs`
2. **Test through traits** - Create test doubles, don't mock concrete types
3. **Follow BAML rules** - PascalCase classes, snake_case fields, always `@description`
4. **Handle GKG gracefully** - UnifiedAdapter must work without GKG server
5. **Document architecture decisions** - Update CLAUDE.md and architecture docs
6. **Run full test suite** - `just test` before committing
7. **Format religiously** - `just fmt` to maintain consistency

## Troubleshooting

**"Command not found: just"**
- Install `just`: `cargo install just` or `brew install just`

**"BAML client not found"**
- Regenerate client: `cd crates/baml && baml-cli generate`

**"GKG server unavailable"**
- Start server: `gkg server start`
- Or let UnifiedAdapter degrade gracefully (it's designed for this)

**"No API key found"**
- Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- For BAML: `export OPENAI_API_KEY=sk-...`

**"Health score seems wrong"**
- Council mode uses multiple perspectives - compare all analysts
- Single analyst may be overly optimistic or pessimistic
- Health scores are signals, not absolute truth

**"Tests failing after BAML changes"**
- Regenerate client: `cd crates/baml && baml-cli generate`
- Update test expectations if schema changed
- Run `just test-pkg devloop-cli` for faster iteration

## Resources

**Project Files:**
- `/Users/joe/dev/devloop/CLAUDE.md` - Main project documentation
- `/Users/joe/dev/devloop/justfile` - Command definitions
- `/Users/joe/dev/devloop/TESTING_CHECKLIST.md` - Comprehensive test guide
- `/Users/joe/dev/devloop/crates/components/src/domain.rs` - Core domain models
- `/Users/joe/dev/devloop/crates/baml/baml_src/` - BAML schemas
- `/Users/joe/.claude/rules/baml.md` - BAML style guide

**Key Concepts:**
- Hexagonal Architecture (Ports and Adapters)
- Domain-Driven Design (Pure domain layer)
- BAML (Boundary AI Modeling Language)
- GKG (GitLab Knowledge Graph)

**External Documentation:**
- BAML: https://docs.boundaryml.com/
- Ratatui: https://ratatui.rs/
- GKG: https://gitlab-org.gitlab.io/rust/knowledge-graph/

## Skill Maintenance

This skill should be updated when:
- New DevLoop commands are added to `justfile`
- Council roles are added/removed
- Architecture patterns change (e.g., new adapter types)
- BAML schema conventions evolve
- GKG integration approach changes

**Version:** 1.0.0
**Last Updated:** 2026-03-15
**Maintained By:** DevLoop contributors
