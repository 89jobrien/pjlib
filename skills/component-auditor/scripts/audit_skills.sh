#!/bin/bash
# audit_skills.sh - Audit skill directories

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
