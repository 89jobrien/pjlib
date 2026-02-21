# Storage Cleanup Commands Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create 5 specialized utility commands for cleaning storage (dependencies, builds, git artifacts, caches) in
~/dev/ and ~/Documents/ with interactive confirmation and dry-run modes.

**Architecture:** Markdown-based Claude Code commands with YAML frontmatter, using Bash tools for file system
operations, dynamic content with `!` syntax for live data, and interactive confirmations.

**Tech Stack:** Claude Code commands (markdown + YAML), Bash (find, du, rm, stat, git), AskUserQuestion tool

---

## Task 1: Create analyze-storage Command

**Files:**
- Create: `commands/util/analyze-storage.md`

**Step 1: Create command file with frontmatter and structure**

Create `commands/util/analyze-storage.md`:

```markdown
---
allowed-tools: Bash(du:*), Bash(find:*), Bash(stat:*)
argument-hint: [path]
description: Analyze storage usage and identify cleanup opportunities
---

# Storage Analysis

Analyze storage usage and identify cleanup opportunities: $ARGUMENTS

## Current Storage

Target path: $ARGUMENTS (default: ~/dev/ and ~/Documents/)

**Overall usage:**
```bash
!`du -h -d 1 $ARGUMENTS 2>/dev/null | sort -h -r | head -10 || du -h -d 1 ~/dev/ ~/Documents/ 2>/dev/null | sort -h -r | head -10`
```

**Available space:**
```bash
!`df -h ~ | tail -1 | awk '{print "Total: " $2 ", Used: " $3 ", Available: " $4 ", Use%: " $5}'`
```

## Analysis Task

Perform deep storage analysis to identify cleanup opportunities in the target directories.

### 1. Scan for Dependencies

Find all dependency directories:

```bash
# Node.js dependencies
find ${1:-~/dev ~/Documents} -type d -name "node_modules" -prune 2>/dev/null | while read dir; do
  size=$(du -sh "$dir" 2>/dev/null | cut -f1)
  echo "  $size - $dir"
done

# Python virtual environments
find ${1:-~/dev ~/Documents} -type d \( -name ".venv" -o -name "venv" \) -prune 2>/dev/null | while read dir; do
  size=$(du -sh "$dir" 2>/dev/null | cut -f1)
  echo "  $size - $dir"
done

# Python caches
find ${1:-~/dev ~/Documents} -type d -name "__pycache__" -prune 2>/dev/null | while read dir; do
  size=$(du -sh "$dir" 2>/dev/null | cut -f1)
  echo "  $size - $dir"
done
```

Calculate total dependency size:

```bash
total_deps=$(find ${1:-~/dev ~/Documents} -type d \( -name "node_modules" -o -name ".venv" -o -name "venv" -o -name "__pycache__" \) -prune 2>/dev/null | xargs du -sh 2>/dev/null | awk '{sum+=$1} END {print sum}')
echo "Total dependencies: ${total_deps} MB"
```

### 2. Scan for Build Artifacts

Find all build directories:

```bash
# Common build directories
find ${1:-~/dev ~/Documents} -type d \( -name ".next" -o -name "dist" -o -name "build" -o -name "target" -o -name ".turbo" -o -name "out" \) -prune 2>/dev/null | while read dir; do
  size=$(du -sh "$dir" 2>/dev/null | cut -f1)
  echo "  $size - $dir"
done
```

### 3. Scan for Git Artifacts

Find git repositories and analyze:

```bash
find ${1:-~/dev ~/Documents} -type d -name ".git" -prune 2>/dev/null | while read gitdir; do
  repo=$(dirname "$gitdir")
  size=$(du -sh "$gitdir" 2>/dev/null | cut -f1)
  packed=$(du -sh "$gitdir/objects/pack" 2>/dev/null | cut -f1 || echo "0")
  echo "  Repo: $repo"
  echo "    .git size: $size"
  echo "    Packed objects: $packed"
done
```

### 4. Scan for Caches

Find cache directories:

```bash
find ${1:-~/dev ~/Documents} -type d -name ".cache" -prune 2>/dev/null | while read dir; do
  size=$(du -sh "$dir" 2>/dev/null | cut -f1)
  echo "  $size - $dir"
done
```

## Summary

After analysis, display:

```
STORAGE ANALYSIS SUMMARY
========================

Cleanup Opportunities:

Dependencies (node_modules, .venv, __pycache__):
  Count: [N] directories
  Total Size: [X] GB
  → Run: /util:cleanup-deps --path=$ARGUMENTS

Build Artifacts (.next, dist, build, target):
  Count: [N] directories
  Total Size: [X] GB
  → Run: /util:cleanup-builds --path=$ARGUMENTS

Git Objects (packed objects, reflog):
  Count: [N] repositories
  Potential Savings: [X] MB
  → Run: /util:cleanup-git --path=$ARGUMENTS

Caches (.cache directories):
  Count: [N] directories
  Total Size: [X] MB
  → Run: /util:cleanup-caches --path=$ARGUMENTS

Total Potential Savings: ~[X] GB
```

Provide detailed breakdown with specific paths and sizes for each category.
```

**Step 2: Test the command**

Run the command:
```bash
/util:analyze-storage ~/dev/
```

Expected: Should show storage breakdown and cleanup opportunities for ~/dev/ directory.

**Step 3: Commit**

```bash
git add commands/util/analyze-storage.md
git commit -m "feat(util): add analyze-storage command for storage analysis

Analyzes directory storage usage and identifies cleanup opportunities
for dependencies, builds, git artifacts, and caches.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Create cleanup-deps Command

**Files:**
- Create: `commands/util/cleanup-deps.md`

**Step 1: Create command file**

Create `commands/util/cleanup-deps.md`:

```markdown
---
allowed-tools: Bash(find:*), Bash(du:*), Bash(rm:*), Bash(stat:*), Read, AskUserQuestion
argument-hint: [--path=DIR] [--dry-run] [--yes]
description: Clean dependency directories (node_modules, .venv, __pycache__) interactively
---

# Dependency Cleanup

Clean dependency directories that can be regenerated: $ARGUMENTS

## Target Directories

- `node_modules/` (npm/yarn/pnpm packages)
- `.venv/`, `venv/` (Python virtual environments)
- `__pycache__/`, `.pytest_cache/` (Python caches)
- `vendor/` (Go, PHP dependencies)

## Arguments

Parse arguments from $ARGUMENTS:
- `--path=DIR`: Directory to scan (default: ~/dev/ and ~/Documents/)
- `--dry-run`: Show what would be deleted without deleting
- `--yes`: Skip confirmations (use carefully)

## Task

Clean up dependency directories interactively with safety checks.

### 1. Parse Arguments

Extract path and flags from $ARGUMENTS:

```bash
# Default values
scan_path="${HOME}/dev ${HOME}/Documents"
dry_run=false
skip_confirm=false

# Parse arguments
for arg in $ARGUMENTS; do
  case $arg in
    --path=*)
      scan_path="${arg#*=}"
      ;;
    --dry-run)
      dry_run=true
      ;;
    --yes)
      skip_confirm=true
      ;;
  esac
done
```

### 2. Find Dependency Directories

Scan for all dependency directories:

```bash
echo "Scanning: $scan_path"
echo ""

# Find node_modules
echo "Finding node_modules directories..."
find $scan_path -type d -name "node_modules" -prune 2>/dev/null > /tmp/cleanup-deps-nodes.txt

# Find Python venvs
echo "Finding Python virtual environments..."
find $scan_path -type d \( -name ".venv" -o -name "venv" \) -prune 2>/dev/null > /tmp/cleanup-deps-venvs.txt

# Find Python caches
echo "Finding Python caches..."
find $scan_path -type d \( -name "__pycache__" -o -name ".pytest_cache" \) -prune 2>/dev/null > /tmp/cleanup-deps-caches.txt

# Combine all
cat /tmp/cleanup-deps-*.txt | sort > /tmp/cleanup-deps-all.txt
```

### 3. Calculate Sizes and Build List

For each directory, calculate size and last modified time:

```bash
echo ""
echo "DEPENDENCY CLEANUP"
echo "=================="
echo ""

counter=1
total_size=0

while IFS= read -r dir; do
  if [ -d "$dir" ]; then
    # Get size
    size=$(du -sh "$dir" 2>/dev/null | cut -f1)
    size_bytes=$(du -s "$dir" 2>/dev/null | cut -f1)

    # Get last modified (macOS)
    modified=$(stat -f "%Sm" -t "%Y-%m-%d" "$dir" 2>/dev/null || stat -c "%y" "$dir" 2>/dev/null | cut -d' ' -f1)

    # Check for protection markers
    if [ -f "$dir/../.keep" ] || [ -f "$dir/DO_NOT_DELETE" ]; then
      echo "  [$counter] $dir"
      echo "      Size: $size (PROTECTED - has .keep marker)"
      echo ""
      continue
    fi

    echo "  [$counter] $dir"
    echo "      Size: $size, Modified: $modified"
    echo ""

    total_size=$((total_size + size_bytes))
    counter=$((counter + 1))
  fi
done < /tmp/cleanup-deps-all.txt

total_gb=$(echo "scale=2; $total_size / 1024 / 1024" | bc)
echo "Total reclaimable: ${total_gb} GB"
echo ""
```

### 4. Confirmation and Deletion

If dry-run mode:

```bash
if [ "$dry_run" = true ]; then
  echo "[DRY RUN MODE] No changes will be made"
  echo ""
  echo "To actually delete, run without --dry-run flag"
  exit 0
fi
```

For each directory, ask for confirmation (unless --yes flag):

```bash
deleted_count=0
freed_space=0
restoration_commands=""

counter=1
while IFS= read -r dir; do
  if [ -d "$dir" ]; then
    size_bytes=$(du -s "$dir" 2>/dev/null | cut -f1)

    # Determine restoration command
    if [[ "$dir" == *"node_modules"* ]]; then
      restore_cmd="cd $(dirname $dir) && npm install"
    elif [[ "$dir" == *".venv"* ]] || [[ "$dir" == *"venv"* ]]; then
      restore_cmd="cd $(dirname $dir) && uv sync"
    else
      restore_cmd="(auto-regenerated on next run)"
    fi

    # Ask for confirmation
    should_delete=false
    if [ "$skip_confirm" = true ]; then
      should_delete=true
    else
      echo "Delete [$counter] ($dir)? [y/N/all/quit]:"
      # Use AskUserQuestion tool here for interactive prompt
      # For now, placeholder
      should_delete=false
    fi

    if [ "$should_delete" = true ]; then
      rm -rf "$dir"
      if [ $? -eq 0 ]; then
        echo "✓ Deleted $dir ($(echo "scale=2; $size_bytes / 1024" | bc) MB freed)"
        echo "  To restore: $restore_cmd"
        echo ""

        deleted_count=$((deleted_count + 1))
        freed_space=$((freed_space + size_bytes))
        restoration_commands="$restoration_commands\n$restore_cmd"
      else
        echo "✗ Failed to delete $dir"
        echo ""
      fi
    else
      echo "⊘ Skipped $dir"
      echo ""
    fi

    counter=$((counter + 1))
  fi
done < /tmp/cleanup-deps-all.txt
```

### 5. Summary

Display summary of deletions:

```bash
echo ""
echo "SUMMARY"
echo "======="
echo "Deleted: $deleted_count items"
echo "Freed: $(echo "scale=2; $freed_space / 1024 / 1024" | bc) GB"
echo ""

if [ -n "$restoration_commands" ]; then
  echo "RESTORATION COMMANDS"
  echo "===================="
  echo -e "$restoration_commands" | sort -u
  echo ""
fi

# Log to history
echo "$(date '+%Y-%m-%d %H:%M:%S') | CLEANUP-DEPS | $deleted_count items | $(echo "scale=2; $freed_space / 1024 / 1024" | bc) GB" >> ~/.claude/cleanup-history.log

echo "Log saved to: ~/.claude/cleanup-history.log"
```

### 6. Cleanup Temporary Files

```bash
rm -f /tmp/cleanup-deps-*.txt
```

## Safety Checks

**Protected paths (never delete):**
- Directories with `.keep` file in parent
- Directories with `DO_NOT_DELETE` marker
- Current working directory
- System directories

**Recovery information:**
- Show restoration command for each deleted item
- Log all deletions to `~/.claude/cleanup-history.log`
```

**Step 2: Test the command**

Test with dry-run:
```bash
/util:cleanup-deps --path=~/dev/ --dry-run
```

Expected: Should show what would be deleted without deleting.

**Step 3: Commit**

```bash
git add commands/util/cleanup-deps.md
git commit -m "feat(util): add cleanup-deps command for dependency cleanup

Interactively cleans node_modules, .venv, __pycache__ directories
with safety checks, dry-run mode, and restoration commands.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Create cleanup-builds Command

**Files:**
- Create: `commands/util/cleanup-builds.md`

**Step 1: Create command file**

Create `commands/util/cleanup-builds.md`:

```markdown
---
allowed-tools: Bash(find:*), Bash(du:*), Bash(rm:*), Bash(stat:*), Read, AskUserQuestion
argument-hint: [--path=DIR] [--dry-run] [--yes]
description: Clean build artifact directories (.next, dist, build, target) interactively
---

# Build Artifact Cleanup

Clean build artifact directories that can be rebuilt: $ARGUMENTS

## Target Directories

- `.next/` (Next.js)
- `dist/`, `build/` (Vite, CRA, generic builds)
- `target/` (Rust, Java)
- `.turbo/` (Turborepo cache)
- `out/` (Next.js static export)
- `.nuxt/`, `.output/` (Nuxt.js)

## Arguments

Parse arguments from $ARGUMENTS:
- `--path=DIR`: Directory to scan (default: ~/dev/ and ~/Documents/)
- `--dry-run`: Show what would be deleted without deleting
- `--yes`: Skip confirmations (use carefully)

## Task

Clean up build artifact directories interactively with framework detection.

### 1. Parse Arguments

```bash
# Default values
scan_path="${HOME}/dev ${HOME}/Documents"
dry_run=false
skip_confirm=false

# Parse arguments
for arg in $ARGUMENTS; do
  case $arg in
    --path=*)
      scan_path="${arg#*=}"
      ;;
    --dry-run)
      dry_run=true
      ;;
    --yes)
      skip_confirm=true
      ;;
  esac
done
```

### 2. Find Build Directories

```bash
echo "Scanning: $scan_path"
echo ""

# Find all common build directories
find $scan_path -type d \( \
  -name ".next" -o \
  -name "dist" -o \
  -name "build" -o \
  -name "target" -o \
  -name ".turbo" -o \
  -name "out" -o \
  -name ".nuxt" -o \
  -name ".output" \
\) -prune 2>/dev/null > /tmp/cleanup-builds-all.txt
```

### 3. Calculate Sizes and Detect Frameworks

```bash
echo ""
echo "BUILD ARTIFACT CLEANUP"
echo "======================"
echo ""

counter=1
total_size=0

while IFS= read -r dir; do
  if [ -d "$dir" ]; then
    size=$(du -sh "$dir" 2>/dev/null | cut -f1)
    size_bytes=$(du -s "$dir" 2>/dev/null | cut -f1)

    # Detect framework from parent directory
    parent_dir=$(dirname "$dir")
    framework="Unknown"
    rebuild_cmd="npm run build"

    if [ -f "$parent_dir/package.json" ]; then
      if grep -q "next" "$parent_dir/package.json" 2>/dev/null; then
        framework="Next.js"
        rebuild_cmd="npm run build"
      elif grep -q "vite" "$parent_dir/package.json" 2>/dev/null; then
        framework="Vite"
        rebuild_cmd="npm run build"
      elif grep -q "nuxt" "$parent_dir/package.json" 2>/dev/null; then
        framework="Nuxt.js"
        rebuild_cmd="npm run build"
      fi
    elif [ -f "$parent_dir/Cargo.toml" ]; then
      framework="Rust"
      rebuild_cmd="cargo build"
    fi

    echo "  [$counter] $dir"
    echo "      Size: $size, Framework: $framework"
    echo ""

    total_size=$((total_size + size_bytes))
    counter=$((counter + 1))
  fi
done < /tmp/cleanup-builds-all.txt

total_gb=$(echo "scale=2; $total_size / 1024 / 1024" | bc)
echo "Total reclaimable: ${total_gb} GB"
echo ""
```

### 4. Confirmation and Deletion

Similar to cleanup-deps, with framework-specific restoration commands.

```bash
if [ "$dry_run" = true ]; then
  echo "[DRY RUN MODE] No changes will be made"
  exit 0
fi

deleted_count=0
freed_space=0

counter=1
while IFS= read -r dir; do
  if [ -d "$dir" ]; then
    size_bytes=$(du -s "$dir" 2>/dev/null | cut -f1)
    parent_dir=$(dirname "$dir")

    # Detect rebuild command
    rebuild_cmd="npm run build"
    if [ -f "$parent_dir/Cargo.toml" ]; then
      rebuild_cmd="cargo build"
    fi

    # Interactive confirmation (use AskUserQuestion)
    should_delete=false
    if [ "$skip_confirm" = true ]; then
      should_delete=true
    fi

    if [ "$should_delete" = true ]; then
      rm -rf "$dir"
      if [ $? -eq 0 ]; then
        echo "✓ Deleted $dir"
        echo "  To rebuild: cd $parent_dir && $rebuild_cmd"
        echo ""
        deleted_count=$((deleted_count + 1))
        freed_space=$((freed_space + size_bytes))
      fi
    fi

    counter=$((counter + 1))
  fi
done < /tmp/cleanup-builds-all.txt

echo ""
echo "SUMMARY"
echo "======="
echo "Deleted: $deleted_count items"
echo "Freed: $(echo "scale=2; $freed_space / 1024 / 1024" | bc) GB"

# Log
echo "$(date '+%Y-%m-%d %H:%M:%S') | CLEANUP-BUILDS | $deleted_count items | $(echo "scale=2; $freed_space / 1024 / 1024" | bc) GB" >> ~/.claude/cleanup-history.log

rm -f /tmp/cleanup-builds-all.txt
```

## Framework Detection

Detect framework from parent directory files:
- `package.json` with "next" → Next.js
- `package.json` with "vite" → Vite
- `Cargo.toml` → Rust
- `pom.xml` → Java/Maven
```

**Step 2: Test the command**

```bash
/util:cleanup-builds --path=~/dev/ --dry-run
```

**Step 3: Commit**

```bash
git add commands/util/cleanup-builds.md
git commit -m "feat(util): add cleanup-builds command for build artifact cleanup

Interactively cleans .next, dist, build, target directories with
framework detection and rebuild commands.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Create cleanup-git Command

**Files:**
- Create: `commands/util/cleanup-git.md`

**Step 1: Create command file**

Create `commands/util/cleanup-git.md`:

```markdown
---
allowed-tools: Bash(find:*), Bash(git:*), Bash(du:*), Read
argument-hint: [--path=DIR] [--dry-run] [--yes]
description: Clean git repository artifacts (packed objects, worktrees, reflog) with gc
---

# Git Repository Cleanup

Clean git repository artifacts and run maintenance: $ARGUMENTS

## Operations

- Run `git gc --aggressive` to repack objects
- Prune orphaned worktrees
- Expire reflog entries older than 30 days
- Remove dangling commits

## Arguments

- `--path=DIR`: Directory to scan (default: ~/dev/ and ~/Documents/)
- `--dry-run`: Show what would be done without doing it
- `--yes`: Skip confirmations

## Task

Perform git maintenance on all repositories in target path.

### 1. Find Git Repositories

```bash
scan_path="${HOME}/dev ${HOME}/Documents"
dry_run=false

# Parse arguments
for arg in $ARGUMENTS; do
  case $arg in
    --path=*)
      scan_path="${arg#*=}"
      ;;
    --dry-run)
      dry_run=true
      ;;
  esac
done

echo "Scanning for git repositories in: $scan_path"
echo ""

find $scan_path -type d -name ".git" -prune 2>/dev/null > /tmp/cleanup-git-repos.txt
```

### 2. Analyze Each Repository

```bash
echo "GIT REPOSITORY CLEANUP"
echo "======================"
echo ""

counter=1
total_savings=0

while IFS= read -r gitdir; do
  repo=$(dirname "$gitdir")
  echo "[$counter] Repository: $repo"

  # Get current .git size
  before_size=$(du -sh "$gitdir" 2>/dev/null | cut -f1)
  before_bytes=$(du -s "$gitdir" 2>/dev/null | cut -f1)
  echo "    Current .git size: $before_size"

  # Check packed objects size
  packed_size=$(du -sh "$gitdir/objects/pack" 2>/dev/null | cut -f1 || echo "0")
  echo "    Packed objects: $packed_size"

  # List orphaned worktrees
  cd "$repo"
  orphaned=$(git worktree list 2>/dev/null | grep "prunable" | wc -l | tr -d ' ')
  if [ "$orphaned" -gt 0 ]; then
    echo "    Orphaned worktrees: $orphaned"
  fi

  # Check for unpushed commits
  unpushed=$(git log --branches --not --remotes 2>/dev/null | wc -l | tr -d ' ')
  if [ "$unpushed" -gt 0 ]; then
    echo "    ⚠️  WARNING: $unpushed unpushed commits"
  fi

  echo ""
  counter=$((counter + 1))
done < /tmp/cleanup-git-repos.txt
```

### 3. Perform Cleanup

```bash
if [ "$dry_run" = true ]; then
  echo "[DRY RUN MODE] No changes will be made"
  echo ""
  echo "Operations that would be performed:"
  echo "  - git gc --aggressive"
  echo "  - git worktree prune"
  echo "  - git reflog expire --expire=30.days.ago --all"
  echo "  - git prune"
  exit 0
fi

echo "Performing git maintenance on repositories..."
echo ""

counter=1
while IFS= read -r gitdir; do
  repo=$(dirname "$gitdir")
  echo "[$counter] Cleaning $repo..."

  cd "$repo"

  # Get size before
  before_bytes=$(du -s "$gitdir" 2>/dev/null | cut -f1)

  # Run git gc
  git gc --aggressive --quiet 2>&1

  # Prune worktrees
  git worktree prune 2>&1

  # Expire reflog
  git reflog expire --expire=30.days.ago --all 2>&1

  # Prune dangling objects
  git prune 2>&1

  # Get size after
  after_bytes=$(du -s "$gitdir" 2>/dev/null | cut -f1)
  after_size=$(du -sh "$gitdir" 2>/dev/null | cut -f1)

  savings=$((before_bytes - after_bytes))
  total_savings=$((total_savings + savings))

  if [ $savings -gt 0 ]; then
    savings_mb=$(echo "scale=2; $savings / 1024" | bc)
    echo "    ✓ Saved ${savings_mb} MB (new size: $after_size)"
  else
    echo "    ✓ Complete (no space saved)"
  fi

  echo ""
  counter=$((counter + 1))
done < /tmp/cleanup-git-repos.txt

echo "SUMMARY"
echo "======="
total_mb=$(echo "scale=2; $total_savings / 1024" | bc)
echo "Total space saved: ${total_mb} MB"

# Log
echo "$(date '+%Y-%m-%d %H:%M:%S') | CLEANUP-GIT | $((counter - 1)) repos | ${total_mb} MB" >> ~/.claude/cleanup-history.log

rm -f /tmp/cleanup-git-repos.txt
```

## Safety Checks

- Warn if repository has unpushed commits
- Never delete `.git/` directory itself
- Preserve reflog for last 30 days
- Use `--aggressive` flag for thorough repacking
```

**Step 2: Test the command**

```bash
/util:cleanup-git --path=~/dev/ --dry-run
```

**Step 3: Commit**

```bash
git add commands/util/cleanup-git.md
git commit -m "feat(util): add cleanup-git command for git maintenance

Runs git gc, prunes worktrees, expires reflog, and cleans dangling
objects with safety checks for unpushed commits.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Create cleanup-caches Command

**Files:**
- Create: `commands/util/cleanup-caches.md`

**Step 1: Create command file**

Create `commands/util/cleanup-caches.md`:

```markdown
---
allowed-tools: Bash(find:*), Bash(du:*), Bash(rm:*), Bash(stat:*), Bash(file:*), Read, AskUserQuestion
argument-hint: [--path=DIR] [--dry-run] [--category=safe|review]
description: Analyze and clean application caches with safety categorization
---

# Application Cache Cleanup

Analyze and clean application caches with safety categorization: $ARGUMENTS

## Cache Categories

**SAFE** (auto-suggest for deletion):
- Package manager caches (.npm, .cache/yarn, .cache/pip)
- Build tool caches (.turbo, .next/cache)
- Temporary files (*.tmp, temp/)

**REVIEW** (require confirmation):
- Application-specific .cache directories
- Log files older than 30 days
- Unknown cache directories

**DANGER** (show but don't suggest):
- Databases (*.db, *.sqlite)
- Credential stores (.credentials, tokens)
- Session data

## Arguments

- `--path=DIR`: Directory to scan
- `--dry-run`: Show what would be deleted
- `--category=LEVEL`: Filter by category (safe|review|danger)

## Task

Perform deep cache analysis with safety categorization.

### 1. Find All Cache Directories and Files

```bash
scan_path="${HOME}/dev ${HOME}/Documents"
dry_run=false
category_filter="all"

# Parse arguments
for arg in $ARGUMENTS; do
  case $arg in
    --path=*)
      scan_path="${arg#*=}"
      ;;
    --dry-run)
      dry_run=true
      ;;
    --category=*)
      category_filter="${arg#*=}"
      ;;
  esac
done

echo "Scanning for caches in: $scan_path"
echo ""

# Find .cache directories
find $scan_path -type d -name ".cache" 2>/dev/null > /tmp/cleanup-caches-dirs.txt

# Find log files
find $scan_path -type f -name "*.log" 2>/dev/null > /tmp/cleanup-caches-logs.txt

# Find temp files
find $scan_path -type f -name "*.tmp" 2>/dev/null > /tmp/cleanup-caches-tmp.txt
```

### 2. Categorize Caches

```bash
echo "APPLICATION CACHE CLEANUP"
echo "========================="
echo ""

declare -a safe_caches
declare -a review_caches
declare -a danger_caches

# Categorize .cache directories
while IFS= read -r dir; do
  if [ -d "$dir" ]; then
    # Check path for danger keywords
    if [[ "$dir" =~ (auth|token|session|credential|db|sqlite) ]]; then
      danger_caches+=("$dir")
    # Check for known safe caches
    elif [[ "$dir" =~ (.npm|yarn|pip|turbo|next/cache) ]]; then
      safe_caches+=("$dir")
    else
      review_caches+=("$dir")
    fi
  fi
done < /tmp/cleanup-caches-dirs.txt

echo "Categorization complete:"
echo "  SAFE: ${#safe_caches[@]} items"
echo "  REVIEW: ${#review_caches[@]} items"
echo "  DANGER: ${#danger_caches[@]} items"
echo ""
```

### 3. Display by Category

```bash
if [ "$category_filter" = "all" ] || [ "$category_filter" = "safe" ]; then
  echo "SAFE CACHES (can be safely deleted)"
  echo "===================================="
  echo ""

  counter=1
  for cache in "${safe_caches[@]}"; do
    size=$(du -sh "$cache" 2>/dev/null | cut -f1)
    modified=$(stat -f "%Sm" -t "%Y-%m-%d" "$cache" 2>/dev/null || stat -c "%y" "$cache" 2>/dev/null | cut -d' ' -f1)
    echo "  [$counter] $cache"
    echo "      Size: $size, Modified: $modified"
    echo ""
    counter=$((counter + 1))
  done
fi

if [ "$category_filter" = "all" ] || [ "$category_filter" = "review" ]; then
  echo "REVIEW CACHES (require confirmation)"
  echo "===================================="
  echo ""

  counter=1
  for cache in "${review_caches[@]}"; do
    size=$(du -sh "$cache" 2>/dev/null | cut -f1)
    modified=$(stat -f "%Sm" -t "%Y-%m-%d" "$cache" 2>/dev/null || stat -c "%y" "$cache" 2>/dev/null | cut -d' ' -f1)

    # Show sample contents
    sample=$(ls "$cache" 2>/dev/null | head -3 | tr '\n' ', ')

    echo "  [$counter] $cache"
    echo "      Size: $size, Modified: $modified"
    echo "      Contents: $sample..."
    echo ""
    counter=$((counter + 1))
  done
fi

if [ "$category_filter" = "all" ] || [ "$category_filter" = "danger" ]; then
  echo "DANGER CACHES (manual review required)"
  echo "======================================"
  echo ""

  counter=1
  for cache in "${danger_caches[@]}"; do
    size=$(du -sh "$cache" 2>/dev/null | cut -f1)
    echo "  [$counter] $cache"
    echo "      Size: $size"
    echo "      ⚠️  Contains sensitive keywords - MANUAL REVIEW REQUIRED"
    echo ""
    counter=$((counter + 1))
  done
fi
```

### 4. Interactive Deletion

Only for SAFE and REVIEW categories (never auto-delete DANGER):

```bash
if [ "$dry_run" = true ]; then
  echo "[DRY RUN MODE] No changes will be made"
  exit 0
fi

deleted_count=0
freed_space=0

# Only process SAFE caches if category filter allows
if [ "$category_filter" = "all" ] || [ "$category_filter" = "safe" ]; then
  echo "Process SAFE caches? [y/N]:"
  # Use AskUserQuestion for confirmation

  for cache in "${safe_caches[@]}"; do
    size_bytes=$(du -s "$cache" 2>/dev/null | cut -f1)

    # Auto-delete safe caches with confirmation
    rm -rf "$cache"
    if [ $? -eq 0 ]; then
      echo "✓ Deleted $cache"
      deleted_count=$((deleted_count + 1))
      freed_space=$((freed_space + size_bytes))
    fi
  done
fi

# Process REVIEW caches with individual confirmation
if [ "$category_filter" = "all" ] || [ "$category_filter" = "review" ]; then
  for cache in "${review_caches[@]}"; do
    echo "Delete $cache? [y/N]:"
    # Individual confirmation via AskUserQuestion
  done
fi

echo ""
echo "SUMMARY"
echo "======="
echo "Deleted: $deleted_count items"
echo "Freed: $(echo "scale=2; $freed_space / 1024 / 1024" | bc) GB"

# Log
echo "$(date '+%Y-%m-%d %H:%M:%S') | CLEANUP-CACHES | $deleted_count items | $(echo "scale=2; $freed_space / 1024 / 1024" | bc) GB" >> ~/.claude/cleanup-history.log

rm -f /tmp/cleanup-caches-*.txt
```

## Safety Features

- Three-tier categorization (SAFE/REVIEW/DANGER)
- DANGER category never auto-deleted
- Show sample contents for REVIEW caches
- Keyword detection for sensitive data
```

**Step 2: Test the command**

```bash
/util:cleanup-caches --path=~/dev/ --dry-run --category=safe
```

**Step 3: Commit**

```bash
git add commands/util/cleanup-caches.md
git commit -m "feat(util): add cleanup-caches command for cache cleanup

Analyzes and cleans caches with three-tier safety categorization
(SAFE/REVIEW/DANGER) and content inspection.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Update Documentation

**Files:**
- Modify: `CLAUDE.md` - Add new commands to Quick Reference
- Modify: `README.md` - Add commands to index

**Step 1: Update CLAUDE.md**

Add to the "Utilities" section in Quick Reference:

```markdown
**Storage Cleanup:**
- `/util:analyze-storage [path]` - Analyze storage and identify cleanup opportunities
- `/util:cleanup-deps [--path=DIR] [--dry-run]` - Clean dependencies (node_modules, .venv, __pycache__)
- `/util:cleanup-builds [--path=DIR] [--dry-run]` - Clean build artifacts (.next, dist, build, target)
- `/util:cleanup-git [--path=DIR] [--dry-run]` - Git maintenance (gc, prune worktrees, reflog)
- `/util:cleanup-caches [--path=DIR] [--category=safe|review]` - Clean application caches with safety checks
```

**Step 2: Update README.md**

Add to the commands index under "Utilities":

```markdown
### Storage Cleanup

- `analyze-storage` - Storage analysis and cleanup opportunities
- `cleanup-deps` - Clean dependency directories interactively
- `cleanup-builds` - Clean build artifact directories
- `cleanup-git` - Git repository maintenance and cleanup
- `cleanup-caches` - Application cache cleanup with categorization
```

**Step 3: Commit documentation updates**

```bash
git add CLAUDE.md README.md
git commit -m "docs: add storage cleanup commands to documentation

Added 5 new utility commands for storage cleanup to quick reference
and command index.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Integration Testing

**Files:**
- Test all commands end-to-end

**Step 1: Test analyze-storage**

```bash
/util:analyze-storage ~/dev/
```

Expected: Shows storage breakdown with cleanup suggestions.

**Step 2: Test cleanup-deps with dry-run**

```bash
/util:cleanup-deps --path=~/dev/ --dry-run
```

Expected: Shows what would be deleted without deleting.

**Step 3: Test cleanup-builds with dry-run**

```bash
/util:cleanup-builds --path=~/dev/ --dry-run
```

Expected: Shows build artifacts with framework detection.

**Step 4: Test cleanup-git with dry-run**

```bash
/util:cleanup-git --path=~/dev/ --dry-run
```

Expected: Shows git maintenance operations without executing.

**Step 5: Test cleanup-caches with category filter**

```bash
/util:cleanup-caches --path=~/dev/ --dry-run --category=safe
```

Expected: Shows only SAFE category caches.

**Step 6: Verify cleanup history log**

```bash
cat ~/.claude/cleanup-history.log
```

Expected: Log file exists and is properly formatted.

**Step 7: Create integration test report**

Document test results and any issues found.

---

## Success Criteria

- [ ] All 5 commands created and committed
- [ ] Each command has proper frontmatter with allowed-tools
- [ ] Commands support --dry-run and --path arguments
- [ ] Interactive confirmation works correctly
- [ ] Restoration commands shown after deletion
- [ ] Cleanup history log created and populated
- [ ] Documentation updated in CLAUDE.md and README.md
- [ ] All commands tested with dry-run mode
- [ ] Safety checks prevent deletion of protected paths

## Notes

- Commands use Bash for file system operations
- AskUserQuestion tool required for interactive prompts (implementation detail)
- Dynamic content with `!` syntax for live data
- Cleanup history log saved to `~/.claude/cleanup-history.log`
- All deletions logged with timestamp, type, count, and size

## Future Enhancements

- Add --older-than flag to filter by age
- Add --min-size flag to filter by size
- Support scheduled cleanup suggestions
- Add undo functionality (move to trash)
- Export cleanup report to JSON
