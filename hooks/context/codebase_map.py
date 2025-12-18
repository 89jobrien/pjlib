#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Add codebase map to context at session start.

This hook generates a tree structure of the codebase for context.
Runs on SessionStart and UserPromptSubmit events (once per session).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

SESSION_CACHE: set[str] = set()


def generate_tree(
    root: Path,
    max_depth: int,
    exclude_dirs: set[str],
    current_depth: int = 0,
    prefix: str = "",
) -> str:
    if current_depth >= max_depth:
        return ""

    try:
        entries = sorted(
            root.iterdir(),
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )
    except PermissionError:
        return ""

    lines = []
    entries = [e for e in entries if e.name not in exclude_dirs]

    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            subtree = generate_tree(
                entry,
                max_depth,
                exclude_dirs,
                current_depth + 1,
                prefix + extension,
            )
            if subtree:
                lines.append(subtree)

    return "\n".join(lines)


def main() -> None:
    with hook_invocation("codebase_map") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        session_id = payload.get("session_id", "default")

        if session_id in SESSION_CACHE:
            sys.exit(0)

        cwd = payload.get("cwd", ".")
        project_root = Path(cwd)

        if not project_root.exists():
            sys.exit(0)

        max_depth = 3
        exclude_dirs = {
            "node_modules",
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "dist",
            "build",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "coverage",
        }

        print("[Progress] Generating codebase map...", file=sys.stderr)

        codebase_map = generate_tree(project_root, max_depth, exclude_dirs)

        print("[Success] Codebase map generated", file=sys.stderr)
        print("\n" + "=" * 60)
        print("CODEBASE STRUCTURE")
        print("=" * 60)
        print(codebase_map)
        print("=" * 60 + "\n")

        SESSION_CACHE.add(session_id)

        sys.exit(0)


if __name__ == "__main__":
    main()
