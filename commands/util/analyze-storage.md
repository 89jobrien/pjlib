---
allowed-tools:
  - Bash(du:*)
  - Bash(find:*)
  - Bash(stat:*)
argument-hint: "[path]"
description: "Analyze storage usage and identify cleanup opportunities"
---

# Storage Analysis

Analyzing storage usage for cleanup opportunities in: **`!echo "${1:-$(pwd)}"`**

---

## Total Size by Category

### Dependencies
```
!find "${1:-.}" -type d \( -name "node_modules" -o -name ".venv" -o -name "venv" -o -name "__pycache__" -o -name ".tox" -o -name "vendor" \) -prune -exec du -sh {} \; 2>/dev/null | sort -hr | head -20
```

**Total Dependencies:**
```
!find "${1:-.}" -type d \( -name "node_modules" -o -name ".venv" -o -name "venv" -o -name "__pycache__" -o -name ".tox" -o -name "vendor" \) -prune -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "%.2f GB\n", sum/1024/1024}'
```

### Build Artifacts
```
!find "${1:-.}" -type d \( -name ".next" -o -name "dist" -o -name "build" -o -name "target" -o -name "out" -o -name ".output" -o -name "_site" \) -prune -exec du -sh {} \; 2>/dev/null | sort -hr | head -20
```

**Total Build Artifacts:**
```
!find "${1:-.}" -type d \( -name ".next" -o -name "dist" -o -name "build" -o -name "target" -o -name "out" -o -name ".output" -o -name "_site" \) -prune -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "%.2f GB\n", sum/1024/1024}'
```

### Git Repositories
```
!find "${1:-.}" -type d -name ".git" -prune -exec du -sh {} \; 2>/dev/null | sort -hr | head -20
```

**Total Git Storage:**
```
!find "${1:-.}" -type d -name ".git" -prune -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "%.2f GB\n", sum/1024/1024}'
```

### Caches
```
!find "${1:-.}" -type d \( -name ".cache" -o -name ".pytest_cache" -o -name ".ruff_cache" -o -name ".mypy_cache" -o -name ".eslintcache" -o -name "coverage" \) -prune -exec du -sh {} \; 2>/dev/null | sort -hr | head -20
```

**Total Cache Storage:**
```
!find "${1:-.}" -type d \( -name ".cache" -o -name ".pytest_cache" -o -name ".ruff_cache" -o -name ".mypy_cache" -o -name ".eslintcache" -o -name "coverage" \) -prune -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "%.2f GB\n", sum/1024/1024}'
```

---

## Largest Directories (Top 20)
```
!du -sh "${1:-.}"/* 2>/dev/null | sort -hr | head -20
```

---

## File Type Distribution (Top 15)
```
!find "${1:-.}" -type f -name "*.*" 2>/dev/null | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15
```

---

## Old Files (Not Modified in 180+ Days)
```
!find "${1:-.}" -type f -mtime +180 -exec ls -lh {} \; 2>/dev/null | awk '{print $9, $5}' | head -20
```

---

## Summary Statistics

**Total Directory Size:**
```
!du -sh "${1:-.}" 2>/dev/null
```

**File Count:**
```
!find "${1:-.}" -type f 2>/dev/null | wc -l | awk '{print $1}'
```

**Directory Count:**
```
!find "${1:-.}" -type d 2>/dev/null | wc -l | awk '{print $1}'
```

---

## Cleanup Recommendations

Based on the analysis above, consider:

1. **Dependencies Cleanup**
   - Remove `node_modules` from archived/unused projects
   - Remove Python virtual environments (`.venv`, `venv`) from old projects
   - Clean `__pycache__` directories: `find . -type d -name "__pycache__" -exec rm -rf {} +`

2. **Build Artifacts Cleanup**
   - Remove `.next`, `dist`, `build`, `target` directories from projects not in active development
   - These can be regenerated when needed

3. **Git Cleanup**
   - Run `git gc --aggressive` in large repositories
   - Consider shallow clones for archived projects: `git clone --depth=1`
   - Remove `.git` from truly archived projects (convert to regular directory)

4. **Cache Cleanup**
   - Safe to delete all cache directories - they regenerate on next use
   - Clear test caches: `.pytest_cache`, `coverage`
   - Clear linter caches: `.ruff_cache`, `.mypy_cache`, `.eslintcache`

5. **Old Files**
   - Review files not modified in 180+ days
   - Archive to external storage or compress if rarely accessed

**Next Steps:**

Use specialized cleanup commands:
- `/util:clean-dependencies [path]` - Remove dependency directories
- `/util:clean-builds [path]` - Remove build artifacts
- `/util:clean-git [path]` - Optimize git repositories
- `/util:clean-caches [path]` - Remove cache directories

Or use the comprehensive cleanup:
- `/util:deep-clean [path]` - Interactive cleanup with all categories
