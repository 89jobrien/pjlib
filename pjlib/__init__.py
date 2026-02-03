"""pjlib: reusable library for parsing Claude Code project logs.

The CLI entry points remain in scripts/pj_*.py; this package contains the
importable building blocks.
"""

from pjlib.dataset import DatasetRow, iter_dataset_rows, iter_dataset_rows_from_events
from pjlib.extract import (
    MessageEvent,
    NormalizedEvent,
    ToolResultEvent,
    ToolUseEvent,
    extract_events,
    iter_jsonl,
    iter_pj_files,
    iter_project_events,
)
from pjlib.index import DEFAULT_BUCKETS, build_pj_index
from pjlib.log_parser import iter_normalized_rows, normalize_event
from pjlib.schema_samples import extract_schema_samples
from pjlib.to_art import (
    LisaTrajectory,
    ToolCall,
    TrajectoryRewards,
    build_trajectory,
    compute_rewards,
    convert_dataset,
)

__all__ = [
    # extract
    "MessageEvent",
    "ToolUseEvent",
    "ToolResultEvent",
    "NormalizedEvent",
    "iter_jsonl",
    "extract_events",
    "iter_project_events",
    "iter_pj_files",
    # dataset
    "DatasetRow",
    "iter_dataset_rows_from_events",
    "iter_dataset_rows",
    # index
    "DEFAULT_BUCKETS",
    "build_pj_index",
    # log_parser
    "normalize_event",
    "iter_normalized_rows",
    # schema_samples
    "extract_schema_samples",
    # to_art
    "ToolCall",
    "TrajectoryRewards",
    "LisaTrajectory",
    "compute_rewards",
    "build_trajectory",
    "convert_dataset",
]
