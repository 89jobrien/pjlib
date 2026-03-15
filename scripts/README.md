# Skills Development Toolkit

Developer experience improvements for managing Claude Code skills.

## Tools

### 1. Skill Validation (`validate-skills.py`)

Validates SKILL.md frontmatter for correctness and consistency.

**Usage:**

```bash
~/.claude/scripts/validate-skills.py ~/.claude/skills
```

**Checks:**

- Required frontmatter fields (name, description)
- Valid tool references
- Valid skill cross-references
- Naming conventions (lowercase, hyphens)
- Description quality

**Exit codes:**

- `0` - All valid (warnings OK)
- `1` - Errors found

### 2. Skill Quality Linter (`lint-skills.py`)

Comprehensive quality checks beyond basic validation.

**Usage:**

```bash
~/.claude/scripts/lint-skills.py ~/.claude/skills
```

**Checks:**

- Content structure (required sections)
- Code block formatting
- Broken links
- Script quality (shebangs, permissions, docs)
- Best practices compliance
- Reference documentation quality

**Output levels:**

- **Errors** - Must fix
- **Warnings** - Should fix
- **Info** - Suggestions for improvement

### 3. Skills Catalog Generator (`generate-skills-catalog.py`)

Generates comprehensive documentation from skill frontmatter.

**Usage:**

```bash
~/.claude/scripts/generate-skills-catalog.py ~/.claude/skills ~/.claude/SKILLS_CATALOG.md
```

**Generates:**

- Alphabetical index
- Category grouping
- Tool usage matrix
- Skill dependency graph
- Statistics

### 4. Skill Template Generator (`create-skill.py`)

Interactive wizard for creating new skills with proper structure.

**Usage:**

```bash
~/.claude/scripts/create-skill.py
```

**Creates:**

- SKILL.md with proper frontmatter
- Directory structure (scripts/, references/)
- Standard sections (When to Use, Examples, etc.)

**Also available as:**

```bash
/meta:new-skill
```

### 5. Git Hooks

Pre-commit hook that validates SKILL.md files before committing.

**Install:**

```bash
~/.claude/scripts/install-skill-hooks.sh
```

**Behavior:**

- Validates staged SKILL.md files
- Blocks commits with errors
- Allows commits with warnings
- Skip with `git commit --no-verify`

## Workflow

### Creating a New Skill

1. Generate template:

   ```bash
   ~/.claude/scripts/create-skill.py
   # or
   /meta:new-skill
   ```

2. Edit SKILL.md and add resources

3. Validate:

   ```bash
   ~/.claude/scripts/validate-skills.py ~/.claude/skills
   ```

4. Lint for quality:

   ```bash
   ~/.claude/scripts/lint-skills.py ~/.claude/skills
   ```

5. Commit (validation runs automatically via hook)

### Maintaining Skills

1. Run validation periodically:

   ```bash
   ~/.claude/scripts/validate-skills.py ~/.claude/skills
   ```

2. Check quality:

   ```bash
   ~/.claude/scripts/lint-skills.py ~/.claude/skills
   ```

3. Update catalog:

   ```bash
   ~/.claude/scripts/generate-skills-catalog.py ~/.claude/skills
   ```

### Pre-commit Workflow

When you commit changes to SKILL.md files, the pre-commit hook automatically:

1. Extracts staged SKILL.md files
2. Runs validation
3. Blocks commit if errors found
4. Allows commit with warnings

## All Scripts at a Glance

| Script                      | Purpose                       | Input         | Output        |
| --------------------------- | ----------------------------- | ------------- | ------------- |
| `validate-skills.py`        | Frontmatter validation        | skills dir    | pass/fail     |
| `lint-skills.py`            | Quality checks                | skills dir    | issues list   |
| `generate-skills-catalog.py`| Generate documentation        | skills dir    | markdown file |
| `create-skill.py`           | New skill wizard              | interactive   | skill dir     |
| `install-skill-hooks.sh`    | Setup git hooks               | none          | hook installed|

## Tips

### Quick Validation

Check all skills at once:

```bash
cd ~/.claude
scripts/validate-skills.py skills/ && scripts/lint-skills.py skills/
```

### Regenerate Catalog

After making changes:

```bash
cd ~/.claude
scripts/generate-skills-catalog.py skills/
```

### Fix Common Issues

**Missing frontmatter:**

```yaml
---
name: my-skill
description: Clear description with use cases and triggers
allowed-tools: [Read, Write, Bash]
---
```

**Missing sections:**

Add these to SKILL.md:

- `## When to Use`
- `## What This Skill Does`
- `## How to Use`
- `## Examples`

**Unlabeled code blocks:**

Use language identifiers:

````markdown
```bash
echo "hello"
```
````

## Dependencies

All scripts use `uv` for dependency management:

- `pyyaml` - YAML parsing

Scripts automatically install dependencies on first run.

## Integration

### With Claude Code

Skills are automatically discovered from:

- `~/.claude/skills/` - User skills
- `<project>/.claude/skills/` - Project skills
- Plugin skills

### With Git

Pre-commit hook validates staged SKILL.md files automatically.

### With CI/CD

Add to your CI pipeline:

```yaml
- name: Validate skills
  run: |
    ~/.claude/scripts/validate-skills.py ~/.claude/skills
    ~/.claude/scripts/lint-skills.py ~/.claude/skills
```

## Troubleshooting

### Hook not running

```bash
# Check hook is installed
ls -la .git/hooks/pre-commit

# Reinstall
~/.claude/scripts/install-skill-hooks.sh
```

### Validation errors

```bash
# See detailed errors
~/.claude/scripts/validate-skills.py ~/.claude/skills

# Fix and retry
git commit
```

### Bypass hook (not recommended)

```bash
git commit --no-verify
```

## Best Practices

1. **Always validate** before committing
2. **Run linter** periodically to catch quality issues
3. **Update catalog** after significant changes
4. **Use template generator** for consistency
5. **Review warnings** even if not blocking
