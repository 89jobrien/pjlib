---
name: emoji-remover
description: Remove emojis from project files and replace them with text equivalents. Use this skill when the user mentions removing emojis, cleaning up documentation, code review mentions emoji issues, or when you notice emojis in files that should be emoji-free. Also trigger for phrases like "clean emojis", "no emojis", "remove emoji", or "emoji cleanup".
---

# Emoji Remover

You are an expert at identifying and removing emojis from text files while preserving meaning and readability.

## When to Use This Skill

Use this skill whenever:

- The user explicitly asks to remove or clean up emojis
- You're doing a code review and notice emojis in documentation
- The user mentions their project has a no-emoji policy
- You see emojis in markdown files, commit messages, or documentation

## How Emojis Should Be Handled

The goal is to remove emojis while preserving the information they conveyed. Use these context-aware replacement strategies:

### Status Indicators

Replace common status emojis with text equivalents:

- ✅ → `[DONE]` or `COMPLETE` (context-dependent)
- ❌ → `[FAILED]` or `ERROR`
- 🔴 → `CRITICAL:` or `HIGH:`
- 🟡 → `MEDIUM:`
- 🟢 → `LOW:` or `OK:`
- ⚠️ → `WARNING:`
- 📝 → `NOTE:`
- 💡 → `TIP:`
- 🐛 → `BUG:`
- 🚀 → `FEATURE:`

### Checkboxes and Lists

- ☑ or ✓ → `[x]` (markdown checked checkbox)
- ☐ → `[ ]` (markdown unchecked checkbox)

### Decorative and Expressive Emojis

Remove entirely if they don't convey essential information:

- 🎉 🎊 💪 👍 🔥 etc. → delete
- Keep spacing natural after removal (don't leave double spaces)

### Semantic Emojis in Technical Content

Replace with text when they carry meaning:

- 📁 → `Directory:` or `Folder:`
- 📄 → `File:`
- 🔧 → `Config:` or `Tool:`
- 🤖 → `AI:` or `Bot:`

## Workflow

Follow these steps when removing emojis:

### Step 1: Scan for Emojis

First, scan the relevant files to identify emoji usage. Use a script to detect Unicode emoji ranges:

```bash
# Find all files containing emojis
rg -l "[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|✅|❌|☑|✓|☐" --glob "*.md" --glob "*.txt"
```

Or use the bundled script:

```bash
python scripts/detect_emojis.py <directory>
```

This will output a report showing:

- Files containing emojis
- Count per file
- Preview of emoji context (surrounding text)

### Step 2: Review Context

Read the files to understand what each emoji represents. The replacement strategy depends on context:

**In markdown headers:**

```markdown
# ✅ Installation Complete

→ # Installation Complete
```

**In status lists:**

```markdown
- ✅ Tests passing
- 🔴 Security audit needed
  → - [DONE] Tests passing
- CRITICAL: Security audit needed
```

**In prose:**

```markdown
The feature is working great! 🎉
→ The feature is working great!
```

### Step 3: Present Plan to User

Before making changes, show the user:

1. Total emoji count
2. Files affected
3. Example replacements (show 3-5 representative examples)
4. Ask: "Should I proceed with these replacements?"

### Step 4: Apply Replacements

Use the bundled script for automated replacement:

```bash
python scripts/remove_emojis.py <directory> --apply
```

Or make manual edits using the Edit tool for files needing human judgment.

### Step 5: Generate Report

After cleanup, create a summary:

```markdown
# Emoji Removal Report

## Summary

- Files processed: 15
- Emojis removed: 73
- Status indicators converted: 45
- Decorative emojis removed: 28

## Files Modified

- agents/IMPLEMENTATION_SUMMARY.md (12 emojis)
- agents/UPDATE_PLAN.md (8 emojis)
- README.md (3 emojis)

## Examples

✅ Task complete → [DONE] Task complete
🔴 Critical bug → CRITICAL: Bug
🎉 Celebration → (removed)
```

## Edge Cases

**Emoji in code blocks or examples:**
If the emoji is part of a code example showing how to handle emojis, leave it alone. Check if it's inside triple backticks.

**Emoji in URLs or identifiers:**
Very rare, but if an emoji appears in a URL or filename reference, flag it for the user rather than auto-replacing.

**Emoji as data:**
If scanning data files (CSV, JSON), ask the user first - the emoji might be legitimate data rather than decorative.

**Language-specific emoji:**
Some languages use emoji-like characters as part of their writing system. Only target actual Unicode emoji blocks.

## Script Usage

The bundled scripts provide both detection and removal:

**Detection only (dry run):**

```bash
python scripts/detect_emojis.py /path/to/project
```

**Removal with preview:**

```bash
python scripts/remove_emojis.py /path/to/project --dry-run
```

**Apply changes:**

```bash
python scripts/remove_emojis.py /path/to/project --apply
```

Both scripts output JSON for programmatic parsing and human-readable reports.

## Best Practices

1. **Always show before/after examples** - Users should see what will change before you apply edits
2. **Preserve meaning** - Don't just delete emojis; replace them with text that conveys the same information
3. **Check git status first** - Recommend committing clean before emoji removal so changes can be reviewed
4. **Respect code blocks** - Don't modify emojis inside code examples or literal strings
5. **File by file for complex cases** - If different files need different strategies, process them individually

## Common Patterns to Watch For

**Status dashboards:**

```markdown
## Status

- ✅ Authentication
- ✅ Database
- 🔴 Caching
```

→ Convert to proper status text or checkbox format

**Commit-style messages:**

```markdown
🐛 Fix memory leak
🚀 Add new feature
```

→ Use conventional commit prefixes: `fix:`, `feat:`

**Section headers:**

```markdown
## 🎯 Goals

## 📋 Requirements
```

→ Remove emojis from headers entirely

## Output Format

Always provide a structured report after emoji removal:

```markdown
# Emoji Cleanup Report

**Date:** YYYY-MM-DD
**Scope:** <directory or file list>

## Summary

- Total emojis removed: N
- Files modified: N
- Status emojis converted: N
- Decorative emojis removed: N

## Changes by File

### file1.md

- Line 10: ✅ Complete → [DONE] Complete
- Line 25: 🎉 → (removed)

### file2.md

- Line 5: 🔴 Critical → CRITICAL:

## Review

Please review the changes with `git diff` before committing.
```

## Remember

The goal isn't just to strip emojis mechanically - it's to improve readability and maintain a consistent, professional tone while preserving all the information the emojis conveyed. Take time to understand context and choose appropriate replacements.
