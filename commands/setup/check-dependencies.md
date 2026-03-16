---
allowed-tools: Read, Bash
argument-hint: [--update] | [--audit]
description: Validate and check Rust project dependencies, Cargo.lock, and outdated crates
---

# Check Dependencies

Validate Rust project dependencies and check for updates: **$ARGUMENTS**

## Current Dependency State

Check current Cargo configuration and lockfile status.

!`pwd`
!`ls -1 Cargo.toml Cargo.lock 2>/dev/null || echo "No Cargo files found"`

## Task

Validate Rust project dependencies, check Cargo.lock status, and optionally identify outdated or vulnerable crates.

**Check Mode**: Use `--update` to check for outdated dependencies or `--audit` for security vulnerabilities.

**Validation Framework**:

1. **Cargo Detection** - Verify Cargo.toml exists and is valid
2. **Lockfile Validation** - Verify Cargo.lock exists and is synchronized
3. **Dependency Installation** - Check if dependencies are built (target/ directory)
4. **Outdated Crates** - Optionally identify crates with newer versions available
5. **Security Audit** - Optionally check for known vulnerabilities in dependencies

**Cargo Dependency Checks**:

```bash
# Check if Cargo.toml exists
if [ ! -f "Cargo.toml" ]; then
  echo "ERROR: No Cargo.toml found (not a Rust project)"
  exit 1
fi

# Verify Cargo.toml is valid
cargo metadata --no-deps > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "Cargo.toml is valid"
else
  echo "ERROR: Cargo.toml has syntax errors"
  cargo metadata --no-deps 2>&1 | head -10
  exit 1
fi

# Check for Cargo.lock
if [ -f "Cargo.lock" ]; then
  echo "Cargo.lock found"
else
  echo "WARNING: No Cargo.lock (run 'cargo build' to generate)"
fi

# Check if dependencies are built
if [ -d "target" ]; then
  echo "Build directory exists"
else
  echo "INFO: No target/ directory (dependencies not built)"
fi
```

**Workspace Detection**:

```bash
# Detect if project is a workspace
if grep -q "\[workspace\]" Cargo.toml; then
  echo "Project type: Cargo workspace"

  # Count workspace members
  MEMBER_COUNT=$(cargo metadata --no-deps --format-version 1 | grep -o '"name"' | wc -l)
  echo "Workspace has $MEMBER_COUNT member crates"
else
  echo "Project type: Single-crate project"
fi
```

**Dependency Tree Analysis**:

```bash
# View dependency tree
cargo tree

# View dependencies for specific crate (in workspace)
cargo tree -p crate-name

# Show duplicate dependencies
cargo tree --duplicates

# Show dependencies with specific features
cargo tree --features feature1,feature2
```

**Checking for Outdated Dependencies** (`--update`):

```bash
# Install cargo-outdated if not available
cargo install cargo-outdated

# Check for outdated dependencies
cargo outdated

# Check for outdated dependencies in workspace
cargo outdated --workspace

# Show only root dependencies (not transitive)
cargo outdated --root-deps-only

# Show outdated dependencies with compatible updates only
cargo outdated --compatible
```

Example output:
```
Name      Project  Compat  Latest  Kind         Platform
----      -------  ------  ------  ----         --------
tokio     1.38.0   1.48.0  1.48.0  Normal       ---
serde     1.0.197  1.0.215 1.0.215 Normal       ---
```

**Security Audit** (`--audit`):

```bash
# Install cargo-audit if not available
cargo install cargo-audit

# Run security audit
cargo audit

# Audit with fix suggestions
cargo audit fix --dry-run

# Audit specific advisory database
cargo audit --db ~/.cargo/advisory-db
```

Example output:
```
    Fetching advisory database from `https://github.com/RustSec/advisory-db.git`
      Loaded 500 security advisories (from ~/.cargo/advisory-db)
    Scanning Cargo.lock for vulnerabilities (125 crate dependencies)

Crate:     tokio
Version:   1.35.0
Warning:   vulnerability
Title:     Tokio has a data race vulnerability
Date:      2024-01-09
ID:        RUSTSEC-2024-0001
URL:       https://rustsec.org/advisories/RUSTSEC-2024-0001
Solution:  Upgrade to >=1.36.0
```

**Dependency Synchronization**:

```bash
# Check if Cargo.lock is in sync with Cargo.toml
cargo check --locked

# If out of sync, update Cargo.lock
cargo update

# Update specific dependency
cargo update -p tokio

# Update to latest compatible version (respecting Cargo.toml constraints)
cargo update

# Update breaking versions (requires editing Cargo.toml)
# Edit Cargo.toml, then:
cargo update
```

**Workspace Dependency Checks**:

For Cargo workspaces, check all member crates:

```bash
# Check all workspace members
cargo check --workspace --locked

# Update dependencies for entire workspace
cargo update --workspace

# Check for outdated dependencies across workspace
cargo outdated --workspace

# Audit all workspace members
cargo audit
```

**Dependency Analysis Commands**:

```bash
# View full dependency metadata
cargo metadata --format-version 1

# Count total dependencies
cargo tree --all | grep -v '├' | grep -v '│' | grep -v '└' | wc -l

# Find why a specific crate is included
cargo tree --invert -p crate-name

# Check license compatibility
cargo tree --format "{l}: {p}"

# Find dependencies by feature
cargo tree --edges features
```

**Common Dependency Issues**:

### Issue 1: Duplicate Dependencies

```bash
# Find duplicate versions of same crate
cargo tree --duplicates

# Example output:
# serde v1.0.197
# └── used by crate-a
# serde v1.0.203
# └── used by crate-b
```

**Solution**: Use `[workspace.dependencies]` to unify versions.

### Issue 2: Lockfile Out of Sync

```bash
# Error: Cargo.lock out of sync
cargo check --locked
# error: the lock file needs to be updated

# Fix by updating lockfile
cargo update
```

### Issue 3: Security Vulnerabilities

```bash
# Find and fix vulnerabilities
cargo audit
cargo update  # Update to patched versions
```

**Dependency Management Best Practices**:

```toml
# Cargo.toml - Use precise version requirements
[dependencies]
# Good: Caret requirement (allows patch and minor updates)
tokio = "1.48"       # Means ^1.48.0 (>=1.48.0, <2.0.0)

# Explicit: Exact version
serde = "=1.0.215"   # Only 1.0.215

# Range: Version range
anyhow = ">=1.0, <2.0"

# Tilde: Minimal version update
tracing = "~0.1.40"  # >=0.1.40, <0.2.0
```

**Workspace Dependency Unification**:

```toml
# Workspace Cargo.toml
[workspace.dependencies]
tokio = { version = "1.48", features = ["full"] }

# Member crate uses workspace version
[dependencies]
tokio = { workspace = true }
```

**CI/CD Dependency Checks**:

```yaml
# .github/workflows/ci.yml
jobs:
  check-deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2

      - name: Check Cargo.lock is up to date
        run: cargo check --locked

      - name: Audit dependencies
        run: |
          cargo install cargo-audit
          cargo audit

      - name: Check for outdated dependencies
        run: |
          cargo install cargo-outdated
          cargo outdated --workspace --exit-code 1
        continue-on-error: true
```

**Validation Checklist**:

- [ ] Cargo.toml exists and is valid
- [ ] Cargo.lock exists (for applications)
- [ ] Cargo.lock is synchronized with Cargo.toml
- [ ] Dependencies build successfully (`cargo check`)
- [ ] No security vulnerabilities (`cargo audit`)
- [ ] Dependencies are up to date (`cargo outdated`)
- [ ] No duplicate dependencies (`cargo tree --duplicates`)
- [ ] Workspace dependencies are unified (if workspace)

**Dependency Update Workflow**:

```bash
# 1. Check current state
cargo outdated

# 2. Update Cargo.lock (patch/minor versions)
cargo update

# 3. Test that everything still works
cargo test

# 4. For breaking updates, edit Cargo.toml manually
# Update version in Cargo.toml:
# tokio = "1.48" -> tokio = "1.50"

# 5. Update and test
cargo update
cargo test

# 6. Commit changes
git add Cargo.toml Cargo.lock
git commit -m "chore: update dependencies"
```

**Output**: Structured report with dependency status, Cargo.lock synchronization, outdated crates list, security vulnerabilities, and recommendations for updates or fixes.

**Quick Check Commands**:

```bash
# One-liner: full dependency validation
cargo check --locked && cargo audit && cargo outdated

# Check if dependencies are synchronized
cargo update --dry-run

# Verify no duplicate dependencies
cargo tree --duplicates
```

**Troubleshooting**:

1. **Cargo.lock conflicts**: `git checkout --theirs Cargo.lock && cargo update`
2. **Out of sync**: `cargo update` to regenerate Cargo.lock
3. **Vulnerabilities**: `cargo audit fix --dry-run` to see suggested fixes
4. **Outdated dependencies**: `cargo outdated --workspace` to identify updates
5. **Duplicate dependencies**: Use `cargo tree --duplicates` and consolidate versions in workspace
