#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Chunk large JSONL dataset files into smaller, manageable pieces for preprocessing.

Usage:
    uv run chunk_dataset.py [input_file] [--chunk-size MB] [--output-dir DIR]

Example:
    uv run chunk_dataset.py datasets/projects_tool_rows.jsonl --chunk-size 100
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def chunk_jsonl(
    input_path: str, output_dir: str, chunk_size_mb: int = 100, by_session: bool = False
) -> dict:
    """
    Chunk a large JSONL file into smaller files.

    Args:
        input_path: Path to input JSONL file
        output_dir: Directory to write chunks
        chunk_size_mb: Target chunk size in MB
        by_session: If True, keep sessions together (may exceed chunk size)

    Returns:
        Dictionary with chunking statistics
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    chunk_size_bytes = chunk_size_mb * 1024 * 1024
    base_name = input_path.stem

    stats = {
        "input_file": str(input_path),
        "input_size_gb": input_path.stat().st_size / 1024 / 1024 / 1024,
        "chunk_size_mb": chunk_size_mb,
        "chunks": [],
        "total_rows": 0,
        "started_at": datetime.now().isoformat(),
    }

    current_chunk = 0
    current_size = 0
    current_rows = 0
    current_file = None
    current_sessions = set()

    def start_new_chunk():
        nonlocal \
            current_chunk, \
            current_size, \
            current_rows, \
            current_file, \
            current_sessions

        if current_file:
            current_file.close()
            stats["chunks"].append(
                {
                    "chunk": current_chunk,
                    "rows": current_rows,
                    "size_mb": current_size / 1024 / 1024,
                    "sessions": len(current_sessions),
                }
            )

        current_chunk += 1
        current_size = 0
        current_rows = 0
        current_sessions = set()

        chunk_path = output_dir / f"{base_name}_chunk_{current_chunk:04d}.jsonl"
        current_file = open(chunk_path, "w")
        print(f"  Writing chunk {current_chunk}: {chunk_path.name}")

        return current_file

    print(f"Chunking {input_path.name} ({stats['input_size_gb']:.2f} GB)")
    print(f"Target chunk size: {chunk_size_mb} MB")
    print(f"Output directory: {output_dir}")
    print()

    current_file = start_new_chunk()

    with open(input_path) as f:
        for line_num, line in enumerate(f, 1):
            line_size = len(line.encode("utf-8"))

            # Parse to get session_id if grouping by session
            if by_session:
                try:
                    data = json.loads(line)
                    session_id = data.get("session_id", "")
                except json.JSONDecodeError:
                    session_id = ""

            # Check if we need a new chunk
            if current_size + line_size > chunk_size_bytes:
                if not by_session or session_id not in current_sessions:
                    current_file = start_new_chunk()

            current_file.write(line)
            current_size += line_size
            current_rows += 1
            stats["total_rows"] += 1

            if by_session and session_id:
                current_sessions.add(session_id)

            # Progress update
            if line_num % 5000 == 0:
                print(f"  Processed {line_num:,} rows...")

    # Close final chunk
    if current_file:
        current_file.close()
        stats["chunks"].append(
            {
                "chunk": current_chunk,
                "rows": current_rows,
                "size_mb": current_size / 1024 / 1024,
                "sessions": len(current_sessions) if by_session else 0,
            }
        )

    stats["completed_at"] = datetime.now().isoformat()
    stats["total_chunks"] = len(stats["chunks"])

    # Write stats
    stats_path = output_dir / f"{base_name}_chunks_stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    print()
    print("Chunking complete!")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Total rows: {stats['total_rows']:,}")
    print(f"  Stats written to: {stats_path.name}")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Chunk large JSONL files into smaller pieces for preprocessing"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="datasets/projects_tool_rows.jsonl",
        help="Input JSONL file path",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=100,
        help="Target chunk size in MB (default: 100)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: <input_dir>/chunks/)",
    )
    parser.add_argument(
        "--by-session", action="store_true", help="Keep rows from same session together"
    )

    args = parser.parse_args()

    # Resolve paths relative to ~/.claude
    claude_dir = Path.home() / ".claude"
    input_path = Path(args.input_file)

    if not input_path.is_absolute():
        input_path = claude_dir / input_path

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    if args.output_dir:
        output_dir = Path(args.output_dir)
        if not output_dir.is_absolute():
            output_dir = claude_dir / output_dir
    else:
        output_dir = input_path.parent / "chunks"

    chunk_jsonl(
        input_path=str(input_path),
        output_dir=str(output_dir),
        chunk_size_mb=args.chunk_size,
        by_session=args.by_session,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
