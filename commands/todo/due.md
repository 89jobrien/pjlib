---
allowed-tools: Read, Write, Edit, Search, Grep, Glob
argument-hint: ' <id> [due date]'
description: Set or update the due date for todo <id> in TO-DO.md.
---

# Set Due Date

Set or update the due date for a specific todo <id> in `TO-DO.md`.

## Instructions

### 1. Determine Project Root

Look for common indicators:

- `.git` directory
- `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`
- Project configuration files

### 2. Locate TO-DO.md

- Read `TO-DO.md` from the project root
- If it doesn't exist, inform the user and suggest using `/todo:add` first

### 3. Parse Arguments

**Todo Number:**

- Extract the todo number <id> from `$ID`
- Validate that <id> is a valid number

**Due Date:**

- Parse date/time expressions like:
  - `tomorrow`, `next week`, `in 3 days`
  - Specific dates: `June 9`, `12-24-2025`, `2025-12-24`
  - Relative times: `in 2 hours`, `in 30 minutes`
- Format dates as `MM/DD/YYYY` (or `DD/MM/YYYY` based on locale)
- Include time only if explicitly requested (e.g., `in 2 hours` → `MM/DD/YYYY @ HH:MM AM/PM`)

### 4. Find and Update Todo

- Locate the <id>th todo in the `## Active` section
- If the todo already has a due date, replace it
- If the todo doesn't have a due date, add it
- Format: `- [ ] Task description | Due: MM/DD/YYYY` (or with time if specified)
- Maintain proper sorting: todos with due dates come before those without, sorted descending by due date

### 5. Update File

- Write the updated content to `TO-DO.md`
- Re-sort Active todos if necessary (due dates first, descending)
- Maintain proper formatting

### 6. Provide Feedback

Show a concise confirmation:

```text
✓ Set due date for todo #<id>: "[task description]"
  Due: MM/DD/YYYY [@ HH:MM AM/PM if time specified]
```

## Examples

- `/todo:due 1 tomorrow` - Set todo <id> tomorrow
- `/todo:due 2 next week` - Set todo <id> next week
- `/todo:due 3 June 15` - Set todo <id> June 15
- `/todo:due 4 in 2 hours` - Set todo <id> in 2 hours (with time)

## Error Handling

- If todo <id> is invalid or out of range, show an error:

  ```text
  ✗ Todo #<id> not found. Use /todo:list to see available todos.
  ```

- If TO-DO.md doesn't exist, inform the user
- Handle invalid date formats gracefully
- Always be concise and helpful in responses

## Behavior

- Update existing due dates or add new ones
- Re-sort Active section after updating (due dates first, descending)
- Times are only included if explicitly requested
- Dates default to `MM/DD/YYYY` format unless user specifies otherwise
