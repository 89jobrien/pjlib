---
paths: "**/*.py"
---

# Python Rules

## General

- Use Python 3.12 or higher
- Use `uv` for all Python operations
- Never use `pip` directly

## uv-Only Environment

**CRITICAL**: This system has no vanilla Python on PATH. Always use `uv` for all Python operations:

| Instead of | Use |
|------------|-----|
| `python` | `uv run python` |
| `python script.py` | `uv run script.py` |
| `pip install` | `uv add` |
| `pip install -e .` | `uv pip install -e .` |
| `pytest` | `uv run pytest` |
| `ruff` | `uvx ruff` |
| `mypy` | `uvx mypy` |

## Running Scripts

```bash
# Run a Python file
uv run script.py

# Run a module
uv run -m pytest

# Run with specific dependencies
uv run --with requests script.py
```

## Package Management

- Use `uv add <package>` to add dependencies to pyproject.toml
- Use `uv sync` to install from lock file
- Use `uv lock` to update lock file
- Never use `pip` directly

## uv Scripts

Prefer inline script dependencies over project dependencies for one-off scripts:

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pyyaml",
#   "requests",
# ]
# ///
"""Script docstring here."""

import yaml
import requests
```

## Type Hints

**Always use modern type hints:**

```python
# Good
def process(items: list[str]) -> dict[str, int]:
    ...

def get_user(user_id: int) -> User | None:
    ...

# Bad
from typing import List, Dict, Optional

def process(items: List[str]) -> Dict[str, int]:  # Deprecated
    ...

def get_user(user_id: int) -> Optional[User]:  # Use | None instead
    ...
```

**Required:**
- All function signatures must have type hints
- Use `| None` instead of `Optional[T]`
- Use built-in `list`, `dict`, `set`, `tuple` instead of `typing.List`, etc.
- Use `typing.Self` for methods returning instance type
- Use `typing.Protocol` for structural typing

## Code Organization

```python
# Module docstring
"""Brief description of module purpose."""

# Imports grouped: stdlib, third-party, local
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel

from .utils import helper

# Constants
DEFAULT_TIMEOUT = 30

# Classes and functions
class MyClass:
    """Class docstring with purpose and usage."""

    def __init__(self, name: str) -> None:
        self.name = name
```

## Error Handling

**Be explicit about exceptions:**

```python
# Good
def load_config(path: Path) -> dict[str, Any]:
    """Load configuration from file.

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config is invalid YAML
    """
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    return yaml.safe_load(path.read_text())

# Bad - catching everything
try:
    config = load_config(path)
except Exception:  # Too broad
    pass
```

## Logging

**Never use print() for logging:**

```python
# Good
import logging

logger = logging.getLogger(__name__)
logger.info("Processing started")
logger.error("Failed to process: %s", error)

# Bad
print("Processing started")  # No control over output
print(f"Error: {error}")  # Can't disable in production
```

## File Operations

**Always use pathlib:**

```python
# Good
from pathlib import Path

config_path = Path.home() / '.config' / 'app.yaml'
content = config_path.read_text()

# Bad
import os

config_path = os.path.join(os.path.expanduser('~'), '.config', 'app.yaml')
with open(config_path) as f:
    content = f.read()
```

## Data Processing

**Prefer polars over pandas:**

```python
# Good
import polars as pl

df = pl.read_csv("data.csv")
result = df.filter(pl.col("value") > 100)

# Bad
import pandas as pd  # Slower, more memory

df = pd.read_csv("data.csv")
result = df[df["value"] > 100]
```

## Database Operations

**Use SQLModel for ORM:**

```python
from sqlmodel import SQLModel, Field, create_engine

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
```

## Testing

```python
# Test file: test_module.py
import pytest
from pathlib import Path

def test_load_config():
    """Test configuration loading."""
    path = Path("fixtures/config.yaml")
    config = load_config(path)

    assert config["version"] == "1.0"
    assert "database" in config

def test_missing_config():
    """Test error handling for missing config."""
    with pytest.raises(FileNotFoundError):
        load_config(Path("nonexistent.yaml"))
```

## Async Operations

```python
import asyncio

async def fetch_data(url: str) -> dict[str, Any]:
    """Fetch data asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Run async code
asyncio.run(fetch_data("https://api.example.com"))
```

## Common Patterns

**Context managers for resources:**

```python
from contextlib import contextmanager

@contextmanager
def temp_directory():
    """Create and cleanup temporary directory."""
    path = Path(tempfile.mkdtemp())
    try:
        yield path
    finally:
        shutil.rmtree(path)

with temp_directory() as tmpdir:
    # Use tmpdir
    pass
```

**Dataclasses for data structures:**

```python
from dataclasses import dataclass

@dataclass
class Config:
    host: str
    port: int
    debug: bool = False
```

## Never Do

- Use `print()` for logging
- Use `pandas` when `polars` works
- Use `typing.Optional` instead of `| None`
- Use old-style string formatting (`%s` or `.format()`)
- Catch bare `Exception` without re-raising
- Use mutable default arguments (`def func(items=[]):`)
- Import `*` from modules
