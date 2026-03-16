---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [--strict] | [--workspace]
description: Configure comprehensive code linting and quality analysis with Clippy for Rust projects
---

# Setup Code Linting

Configure comprehensive Rust code linting and quality analysis: **$ARGUMENTS**

## Current Code Quality State

- Rust files detected: !`find . -name "*.rs" | head -10`
- Existing clippy config: @clippy.toml
- Cargo workspace: @Cargo.toml with [workspace] section
- Installed linters: !`cargo clippy --version 2>/dev/null || echo "clippy not installed"`

## Task

Setup comprehensive Rust linting system with Clippy quality analysis and automated enforcement:

**Configuration Mode**: Use `--strict` for error-level lints or `--workspace` for workspace-wide configuration

**Clippy Configuration**:

1. **Tool Installation** - Install clippy via rustup, configure nightly features if needed
2. **Configuration File** - Create `clippy.toml` with custom rules, disallowed methods, and project-specific constraints
3. **IDE Integration** - Configure rust-analyzer for real-time linting, error highlighting, and quick fixes
4. **CI/CD Integration** - Add clippy checks to GitHub Actions with `-D warnings` flag
5. **Custom Lint Rules** - Define project-specific patterns, architecture constraints, and safety requirements
6. **Workspace Configuration** - Shared clippy.toml for monorepos with per-crate overrides

**Clippy Configuration Example**:

```toml
# clippy.toml
# Disallow unsafe patterns and enforce testability
[[disallowed-methods]]
path = "std::env::set_var"
reason = "Use dependency injection for testability; env::set_var is not thread-safe"

[[disallowed-methods]]
path = "std::thread::sleep"
reason = "Use tokio::time::sleep in async contexts; thread::sleep blocks the executor"

[[disallowed-methods]]
path = "std::env::var"
reason = "Prefer explicit configuration structs over direct env::var calls"

# Enforce explicit error handling
[[disallowed-types]]
path = "std::result::Result<T, Box<dyn std::error::Error>>"
reason = "Use concrete error types (anyhow::Error or custom types) instead of Box<dyn Error>"
```

**CI/CD Integration Example**:

```yaml
# .github/workflows/ci.yml
jobs:
  clippy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy
      - uses: Swatinem/rust-cache@v2

      - name: Run Clippy
        run: cargo clippy --all-targets --all-features --locked -- -D warnings

      - name: Run Clippy (pedantic)
        run: cargo clippy --all-targets --all-features --locked -- -W clippy::pedantic
```

**Common Clippy Lint Groups**:

- `clippy::all` - All lints enabled by default
- `clippy::pedantic` - Stricter lints for code quality
- `clippy::nursery` - Experimental lints (may have false positives)
- `clippy::cargo` - Lints for Cargo.toml issues
- `clippy::restriction` - Lints that restrict language features (use selectively)

**Workspace Configuration**:

For Cargo workspaces, create a root-level `clippy.toml`:

```toml
# Root clippy.toml for workspace
avoid-breaking-exported-api = true
cognitive-complexity-threshold = 15
```

**Advanced Features**:

- **Security Linting**: Enable `clippy::suspicious`, `clippy::unwrap_used`, `clippy::expect_used`
- **Performance Analysis**: Enable `clippy::perf` group for optimization hints
- **Complexity Metrics**: Configure `cognitive-complexity-threshold` and `type-complexity-threshold`
- **Custom Allow Lists**: Use `#[allow(clippy::lint_name)]` for justified exceptions with comments

**IDE Integration**:

Configure rust-analyzer in `.vscode/settings.json`:

```json
{
  "rust-analyzer.check.command": "clippy",
  "rust-analyzer.check.allTargets": true,
  "rust-analyzer.check.extraArgs": ["--all-features", "--", "-D", "warnings"],
  "editor.formatOnSave": true
}
```

**Team Standards**:

- Shared `clippy.toml` in repository root
- Documented exception policy for `#[allow()]` attributes
- CI enforcement with `--locked` flag for reproducible builds
- Pre-commit hooks for local validation

**Output**: Complete Clippy linting system with automated quality gates, workspace configuration, and CI/CD integration for comprehensive Rust code analysis.
