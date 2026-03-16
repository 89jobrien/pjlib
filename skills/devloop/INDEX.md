# DevLoop Skill - Quick Navigation Index

Fast lookup for common DevLoop tasks and references.

## Need to...

### Run DevLoop Commands

→ See: `SKILL.md` → Section "1. DevLoop Commands Wrapper"

**Quick commands:**
```bash
just analyze [BRANCH]          # Single analyst
just analyze --council [BRANCH] # Multiple perspectives
just logs [SESSION]            # View transcripts
just export                    # JSON timeline
just run                       # Start TUI
```

**Helper script:**
```bash
./skills/devloop/scripts/analyze-branch.sh --council
```

---

### Understand Analysis Results

→ See: `SKILL.md` → Section "2. Branch Analysis Helper"

**Health score interpretation:**
- 0.8-1.0: Excellent (merge ready)
- 0.6-0.8: Good (minor fixes)
- 0.4-0.6: Fair (address issues)
- 0.0-0.4: Poor (major concerns)

**Council roles:**
1. Strict Critic → Conservative risk
2. Creative Explorer → Innovation
3. General Analyst → Balanced view
4. Security Reviewer → Vulnerabilities
5. Performance Analyst → Optimization

---

### Analyze Development Patterns

→ See: `SKILL.md` → Section "3. Development Observability"

**Data sources:**
- Git activity (commits, branches)
- `~/.claude/projects/` (project config)
- `~/.claude/transcripts/` (AI sessions)

**Insights:**
- Session-to-commit lag
- Branch focus patterns
- Commit batching behavior
- AI reliance metrics

---

### Work on DevLoop Architecture

→ See: `resources/architecture-patterns.md`

**Key patterns:**
1. Domain Model Design → Pattern 1
2. Port Definition (Traits) → Pattern 2
3. Adapter Implementation → Pattern 3
4. Dependency Injection → Pattern 4
5. Adapter Composition → Pattern 5
6. Test Doubles → Pattern 6
7. BAML Integration → Pattern 7
8. Error Handling → Pattern 8
9. Graceful Degradation → Pattern 9
10. Council Pattern → Pattern 10

**Quick architecture lookup:**
```
Primary Adapters (UI)
    ↓ traits
Application Core (domain)
    ↓ traits
Secondary Adapters (infrastructure)
```

---

### Work with BAML Schemas

→ See: `resources/baml-quick-reference.md`

**File locations:**
- Source: `crates/baml/baml_src/*.baml`
- Generated: `crates/baml/baml_client/`

**Common tasks:**
- Regenerate: `cd crates/baml && baml-cli generate`
- Test: `baml-cli test`
- Validate: `baml-cli validate`

**Naming cheat sheet:**
- Classes/Functions/Clients: `PascalCase`
- Fields/Parameters/Tests: `snake_case`
- Always end prompts: `{{ ctx.output_format }}`
- All fields need: `@description`

---

### Add a New Council Analyst

→ See: `resources/baml-quick-reference.md` → Section "Adding a New Analyst"

**Steps:**
1. Create function in `crates/baml/baml_src/analysis.baml`
2. Add test case
3. Regenerate: `baml-cli generate`
4. Update `CouncilAdapter` in `crates/cli/src/adapters/council.rs`
5. Test: `just test`

**Template:**
```baml
function AnalyzeBranch_NewRole(
  branch_name: string
  commits: string
  sessions: string
  commit_count: int
  session_count: int
) -> BranchInsight {
  client CustomGPT5Mini
  prompt #"
    You are a [ROLE] reviewer.
    Focus on: [specific concerns]

    {{ commits }}
    {{ sessions }}

    {{ ctx.output_format }}
  "#
}
```

---

### Create a New Adapter

→ See: `resources/architecture-patterns.md` → Pattern 3

**Steps:**
1. Define port trait (if needed) in `components/src/ports.rs`
2. Create adapter in `cli/src/adapters/your_adapter.rs`
3. Implement trait with `#[async_trait]`
4. Return domain types from `components/src/domain.rs`
5. Handle errors gracefully (return `String` or custom error)
6. Add to `UnifiedAdapter` if appropriate

**Pattern:**
```rust
pub struct YourAdapter { /* fields */ }

#[async_trait]
impl YourPort for YourAdapter {
    async fn method(&self) -> Result<DomainType, String> {
        // Implementation
    }
}
```

---

### Write Tests with Test Doubles

→ See: `resources/architecture-patterns.md` → Pattern 6

**Steps:**
1. Create mock struct implementing trait
2. Inject into `App` or component under test
3. Assert on domain types

**Pattern:**
```rust
pub struct MockProvider {
    data: Vec<DomainType>,
}

#[async_trait]
impl Port for MockProvider {
    async fn get_data(&self) -> Result<Vec<DomainType>, String> {
        Ok(self.data.clone())
    }
}
```

---

### Debug GKG Integration

→ See: `SKILL.md` → Example 4: "Debugging GKG Integration"

**Steps:**
1. Check server: `gkg server status`
2. Reindex: `gkg server stop && gkg index . && gkg server start`
3. Test connectivity: `curl http://localhost:27495/health`
4. Check env: `echo $GKG_SERVER_URL`
5. Enable logging: `RUST_LOG=devloop_cli::adapters::gkg=debug just run`

**Remember:** UnifiedAdapter gracefully degrades if GKG unavailable.

---

### Check Environment Health

→ Use: `./skills/devloop/scripts/check-health.sh`

**Checks:**
- Rust toolchain ✓
- `just` command runner ✓
- DevLoop build status ✓
- API keys (OPENAI_API_KEY or ANTHROPIC_API_KEY) ✓
- GKG server (optional) ⚠
- Git repository ✓
- Claude directories ✓
- BAML setup ✓

---

### Common Workflows

#### Pre-merge Branch Check
```bash
./skills/devloop/scripts/analyze-branch.sh --council feature/my-branch
# Review all council perspectives
# Address issues if health < 0.6
# Re-run analysis
# Merge when green
```

#### Add New BAML Function
```bash
# 1. Edit crates/baml/baml_src/analysis.baml
# 2. Add test
# 3. Generate
cd crates/baml && baml-cli generate
# 4. Test
baml-cli test
# 5. Update Rust code
# 6. Run tests
just test
```

#### Create New Adapter
```bash
# 1. Define port trait (if needed)
# Edit: crates/components/src/ports.rs

# 2. Create adapter
# Edit: crates/cli/src/adapters/my_adapter.rs

# 3. Write tests
# Edit: crates/cli/tests/my_adapter_tests.rs

# 4. Run tests
just test
```

---

## File Locations Quick Reference

| What | Where |
|------|-------|
| Domain models | `crates/components/src/domain.rs` |
| Port traits | `crates/components/src/ports.rs` |
| Adapters | `crates/cli/src/adapters/` |
| BAML source | `crates/baml/baml_src/` |
| BAML generated | `crates/baml/baml_client/` |
| TUI app | `crates/cli/src/app.rs` |
| Main entry | `crates/cli/src/main.rs` |
| Tests | `crates/*/tests/` |
| Commands | `justfile` |
| Project docs | `CLAUDE.md` |
| BAML rules | `~/.claude/rules/baml.md` |
| Test guide | `TESTING_CHECKLIST.md` |

---

## External Links

| Resource | URL |
|----------|-----|
| BAML Docs | https://docs.boundaryml.com/ |
| Ratatui | https://ratatui.rs/ |
| GKG Docs | https://gitlab-org.gitlab.io/rust/knowledge-graph/ |
| Rust Book | https://doc.rust-lang.org/book/ |
| async-trait | https://docs.rs/async-trait/ |

---

## Skill Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill definition (read by Claude Code) |
| `README.md` | Skill overview and structure |
| `INDEX.md` | This file - quick navigation |
| `resources/architecture-patterns.md` | Detailed architecture patterns |
| `resources/baml-quick-reference.md` | BAML development guide |
| `scripts/analyze-branch.sh` | Branch analysis wrapper |
| `scripts/check-health.sh` | Environment health check |

---

## Quick Command Reference

```bash
# Build & Run
just run                    # Build + run TUI (release)
just dev                    # Run TUI (debug)
just build                  # Build only
just clean                  # Clean build artifacts

# Analysis
just analyze [BRANCH]       # Single analyst
just analyze --council      # Council mode

# Logs & Export
just logs [SESSION]         # View session transcripts
just export                 # Export timeline JSON

# Development
just test                   # Run all tests
just test-cli               # CLI tests only
just test-pkg <PKG>         # Specific package
just fmt                    # Format code
just check                  # Quick compile check
just lint                   # Clippy lints

# BAML
cd crates/baml
baml-cli generate          # Regenerate client
baml-cli test              # Run BAML tests
baml-cli validate          # Validate schemas

# GKG
gkg server status          # Check server
gkg server start           # Start server
gkg server stop            # Stop server
gkg index .                # Index project

# Health Check
./skills/devloop/scripts/check-health.sh
```

---

## Need Help?

1. **For DevLoop usage questions**: See `SKILL.md` sections 1-3
2. **For architecture questions**: See `resources/architecture-patterns.md`
3. **For BAML questions**: See `resources/baml-quick-reference.md`
4. **For environment issues**: Run `./skills/devloop/scripts/check-health.sh`
5. **For project context**: See `CLAUDE.md`

---

**Last Updated:** 2026-03-15
**Version:** 1.0.0
