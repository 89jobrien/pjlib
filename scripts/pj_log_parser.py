"""Normalize project JSONL logs into structured rows.

This module remains as a project-targeted entry point under scripts/.
The reusable implementation lives in pjlib.log_parser.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    _ROOT = Path(__file__).resolve().parents[1]
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))

from pjlib.log_parser import (  # noqa: E402
    NormalizedLogRow,
    iter_normalized_rows,
    main,
    normalize_event,
    write_jsonl,
)

__all__ = [
    "NormalizedLogRow",
    "normalize_event",
    "iter_normalized_rows",
    "write_jsonl",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
