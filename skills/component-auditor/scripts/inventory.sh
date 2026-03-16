#!/bin/bash
# inventory.sh - Component inventory count

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
