---
paths: "**/*.sh"
---

# Shell Script Rules

## Header

```bash
#!/usr/bin/env bash
set -euo pipefail
```

## Style

- Quote all variable expansions: `"$var"` not `$var`
- Use `[[ ]]` for conditionals, not `[ ]`
- Use lowercase for local variables, UPPERCASE for env vars
- Never use emojis in code or documentation unless explicitly requested

## Python Commands

Remember: no vanilla Python on PATH. Use `uv run` for any Python:

```bash
uv run pytest tests/
uv run python -c "print('hello')"
```
