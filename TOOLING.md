# Development Tooling Reference

> Complete reference for all development tools. Use this as a quick lookup guide.

## TL;DR - Most Common Commands

```bash
# Create new Rust project
~/.claude/scripts/new-rust-project.sh myapp --workspace
cd ~/dev/myapp

# Daily development
cargo qa                                    # Run all checks
cargo c && cargo t                         # Quick check + test

# Skills management
~/.claude/scripts/validate-skills.py ~/.claude/skills  # Validate
~/.claude/scripts/lint-skills.py ~/.claude/skills      # Quality check

# Python/TypeScript
uv run script.py                           # Run Python
bun script.ts                              # Run TypeScript
```

## Environment at a Glance

| Aspect | Configuration |
|--------|---------------|
| **Primary Language** | Rust |
| **Project Location** | `~/dev/` |
| **Rust** | cargo + custom aliases |
| **Python** | uv ONLY (no pip) |
| **TypeScript** | bun ONLY (no npm/node) |

## Quick Command Reference

### Rust Development

```bash
# Create new project
~/.claude/scripts/new-rust-project.sh myapp --workspace

# Quality checks
cargo qa              # Format + lint + test
cargo c               # Check
cargo lint            # Clippy with -D warnings

# Build & run
cargo b               # Build
cargo br              # Build release
cargo r               # Run
cargo rr              # Run release

# Testing
cargo t               # Test
cargo nt              # Nextest (faster)

# Documentation
cargo doc             # Build and open docs
```

### Python Development

```bash
# Run script with inline deps
uv run script.py

# Add dependency
uv add package

# Run tests
uv run pytest
```

### TypeScript Development

```bash
# Run TypeScript directly
bun script.ts

# Install dependencies
bun install

# Run tests
bun test
```

## Scripts & Tools

### Skills Toolkit (`~/.claude/scripts/`)

**Skill Management:**
- `validate-skills.py` - Validate SKILL.md frontmatter
- `lint-skills.py` - Quality linter for skills
- `generate-skills-catalog.py` - Generate documentation
- `create-skill.py` - Interactive skill wizard

**Usage:**
```bash
# Validate all skills
~/.claude/scripts/validate-skills.py ~/.claude/skills

# Check quality
~/.claude/scripts/lint-skills.py ~/.claude/skills

# Generate catalog
~/.claude/scripts/generate-skills-catalog.py ~/.claude/skills

# Create new skill
~/.claude/scripts/create-skill.py
```

**Git Hooks:**
```bash
# Install pre-commit hook for skill validation
~/.claude/scripts/install-skill-hooks.sh
```

### Project Scaffolding

**Rust Projects:**
```bash
# Create new Rust project with hexagonal architecture
~/.claude/scripts/new-rust-project.sh myapp --workspace

# Simple library
~/.claude/scripts/new-rust-project.sh mylib --lib

# Binary application
~/.claude/scripts/new-rust-project.sh myapp --bin
```

**What gets created:**
- Workspace with core/app/infra crates
- Hexagonal architecture structure
- CI/CD workflow
- CLAUDE.md project instructions
- Git repository with initial commit

## Cargo Configuration

### Aliases (`~/.cargo/config.toml`)

**Quick Commands:**
- `cargo b` - build
- `cargo br` - build --release
- `cargo c` - check
- `cargo ca` - check --all-features
- `cargo t` - test
- `cargo ta` - test --all-features
- `cargo r` - run
- `cargo rr` - run --release

**Quality:**
- `cargo qa` - format + clippy + test (all checks)
- `cargo lint` - clippy with -D warnings
- `cargo fmt-check` - check formatting without fixing

**Testing:**
- `cargo nt` - nextest run (faster)
- `cargo nta` - nextest run --all-features

**Documentation:**
- `cargo doc` - build and open docs
- `cargo doc-all` - docs with all features

**Dependencies:**
- `cargo up` - update dependencies
- `cargo tree` - show dependency tree

**Profiling:**
- `cargo bloat` - analyze binary size
- `cargo timings` - build time analysis

### Build Profiles

**dev** (default):
- Fast compilation
- Debug symbols
- No optimization

**release**:
- Full optimization (opt-level = 3)
- LTO enabled
- Single codegen unit
- Stripped binary

**release-with-debug**:
- Same as release
- With debug symbols for profiling

## Rules & Guidelines

### Code Style Rules (`~/.claude/rules/`)

- `general.md` - Universal principles, git workflow
- `rust.md` - Comprehensive Rust guide with SOLID principles
- `python.md` - Python with uv, type hints, patterns
- `typescript.md` - TypeScript with bun, strict types
- `shell.md` - Bash best practices
- `baml.md` - BAML schema conventions
- `yaml.md`, `json.md`, `toml.md` - Config file standards

### Templates

**Rust Project CLAUDE.md:**
- Location: `~/.claude/templates/rust-project-CLAUDE.md`
- Automatically copied to new projects
- Contains project-specific guidelines

## Memory Files

### Context Preservation (`~/.claude/projects/-Users-joe--claude/memory/`)

- `MEMORY.md` - Core environment setup and preferences
- `rust-patterns.md` - Rust-specific patterns and conventions

These files persist across sessions and inform Claude about your preferences.

## Git Workflow

### Commit Message Format

```bash
<type>: <description>

<body>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `chore:` - Maintenance
- `refactor:` - Code refactoring
- `test:` - Testing

### Pre-commit Hooks

**For skills:**
- Automatically validates SKILL.md frontmatter
- Blocks commits with errors
- Allows commits with warnings

**For Rust projects:**
- Can add custom hooks for formatting and linting

## Development Workflow

### Starting New Rust Project

```bash
# 1. Create project
~/.claude/scripts/new-rust-project.sh myapp --workspace
cd ~/dev/myapp

# 2. Customize CLAUDE.md
vim CLAUDE.md

# 3. Set up environment variables
cp .env.example .env  # if needed

# 4. Verify setup
cargo qa
```

### Daily Development

```bash
# Before starting work
cd ~/dev/myapp
git pull
cargo c

# During development
cargo c              # Check types
cargo t              # Run tests
cargo qa             # Full quality check

# Before commit
cargo qa             # Ensure all checks pass
git add .
git commit           # Hook runs automatically
```

### Code Review

```bash
# Check code quality
cargo lint
cargo t
cargo doc

# Performance check
cargo bloat
cargo timings
```

## IDE Integration

### VS Code

Recommended extensions:
- rust-analyzer
- CodeLLDB
- Even Better TOML
- crates
- Error Lens

Settings managed in `.vscode/settings.json` per project.

### Command Line

```bash
# Rust analyzer (if not using IDE)
rust-analyzer

# Documentation server
cargo doc --open

# Code formatting
cargo fmt

# Linting
cargo clippy
```

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| **Rust build fails** | `cargo clean && cargo build` |
| **Tests fail mysteriously** | `cargo clean && cargo test` |
| **Clippy errors** | `cargo clippy --fix --allow-dirty` |
| **Python command not found** | Use `uv run` instead |
| **"pip: command not found"** | CORRECT - use `uv` instead |
| **"npm: command not found"** | CORRECT - use `bun` instead |
| **Outdated dependencies** | `cargo update` |
| **Git hook failed** | Check `~/.claude/scripts/validate-skills.py` output |

### Detailed Troubleshooting

**Rust Build Issues:**
```bash
# Nuclear option
cargo clean && cargo build

# Check what's outdated
cargo tree | grep duplicate

# Verbose build for details
cargo build -vv
```

**Python Issues:**
```bash
# Verify uv is used
which uv  # Should show path

# Reset environment
rm -rf .venv && uv sync
```

**TypeScript Issues:**
```bash
# Verify bun is used
which bun  # Should show path

# Clean install
rm -rf node_modules && bun install
```

## Performance Tips

### Rust

- Use `cargo check` during development (faster than build)
- Use `cargo nextest` for faster testing
- Use `sccache` for build caching (optional)
- Profile with `cargo flamegraph` (install cargo-flamegraph)

### Compilation Speed

```bash
# Install faster linker
brew install llvm

# Already configured in ~/.cargo/config.toml
# Uses lld linker when available
```

## Resources

### Documentation

- Rust Book: https://doc.rust-lang.org/book/
- Cargo Book: https://doc.rust-lang.org/cargo/
- Rust By Example: https://doc.rust-lang.org/rust-by-example/

### Local Docs

- `~/.claude/rules/rust.md` - Your Rust guidelines
- `~/.claude/scripts/README.md` - Skills toolkit docs
- `cargo doc --open` - Project documentation

## Updating This Setup

### Add New Cargo Alias

Edit `~/.cargo/config.toml`:

```toml
[alias]
my-command = "build --features=special"
```

### Add New Script

1. Create in `~/.claude/scripts/`
2. Make executable: `chmod +x script.sh`
3. Document in this file

### Update Rules

Edit relevant file in `~/.claude/rules/`:

```bash
vim ~/.claude/rules/rust.md
```

## Quick Links

- Skills Catalog: `~/.claude/SKILLS_CATALOG.md`
- Rust Rules: `~/.claude/rules/rust.md`
- Scripts README: `~/.claude/scripts/README.md`
- Memory: `~/.claude/projects/-Users-joe--claude/memory/MEMORY.md`
