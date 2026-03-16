#!/usr/bin/env bash
# validate-skill.sh - Validate DevLoop skill structure
#
# Usage:
#   ./validate-skill.sh
#
# Checks:
#   - Required files exist
#   - Scripts are executable
#   - Markdown files are valid
#   - File permissions are correct

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASS=0
FAIL=0

check_pass() {
  echo -e "${GREEN}✓${NC} $1"
  ((PASS++))
}

check_fail() {
  echo -e "${RED}✗${NC} $1"
  ((FAIL++))
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}DevLoop Skill Validation${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "${BLUE}Skill directory: ${NC}$SKILL_DIR"
echo ""

# Check required files
echo -e "${BLUE}Checking required files...${NC}"

required_files=(
  "SKILL.md"
  "README.md"
  "INDEX.md"
  "resources/architecture-patterns.md"
  "resources/baml-quick-reference.md"
  "scripts/analyze-branch.sh"
  "scripts/check-health.sh"
  "scripts/validate-skill.sh"
)

for file in "${required_files[@]}"; do
  if [[ -f "$SKILL_DIR/$file" ]]; then
    check_pass "Found: $file"
  else
    check_fail "Missing: $file"
  fi
done

echo ""

# Check script executability
echo -e "${BLUE}Checking script permissions...${NC}"

scripts=(
  "scripts/analyze-branch.sh"
  "scripts/check-health.sh"
  "scripts/validate-skill.sh"
)

for script in "${scripts[@]}"; do
  if [[ -x "$SKILL_DIR/$script" ]]; then
    check_pass "Executable: $script"
  else
    check_fail "Not executable: $script (run: chmod +x $SKILL_DIR/$script)"
  fi
done

echo ""

# Check markdown structure
echo -e "${BLUE}Checking SKILL.md structure...${NC}"

if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
  # Check for required sections
  required_sections=(
    "# DevLoop Development Observability Skill"
    "## Overview"
    "## When to Use This Skill"
    "## Prerequisites"
    "## Core Capabilities"
    "## Workflow Examples"
    "## Tips and Best Practices"
    "## Troubleshooting"
    "## Resources"
  )

  for section in "${required_sections[@]}"; do
    if grep -q "^$section" "$SKILL_DIR/SKILL.md"; then
      check_pass "Section found: ${section#\# }"
    else
      check_fail "Section missing: ${section#\# }"
    fi
  done
else
  check_fail "SKILL.md not found"
fi

echo ""

# Check file sizes (detect empty files)
echo -e "${BLUE}Checking file sizes...${NC}"

for file in "${required_files[@]}"; do
  if [[ -f "$SKILL_DIR/$file" ]]; then
    size=$(wc -c < "$SKILL_DIR/$file" | tr -d ' ')
    if [[ $size -gt 100 ]]; then
      check_pass "Non-empty: $file ($size bytes)"
    else
      check_fail "Too small: $file ($size bytes)"
    fi
  fi
done

echo ""

# Check for shell script syntax
echo -e "${BLUE}Checking shell script syntax...${NC}"

for script in "${scripts[@]}"; do
  if [[ -f "$SKILL_DIR/$script" ]]; then
    if bash -n "$SKILL_DIR/$script" 2>/dev/null; then
      check_pass "Valid syntax: $script"
    else
      check_fail "Syntax error: $script"
    fi
  fi
done

echo ""

# Check for proper shebang
echo -e "${BLUE}Checking script shebangs...${NC}"

for script in "${scripts[@]}"; do
  if [[ -f "$SKILL_DIR/$script" ]]; then
    first_line=$(head -n1 "$SKILL_DIR/$script")
    if [[ "$first_line" =~ ^#!/usr/bin/env\ bash$ ]] || [[ "$first_line" =~ ^#!/bin/bash$ ]]; then
      check_pass "Valid shebang: $script"
    else
      check_fail "Invalid shebang: $script (found: $first_line)"
    fi
  fi
done

echo ""

# Check directory structure
echo -e "${BLUE}Checking directory structure...${NC}"

if [[ -d "$SKILL_DIR/resources" ]]; then
  check_pass "resources/ directory exists"
else
  check_fail "resources/ directory missing"
fi

if [[ -d "$SKILL_DIR/scripts" ]]; then
  check_pass "scripts/ directory exists"
else
  check_fail "scripts/ directory missing"
fi

echo ""

# Summary
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [[ $FAIL -eq 0 ]]; then
  echo -e "${GREEN}✓ Skill validation passed!${NC}"
  echo -e "${GREEN}  The DevLoop skill is properly structured.${NC}"
  exit 0
else
  echo -e "${RED}✗ Skill validation failed.${NC}"
  echo -e "${RED}  Please fix the issues above.${NC}"
  exit 1
fi
