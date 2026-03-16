---
name: rust-multi-agent
description: Coordinated multi-agent workflow for comprehensive Rust development with parallel architecture review, optimization scanning, and test engineering. Use when starting new Rust features, reviewing architecture changes before PR submission, conducting code quality assessments, or setting up testing infrastructure. Triggers parallel execution of architect-reviewer, rust-optimization-scanner, and test-engineer agents for maximum efficiency.
allowed-tools: [Agent, Read, Grep, Glob, Bash]
skills: writing-solid-rust, test-automation
---

# Rust Multi-Agent Development Workflow

A coordinated multi-agent workflow for comprehensive Rust development with parallel architecture review, optimization scanning, and test engineering.

## Overview

This skill orchestrates multiple specialized agents to provide comprehensive analysis and development support for Rust projects:

1. **architect-reviewer** - Architecture review with SOLID principles and design patterns
2. **rust-optimization-scanner** - Performance optimization opportunities
3. **test-engineer** - Comprehensive test strategy and coverage

## Usage

Invoke this skill when:
- Starting work on a new Rust feature or refactor
- Reviewing architecture changes before PR submission
- Conducting comprehensive code quality assessments
- Setting up testing infrastructure

## Workflow

The skill runs agents in parallel for maximum efficiency:

```bash
# Automatic parallel execution
/rust-multi-agent
```

Or run specific phases:

```bash
# Architecture review only
/rust-multi-agent --phase=architecture

# Optimization scan only
/rust-multi-agent --phase=optimization

# Test strategy only
/rust-multi-agent --phase=testing

# Full workflow (default)
/rust-multi-agent --phase=all
```

## Agent Responsibilities

### architect-reviewer
- Evaluates SOLID principles adherence
- Reviews layering and separation of concerns
- Checks for proper abstraction boundaries
- Validates hexagonal architecture patterns

### rust-optimization-scanner
- Identifies excessive clone() usage
- Finds serialization optimization opportunities
- Reviews Arc/Mutex usage patterns
- Suggests zero-cost abstractions

### test-engineer
- Designs comprehensive test strategy
- Plans unit, integration, and e2e tests
- Sets up test infrastructure
- Reviews test coverage

## Output

Generates a consolidated report with:
- Architecture assessment and recommendations
- Performance optimization opportunities
- Test strategy and implementation plan
- Prioritized action items

## Configuration

Set these environment variables to customize behavior:

```bash
# Skip specific agents
SKIP_ARCHITECTURE=true
SKIP_OPTIMIZATION=true
SKIP_TESTING=true

# Detail level
DETAIL_LEVEL=summary  # or 'detailed'

# Focus areas
FOCUS_CRATES="cli,components"  # Comma-separated crate names
```

## Integration with DevLoop

This skill works seamlessly with DevLoop pipeline data:

1. Automatically detects active crates from recent git activity
2. Focuses analysis on recently modified code
3. Surfaces context from recent Claude Code sessions
4. Uses council analysis results for deeper insights

## Examples

### Basic usage - Full workflow
```bash
/rust-multi-agent
```

### Focus on specific crates
```bash
FOCUS_CRATES="cli,eddos" /rust-multi-agent
```

### Architecture review before PR
```bash
/rust-multi-agent --phase=architecture --detail=detailed
```

### Quick optimization check
```bash
/rust-multi-agent --phase=optimization
```

## Tips

- Run this proactively after significant code changes
- Use before creating pull requests for comprehensive review
- Combine with `/test:run` to validate recommendations
- Reference output in PR descriptions for reviewers
