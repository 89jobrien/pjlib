---
description: Get kan cheatsheet
---

## References

Get Project README: !` cat /Users/joe/Documents/GitHub/kan/README.md`

`kan` ships two binaries:

- `kan` — the interactive TUI
- `kan-cli` — a non-interactive CLI for scripting

Run `kan-cli --help` to see:

### Commands

- `kan-cli list`  
  Show a quick overview of the current board.

- `kan-cli columns`  
  List all columns on the current board.

- `kan-cli show <CARD_ID>`  
  Show details for one card. `<CARD_ID>` can be the internal ID or the display ID (e.g. `KAN-001`).

- `kan-cli add [OPTIONS] <COLUMN> <TITLE>`  
  Add a card to a column (column title or ID).
  - `-d, --description <TEXT>` (default: empty)
  - `-T, --tags <TAG1,TAG2,...>` (comma-separated; tags are normalized to start with `#`)

- `kan-cli move <CARD_ID> <COLUMN>`  
  Move a card to another column (column title or ID).

- `kan-cli update [OPTIONS] <CARD_ID>`  
  Update fields on a card.
  - `-t, --title <TITLE>`
  - `-d, --description <TEXT>`
  - `-T, --tags <TAG1,TAG2,...>` (overwrites existing tags)

- `kan-cli delete <CARD_ID>`  
  Delete a card.

- `kan-cli init [OPTIONS] <NAME>`  
  Create a new local board with default columns.
  - `-c, --columns "To Do, Doing, Done"` (comma-separated string)
  - `-p, --prefix <PREFIX>` (for generated card display IDs)

- `kan-cli boards`  
  List available local boards.

### Provider configuration (same as TUI)
The CLI uses the same backend selection as the app, controlled via env vars (e.g. local SQLite via `KAN_DB_PATH`, Jira via `FLOW_PROVIDER=jira` + `JIRA_*`).