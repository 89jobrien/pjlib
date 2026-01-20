# Hookmap from `$home/.claude`

```json
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "uv run ~/.claude/hooks/workflows/post_tool_use.py"
          }
        ]
      },
      {
        "matcher": "TodoWrite",
        "hooks": [
          {
            "type": "command",
            "command": "uv run ~/.claude/hooks/workflows/todo_sync.py"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bd prime"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$CLAUDE_FILE_PATHS\" | grep -qE '(\\.zshrc|\\.zshrc$)'; then echo 'BLOCK: ~/.zshrc is protected - edit manually if needed' >&2; exit 2; fi"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$TOOL_INPUT\" | grep -qE '(gh repo edit.*--default-branch|gh api.*default_branch)'; then echo 'BLOCKED: Default branch must remain main.' >&2; exit 1; fi"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv run ~/.claude/hooks/workflows/session_end.py"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv run ~/.claude/hooks/workflows/session_start.py"
          },
          {
            "type": "command",
            "command": "uv run ~/.claude/hooks/context/codebase_map.py"
          }
        ]
      },
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bd prime"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv run ~/.claude/hooks/workflows/stop.py"
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv run ~/.claude/hooks/workflows/subagent_stop.py"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv run ~/.claude/hooks/workflows/user_prompt.py"
          },
          {
            "type": "command",
            "command": "uv run ~/.claude/hooks/context/jit_context.py"
          }
        ]
      }
    ]
  }
```
