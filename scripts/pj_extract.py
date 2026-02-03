"""Extract normalized events from ~/.claude/projects/*.jsonl.

This module remains as a project-targeted entry point under scripts/.
The reusable implementation lives in pjlib.extract.
"""

from __future__ import annotations

import sys
from pathlib import Path

# When executed as a file (e.g. `uv run python scripts/pj_extract.py`), ensure the
# repo root is importable so `import pjlib` works.
if __package__ in {None, ""}:
    _ROOT = Path(__file__).resolve().parents[1]
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))

from pjlib.extract import (  # noqa: E402
    MessageEvent,
    NormalizedEvent,
    ToolResultEvent,
    ToolUseEvent,
    extract_events,
    iter_jsonl,
    iter_pj_files,
    iter_project_events,
)

__all__ = [
    "MessageEvent",
    "ToolUseEvent",
    "ToolResultEvent",
    "NormalizedEvent",
    "iter_jsonl",
    "extract_events",
    "iter_project_events",
    "iter_pj_files",
]
