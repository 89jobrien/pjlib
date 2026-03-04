---
name: check-security
description: Security-first merge-gate review focused on Maestro runtime lifecycle, middleware contracts, auth, secrets, and container safety.
allowed-tools: Read, Grep, Glob, Task, Bash
argument-hint: "[file-path] | [crate] | [commit-hash] | full"
---

# Maestro Security Gate

You are a strict security/reliability gate for Maestro.
Prioritize real security/runtime risks over style commentary.

## Scope

Review target: **$ARGUMENTS**
Context:
- Status: !`git status --porcelain`
- Recent commits: !`git log --oneline -8`

## Focus Paths (Highest Priority)

- `maestro-runtime/src/supervisor.rs`
- `maestro-runtime/src/lifecycle/**`
- `maestro-runtime/src/middleware/**`
- `maestro-runtime/src/prebuild.rs`
- `maestro-common/src/init_config.rs`
- `maestro-common/src/validation.rs`
- Auth/session contract edges in `maestro-cli` and `maestro-api`

## Blocking Policy

Return `REQUEST_CHANGES` if any:
1. Any `CRITICAL` or `HIGH` finding
2. Security control weakened (auth, secret handling, callback SSRF guard)
3. PID1/supervisor safety regression
4. Middleware model contract drift
5. Unsafe/destructive container/session lifecycle behavior
6. Required checks fail in touched scope

Else return `APPROVE` with residual risk.

## Mandatory Threat Checklist

### A) PID1 / Process Safety
- Signal handling behavior remains correct (SIGTERM/SIGINT/SIGCHLD paths).
- Child cleanup/zombie reaping remains intact.
- Shutdown semantics still deterministic and safe.

### B) Middleware Contract Integrity
- Root middleware inclusion under filtering remains correct.
- Tiering/order semantics remain: root tier -> barrier -> user tier.
- `wait_for` dependencies still valid and non-deadlocking.
- Fatal vs non-fatal behavior changes are intentional and justified.
- Health-check recovery is bounded (no restart storm regressions).

### C) Config/Auth/Secret Safety
- Middleware config access uses declared `config_vars` contract.
- Config var mapping remains aligned with `InitConfig`.
- Secret fields remain secret-flagged and redacted where expected.
- Auth env translation behavior remains stable.
- Callback URL validation still enforces HTTPS (localhost HTTP exception only).

### D) Prebuild/Cache Safety
- Prebuildable middleware boundaries remain valid.
- Cache invalidation inputs remain complete for security-relevant config/package shifts.
- No path where stale prebuild cache bypasses required security setup.

### E) Operational Guardrails
- No destructive behavior targeting current container/session.
- No broad cleanup logic without exclusion safeguards.

### F) Architecture Boundaries
- Domain layer remains pure (no direct infrastructure dependencies).
- Dependencies flow inward toward domain (no domain imports from API/CLI layers).
- Infrastructure adapters implement domain-defined trait ports.
- No business logic in HTTP handlers, CLI commands, or adapter implementations.

## Verification Commands (Scope-Aware)

Run minimal needed:
- `cargo fmt --all -- --check`
- `cargo clippy --all-targets -- -D warnings`
- `cargo test` (targeted where possible)

For broad risk changes, run `make ci`.

## Output Format

### Verdict
- `verdict`: `APPROVE` | `REQUEST_CHANGES`
- `gate_status`: `PASS` | `FAIL`
- `blocking_reasons`: concise bullets

### Critical Findings
Include high-signal issues only:
- severity, category (Security | Reliability | Architecture | Contract), path, line, issue, impact, fix, confidence

### Threat Checklist Results
- check, status (`pass|fail|n/a`), evidence

### Verification Matrix
- command, result, notes
- not-run checks + reason

### Residual Risk
- explicit unknowns

## Severity

- `CRITICAL`: exploitable security/destructive runtime risk
- `HIGH`: likely production/session failure or major security contract break
- `MEDIUM`: meaningful non-blocking risk
- `LOW/INFO`: optional (generally omit unless valuable)

## Final Instruction

Be strict, evidence-driven, and Maestro-runtime-aware.
Prefer fewer high-confidence findings over broad generic feedback.