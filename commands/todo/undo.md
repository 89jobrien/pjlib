---
allowed-tools: Read, Write, Edit, Search, Grep, Glob
argument-hint: ' <id>'
description: Mark completed todo <id> as incomplete and move it back to Active section in TO-DO.md.
---

# Undo Todo Completion

Mark a completed todo <id> as incomplete and move it from the `## Completed` section back to the `## Active` section in `TO-DO.md`.

## Instructions

### 1. Determine Project Root

Look for common indicators:

- `.git` directory
- `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`
- Project configuration files

### 2. Locate TO-DO.md

- Read `TO-DO.md` from the project root
- If it doesn't exist, inform the user

### 3. Parse Todo Number

- Extract the todo number <id> from `$ID`
- Validate that <id> is a valid number
- Number todos in the Completed section (1, 2, 3...) for reference

### 4. Find and Update Todo

- Locate the <id>th todo in the `## Completed` section
- Change `- [x]` to `- [ ]`
- Remove the `| Done: MM/DD/YYYY` completion date
- Preserve any existing due date information
- Move the todo from `## Completed` back to `## Active` section
- Maintain proper sorting in Active section (due dates first, descending)

### 5. Update File

- Write the updated content to `TO-DO.md`
- Maintain proper formatting
- Keep other todos unchanged

### 6. Provide Feedback

Show a concise confirmation:

```text
✓ Undid completion for todo #<id>: "[task description]"
  Moved back to Active section

  Active todos: M
```

## Examples

- `/todo:undo 1` - Mark the first completed todo <id> as incomplete
- `/todo:undo 3` - Mark the third completed todo <id> as incomplete

## Error Handling

- If todo <id> is invalid or out of range, show an error:

  ```text
  ✗ Completed todo #<id> not found. Use /todo:list to see available todos.
  ```

- If TO-DO.md doesn't exist, inform the user
- If the todo is already in Active section, inform the user
- Handle edge cases gracefully

## Behavior

- Preserve due date information when moving back to Active
- Remove completion date
- Re-sort Active section after moving (due dates first, descending)
- Number todos when displaying for easy reference
- Always be concise and helpful in responses
