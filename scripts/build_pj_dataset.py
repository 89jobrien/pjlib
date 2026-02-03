"""Build a projects-only tool-use dataset (JSONL).

Uses only data under ~/.claude/projects.

Output rows:
{session_id, t, messages, tool_name, tool_input, tool_result, trace, reward}

Example:
  python3 scripts/build_pj_dataset.py \
    --projects-dir ~/.claude/projects \
    --out ~/.claude/datasets/pj_tool_rows.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# Allow running as a script: `python3 scripts/build_pj_dataset.py ...`
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from pjlib.dataset import iter_dataset_rows  # noqa: E402
from pjlib.extract import iter_pj_files  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects-dir", type=Path, required=True, dest="pj_dir")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--max-files", type=int, default=0)
    ap.add_argument("--max-rows", type=int, default=0)
    ap.add_argument("--max-context-messages", type=int, default=50)
    args = ap.parse_args()

    pj_dir: Path = args.pj_dir.expanduser()
    out: Path = args.out.expanduser()

    files = list(iter_pj_files(pj_dir))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if args.max_files and args.max_files > 0:
        files = files[: args.max_files]

    out.parent.mkdir(parents=True, exist_ok=True)

    counts = Counter()
    n = 0
    with out.open("w", encoding="utf-8") as f:
        for row in iter_dataset_rows(
            files, max_context_messages=args.max_context_messages
        ):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
            counts[row.get("tool_name", "")] += 1
            if args.max_rows and args.max_rows > 0 and n >= args.max_rows:
                break

    stats_path = out.with_suffix(out.suffix + ".stats.json")
    stats_path.write_text(
        json.dumps(
            {
                "rows": n,
                "files": len(files),
                "tool_name_counts": dict(counts.most_common(50)),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"wrote {n} rows to {out}")
    print(f"wrote stats to {stats_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
