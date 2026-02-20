---
allowed-tools: Read, Write, Bash
argument-hint: [--type=framework]
description: Scaffold new project with framework-specific initialization and boilerplate
---

# Scaffold Project

Initialize new project with framework-specific scaffolding: **$ARGUMENTS**

## Current Directory State

Check if directory is suitable for project initialization.

!`pwd`
!`ls -A | wc -l | xargs echo "Files in directory:"`

## Task

Scaffold new project using framework-specific initialization commands and create boilerplate files.

**Framework Selection**: Use `--type=<framework>` to specify project type (nextjs, fastapi, django, flask, rust, go, python).

**Scaffolding Framework**:

1. **Project Type Detection** - Auto-detect or use specified framework
2. **Tool Validation** - Ensure required tools are installed (npx, cargo, go, uv, etc.)
3. **Directory Check** - Verify directory is empty or suitable for initialization
4. **Framework Initialization** - Run framework-specific scaffold command
5. **Boilerplate Creation** - Create additional framework-specific files

**Supported Frameworks**:

- **nextjs**: Next.js application with App Router (requires npx)
- **fastapi**: FastAPI Python project with uv (requires uv)
- **django**: Django web application (requires django-admin)
- **flask**: Flask web application (requires uv)
- **rust**: Rust project with Cargo (requires cargo)
- **go**: Go module (requires go)
- **python**: Generic Python project with uv (requires uv)

**Implementation**:

Run the project scaffolder workflow:

```bash
PROJECT_TYPE=$(echo "$ARGUMENTS" | sed 's/--type=//' | sed 's/=.*//')
echo "{\"task\": \"scaffold\", \"cwd\": \".\", \"type\": \"$PROJECT_TYPE\", \"auto_install\": false}" | uv run ~/.claude/hooks/workflows/setup.py
```

**Scaffold Commands**:

- **Next.js**: `npx create-next-app@latest . --use-npm`
- **FastAPI**: `uv init --lib` + create main.py with FastAPI app
- **Django**: `django-admin startproject myproject .`
- **Flask**: `uv init` + create app.py with Flask app
- **Rust**: `cargo init`
- **Go**: `go mod init example.com/myproject`
- **Python**: `uv init`

**Post-Scaffolding**:

- Review generated project structure
- Install dependencies: npm install, uv sync, cargo build, etc.
- Initialize git repository if not already done
- Update configuration files as needed
- Set up environment variables

**Warning**: This command may fail if the directory is not empty. Clean the directory or choose a new location for scaffolding.

**Configuration**: Customize scaffolding behavior in `~/.claude/hooks/hooks_config.yaml` under the `setup.project_scaffold` section.
