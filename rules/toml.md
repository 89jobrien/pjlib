---
paths: "**/*.toml"
---

# TOML Rules

## pyproject.toml

- Use `uv add` to manage dependencies, don't edit manually
- Keep `[project.scripts]` for CLI entry points
- Configure tools (ruff, pytest) in their respective sections
