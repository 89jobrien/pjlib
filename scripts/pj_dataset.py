"""Build RL/FT dataset rows from ~/.claude/projects/*.jsonl.

This module remains as a project-targeted entry point under scripts/.
The reusable implementation lives in pjlib.dataset.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    _ROOT = Path(__file__).resolve().parents[1]
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))

from pjlib.dataset import (  # noqa: E402
    DatasetRow,
    iter_dataset_rows,
    iter_dataset_rows_from_events,
    main,
    write_jsonl,
)

__all__ = [
    "DatasetRow",
    "iter_dataset_rows_from_events",
    "iter_dataset_rows",
    "write_jsonl",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
