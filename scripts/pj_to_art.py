"""Convert projects dataset to OpenPipe ART trajectory format.

This module remains as a project-targeted entry point under scripts/.
The reusable implementation lives in pjlib.to_art.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    _ROOT = Path(__file__).resolve().parents[1]
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))

from pjlib.to_art import (  # noqa: E402
    ERROR_PATTERNS,
    TOOL_CATEGORIES,
    LisaTrajectory,
    ToolCall,
    TrajectoryRewards,
    build_trajectory,
    compute_rewards,
    convert_dataset,
    detect_language,
    extract_file_path,
    group_rows_by_session,
    is_tool_error,
    is_warmup_message,
    main,
)

__all__ = [
    "ToolCall",
    "TrajectoryRewards",
    "LisaTrajectory",
    "TOOL_CATEGORIES",
    "ERROR_PATTERNS",
    "is_tool_error",
    "extract_file_path",
    "detect_language",
    "is_warmup_message",
    "compute_rewards",
    "group_rows_by_session",
    "build_trajectory",
    "convert_dataset",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
