#!/usr/bin/env python3
"""
Claude workspace cleanup script.

Reclaims disk space by archiving old session data to iCloud
and deleting temporary files based on configurable retention policy.
"""
import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import NamedTuple


class Args(NamedTuple):
    """Parsed CLI arguments"""

    dry_run: bool
    execute: bool
    days: int


@dataclass
class CleanupConfig:
    """Configuration for cleanup operation"""
    claude_dir: Path
    archive_dir: Path
    retention_days: int

    @property
    def cutoff_date(self) -> datetime:
        """Calculate cutoff date based on retention days"""
        return datetime.now() - timedelta(days=self.retention_days)

    @property
    def archive_dirs(self) -> list[str]:
        """Directories to archive before deletion"""
        return ['projects', 'transcripts']

    @property
    def delete_only_dirs(self) -> list[str]:
        """Directories to delete without archiving"""
        return ['plugins', 'debug', 'shell-snapshots', 'file-history', 'logs']

    @property
    def temp_patterns(self) -> list[str]:
        """Patterns for temp files to delete entirely"""
        return ['paste-cache', '*.backup*', '.DS_Store']


def find_old_items(directory: Path, cutoff_date: datetime) -> list[Path]:
    """
    Find files and directories older than cutoff date.

    Args:
        directory: Directory to search
        cutoff_date: Files older than this are returned

    Returns:
        List of paths to old items
    """
    if not directory.exists():
        return []

    old_items: list[Path] = []

    try:
        for item in directory.iterdir():
            # Get modification time
            mtime = datetime.fromtimestamp(item.stat().st_mtime)

            if mtime < cutoff_date:
                old_items.append(item)
    except (PermissionError, OSError):
        # Skip directories we can't read
        pass

    return old_items


def get_size(path: Path) -> int:
    """
    Calculate total size of file or directory.

    Args:
        path: File or directory path

    Returns:
        Total size in bytes
    """
    if path.is_file():
        return path.stat().st_size

    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
    except (PermissionError, OSError):
        # Skip items we can't access
        pass

    return total


def format_size(size_bytes: int) -> str:
    """
    Format byte size as human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5MB")
    """
    if size_bytes == 0:
        return '0B'

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f'{int(size)}{units[unit_index]}'
    return f'{size:.1f}{units[unit_index]}'


def parse_args(argv: list[str] | None = None) -> Args:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Clean up Claude workspace by archiving old data and removing temp files"
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without executing (default)",
    )
    mode_group.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform cleanup operations",
    )

    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Retention period in days (default: 7)",
    )

    parsed = parser.parse_args(argv)

    return Args(
        dry_run=not parsed.execute,
        execute=parsed.execute,
        days=parsed.days,
    )


def main() -> int:
    """Main entry point"""
    args = parse_args()
    print(f"Args: dry_run={args.dry_run}, execute={args.execute}, days={args.days}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
