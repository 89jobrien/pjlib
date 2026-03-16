---
allowed-tools:
  - Bash(du:*)
  - Bash(find:*)
  - Bash(df:*)
argument-hint: "[path]"
description: "Analyze storage usage and identify cleanup opportunities"
---

# Storage Analysis

Analyzing storage usage for cleanup opportunities in: **`!echo "${1:-$(pwd)}"`**

---

## Current Storage

**Overall Usage:**
```
!du -sh "${1:-.}" 2>/dev/null
```

**Available Space:**
```
!df -h "${1:-.}" | tail -1
```

---

## Total Size by Category

### Dependencies
```
!find "${1:-.}" -type d \( -name "node_modules" -o -name ".venv" -o -name "venv" -o -name "__pycache__" \) -prune -exec du -sh {} \; 2>/dev/null | sort -hr | head -20
```

**Total Dependencies:**
```
!find "${1:-.}" -type d \( -name "node_modules" -o -name ".venv" -o -name "venv" -o -name "__pycache__" \) -prune -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "%.2f GB\n", sum/1024/1024}'
```

### Build Artifacts
```
!find "${1:-.}" -type d \( -name ".next" -o -name "dist" -o -name "build" -o -name "target" -o -name ".turbo" -o -name "out" \) -prune -exec du -sh {} \; 2>/dev/null | sort -hr | head -20
```

**Total Build Artifacts:**
```
!find "${1:-.}" -type d \( -name ".next" -o -name "dist" -o -name "build" -o -name "target" -o -name ".turbo" -o -name "out" \) -prune -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "%.2f GB\n", sum/1024/1024}'
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
!find "${1:-.}" -type d -name ".cache" -prune -exec du -sh {} \; 2>/dev/null | sort -hr | head -20
```

**Total Cache Storage:**
```
!find "${1:-.}" -type d -name ".cache" -prune -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "%.2f GB\n", sum/1024/1024}'
```

---

## Summary

### Cleanup Opportunities

**Dependencies:**
```
!find "${1:-.}" -type d \( -name "node_modules" -o -name ".venv" -o -name "venv" -o -name "__pycache__" \) -prune 2>/dev/null | wc -l | awk '{print $1 " directories found"}' && find "${1:-.}" -type d \( -name "node_modules" -o -name ".venv" -o -name "venv" -o -name "__pycache__" \) -prune -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "Total: %.2f GB\n", sum/1024/1024}'
```
→ Run: `/util:cleanup-deps [path]`

**Build Artifacts:**
```
!find "${1:-.}" -type d \( -name ".next" -o -name "dist" -o -name "build" -o -name "target" -o -name ".turbo" -o -name "out" \) -prune 2>/dev/null | wc -l | awk '{print $1 " directories found"}' && find "${1:-.}" -type d \( -name ".next" -o -name "dist" -o -name "build" -o -name "target" -o -name ".turbo" -o -name "out" \) -prune -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "Total: %.2f GB\n", sum/1024/1024}'
```
→ Run: `/util:cleanup-builds [path]`

**Git Repositories:**
```
!find "${1:-.}" -type d -name ".git" -prune 2>/dev/null | wc -l | awk '{print $1 " repositories found"}' && find "${1:-.}" -type d -name ".git" -prune -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "Total: %.2f GB\n", sum/1024/1024}'
```
→ Run: `/util:cleanup-git [path]`

**Caches:**
```
!find "${1:-.}" -type d -name ".cache" -prune 2>/dev/null | wc -l | awk '{print $1 " directories found"}' && find "${1:-.}" -type d -name ".cache" -prune -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "Total: %.2f GB\n", sum/1024/1024}'
```
→ Run: `/util:cleanup-caches [path]`

**Total Potential Savings:**
```
!find "${1:-.}" -type d \( -name "node_modules" -o -name ".venv" -o -name "venv" -o -name "__pycache__" -o -name ".next" -o -name "dist" -o -name "build" -o -name "target" -o -name ".turbo" -o -name "out" -o -name ".git" -o -name ".cache" \) -prune -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "%.2f GB\n", sum/1024/1024}'
```

---

**Next Steps:**

Use specialized cleanup commands or run comprehensive cleanup:
- `/util:deep-clean [path]` - Interactive cleanup with all categories
