"""Extract schema samples from project JSONL logs."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from pjlib.extract import iter_jsonl


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "unknown"


def _merge_schema(a: dict[str, Any] | None, b: dict[str, Any]) -> dict[str, Any]:
    if a is None:
        return b

    merged_types = sorted(set(a["type"]) | set(b["type"]))
    merged: dict[str, Any] = {"type": merged_types}

    if "properties" in a or "properties" in b:
        props: dict[str, Any] = {}
        a_props = a.get("properties", {})
        b_props = b.get("properties", {})
        for key in set(a_props) | set(b_props):
            props[key] = _merge_schema(a_props.get(key), b_props.get(key, {"type": []}))
        merged["properties"] = props

    if "items" in a or "items" in b:
        merged["items"] = _merge_schema(a.get("items"), b.get("items", {"type": []}))

    return merged


def _schema_for_value(value: Any) -> dict[str, Any]:
    t = _type_name(value)
    schema: dict[str, Any] = {"type": [t]}
    if t == "object" and isinstance(value, dict):
        schema["properties"] = {k: _schema_for_value(v) for k, v in value.items()}
    elif t == "array" and isinstance(value, list):
        item_schema: dict[str, Any] | None = None
        for item in value:
            item_schema = _merge_schema(item_schema, _schema_for_value(item))
        schema["items"] = item_schema or {"type": []}
    return schema


def extract_schema_samples(
    paths: Iterable[Path],
    *,
    sample_limit: int = 3,
) -> dict[str, Any]:
    stats: dict[str, dict[str, Any]] = {}
    total_records = 0

    for path in paths:
        for record in iter_jsonl(path):
            total_records += 1
            record_type = record.get("type")
            type_key = record_type if isinstance(record_type, str) else "unknown"
            entry = stats.setdefault(
                type_key,
                {
                    "count": 0,
                    "examples": [],
                    "schema": None,
                    "required_keys": None,
                },
            )

            entry["count"] += 1
            if len(entry["examples"]) < sample_limit:
                entry["examples"].append(record)
                entry["schema"] = _merge_schema(
                    entry["schema"], _schema_for_value(record)
                )
                keys = set(record.keys())
                if entry["required_keys"] is None:
                    entry["required_keys"] = keys
                else:
                    entry["required_keys"] &= keys

    output = {"total_records": total_records, "sample_limit": sample_limit, "types": {}}

    for key, entry in stats.items():
        output["types"][key] = {
            "count": entry["count"],
            "required_keys": sorted(entry["required_keys"] or []),
            "schema": entry["schema"] or {"type": []},
            "examples": entry["examples"],
        }

    return output


def write_schema_samples(samples: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(samples, indent=2), encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        raise SystemExit(
            "usage: pj_schema_samples.py OUT.json PROJECT.jsonl [PROJECT2.jsonl ...]"
        )

    out_path = Path(argv[1]).expanduser()
    paths = [Path(p).expanduser() for p in argv[2:]]
    samples = extract_schema_samples(paths)
    write_schema_samples(samples, out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv))
