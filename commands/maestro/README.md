# Maestro Review Commands

Specialized Claude Code slash commands for reviewing code changes in the Maestro monorepo.

## Overview

Maestro is a Rust-based container orchestration system with operationally sensitive middleware, PID 1 init/supervisor
logic, and complex lifecycle management. These commands provide progressive review workflows tailored to Maestro's
architecture and security requirements.

## Available Commands

### `/refactor-hexagonal` - Refactor to Hexagonal Architecture

Systematic refactoring to apply hexagonal architecture (ports & adapters) pattern to Rust code.

**Usage:**

```bash
/refactor-hexagonal [file-path] | [crate] | full
```

**Purpose:**

Transform tightly coupled code into clean hexagonal architecture with:
- Pure domain layer (zero infrastructure dependencies)
- Port traits defined by domain
- Adapters implementing ports
- Proper dependency inversion

**What it does:**

1. Analyzes current architecture violations
2. Identifies infrastructure coupling in domain
3. Extracts domain types and port traits
4. Creates real and test adapters
5. Refactors handlers/commands to thin orchestration
6. Updates composition root (main.rs)
7. Verifies dependency boundaries

**Example transformations:**

**Before:** Domain depends on infrastructure

```rust
pub struct UserService {
    http_client: reqwest::Client, // ❌ infrastructure leak
    db_pool: PgPool,              // ❌ infrastructure leak
}
```

**After:** Domain depends on traits

```rust
pub trait HttpClient {
    fn get(&self, url: &str) -> Result<Response>;
}

pub trait UserRepository {
    fn save(&self, user: &User) -> Result<()>;
}

pub struct UserService<H: HttpClient, R: UserRepository> {
    http_client: H,  // ✅ trait abstraction
    user_repo: R,    // ✅ trait abstraction
}
```

**Output:**

- Refactoring plan with violation analysis
- Incremental implementation with Edit/Write/MultiEdit
- Verification report (dependency analysis, test coverage, quality gates)

### `/triage-pr` - Fast PR Triage

Quick risk assessment and routing for pull requests.

**Usage:**

```bash
/triage-pr [file-path] | [commit-hash] | full
```

**Purpose:**

- Rapidly identify changed subsystems and risk hotspots
- Flag likely blockers early (security/runtime/contract/test failures)
- Route to appropriate next review command(s)

**What it does:**

1. Computes diff profile (files changed, lines changed)
2. Classifies change size: small (<250 lines), medium (250-1000 lines), large (>1000 lines)
3. Identifies high-risk areas (runtime middleware, supervisor, auth boundaries)
4. Runs minimal gate checks (fmt, clippy, targeted tests if feasible)
5. Recommends next steps: `/check-security` and/or `/review`

**Output:**

- PR profile (size, touched subsystems, hotspot files)
- Top risks (max 10, severity-ranked)
- Recommended review route
- Gate snapshot (pass/fail status)

### `/check-security` - Security Gate Review

Strict security and reliability review focused on Maestro-specific runtime concerns.

**Usage:**

```bash
/check-security [file-path] | [crate] | [commit-hash] | full
```

**Purpose:**

Merge-gating security review that prioritizes real security/runtime risks over style issues.

**Critical Focus Areas:**

- PID 1 process safety (signal handling, zombie reaping, shutdown)
- Middleware contract integrity (tiering, ordering, dependencies)
- Config/auth/secret safety (credential handling, SSRF protections)
- Prebuild/cache safety (invalidation logic, stale cache risks)
- Operational guardrails (destructive behavior prevention)

**Blocking Policy:**

Returns `REQUEST_CHANGES` if:

- Any `CRITICAL` or `HIGH` finding exists
- Security controls weakened
- PID1/supervisor safety regression
- Middleware model contract drift
- Unsafe container/session lifecycle behavior
- Required checks fail

**Output:**

- Verdict: `APPROVE` or `REQUEST_CHANGES`
- Gate status: `PASS` or `FAIL`
- Critical findings with severity, category, path, issue, impact
- Threat checklist results
- Verification matrix
- Residual risk assessment

### `/review` - Comprehensive Code Review

Deep merge-gating review with full middleware model validation and quality gates.

**Usage:**

```bash
/review [file-path] | [crate] | [commit-hash] | full
```

**Purpose:**

Complete code review enforcing Maestro project guardrails and finding real defects.

**Review Dimensions:**

- **Security**: auth bypass, secret leakage, injection surfaces
- **Reliability**: startup deadlocks, marker misuse, race conditions, PID1/signal bugs
- **Performance**: N+1 patterns, blocking IO, hot path regressions
- **Contracts**: CLI/API compatibility, env var contracts
- **Maintainability**: complexity, duplicated logic, error context
- **Test quality**: regression coverage, isolation, flaky assumptions

**Middleware Model Validation:**

When changes touch runtime/middleware/lifecycle, validates:

1. Registry + Selection Model (root middleware inclusion)
2. Tiering + Ordering Model (root tier → barrier → user tier)
3. Lifecycle Phase Model (provision/start/stop/health)
4. Marker + State Model (lifecycle markers, session isolation)
5. Failure + Fatality Model (fatal vs non-fatal classification)
6. Recovery/Self-Heal Model (bounded retry, restart loops)
7. Config Contract Model (config vars, secret handling)
8. Prebuild + Cache Model (invalidation, determinism)

**Output:**

- Verdict and gate status
- Middleware model validation results
- Severity-ranked findings
- Verification matrix
- Residual risk assessment

## Recommended Workflow

### Code Review Workflow

For most PRs, use progressive review:

```bash
# 1. Start with triage to assess scope
/triage-pr

# 2. If high-risk areas touched, run security gate
/check-security

# 3. Always run comprehensive review before merge
/review
```

For focused changes to known files:

```bash
# Review specific file
/review path/to/file.rs

# Review specific crate
/review maestro-runtime

# Review specific commit
/review abc123
```

### Refactoring Workflow

When improving architecture:

```bash
# Refactor specific file to hexagonal architecture
/refactor-hexagonal src/services/user_service.rs

# Refactor entire crate
/refactor-hexagonal maestro-api

# After refactoring, verify with review
/review maestro-api
```

## Maestro Architecture Context

### Primary Crates

- `maestro-runtime` - PID 1 init/supervisor in containers
- `maestro-cli`, `maestro-api`, `maestro-common`
- `maestro-hooks`, `maestro-devcontainer`, `maestro-docker`, `maestro-k8s`
- `maestro-test-utils`, `maestro-tui`, `e2e`, `maestro-confluence-sync`

### High-Risk Paths

Changes to these paths receive elevated scrutiny:

- `maestro-runtime/src/supervisor.rs`
- `maestro-runtime/src/lifecycle/**`
- `maestro-runtime/src/middleware/**`
- `maestro-runtime/src/prebuild.rs`
- `maestro-common/src/init_config.rs`
- `maestro-common/src/validation.rs`
- Auth/session boundaries in CLI/API

### Quality Gates

All commands may run scope-appropriate checks:

- `cargo fmt --all -- --check`
- `cargo clippy --all-targets -- -D warnings`
- `cargo test` (targeted or full)
- `make ci` (for broad changes)

## Severity Calibration

- **CRITICAL**: Exploitable security, destructive lifecycle risk, severe init/supervisor failure
- **HIGH**: Likely session failure, contract break, major middleware regression
- **MEDIUM**: Significant reliability/maintainability concern
- **LOW/INFO**: Non-blocking improvements (generally omitted unless valuable)

## Installation

These commands are automatically available in Claude Code when working in the Maestro repository at
`~/.claude/commands/maestro/`.

## Contributing

When modifying these commands:

1. Maintain strict focus on Maestro-specific risks
2. Keep triage fast (max signal, minimal noise)
3. Ensure security gate catches real threats
4. Update middleware model validation when architecture changes
5. Test commands on representative PRs before deploying
