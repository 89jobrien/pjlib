---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [--nightly] | [--workspace]
description: Configure comprehensive code formatting with rustfmt for consistent Rust code style
---

# Setup Code Formatting

Configure comprehensive Rust code formatting with rustfmt: **$ARGUMENTS**

## Current Project State

- Rust files detected: !`find . -name "*.rs" | head -10`
- Existing rustfmt config: @rustfmt.toml or @.rustfmt.toml
- Cargo workspace: @Cargo.toml with [workspace] section
- Rustfmt version: !`rustfmt --version 2>/dev/null || echo "rustfmt not installed"`
- IDE config: @.vscode/settings.json or @.editorconfig

## Task

Setup comprehensive Rust code formatting system with rustfmt and automated enforcement:

**Configuration Mode**: Use `--nightly` for nightly-only features or `--workspace` for workspace-wide formatting

**Rustfmt Installation**:

```bash
# Install rustfmt component
rustup component add rustfmt

# For nightly features (optional)
rustup toolchain install nightly
rustup component add rustfmt --toolchain nightly
```

**Rustfmt Configuration**:

1. **Configuration File** - Create `rustfmt.toml` with style rules, line length, edition settings
2. **Edition Settings** - Configure Rust edition (2021, 2024) for proper formatting
3. **IDE Integration** - Configure editor for format-on-save with rust-analyzer
4. **CI/CD Checks** - Add rustfmt verification to GitHub Actions
5. **Team Synchronization** - Shared configuration for consistent team formatting
6. **Nightly Features** - Optional advanced formatting features with nightly toolchain

**Rustfmt Configuration Example**:

```toml
# rustfmt.toml
edition = "2024"
max_width = 100
hard_tabs = false
tab_spaces = 4

# Imports
imports_granularity = "Crate"
group_imports = "StdExternalCrate"

# Formatting style
use_small_heuristics = "Default"
fn_single_line = false
where_single_line = false

# Comments and documentation
normalize_comments = true
wrap_comments = true
comment_width = 100

# Nightly-only features (requires nightly toolchain)
# unstable_features = true
# format_code_in_doc_comments = true
# format_strings = true
# imports_granularity = "Module"
```

**Maestro Project Configuration** (from actual production project):

```toml
# rustfmt.toml - based on maestro project patterns
edition = "2024"
max_width = 100
use_small_heuristics = "Default"
```

**CI/CD Integration**:

```yaml
# .github/workflows/ci.yml
jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt

      - name: Check formatting
        run: cargo fmt --all -- --check

      # For nightly features
      # - uses: dtolnay/rust-toolchain@nightly
      #   with:
      #     components: rustfmt
      # - name: Check formatting (nightly)
      #   run: cargo +nightly fmt --all -- --check
```

**IDE Integration**:

Configure rust-analyzer in `.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "rust-lang.rust-analyzer",
  "rust-analyzer.rustfmt.extraArgs": ["+nightly"],
  "[rust]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "rust-lang.rust-analyzer"
  }
}
```

**Pre-commit Hook**:

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Ensure code is formatted before commit
cargo fmt --all -- --check
if [ $? -ne 0 ]; then
  echo "Code formatting check failed. Run 'cargo fmt' to fix."
  exit 1
fi
```

**Common Formatting Commands**:

```bash
# Format all files in workspace
cargo fmt --all

# Check formatting without modifying files
cargo fmt --all -- --check

# Format specific package in workspace
cargo fmt -p package-name

# Format with nightly features
cargo +nightly fmt --all

# Format and show which files changed
cargo fmt --all -- --check -v
```

**Workspace Configuration**:

For Cargo workspaces, place `rustfmt.toml` in the workspace root. All member crates inherit the configuration:

```
workspace/
├── rustfmt.toml          # Workspace-wide configuration
├── Cargo.toml            # Workspace manifest
├── crate-a/
│   ├── Cargo.toml
│   └── src/
└── crate-b/
    ├── Cargo.toml
    └── src/
```

**Edition-Specific Features**:

Rust 2024 edition formatting improvements:
- Better formatting for `gen` blocks
- Improved macro formatting
- Enhanced match arm alignment

**Advanced Configuration Options**:

```toml
# Control function signatures
fn_args_layout = "Tall"
brace_style = "SameLineWhere"

# Control match expressions
match_block_trailing_comma = true
match_arm_blocks = true

# Control arrays and structs
array_width = 60
struct_lit_width = 18
```

**Team Consistency**:

- Commit `rustfmt.toml` to version control
- Document any non-default settings in CONTRIBUTING.md
- Enforce formatting in CI with `--check` flag
- Use EditorConfig for cross-editor consistency:

```ini
# .editorconfig
[*.rs]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
```

**Troubleshooting**:

- If rustfmt not found: `rustup component add rustfmt`
- For nightly features: `rustup component add rustfmt --toolchain nightly`
- Verify configuration: `rustfmt --print-config default rustfmt.toml`
- IDE not formatting: Check rust-analyzer extension is installed and enabled

**Output**: Complete rustfmt formatting system with automated enforcement, team configurations, CI/CD integration, and style compliance monitoring for consistent Rust code formatting.
