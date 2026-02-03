"""Extract schema samples from project JSONL logs.

This module remains as a project-targeted entry point under scripts/.
The reusable implementation lives in pjlib.schema_samples.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    _ROOT = Path(__file__).resolve().parents[1]
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))

from pjlib.schema_samples import (  # noqa: E402
    extract_schema_samples,
    main,
    write_schema_samples,
)

__all__ = [
    "extract_schema_samples",
    "write_schema_samples",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
