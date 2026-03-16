---
paths: "**/*.toml"
---

# TOML Rules

## Formatting

**Basic syntax:**

```toml
# Comments start with #
key = "value"
number = 42
boolean = true
array = ["item1", "item2", "item3"]

# Sections
[section]
nested_key = "value"

# Subsections
[section.subsection]
deep_key = "value"

# Table arrays
[[items]]
name = "first"
value = 1

[[items]]
name = "second"
value = 2
```

## pyproject.toml

**Python project configuration (managed by uv):**

```toml
[project]
name = "myapp"
version = "0.1.0"
description = "Application description"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "pyyaml>=6.0",
    "requests>=2.31.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.3.0",
    "mypy>=1.9",
]

[project.scripts]
myapp = "myapp.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
]

# Tool configurations
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.mypy]
strict = true
python_version = "3.12"
```

## Managing Dependencies

**Use uv commands, don't edit manually:**

```bash
# Add dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Add with version constraint
uv add "package>=1.0,<2.0"

# Remove dependency
uv remove package-name

# Update dependencies
uv lock
```

## Tool Configuration

### Ruff (Python linter/formatter)

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
exclude = [
    ".git",
    "__pycache__",
    "build",
    "dist",
]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "W",   # pycodestyle warnings
]
ignore = ["E501"]  # Line too long

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Pytest

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--strict-markers",
    "--cov=src",
]
```

### MyPy

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
exclude = [
    "build/",
    "dist/",
]
```

## Cargo.toml (Rust)

**Rust project configuration:**

```toml
[package]
name = "myapp"
version = "0.1.0"
edition = "2021"
authors = ["Author <email@example.com>"]

[dependencies]
tokio = { version = "1.36", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }

[dev-dependencies]
proptest = "1.4"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1

[[bin]]
name = "myapp"
path = "src/main.rs"
```

## Data Types

```toml
# Strings
string = "basic string"
literal = 'literal string'
multiline = """
This is a
multiline string
"""

# Numbers
integer = 42
float = 3.14
hex = 0xDEADBEEF
octal = 0o755

# Booleans
enabled = true
disabled = false

# Dates
date = 2024-03-15
datetime = 2024-03-15T10:30:00Z

# Arrays
numbers = [1, 2, 3]
strings = ["a", "b", "c"]
mixed_not_allowed = [1, "two"]  # Invalid!

# Inline tables
point = { x = 1, y = 2 }

# Tables
[server]
host = "localhost"
port = 8080

# Array of tables
[[servers]]
name = "prod"
host = "prod.example.com"

[[servers]]
name = "staging"
host = "staging.example.com"
```

## Best Practices

### DO

- Use `uv add` for Python dependencies
- Group related configuration in sections
- Use meaningful section names
- Add comments for non-obvious settings
- Keep configuration flat when possible

### DON'T

- Manually edit `[project.dependencies]` (use `uv add`)
- Mix types in arrays
- Over-nest sections
- Hardcode secrets
- Use tabs (spaces only)

## Common Files

- `pyproject.toml` - Python project config (uv)
- `Cargo.toml` - Rust project config
- `.taplo.toml` - TOML formatter config

## Validation

**Check TOML syntax:**

```bash
# Python
uv run python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# Using taplo
brew install taplo
taplo check pyproject.toml
taplo format pyproject.toml
```

## Section Organization

**Recommended order for pyproject.toml:**

```toml
# 1. Project metadata
[project]
# ...

# 2. Build system
[build-system]
# ...

# 3. Tool configurations (alphabetical)
[tool.mypy]
# ...

[tool.pytest.ini_options]
# ...

[tool.ruff]
# ...

[tool.uv]
# ...
```
