---
name: component-auditor
description: Audit Claude Code agents, skills, commands, and hooks for quality, completeness, and adherence to templates and best practices. Use this skill when reviewing workspace components, ensuring quality standards, preparing for deployment, or investigating component issues. Trigger for phrases like "audit components", "check agents", "review skills", "validate commands", or proactively before major releases or when onboarding new components.
allowed-tools: [Read, Grep, Glob, Bash]
---

# Component Auditor

You are an expert at auditing Claude Code components (agents, skills, commands, hooks) for quality, completeness, and adherence to best practices.

## When to Use This Skill

Use this skill whenever:

- Adding new agents, skills, or commands to the workspace
- Before deploying workspace changes to production
- Investigating why a component isn't working as expected
- Ensuring consistency across all components
- The user mentions "audit", "review", "check quality", or "validate"
- Quarterly quality reviews or workspace cleanup

## Component Types

**Agents** (`~/.claude/agents/**/*.md`)

- Specialized subagents with specific capabilities
- Frontmatter: name, description, tools, model, etc.

**Skills** (`~/.claude/skills/*/SKILL.md`)

- Reusable workflows and procedures
- Frontmatter: name, description
- Optional: references/, scripts/, resources/

**Commands** (`~/.claude/commands/**/*.md`)

- User-invocable slash commands
- Frontmatter: description, allowed-tools, argument-hint

**Hooks** (`~/.claude/settings.json`)

- Automated workflows triggered by events
- JSON configuration with event matchers

## Core Workflow

### Step 1: Inventory Components

Scan the workspace:

```bash
# Count components
echo "=== Component Inventory ==="

AGENTS=$(find ~/.claude/agents -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "Agents: $AGENTS"

SKILLS=$(find ~/.claude/skills -name "SKILL.md" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "Skills: $SKILLS"

COMMANDS=$(find ~/.claude/commands -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "Commands: $COMMANDS"

if [ -f ~/.claude/settings.json ]; then
    echo "Hooks: configured"
else
    echo "Hooks: not configured"
fi

echo ""
echo "Total components: $((AGENTS + SKILLS + COMMANDS))"
```

### Step 2: Audit Agents

For each agent file:

```bash
# Find all agent files
find ~/.claude/agents -name "*.md" -type f | while read agent; do
    echo "=== Auditing: $agent ==="

    # Check frontmatter presence
    if ! head -1 "$agent" | grep -q "^---$"; then
        echo "ERROR: Missing frontmatter"
        continue
    fi

    # Extract frontmatter
    FRONTMATTER=$(awk '/^---$/,/^---$/' "$agent" | sed '1d;$d')

    # Check required fields
    echo "$FRONTMATTER" | grep -q "^name:" || echo "WARN: Missing 'name' field"
    echo "$FRONTMATTER" | grep -q "^description:" || echo "ERROR: Missing 'description' field"
    echo "$FRONTMATTER" | grep -q "^tools:" || echo "ERROR: Missing 'tools' field"

    # Check description quality
    DESC=$(echo "$FRONTMATTER" | grep "^description:" | cut -d: -f2- | sed 's/^ *//')
    DESC_LEN=${#DESC}

    if [ $DESC_LEN -lt 50 ]; then
        echo "WARN: Description too short ($DESC_LEN chars, recommend 50-300)"
    elif [ $DESC_LEN -gt 300 ]; then
        echo "WARN: Description too long ($DESC_LEN chars, recommend 50-300)"
    fi

    # Check for PROACTIVELY in description
    if echo "$DESC" | grep -qi "proactively\|use this"; then
        echo "PASS: Description includes usage guidance"
    else
        echo "WARN: Description should start with 'Use PROACTIVELY' or 'Use this'"
    fi

    # Check body structure
    BODY=$(sed '1,/^---$/d' "$agent" | tail -n +2)

    echo "$BODY" | grep -q "^## " || echo "WARN: No sections (should have ##)"
    echo "$BODY" | grep -qi "instructions\|workflow\|process" || echo "WARN: Missing Instructions section"
    echo "$BODY" | grep -q "{{" && echo "ERROR: Contains placeholder text {{}}"

    echo ""
done
```

**Agent Checklist:**

- [ ] Has valid frontmatter with `---` delimiters
- [ ] Has `name` field
- [ ] Has `description` field (50-300 chars)
- [ ] Has `tools` field (array of tool names)
- [ ] Description starts with usage guidance
- [ ] Has workflow/instructions section
- [ ] No placeholder text (`{{...}}`)
- [ ] Model field is valid (haiku, sonnet, opus) if present

### Step 3: Audit Skills

For each skill directory:

```bash
# Find all skills
find ~/.claude/skills -type d -mindepth 1 -maxdepth 1 | while read skill_dir; do
    echo "=== Auditing: $(basename "$skill_dir") ==="

    # Check for SKILL.md
    if [ ! -f "$skill_dir/SKILL.md" ]; then
        echo "ERROR: Missing SKILL.md file"
        continue
    fi

    SKILL_FILE="$skill_dir/SKILL.md"

    # Check frontmatter
    if ! head -1 "$SKILL_FILE" | grep -q "^---$"; then
        echo "ERROR: Missing frontmatter"
        continue
    fi

    # Extract frontmatter
    FRONTMATTER=$(awk '/^---$/,/^---$/' "$SKILL_FILE" | sed '1d;$d')

    # Check required fields
    echo "$FRONTMATTER" | grep -q "^name:" || echo "ERROR: Missing 'name' field"
    echo "$FRONTMATTER" | grep -q "^description:" || echo "ERROR: Missing 'description' field"

    # Verify name matches directory
    SKILL_NAME=$(echo "$FRONTMATTER" | grep "^name:" | cut -d: -f2- | sed 's/^ *//')
    DIR_NAME=$(basename "$skill_dir")

    if [ "$SKILL_NAME" != "$DIR_NAME" ]; then
        echo "WARN: Name mismatch (frontmatter: $SKILL_NAME, dir: $DIR_NAME)"
    fi

    # Check description style (should be third-person)
    DESC=$(echo "$FRONTMATTER" | grep "^description:" | cut -d: -f2-)
    if echo "$DESC" | grep -qi "^You are\|^I am"; then
        echo "WARN: Description should be third-person, not 'You are' or 'I am'"
    fi

    # Check file size (should be < 5000 words for main file)
    WORD_COUNT=$(wc -w < "$SKILL_FILE" | tr -d ' ')
    if [ "$WORD_COUNT" -gt 5000 ]; then
        echo "WARN: SKILL.md is large ($WORD_COUNT words, recommend <5000)"
        echo "      Consider moving content to references/"
    fi

    # Check for "When to Use" section
    grep -q "## When to Use" "$SKILL_FILE" || echo "WARN: Missing 'When to Use' section"

    # Check for workflow/process
    grep -qi "## .*workflow\|## .*process\|## .*steps" "$SKILL_FILE" || \
        echo "WARN: Missing workflow/process section"

    # Check for examples
    grep -qi "## .*example" "$SKILL_FILE" || echo "WARN: Missing examples section"

    # Check for placeholder text
    grep -q "{{" "$SKILL_FILE" && echo "ERROR: Contains placeholder text {{}}"

    # Check for bundled resources
    if [ -d "$skill_dir/references" ]; then
        echo "INFO: Has references/ directory"
    fi

    if [ -d "$skill_dir/scripts" ]; then
        echo "INFO: Has scripts/ directory"

        # Check script permissions
        find "$skill_dir/scripts" -type f -name "*.sh" -o -name "*.bash" | while read script; do
            if [ ! -x "$script" ]; then
                echo "WARN: Script not executable: $(basename "$script")"
            fi
        done
    fi

    echo ""
done
```

**Skill Checklist:**

- [ ] Has SKILL.md file
- [ ] Has valid frontmatter
- [ ] Has `name` field matching directory name
- [ ] Has `description` field (third-person)
- [ ] Has "When to Use" section
- [ ] Has workflow/process section
- [ ] Has examples section
- [ ] Under 5000 words (or uses references/)
- [ ] No placeholder text
- [ ] Scripts are executable if present

### Step 4: Audit Commands

For each command file:

```bash
# Find all commands
find ~/.claude/commands -name "*.md" -type f | while read cmd; do
    echo "=== Auditing: $cmd ==="

    # Check frontmatter
    if ! head -1 "$cmd" | grep -q "^---$"; then
        echo "ERROR: Missing frontmatter"
        continue
    fi

    # Extract frontmatter
    FRONTMATTER=$(awk '/^---$/,/^---$/' "$cmd" | sed '1d;$d')

    # Check required fields
    echo "$FRONTMATTER" | grep -q "^description:" || echo "ERROR: Missing 'description' field"

    # Check description length
    DESC=$(echo "$FRONTMATTER" | grep "^description:" | cut -d: -f2- | sed 's/^ *//')
    DESC_LEN=${#DESC}

    if [ $DESC_LEN -gt 100 ]; then
        echo "WARN: Description too long ($DESC_LEN chars, recommend <100)"
    fi

    # Check for task description
    BODY=$(sed '1,/^---$/d' "$cmd" | tail -n +2)
    echo "$BODY" | grep -q "^# " || echo "WARN: Missing title (# heading)"

    # Check for $ARGUMENTS usage if argument-hint present
    if echo "$FRONTMATTER" | grep -q "^argument-hint:"; then
        if ! echo "$BODY" | grep -q '\$ARGUMENTS'; then
            echo "WARN: Has argument-hint but doesn't use \$ARGUMENTS"
        fi
    fi

    # Check for dynamic context (! syntax)
    if echo "$BODY" | grep -q '!\`'; then
        echo "INFO: Uses dynamic context (! syntax)"
    fi

    # Check for placeholder text
    echo "$BODY" | grep -q "{{" && echo "ERROR: Contains placeholder text {{}}"

    echo ""
done
```

**Command Checklist:**

- [ ] Has valid frontmatter
- [ ] Has `description` field (<100 chars)
- [ ] Has clear title
- [ ] Uses `$ARGUMENTS` if takes arguments
- [ ] Has actionable workflow
- [ ] No placeholder text
- [ ] Dynamic context uses `!` syntax correctly

### Step 5: Audit Hooks

Check hooks configuration:

```bash
# Check settings.json
if [ ! -f ~/.claude/settings.json ]; then
    echo "WARN: No settings.json found"
    exit 0
fi

echo "=== Auditing Hooks ==="

# Validate JSON
if ! jq empty ~/.claude/settings.json 2>/dev/null; then
    echo "ERROR: Invalid JSON in settings.json"
    exit 1
fi

# Check for hooks
HOOKS=$(jq -r '.hooks // {} | keys[]' ~/.claude/settings.json 2>/dev/null)

if [ -z "$HOOKS" ]; then
    echo "INFO: No hooks configured"
else
    echo "Configured hooks:"
    echo "$HOOKS" | while read hook; do
        echo "  - $hook"

        # Check hook structure
        EVENT=$(jq -r ".hooks.\"$hook\".event // \"\"" ~/.claude/settings.json)
        COMMAND=$(jq -r ".hooks.\"$hook\".command // \"\"" ~/.claude/settings.json)

        if [ -z "$EVENT" ]; then
            echo "    ERROR: Missing 'event' field"
        fi

        if [ -z "$COMMAND" ]; then
            echo "    ERROR: Missing 'command' field"
        fi

        # Validate event type
        case "$EVENT" in
            UserPromptSubmit|PreToolUse|PostToolUse|SessionStart)
                echo "    PASS: Valid event type ($EVENT)"
                ;;
            *)
                echo "    WARN: Unknown event type ($EVENT)"
                ;;
        esac

        # Check command is executable
        CMD_FIRST=$(echo "$COMMAND" | awk '{print $1}')
        if ! command -v "$CMD_FIRST" >/dev/null 2>&1; then
            echo "    WARN: Command not found in PATH: $CMD_FIRST"
        fi
    done
fi

echo ""
```

**Hooks Checklist:**

- [ ] settings.json is valid JSON
- [ ] Each hook has `event` field
- [ ] Each hook has `command` field
- [ ] Event types are valid
- [ ] Commands are executable
- [ ] Matchers are specific (not too broad)

### Step 6: Generate Report

Create comprehensive audit report:

```bash
#!/bin/bash
# audit_report.sh - Generate full audit report

REPORT_FILE="component-audit-$(date +%Y%m%d).md"

cat > "$REPORT_FILE" <<EOF
# Claude Code Component Audit Report

Generated: $(date +"%Y-%m-%d %H:%M:%S")

## Summary

| Component | Total | Pass | Warn | Fail |
|-----------|-------|------|------|------|
| Agents    | $AGENT_TOTAL | $AGENT_PASS | $AGENT_WARN | $AGENT_FAIL |
| Skills    | $SKILL_TOTAL | $SKILL_PASS | $SKILL_WARN | $SKILL_FAIL |
| Commands  | $CMD_TOTAL | $CMD_PASS | $CMD_WARN | $CMD_FAIL |
| Hooks     | $HOOK_TOTAL | $HOOK_PASS | $HOOK_WARN | $HOOK_FAIL |

## Agents

$(cat /tmp/agent-audit.log)

## Skills

$(cat /tmp/skill-audit.log)

## Commands

$(cat /tmp/command-audit.log)

## Hooks

$(cat /tmp/hook-audit.log)

## Recommendations

$(generate_recommendations)

## Quick Fixes

To fix common issues:

1. Missing frontmatter: Add YAML frontmatter with --- delimiters
2. Placeholder text: Search for {{ and replace with actual content
3. Non-executable scripts: Run chmod +x on script files
4. Invalid JSON: Use jq to validate and format settings.json

EOF

echo "Report generated: $REPORT_FILE"
```

## Severity Levels

**PASS** - Meets all requirements, no action needed

**WARN** - Works but improvable, review when possible

- Descriptions too short/long
- Missing optional sections
- Style inconsistencies

**ERROR** - Missing requirements, fix before using

- Missing required frontmatter fields
- Invalid JSON syntax
- Placeholder text remains
- Broken file structure

**INFO** - Informational notices

- Uses advanced features
- Has bundled resources
- Configuration notes

## Best Practices

1. **Run audit before commits** - Catch issues early
2. **Fix errors immediately** - Don't commit broken components
3. **Address warnings gradually** - Improve quality over time
4. **Update templates** - Keep templates current with best practices
5. **Document exceptions** - Note when deviations are intentional

## Output Format

Provide structured audit summary:

```markdown
# Component Audit Report

Date: YYYY-MM-DD HH:MM

## Executive Summary

Total components: 87
Status: 73 PASS, 12 WARN, 2 FAIL
Overall health: Good

## Critical Issues (Fix Immediately)

1. agents/broken-agent.md - Missing 'tools' field
2. skills/incomplete-skill/SKILL.md - Contains placeholder text

## Warnings (Review Soon)

1. agents/verbose-agent.md - Description too long (420 chars)
2. skills/large-skill/SKILL.md - Over 5000 words, needs references/
3. commands/setup/long-cmd.md - Missing workflow section

## Recommendations

1. Add frontmatter to 2 agents missing it
2. Move skill content to references/ for 3 large skills
3. Fix JSON formatting in settings.json
4. Make 5 scripts executable (chmod +x)

## Next Steps

1. Fix critical issues this session
2. Address warnings in next sprint
3. Update component templates
4. Schedule monthly audits

## Detailed Results

Saved to: ~/logs/dot-claude/component-audit-YYYYMMDD.log
```

## Remember

The goal is to maintain high-quality, consistent components across the workspace. Regular audits prevent technical debt and ensure components work as expected. Fix critical issues immediately, address warnings gradually, and use audits as learning opportunities to improve component creation skills.
