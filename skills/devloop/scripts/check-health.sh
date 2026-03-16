#!/usr/bin/env bash
# check-health.sh - DevLoop development environment health check
#
# Usage:
#   ./check-health.sh
#
# Checks:
#   - Rust toolchain
#   - just command runner
#   - DevLoop build status
#   - API keys for BAML
#   - GKG server (optional)
#   - Git repository status

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASS=0
WARN=0
FAIL=0

check_pass() {
  echo -e "${GREEN}✓${NC} $1"
  ((PASS++))
}

check_warn() {
  echo -e "${YELLOW}⚠${NC} $1"
  ((WARN++))
}

check_fail() {
  echo -e "${RED}✗${NC} $1"
  ((FAIL++))
}

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}DevLoop Health Check${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check Rust
echo -e "${BLUE}Checking Rust toolchain...${NC}"
if command -v rustc &> /dev/null; then
  RUST_VERSION=$(rustc --version)
  check_pass "Rust installed: $RUST_VERSION"
else
  check_fail "Rust not found. Install from https://rustup.rs"
fi

# Check Cargo
if command -v cargo &> /dev/null; then
  CARGO_VERSION=$(cargo --version)
  check_pass "Cargo installed: $CARGO_VERSION"
else
  check_fail "Cargo not found"
fi

echo ""

# Check just
echo -e "${BLUE}Checking command runner...${NC}"
if command -v just &> /dev/null; then
  JUST_VERSION=$(just --version)
  check_pass "just installed: $JUST_VERSION"
else
  check_fail "just not found. Install with: cargo install just"
fi

echo ""

# Check DevLoop build
echo -e "${BLUE}Checking DevLoop build...${NC}"
if [[ -d "target/release" ]] || [[ -d "target/debug" ]]; then
  check_pass "DevLoop has been built"

  # Check if binary exists
  if [[ -f "target/release/devloop-cli" ]] || [[ -f "target/debug/devloop-cli" ]]; then
    check_pass "devloop-cli binary found"
  else
    check_warn "devloop-cli binary not found. Run: just build"
  fi
else
  check_warn "No build artifacts found. Run: just build"
fi

echo ""

# Check API keys
echo -e "${BLUE}Checking API keys for BAML...${NC}"
if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  check_pass "OPENAI_API_KEY is set"
elif [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  check_pass "ANTHROPIC_API_KEY is set"
else
  check_fail "No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY"
fi

echo ""

# Check GKG (optional)
echo -e "${BLUE}Checking GKG integration (optional)...${NC}"
if command -v gkg &> /dev/null; then
  GKG_VERSION=$(gkg --version 2>&1 | head -n1 || echo "unknown")
  check_pass "GKG installed: $GKG_VERSION"

  # Check GKG server
  if curl -s http://localhost:27495/health &> /dev/null; then
    check_pass "GKG server is running"
  else
    check_warn "GKG server not running. Start with: gkg server start"
  fi
else
  check_warn "GKG not installed (optional). DevLoop will work without it"
fi

echo ""

# Check Git repository
echo -e "${BLUE}Checking Git repository...${NC}"
if git rev-parse --git-dir &> /dev/null; then
  check_pass "In a Git repository"

  # Check if repo has commits
  if git log -1 &> /dev/null 2>&1; then
    check_pass "Repository has commit history"

    # Count branches
    BRANCH_COUNT=$(git branch -a | wc -l | tr -d ' ')
    check_pass "Found $BRANCH_COUNT branches"
  else
    check_warn "Repository has no commits yet"
  fi
else
  check_fail "Not in a Git repository"
fi

echo ""

# Check Claude directories
echo -e "${BLUE}Checking Claude directories...${NC}"
if [[ -d "$HOME/.claude/projects" ]]; then
  check_pass "Claude projects directory exists"
else
  check_warn "Claude projects directory not found at ~/.claude/projects"
fi

if [[ -d "$HOME/.claude/transcripts" ]]; then
  check_pass "Claude transcripts directory exists"

  # Count transcripts
  TRANSCRIPT_COUNT=$(find "$HOME/.claude/transcripts" -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  check_pass "Found $TRANSCRIPT_COUNT transcript files"
else
  check_warn "Claude transcripts directory not found at ~/.claude/transcripts"
fi

echo ""

# Check BAML
echo -e "${BLUE}Checking BAML setup...${NC}"
if [[ -d "crates/baml/baml_src" ]]; then
  check_pass "BAML source directory exists"

  # Count BAML files
  BAML_FILES=$(find crates/baml/baml_src -name "*.baml" 2>/dev/null | wc -l | tr -d ' ')
  check_pass "Found $BAML_FILES BAML files"
else
  check_fail "BAML source directory not found"
fi

if [[ -d "crates/baml/baml_client" ]]; then
  check_pass "BAML client directory exists"
else
  check_warn "BAML client not generated. Run: cd crates/baml && baml-cli generate"
fi

if command -v baml-cli &> /dev/null; then
  check_pass "baml-cli is installed"
else
  check_warn "baml-cli not found. Install from https://docs.boundaryml.com"
fi

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${YELLOW}Warnings: $WARN${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [[ $FAIL -eq 0 ]]; then
  if [[ $WARN -eq 0 ]]; then
    echo -e "${GREEN}✓ All checks passed! DevLoop is ready.${NC}"
    exit 0
  else
    echo -e "${YELLOW}⚠ Some optional components are missing.${NC}"
    echo -e "${YELLOW}  DevLoop will work, but some features may be limited.${NC}"
    exit 0
  fi
else
  echo -e "${RED}✗ Some critical checks failed.${NC}"
  echo -e "${RED}  Please address the failures above before using DevLoop.${NC}"
  exit 1
fi
