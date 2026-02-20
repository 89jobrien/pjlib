---
allowed-tools: Read, Write, Bash
argument-hint: [--template=type]
description: Initialize workspace with standard directory structure and configuration files
---

# Initialize Workspace

Initialize workspace with template-based structure: **$ARGUMENTS**

## Current Workspace State

Check current directory contents before initialization.

!`pwd`
!`ls -la | head -20`

## Task

Create standard directory structure and configuration files based on project template.

**Template Selection**: Use `--template=<type>` to specify workspace template (basic, python, node, full-stack).

**Initialization Framework**:

1. **Directory Creation** - Standard project directories (src/, tests/, docs/, .claude/)
2. **Configuration Files** - Generate boilerplate configs (pyproject.toml, package.json, .gitignore)
3. **Git Initialization** - Optionally initialize git repository
4. **README Generation** - Create basic README.md with project structure

**Available Templates**:

- **basic**: Minimal structure with .claude/ and docs/
- **python**: Python project with src/, tests/, pyproject.toml, .venv/
- **node**: Node.js project with src/, test/, package.json
- **full-stack**: Combined frontend/ and backend/ structure

**Implementation**:

Run the workspace initializer workflow:

```bash
TEMPLATE="${ARGUMENTS:-basic}"
echo "{\"task\": \"init\", \"cwd\": \".\", \"template\": \"$TEMPLATE\", \"auto_git_init\": true}" | uv run ~/.claude/hooks/workflows/setup.py
```

**Post-Initialization**:

- Review generated directory structure
- Customize configuration files as needed
- Initialize version control if not already done
- Install dependencies for the project type

**Configuration**: Customize default template and options in `~/.claude/hooks/hooks_config.yaml` under the `setup.workspace_init` section.
