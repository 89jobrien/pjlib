#!/bin/bash
# audit_agents.sh - Audit agent files

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
