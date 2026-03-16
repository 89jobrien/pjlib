---
allowed-tools: Read, Bash
argument-hint: [--strict]
description: Validate Rust development environment tools, versions, and project configuration
---

# Validate Environment

Validate Rust development environment with comprehensive checks: **$ARGUMENTS**

## Current Environment State

Check current system state before validation.

!`uname -s`
!`echo "Working directory: $(pwd)"`

## Task

Run comprehensive environment validation to ensure all required Rust tools and configurations are in place.

**Validation Mode**: Use `--strict` flag to enforce version requirements and fail on warnings.

**Validation Framework**:

1. **Rust Toolchain Detection** - Check for rustc, cargo, rustup installation and versions
2. **Component Verification** - Verify rustfmt, clippy, rust-analyzer, rust-src are installed
3. **Development Tools** - Confirm cargo-nextest, cargo-watch, and other extensions
4. **Project Configuration** - Validate Cargo.toml, rustfmt.toml, clippy.toml
5. **Environment Variables** - Confirm RUST_BACKTRACE and other Rust-specific variables

**Core Rust Toolchain Validation**:

```bash
# Check Rust installation
rustc --version || echo "ERROR: rustc not installed"
cargo --version || echo "ERROR: cargo not installed"
rustup --version || echo "ERROR: rustup not installed"

# Check active toolchain
rustup show

# Verify minimum Rust version (example: 1.75.0+)
rustc --version | grep -E "1\.(7[5-9]|[8-9][0-9]|[1-9][0-9]{2})\." || echo "WARNING: Rust version may be outdated"
```

**Component Validation**:

```bash
# Check installed components
rustup component list --installed

# Verify critical components
rustup component list --installed | grep rustfmt || echo "ERROR: rustfmt not installed"
rustup component list --installed | grep clippy || echo "ERROR: clippy not installed"
rustup component list --installed | grep rust-analyzer || echo "WARNING: rust-analyzer not installed"
rustup component list --installed | grep rust-src || echo "WARNING: rust-src not installed"
```

**Cargo Extension Validation**:

```bash
# Check for cargo-nextest (preferred test runner)
cargo nextest --version 2>/dev/null || echo "WARNING: cargo-nextest not installed"

# Check for cargo-watch (development workflow)
cargo watch --version 2>/dev/null || echo "INFO: cargo-watch not installed"

# Check for cargo-edit (dependency management)
cargo upgrade --version 2>/dev/null || echo "INFO: cargo-edit not installed"

# Check for cargo-llvm-cov (code coverage)
cargo llvm-cov --version 2>/dev/null || echo "INFO: cargo-llvm-cov not installed"

# Check for cargo-audit (security auditing)
cargo audit --version 2>/dev/null || echo "INFO: cargo-audit not installed"
```

**Project Configuration Validation**:

```bash
# Check for Cargo.toml
if [ -f "Cargo.toml" ]; then
  echo "Found Cargo.toml"

  # Detect workspace vs single-crate project
  if grep -q "\[workspace\]" Cargo.toml; then
    echo "Project type: Cargo workspace"

    # Validate workspace members
    grep "members" Cargo.toml || echo "WARNING: Workspace has no members defined"
  else
    echo "Project type: Single-crate project"
  fi

  # Check Rust edition
  grep "edition" Cargo.toml || echo "WARNING: No Rust edition specified in Cargo.toml"

else
  echo "INFO: No Cargo.toml found (not a Rust project directory)"
fi

# Check for rustfmt configuration
if [ -f "rustfmt.toml" ] || [ -f ".rustfmt.toml" ]; then
  echo "Found rustfmt configuration"
else
  echo "INFO: No rustfmt.toml found (using default formatting)"
fi

# Check for clippy configuration
if [ -f "clippy.toml" ] || [ -f ".clippy.toml" ]; then
  echo "Found clippy configuration"
else
  echo "INFO: No clippy.toml found (using default lints)"
fi
```

**Environment Variable Validation**:

```bash
# Check common Rust environment variables
echo "RUST_BACKTRACE: ${RUST_BACKTRACE:-not set}"
echo "CARGO_HOME: ${CARGO_HOME:-not set (default: ~/.cargo)}"
echo "RUSTUP_HOME: ${RUSTUP_HOME:-not set (default: ~/.rustup)}"

# Verify cargo bin directory is in PATH
echo $PATH | grep -q ".cargo/bin" || echo "WARNING: ~/.cargo/bin not in PATH"
```

**Build Validation**:

```bash
# If Cargo.toml exists, validate project builds
if [ -f "Cargo.toml" ]; then
  echo "Running cargo check..."
  cargo check --locked 2>&1 | head -20

  # Check if Cargo.lock exists
  if [ ! -f "Cargo.lock" ]; then
    echo "WARNING: No Cargo.lock found (run 'cargo build' to generate)"
  fi
fi
```

**Strict Mode Validation**:

If `--strict` flag is used, enforce stricter requirements:

```bash
# Strict mode checks
if [[ "$1" == "--strict" ]]; then
  # Fail on missing components
  rustup component list --installed | grep rustfmt || exit 1
  rustup component list --installed | grep clippy || exit 1
  rustup component list --installed | grep rust-analyzer || exit 1

  # Require minimum Rust version (1.75.0+)
  RUST_VERSION=$(rustc --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+")
  REQUIRED_VERSION="1.75.0"

  if ! printf '%s\n' "$REQUIRED_VERSION" "$RUST_VERSION" | sort -V -C; then
    echo "ERROR: Rust version $RUST_VERSION is below required $REQUIRED_VERSION"
    exit 1
  fi

  # Require cargo-nextest for testing
  cargo nextest --version || exit 1

  # Require project configuration files
  [ -f "Cargo.toml" ] || { echo "ERROR: No Cargo.toml found"; exit 1; }
fi
```

**Comprehensive Validation Script**:

```bash
#!/bin/bash
# validate-rust-env.sh - Comprehensive Rust environment validation

set -e

STRICT_MODE=false
if [[ "$1" == "--strict" ]]; then
  STRICT_MODE=true
fi

echo "=== Rust Environment Validation ==="
echo

# Toolchain validation
echo "Checking Rust toolchain..."
rustc --version || { echo "ERROR: rustc not found"; exit 1; }
cargo --version || { echo "ERROR: cargo not found"; exit 1; }
rustup --version || { echo "ERROR: rustup not found"; exit 1; }
echo "Active toolchain: $(rustup show active-toolchain)"
echo

# Component validation
echo "Checking components..."
COMPONENTS=$(rustup component list --installed)
echo "$COMPONENTS" | grep rustfmt > /dev/null || echo "WARNING: rustfmt not installed"
echo "$COMPONENTS" | grep clippy > /dev/null || echo "WARNING: clippy not installed"
echo "$COMPONENTS" | grep rust-analyzer > /dev/null || echo "INFO: rust-analyzer not installed"
echo "$COMPONENTS" | grep rust-src > /dev/null || echo "INFO: rust-src not installed"
echo

# Cargo extensions
echo "Checking cargo extensions..."
cargo nextest --version 2>/dev/null || echo "INFO: cargo-nextest not installed"
cargo watch --version 2>/dev/null || echo "INFO: cargo-watch not installed"
cargo audit --version 2>/dev/null || echo "INFO: cargo-audit not installed"
echo

# Project validation
if [ -f "Cargo.toml" ]; then
  echo "Checking project configuration..."

  if grep -q "\[workspace\]" Cargo.toml; then
    echo "Project type: Cargo workspace"
  else
    echo "Project type: Single-crate"
  fi

  EDITION=$(grep "^edition" Cargo.toml | head -1 | grep -oE "[0-9]+")
  echo "Rust edition: ${EDITION:-not specified}"

  # Check if project builds
  echo "Validating project builds..."
  cargo check --locked || { echo "ERROR: Project does not build"; exit 1; }
  echo
fi

echo "=== Validation Complete ==="

if [ "$STRICT_MODE" = true ]; then
  echo "All strict mode checks passed!"
fi
```

**IDE Validation**:

For VS Code users:

```bash
# Check if rust-analyzer extension is configured
if [ -d ".vscode" ]; then
  if [ -f ".vscode/settings.json" ]; then
    echo "Found VS Code settings"
    grep "rust-analyzer" .vscode/settings.json > /dev/null && echo "rust-analyzer configured"
  fi
fi
```

**Validation Checklist**:

- [ ] rustc installed (minimum 1.75.0)
- [ ] cargo installed
- [ ] rustup installed and configured
- [ ] rustfmt component installed
- [ ] clippy component installed
- [ ] rust-analyzer component installed (recommended)
- [ ] rust-src component installed (recommended)
- [ ] cargo-nextest installed (recommended)
- [ ] cargo-watch installed (optional)
- [ ] ~/.cargo/bin in PATH
- [ ] Cargo.toml exists and is valid
- [ ] Project builds successfully (cargo check)
- [ ] Cargo.lock exists (for applications)

**Common Issues and Solutions**:

1. **rustc not found**: Install Rust via rustup: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
2. **Component missing**: Install with `rustup component add <component-name>`
3. **cargo extension missing**: Install with `cargo install <extension-name>`
4. **PATH not configured**: Add `~/.cargo/bin` to PATH in shell config
5. **Old Rust version**: Update with `rustup update stable`
6. **Project won't build**: Check `cargo build` output for missing dependencies or syntax errors

**Output**: Structured validation report with pass/fail status for each check, including version information, component status, and recommendations for missing tools or configuration issues.

**Quick Validation Command**:

```bash
# One-liner for quick validation
rustc --version && cargo --version && rustup component list --installed | grep -E "(rustfmt|clippy)" && echo "Basic Rust environment OK"
```

**Integration with CI/CD**:

Add validation to GitHub Actions:

```yaml
# .github/workflows/ci.yml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy

      - name: Validate environment
        run: |
          rustc --version
          cargo --version
          rustfmt --version
          cargo clippy --version

      - name: Validate project
        run: cargo check --locked
```
