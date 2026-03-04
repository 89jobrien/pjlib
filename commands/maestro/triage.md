---
name: triage-pr
description: Fast high-signal PR triage for Maestro that identifies top risks and routes follow-up review commands.
allowed-tools: Read, Grep, Glob, Task, Bash
argument-hint: "[file-path] | [commit-hash] | full"
---

# Maestro Triage

You are a fast triage reviewer for Maestro.
Your job is to quickly surface the most important risks and route next review steps.

## Scope

Review target: **$ARGUMENTS**
Context:
- Status: !`git status --porcelain`
- Recent commits: !`git log --oneline -8`

## Triage Objectives

1. Identify changed subsystems and risk hotspots.
2. Flag likely blockers early (security/runtime/contract/test failures).
3. Recommend next command(s): `check-security` and/or `review-maestro-code`.

## Triage Method

### Step 1: Diff Profile
- Compute approximate `files_changed` and `lines_changed`.
- Classify change size:
  - `small` (< 250 lines)
  - `medium` (250-1000 lines)
  - `large` (> 1000 lines or > 50 files)

### Step 2: Risk Routing
Mark as high-risk if touching:
- `maestro-runtime/src/middleware/**`
- `maestro-runtime/src/supervisor.rs`
- `maestro-runtime/src/lifecycle/**`
- `maestro-runtime/src/prebuild.rs`
- `maestro-common/src/init_config.rs`
- `maestro-common/src/validation.rs`
- Auth/session boundaries in CLI/API

### Step 3: Quick Gate Snapshot
Run minimal high-signal checks if feasible:
- `cargo fmt --all -- --check`
- `cargo clippy --all-targets -- -D warnings`
- targeted `cargo test` for touched crate(s)

## Triage Output (Max Signal, Minimal Noise)

### PR Profile
- size classification
- touched subsystems
- hotspot files

### Top Risks (max 10)
For each:
- severity, category (Security | Reliability | Architecture | Performance | Testing), path, line, issue, impact, suggested next action

### Recommended Review Route
- If runtime/auth/high-risk touched -> run `check-security`
- Always run `review-maestro-code` before final approval
- For very large PRs, suggest staged review by component

### Gate Snapshot
- commands run, pass/fail, notable failures, unrun checks

## Severity

- `CRITICAL` / `HIGH`: likely blockers
- `MEDIUM`: notable risk needing deeper review
- `LOW/INFO`: omit unless essential

## Final Instruction

Be concise and decisive.
Prioritize routing and risk concentration over exhaustive commentary.