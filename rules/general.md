---
paths: ["**/*.json", "**/*.md", "**/*.sh", "**/*.py", "**/*.yaml", "**/*.yml", "**/*.toml", "**/*.ts", "**/*.tsx"]
---

# General Rules

Applies to all files in this project.

## Environment

- **Projects location**: `~/dev/` - all development projects
- **Primary language**: Rust
- **Python**: No vanilla Python on PATH - always use `uv run`
- **JavaScript/TypeScript**: Use `bun` for all operations
- **Package managers**:
  - Rust: `cargo` with workspace setup
  - Python: `uv` only, never `pip`
  - TypeScript: `bun` only, never `npm`

## Code Style

### Universal Principles

- **No emojis** in code or documentation unless explicitly requested
- **No AI slop**: Remove comments like "TODO: implement", "FIXME: refactor", empty docstrings
- **Delete unused code** completely, don't comment it out
- **Prefer editing** existing files over creating new ones
- **Type safety**: Always use type hints/annotations
- **Explicit is better than implicit**: Clear variable names, explicit error handling

### Documentation

- Every module/file needs a brief docstring explaining purpose
- Functions need docstrings for non-trivial logic
- Include `Raises:` section for documented exceptions
- Use triple-quoted docstrings, not comments

### Error Handling

- Never catch exceptions silently
- Be specific about exception types
- Document raised exceptions in docstrings
- Provide helpful error messages

## Git Workflow

### Commits

- **Atomic commits**: One logical change per commit
- **Conventional commits**: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`
- **Co-authored**: Include `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`
- **Never commit**:
  - Secrets, credentials, API keys
  - `.env` files with real values
  - `*.local.md` files
  - Large binary files
  - `node_modules/`, `__pycache__/`

### Branches

- `main` - production-ready code
- `feature/*` - new features
- `fix/*` - bug fixes
- `chore/*` - maintenance tasks

### Hooks

- Pre-commit hooks validate:
  - Code formatting (prettier, ruff)
  - Linting
  - Type checking
  - SKILL.md frontmatter (if applicable)

## File Patterns

### Special Files

- `*.local.md` - Personal notes, gitignored
- `CLAUDE.md` - Project-specific instructions for Claude
- `TO-DO.md` - Task tracking (markdown format)
- `TO-FIX.md` - Issues and bugs to fix
- `SKILL.md` - Skill definition with YAML frontmatter
- `pyproject.toml` - Python project configuration
- `package.json` - TypeScript/JavaScript project configuration

### Configuration Files

- `.prettierrc` - Code formatting rules
- `.markdownlint.json` - Markdown linting
- `pyproject.toml` - Python tool configuration (ruff, pytest, mypy)
- `tsconfig.json` - TypeScript configuration

### Ignore Patterns

Gitignored by default:
- `*.local.md`
- `*.backup.*`
- `.DS_Store`
- `__pycache__/`
- `node_modules/`
- `.env`
- `.venv/`
- `*.egg-info/`

## Directory Structure

### Python Projects

```
project/
├── pyproject.toml          # uv project config
├── README.md
├── src/
│   └── package/
│       ├── __init__.py
│       ├── core.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_core.py
└── scripts/               # uv scripts with inline deps
    └── tool.py
```

### TypeScript Projects

```
project/
├── package.json           # bun project config
├── tsconfig.json
├── README.md
├── src/
│   ├── index.ts
│   └── utils.ts
└── tests/
    └── index.test.ts
```

## Best Practices

### Code Quality

1. **Run formatters** before committing (automated via hooks)
2. **Type check** all code (`mypy`, `tsc --noEmit`)
3. **Write tests** for non-trivial logic
4. **Document public APIs** with clear docstrings
5. **Handle errors** explicitly and helpfully

### Developer Experience

1. **Use pre-commit hooks** for validation
2. **Include setup instructions** in README
3. **One-command setup** where possible
4. **Fast feedback loops** (quick tests, fast builds)
5. **Clear error messages** for debugging

### Security

1. **Never hardcode** credentials
2. **Use environment variables** for secrets
3. **Validate input** at system boundaries
4. **Keep dependencies** updated
5. **Review dependencies** before adding

## Common Commands

### Python (with uv)

```bash
uv run script.py           # Run Python script
uv add package             # Add dependency
uv sync                    # Install dependencies
uv run pytest              # Run tests
uvx ruff check .           # Lint code
uvx mypy .                 # Type check
```

### TypeScript (with bun)

```bash
bun script.ts              # Run TypeScript directly
bun add package            # Add dependency
bun install                # Install dependencies
bun test                   # Run tests
bunx tsc --noEmit          # Type check
```

### Git

```bash
git status                 # Check status
git add file.py            # Stage specific file
git commit                 # Commit (hooks run automatically)
git push                   # Push to remote
```
