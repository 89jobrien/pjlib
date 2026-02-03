"""Generate index statistics for ~/.claude/projects JSONL files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT_BUCKETS: list[tuple[str, int, int]] = [
    ("<1MB", 0, 1 * 1024 * 1024),
    ("1-5MB", 1 * 1024 * 1024, 5 * 1024 * 1024),
    ("5-20MB", 5 * 1024 * 1024, 20 * 1024 * 1024),
    ("20-50MB", 20 * 1024 * 1024, 50 * 1024 * 1024),
    (">=50MB", 50 * 1024 * 1024, 1 << 63),
]


def _bucket_for_size(size: int, buckets: list[tuple[str, int, int]]) -> str:
    for label, low, high in buckets:
        if low <= size < high:
            return label
    return buckets[-1][0]


def build_pj_index(
    pj_dir: Path,
    *,
    top_n: int = 20,
    buckets: list[tuple[str, int, int]] | None = None,
) -> dict[str, object]:
    if not pj_dir.exists() or not pj_dir.is_dir():
        raise ValueError(f"pj_dir not found: {pj_dir}")

    bucket_defs = buckets or DEFAULT_BUCKETS
    bucket_stats: dict[str, dict[str, int | str]] = {
        label: {"bucket": label, "count": 0, "total_bytes": 0}
        for label, _, _ in bucket_defs
    }

    files: list[dict[str, int | str]] = []
    total_bytes = 0

    for path in pj_dir.rglob("*.jsonl"):
        size = path.stat().st_size
        total_bytes += size
        files.append({"path": str(path), "size_bytes": size})

        label = _bucket_for_size(size, bucket_defs)
        bucket = bucket_stats[label]
        bucket["count"] = int(bucket["count"]) + 1
        bucket["total_bytes"] = int(bucket["total_bytes"]) + size

    files_sorted = sorted(files, key=lambda f: int(f["size_bytes"]), reverse=True)
    buckets_sorted = [bucket_stats[label] for label, _, _ in bucket_defs]

    summary = {
        "total_files": len(files),
        "total_bytes": total_bytes,
        "avg_bytes": int(total_bytes / len(files)) if files else 0,
    }

    return {
        "summary": summary,
        "buckets": buckets_sorted,
        "top_files": files_sorted[:top_n],
    }


def write_index(index: dict[str, object], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(index, indent=2), encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        raise SystemExit("usage: pj_index.py OUT.json PROJECTS_DIR [TOP_N]")

    out_path = Path(argv[1]).expanduser()
    pj_dir = Path(argv[2]).expanduser()
    top_n = int(argv[3]) if len(argv) > 3 else 20

    index = build_pj_index(pj_dir, top_n=top_n)
    write_index(index, out_path)
    return 0


def cli() -> None:
    """Console-script entry point (pj-index)."""

    raise SystemExit(main(sys.argv))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
