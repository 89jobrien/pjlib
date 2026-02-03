"""Generate index statistics for ~/.claude/projects JSONL files.

This module remains as a project-targeted entry point under scripts/.
The reusable implementation lives in pjlib.index.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    _ROOT = Path(__file__).resolve().parents[1]
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))

from pjlib.index import (  # noqa: E402
    DEFAULT_BUCKETS,
    build_pj_index,
    main,
    write_index,
)

__all__ = [
    "DEFAULT_BUCKETS",
    "build_pj_index",
    "write_index",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
