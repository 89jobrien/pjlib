---
allowed-tools: Read, Bash
argument-hint: [--update]
description: Validate and check project dependencies, lockfiles, and outdated packages
---

# Check Dependencies

Validate project dependencies and check for updates: **$ARGUMENTS**

## Current Dependency State

Check current package manager and lockfile status.

!`pwd`
!`ls -1 package*.json poetry.lock Cargo.lock go.sum uv.lock 2>/dev/null || echo "No lockfiles found"`

## Task

Validate project dependencies, check lockfile status, and optionally identify outdated packages.

**Check Mode**: Use `--update` flag to check for outdated dependencies (may be slow).

**Validation Framework**:

1. **Package Manager Detection** - Identify package manager (npm, yarn, pnpm, uv, cargo, go, etc.)
2. **Lockfile Validation** - Verify lockfile exists and is in sync
3. **Installation Status** - Check if dependencies are installed (node_modules/, .venv/, etc.)
4. **Outdated Packages** - Optionally identify packages with newer versions available

**Implementation**:

Run the dependency manager workflow:

```bash
CHECK_OUTDATED=$(echo "$ARGUMENTS" | grep -q "update" && echo "true" || echo "false")
echo "{\"task\": \"deps\", \"cwd\": \".\", \"check_outdated\": $CHECK_OUTDATED}" | uv run ~/.claude/hooks/workflows/setup.py
```

**Dependency Checks**:

- Package manager detection (npm, yarn, pnpm, uv, pip, poetry, cargo, go)
- Lockfile presence (package-lock.json, yarn.lock, uv.lock, Cargo.lock, etc.)
- Installation directory existence (node_modules/, .venv/, target/)
- Outdated dependency detection (if --update flag provided)

**Output**: Structured report with package manager information, lockfile status, installation status, and list of outdated packages.

**Recommendations**:

- Run package manager install command if dependencies not installed
- Update lockfile if out of sync
- Review and update outdated dependencies as needed
- Check for security vulnerabilities in dependencies

**Configuration**: Customize dependency check behavior in `~/.claude/hooks/hooks_config.yaml` under the `setup.dependency_check` section.
