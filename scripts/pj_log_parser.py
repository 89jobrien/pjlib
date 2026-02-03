"""Normalize project JSONL logs into structured rows."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from scripts.pj_extract import (
    MessageEvent,
    ToolResultEvent,
    ToolUseEvent,
    iter_project_events,
)


@dataclass(frozen=True)
class NormalizedLogRow:
    session_id: str | None
    uuid: str | None
    parent_uuid: str | None
    timestamp: str | None
    event_type: str
    role: str | None
    text: str | None
    tool_name: str | None
    tool_use_id: str | None
    tool_input: dict[str, Any] | None
    tool_result_text: str | None
    is_error: bool | None


def normalize_event(
    event: MessageEvent | ToolUseEvent | ToolResultEvent,
) -> dict[str, Any]:
    if isinstance(event, MessageEvent):
        row = NormalizedLogRow(
            session_id=event.session_id,
            uuid=event.uuid,
            parent_uuid=event.parent_uuid,
            timestamp=event.timestamp,
            event_type="message",
            role=event.role,
            text=event.text,
            tool_name=None,
            tool_use_id=None,
            tool_input=None,
            tool_result_text=None,
            is_error=None,
        )
        return asdict(row)

    if isinstance(event, ToolUseEvent):
        row = NormalizedLogRow(
            session_id=event.session_id,
            uuid=event.uuid,
            parent_uuid=event.parent_uuid,
            timestamp=event.timestamp,
            event_type="tool_use",
            role=event.role,
            text=None,
            tool_name=event.tool_name,
            tool_use_id=event.tool_use_id,
            tool_input=event.tool_input,
            tool_result_text=None,
            is_error=None,
        )
        return asdict(row)

    row = NormalizedLogRow(
        session_id=event.session_id,
        uuid=event.uuid,
        parent_uuid=event.parent_uuid,
        timestamp=event.timestamp,
        event_type="tool_result",
        role=event.role,
        text=None,
        tool_name=None,
        tool_use_id=event.tool_use_id,
        tool_input=None,
        tool_result_text=event.content_text,
        is_error=event.is_error,
    )
    return asdict(row)


def iter_normalized_rows(paths: Iterable[Path]) -> Iterator[dict[str, Any]]:
    for event in iter_project_events(paths):
        yield normalize_event(event)


def write_jsonl(rows: Iterable[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        raise SystemExit(
            "usage: pj_log_parser.py OUT.jsonl PROJECT.jsonl [PROJECT2.jsonl ...]"
        )

    out_path = Path(argv[1]).expanduser()
    paths = [Path(p).expanduser() for p in argv[2:]]
    rows = iter_normalized_rows(paths)
    write_jsonl(rows, out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv))
