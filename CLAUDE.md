# CLAUDE.md

This file provides guidance to Claude Code when working in this personal workspace configuration directory (`~/.claude`).

## Repository Overview

This is a personal Claude Code workspace containing specialized agents, slash commands, and skills that extend Claude Code's capabilities. This directory is a meta-configuration workspace for managing Claude Code itself.

## File Boundaries

**Safe to edit:**

- `agents/`, `commands/`, `skills/`, `templates/` - Core components
- `settings.json`, `settings.local.json` - Configuration files
- `CLAUDE.md`, `README.md` - Documentation

**Never touch:**

- `projects/`, `file-history/`, `shell-snapshots/` - Auto-generated/managed
- `plugins/` - External marketplace plugins (use plugin commands instead)
- `debug/`, `statsig/`, `ide/` - Internal Claude Code state

## Quick Reference

### Common Commands

**Development:**

- `/dev:review-code [file-path|commit-hash|full]` - Code quality review
- `/dev:review-architecture [scope]` - Architecture review
- `/dev:remove-ai-slop [base-branch]` - Remove AI-generated code bloat
- `/dev:debug-error` - Debug error messages

**Git Operations:**

- `/git:create-pr` - Create branch, commit, and submit PR
- `/git:clean-branches` - Clean up merged and stale branches
- `/git:git-bisect-helper [commits]` - Find regression commits
- `/git:pr-review` - Review pull requests

**Testing:**

- `/test:test [file-path|component|description]` - Write tests using TDD
- `/test:run [options]` - Run tests with framework detection
- `/test:report [options]` - Generate test audit and coverage report

**Memory & Knowledge:**

- `/memory:add` - Add entities/observations to knowledge graph
- `/memory:search` - Search knowledge graph
- `/memory:view` - View knowledge graph

**Utilities:**

- `/util:ultra-think [problem]` - Deep multi-dimensional analysis
- `/analyze-codebase` - Parallel code review, test audit, and architecture analysis
- `/research [query]` - Deep research with parallel agents

### Agent Selection Guide

**For code quality:** `code-reviewer`, `code-linter`, `triage-expert`
**For debugging:** `debugger`, `error-detective`, `performance-profiler`
**For architecture:** `backend-architect`, `cloud-architect`, `database-architect`
**For research:** `academic-researcher`, `technical-researcher`, `research-orchestrator-v2`
**For testing:** `test-engineer`, `test-automator`, `parallel-tdd-expert`

See `README.md` for complete agent index.

## Component Architecture

### Agents (`agents/`)

- **Location:** `agents/` with subdirectories by domain
- **Format:** Markdown files with YAML frontmatter
- **Frontmatter fields:** `name`, `description`, `tools`, `model`, `skills`
- **Invocation:** Via Task tool with `subagent_type` matching agent name
- **Organization:** By domain (development-tools, database, web-tools, etc.)

### Commands (`commands/`)

- **Location:** `commands/` with subdirectories by category
- **Format:** Markdown files with YAML frontmatter
- **Frontmatter fields:** `allowed-tools`, `argument-hint`, `description`
- **Invocation:** Slash syntax `/command-name` or `/category:command-name`
- **Features:** Can embed shell output with `!` syntax, invoke agents via Task tool

### Skills (`skills/`)

- **Location:** `skills/` with subdirectory per skill
- **Required:** `SKILL.md` (main content)
- **Optional:** `references/`, `scripts/`, `examples/`
- **Usage:** Referenced by agents via `skills:` frontmatter field
- **Purpose:** Reusable domain expertise, frameworks, methodologies

## Development Workflow

### Creating New Components

**New Agent:**

1. Use `/meta:create-subagent` command
2. Place in appropriate domain subdirectory
3. Add frontmatter with name, description, tools, model, skills
4. Update `README.md` index

**New Command:**

1. Use `/meta:create-command` command
2. Place in appropriate category subdirectory
3. Add frontmatter with description, allowed-tools, argument-hint
4. Document in this file's Quick Reference section

**New Skill:**

1. Use `/meta:create-skill` command
2. Create subdirectory in `skills/`
3. Add `SKILL.md` with instructions
4. Optionally add `references/`, `scripts/`, `examples/`

### Working with Agents

- Agents are invoked via Task tool: `Task(subagent_type="agent-name", ...)`
- Use specialized agents for domain-specific tasks
- Agents automatically access referenced skills
- Check agent frontmatter for available tools and capabilities

### Working with Commands

- Commands expand to prompts that guide task execution
- Commands can chain: invoke agents, run scripts, execute workflows
- Use argument hints: `/command-name [arg1|arg2|arg3]`
- Commands in subdirectories use namespace: `/category:command-name`

## Rules & Constraints

1. **Component Organization:**
   - Keep agents, commands, and skills in their respective directories
   - Use subdirectories for logical grouping (domain, category)
   - Follow existing naming conventions

2. **YAML Frontmatter:**
   - Always include required fields (name, description for agents/commands)
   - Specify `tools` explicitly for agents
   - Use `skills:` to reference reusable expertise

3. **Documentation:**
   - Update `README.md` when adding new components
   - Keep `CLAUDE.md` updated with new commands/workflows
   - Document agent capabilities in frontmatter descriptions

4. **Version Control:**
   - Commit component changes to git
   - Keep `settings.local.json` out of version control
   - Review changes to shared components

5. **Performance:**
   - Keep agent descriptions concise but specific
   - Avoid redundant skills across agents
   - Use skills for shared knowledge, not duplicate it

## Settings & Configuration

- **`settings.json`**: Project-level settings (hooks, permissions, components) - shareable
- **`settings.local.json`**: Local overrides (permissions, env vars) - not synced
- **`~/.claude.json`**: User-level global settings (MCP servers, preferences)

## Important Files

- **`README.md`**: Comprehensive index of all agents, commands, and skills
- **`CLAUDE.md`**: This file - workspace guidance
- **`mcp.local.md`**: MCP server documentation
- **`history.jsonl`**: Session history (auto-generated)

## Best Practices

1. **Use specialized agents** for domain-specific tasks rather than general agents
2. **Invoke commands** via slash syntax for common workflows
3. **Reference README.md** to find appropriate agents/commands/skills
4. **Keep components organized** in their respective directories with logical subdirectories
5. **Use YAML frontmatter** to define metadata for all components
6. **Make skills modular** and reusable across multiple agents
7. **Update documentation** when adding or modifying components
8. **Test new components** before committing to ensure they work as expected
