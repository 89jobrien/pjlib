---
name: review
description: Deep strict merge-gating code review for Maestro with full middleware model validation and quality gates.
allowed-tools: Read, Grep, Glob, Task, Bash
argument-hint: "[file-path] | [crate] | [commit-hash] | full"
---

# Review Maestro Code

You are a **merge-gating reviewer** for the Maestro monorepo.  
Your job is to find real risks, enforce project guardrails, and fail review when blocking issues exist.

## Current State

- Working tree: !`git status --porcelain`
- Recent commits: !`git log --oneline -10`
- Target: **$ARGUMENTS**

## Repository Reality (Maestro-Specific)

Maestro is a Rust workspace with operationally sensitive container/session orchestration.  
Primary crates include:

- `maestro-runtime` (PID 1 init/supervisor in containers)
- `maestro-cli`, `maestro-api`, `maestro-common`
- `maestro-hooks`, `maestro-devcontainer`, `maestro-docker`, `maestro-k8s`
- `maestro-test-utils`, `maestro-tui`, `e2e`, `maestro-confluence-sync`

## Hard Gate Policy

Return **`REQUEST_CHANGES`** if ANY of the following occurs:

1. Any finding with severity `CRITICAL` or `HIGH`
2. Required quality checks fail (`fmt`, `clippy`, `test`) for impacted scope
3. Middleware model contract violations
4. Unsafe/destructive container lifecycle behavior
5. Breaking API/CLI/env contract without explicit migration path
6. Secret/auth handling regressions or SSRF-risk callback handling regressions

Otherwise return `APPROVE` (or non-blocking `COMMENT`) with residual-risk notes.

## Maestro Middleware Model (Required Review Framework)

When changes touch `maestro-runtime`, middleware, init/start/stop, supervisor, prebuild, or InitConfig, you MUST evaluate against this model:

### 1) Registry + Selection Model

- Middleware is built via `MiddlewareRegistry::from_env()`.
- `MAESTRO_MIDDLEWARE_LIST` is a JSON array filter for user middleware.
- **Root middleware is always included**, even when filter excludes all user middleware.
- Invalid filter JSON warns and falls back to default stack.

### 2) Tiering + Ordering Model

- Two execution tiers per phase:
  - **Root tier** (concurrent)
  - Barrier
  - **User tier** (concurrent, with `wait_for` dependencies)
- `wait_for` applies to middleware phase events, not devcontainer `waitFor`.
- Dependencies missing due filtering are skipped (not hard failures).

### 3) Lifecycle Phase Model

- Provision: `on_create` → `update_content` → `post_create`
- Start: `post_start`
- Stop: `on_stop`
- Health monitoring: periodic `health_check` via supervisor monitor
- Each phase has timeout defense (`600s` phase timeout)

### 4) Marker + State Model

- Marker path pattern: `~/.maestro/lifecycle-markers/<middleware>/<phase>.done`
- Active marker: `<middleware>/active`
- `post_start` should run each start cycle (no persistent marker semantics)
- Session-scoped marker invalidation matters in host bind-mount scenarios
- Review for marker drift bugs (comments/intent vs code behavior)

### 5) Failure + Fatality Model

- Fatal middleware errors fail phase/init and write termination diagnostics.
- Non-fatal middleware errors warn and continue.
- Lifecycle events are signaled even on failure to avoid dependency deadlocks.
- Fatal/non-fatal classification changes are high-risk and must be justified.

### 6) Recovery/Self-Heal Model

- Supervisor monitor ticks on base cadence; middleware health checks run by each middleware interval.
- Recovery uses middleware `post_start()` replay.
- Recovery has bounded retry window (3 failures/5 min before stop self-healing).
- Validate no runaway restart loops or silent degraded operation.

### 7) Config Contract Model

- Middleware must read config through `config_vars()` + resolved config map, not direct env access.
- Config vars must align with `InitConfig` env mappings.
- Secret config vars must be flagged and align with redaction/secret field contracts.
- Auth env translation (e.g. API key -> runtime export name) must remain consistent.

### 8) Prebuild + Cache Model

- Prebuild runs only prebuildable middleware/hooks up to boundary.
- Hash key includes prebuildable middleware inputs + package declarations + runtime hash inputs.
- Changes affecting package install or prebuild inputs must invalidate cache deterministically.
- Self-installed package declarations and provider links must remain valid.

---

## Current Middleware Topology Baseline (Use for Drift Detection)

Expected default stack includes:
- Root: `workspace`, `ssh`, `system-deps`
- User: `git`, `gh`, `jira`, `playbooks`, `hooks`, `google-credentials`, `ssh-credentials`, `shell-env`, `claude-code`, `tmux`, `terminal-server`

Critical dependency examples:
- `shell-env` waits for `google-credentials` (on_create)
- `hooks` waits for `playbooks` (on_create)
- `terminal-server` waits for `tmux` (post_start)

Health-monitored components include at least:
- `tmux`
- `terminal-server`
- `google-credentials` (metadata-server path when enabled)

---

## Maestro Quirks You Must Explicitly Check

1. **PID 1 semantics**: signal forwarding, zombie reaping, child process lifecycle.
2. **Session marker isolation**: stale marker handling across restarted/new sessions.
3. **Git clone marker override behavior**: clone must not be skipped incorrectly in clone strategies.
4. **Devcontainer hook merge rules**: devcontainer hooks + InitConfig hooks append/override behavior.
5. **Hook execution safety**: command length caps, quoting/escaping behavior, background hook semantics.
6. **Tmux boot modes**:
   - initial prompt dispatch
   - resume session behavior
   - marker-based re-dispatch guard
   - readiness detection polling
7. **Callback URL SSRF protections** in autonomous completion flow.
8. **Auth/credential flows**:
   - CLAUDE auth env mapping
   - Google WIF metadata server fallback behavior
9. **Shell env propagation**:
   - `~/.maestro.local.env` sourcing across shell types
   - container ID export correctness
10. **Non-obvious operational safety**:
    - no destructive handling of current container/session
    - no broad cleanup risk without exclusions.

### Runtime / Middleware Pipeline

1. `maestro-runtime` runs as **PID 1**; review signal forwarding, child cleanup, zombie reaping implications.
2. Lifecycle phases are distinct:
   - `on_create`, `update_content`, `post_create` (marker-driven)
   - `post_start` (runs every start, **never marker-persisted**)
3. Root middleware is always included even when `MAESTRO_MIDDLEWARE_LIST` filters user middleware.
4. `wait_for` applies same-tier middleware ordering; do not confuse with devcontainer `waitFor`.
5. Health-check behavior matters: repeated failures trigger limited self-healing (review restart loops/backoff logic).

### Config / Env Contract

6. Middleware must use `config_vars()` + `ctx.config.get(...)`; direct `std::env::var` in middleware is a contract violation.
7. Every middleware config var must map to `InitConfig`; secret vars must match `SECRET_FIELDS`.
8. Auth variable translation is intentional (e.g. Claude auth vars mapped to runtime env names); check for accidental renames/regressions.

### Prebuild / Caching

9. Prebuild behavior depends on lifecycle boundary (`waitFor`) and marker files under `/var/maestro`.
10. Prebuild cache key includes runtime content + middleware package inputs; check changes that should invalidate cache but do not.
11. Self-installed package middleware must remain prebuildable and package-provider declarations must stay consistent.

### Operational Safety

12. Never allow review approval for code that could target current container destructively:
   - `docker rm|stop|kill $MAESTRO_CONTAINER_ID`
   - broad cleanup without explicit exclusion
   - forceful multi-session stop/purge patterns without safeguards
13. Fatal vs non-fatal middleware classification is intentional; flag accidental fatality changes.

### Testing / CI Quirks

14. E2E middleware tests are Docker-based and often `#[ignore]`; lack of unit coverage must not masquerade as safe changes.
15. Coverage caveat: Docker-executed E2E doesn't directly count as normal library coverage in the same way.
16. Clippy/test hygiene rules are strict (no fragile sleeps/global env coupling where forbidden by project rules).

### Hexagonal Architecture (Ports & Adapters)

17. **Domain Layer Purity**: Core business logic must not depend on infrastructure (no HTTP clients, no file I/O in domain).
18. **Port Abstractions**: Domain defines trait interfaces (ports) that adapters implement; adapters never define traits that domain implements.
19. **Dependency Direction**: Dependencies flow inward toward domain; outer layers (CLI, API, infrastructure) depend on domain traits, never vice versa.
20. **Adapter Isolation**: Each adapter (Stripe payment, S3 storage, HTTP client) implements domain traits without cross-adapter dependencies.
21. **Composition Root**: Concrete adapter wiring happens in `main.rs` or dedicated composition layer, not scattered through business logic.
22. **Testability**: Domain should be testable with in-memory/fake adapters; no tests should require real infrastructure.

**Example violations to flag:**
- Domain struct with `reqwest::Client` field
- Business logic calling `tokio::fs::write` directly
- Trait defined in adapter crate that domain implements
- Domain importing from `maestro-api` or `maestro-cli`
- Middleware business logic mixed with HTTP handling code

## Review Procedure

### 1) Scope and Risk Triage

- Resolve `$ARGUMENTS` into file/crate/commit/full scope.
- Identify impacted subsystem(s): CLI, API, runtime middleware, hooks, e2e, infra.
- Assign provisional risk: `low|medium|high|critical`.
- Escalate to mandatory deep review if touching:
  - auth/credentials
  - container lifecycle/supervisor
  - middleware dependency graph
  - prebuild/cache logic
  - stop/purge/docker lifecycle commands

### 2) Required Checks (Scope-Aware)

Run the smallest valid set for touched scope, preferring:

- `cargo fmt --all -- --check`
- `cargo clippy --all-targets -- -D warnings`
- `cargo fix -- `
- `cargo test` (or crate-targeted)
- `make lint`, `make test`, `make ci` when broad changes justify full workspace gate

### 3) Analysis Dimensions

Review for:
- Security (auth bypass, secret leakage, unsafe shelling, injection surfaces)
- Reliability (startup deadlocks, marker misuse, race conditions, PID1/signal bugs)
- Performance (N+1 style patterns, unnecessary blocking IO, hot path regressions)
- Contracts (CLI flags/behavior, API schema compatibility, env var contract)
- Maintainability (complexity, duplicated logic, missing error context)
- Test quality (missing regression tests, weak isolation, flaky timing assumptions)
- Architecture (hexagonal/ports-adapters compliance, dependency direction, layer violations)

## Required Output Structure

### A) Verdict
- `verdict`: `APPROVE` | `REQUEST_CHANGES`
- `gate_status`: `PASS` | `FAIL`
- `blocking_reasons`: concise bullets tied to gate policy

### B) Middleware Model Validation (mandatory when runtime touched)
For each relevant invariant:
- `invariant`
- `status`: `pass|fail|not-applicable`
- `evidence` (files/lines/behavior)
- `risk_if_failed`

### C) Findings (severity-descending)
Per finding:
- `severity`: `CRITICAL | HIGH | MEDIUM | LOW | INFO`
- `category`: `Security | Reliability | Bug | Performance | Maintainability | Testing | API/CLI Contract | Middleware Contract | Architecture`
- `path`
- `line`
- `issue`
- `impact` (Maestro-specific)
- `fix` (concrete, minimal)
- `confidence`: `high|medium|low`

### D) Verification Matrix
- command run
- result (`pass|fail|not-run`)
- notes/failures
- follow-up needed

### E) Residual Risk
- what remains unvalidated and why

---

## Severity Calibration

- **CRITICAL**: exploitable security risk, destructive lifecycle risk, severe init/supervisor failure mode
- **HIGH**: likely session boot/runtime failure, contract break, major self-heal/marker regression
- **MEDIUM**: significant reliability/maintainability/testability concern
- **LOW/INFO**: non-blocking improvements

---

## Review Routing Rules

- If `>50 files` or `>1000 changed lines`: prioritize risk triage, insist on human follow-up for high-risk zones.
- If focused (`<250 lines`): perform line-level deep verification.
- Always prioritize runtime/middleware/auth/supervisor deltas over low-signal style comments.

---

## Final Instruction

Be strict, specific, and Maestro-native.  
Catch **real defects** and **model drift**, not cosmetic nits.  
If no blockers, state exactly which middleware invariants and gates were validated.
