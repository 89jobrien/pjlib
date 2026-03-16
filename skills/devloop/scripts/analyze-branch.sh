#!/usr/bin/env bash
# analyze-branch.sh - Helper script for DevLoop branch analysis
#
# Usage:
#   ./analyze-branch.sh [OPTIONS] [BRANCH]
#
# Options:
#   --council    Use council mode (multiple AI perspectives)
#   --help       Show this help message
#
# Examples:
#   ./analyze-branch.sh                        # Analyze current branch (single analyst)
#   ./analyze-branch.sh --council              # Analyze current branch (council mode)
#   ./analyze-branch.sh feature/auth           # Analyze specific branch
#   ./analyze-branch.sh --council feature/auth # Analyze specific branch with council

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
COUNCIL_MODE=false
BRANCH=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --council)
      COUNCIL_MODE=true
      shift
      ;;
    --help)
      grep "^#" "$0" | sed 's/^# //' | sed 's/^#!//'
      exit 0
      ;;
    *)
      BRANCH="$1"
      shift
      ;;
  esac
done

# Get current branch if not specified
if [[ -z "$BRANCH" ]]; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD)
  echo -e "${BLUE}Analyzing current branch: ${GREEN}$BRANCH${NC}"
else
  echo -e "${BLUE}Analyzing branch: ${GREEN}$BRANCH${NC}"
fi

# Check if DevLoop is built
if ! command -v just &> /dev/null; then
  echo -e "${RED}Error: 'just' command not found${NC}"
  echo "Install with: cargo install just"
  exit 1
fi

# Build command
CMD="just analyze"
if [[ "$COUNCIL_MODE" == true ]]; then
  CMD="$CMD --council"
  echo -e "${YELLOW}Using council mode (multiple perspectives)${NC}"
fi
CMD="$CMD $BRANCH"

# Run analysis
echo -e "${BLUE}Running: ${NC}$CMD"
echo ""
eval "$CMD"

# Interpret results
echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Analysis Complete${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "${YELLOW}Interpreting Results:${NC}"
echo ""
echo -e "${GREEN}Health Score Ranges:${NC}"
echo "  0.8 - 1.0: Excellent (ready to merge)"
echo "  0.6 - 0.8: Good (minor improvements suggested)"
echo "  0.4 - 0.6: Fair (address recommendations)"
echo "  0.0 - 0.4: Poor (significant issues)"
echo ""

if [[ "$COUNCIL_MODE" == true ]]; then
  echo -e "${GREEN}Council Perspectives:${NC}"
  echo "  1. Strict Critic: Conservative risk assessment"
  echo "  2. Creative Explorer: Innovation opportunities"
  echo "  3. General Analyst: Balanced overall view"
  echo "  4. Security Reviewer: Security concerns"
  echo "  5. Performance Analyst: Performance implications"
  echo ""
  echo -e "${YELLOW}Next Steps:${NC}"
  echo "  1. Review all perspectives"
  echo "  2. Check if any analyst flagged serious issues"
  echo "  3. Address high-priority recommendations"
  echo "  4. Re-run analysis after fixes"
  echo "  5. Merge when all scores > 0.6"
else
  echo -e "${YELLOW}Tip:${NC} Use --council for multiple perspectives"
fi
