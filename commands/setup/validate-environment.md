---
allowed-tools: Read, Bash
argument-hint: [--strict]
description: Validate development environment tools, versions, and environment variables
---

# Validate Environment

Validate development environment with comprehensive checks: **$ARGUMENTS**

## Current Environment State

Check current system state before validation.

!`uname -s`
!`echo "Working directory: $(pwd)"`

## Task

Run comprehensive environment validation to ensure all required tools and configurations are in place.

**Validation Mode**: Use `--strict` flag to enforce version requirements and fail on warnings.

**Validation Framework**:

1. **Tool Detection** - Check for required development tools (git, node, python, docker, etc.)
2. **Version Validation** - Verify tool versions meet minimum requirements
3. **Environment Variables** - Confirm required environment variables are set
4. **PATH Configuration** - Validate critical tools are accessible via PATH

**Implementation**:

Run the environment validator workflow:

```bash
echo '{"task": "validate", "cwd": ".", "required_tools": ["git", "node:>=18.0.0", "python3:>=3.12"], "required_env_vars": ["HOME", "PATH"]}' | uv run ~/.claude/hooks/workflows/setup.py
```

**Validation Checks**:

- Git installation and version
- Node.js/npm (if JavaScript/TypeScript project)
- Python 3.12+ (if Python project)
- Docker (if containerized project)
- Project-specific tools based on detected project type

**Output**: Structured validation report with pass/fail status for each check, including version information and recommendations for missing tools.

**Configuration**: Customize required tools and environment variables in `~/.claude/hooks/hooks_config.yaml` under the `setup.env_validation` section.
