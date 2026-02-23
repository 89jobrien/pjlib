#!/usr/bin/env python3
"""
Claude workspace cleanup script.

Reclaims disk space by archiving old session data to iCloud
and deleting temporary files based on configurable retention policy.
"""
import argparse
import shutil
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


@dataclass
class CleanupResults:
    """Results of cleanup operation"""
    archived_items: list[tuple[Path, int]] | None = None
    deleted_items: list[tuple[Path, int]] | None = None
    errors: list[str] | None = None
    total_archived_size: int = 0
    total_deleted_size: int = 0

    def __post_init__(self) -> None:
        """Initialize mutable default values"""
        if self.archived_items is None:
            self.archived_items = []
        if self.deleted_items is None:
            self.deleted_items = []
        if self.errors is None:
            self.errors = []

    def add_archived(self, item: Path, size: int) -> None:
        """Add archived item to results"""
        self.archived_items.append((item, size))
        self.total_archived_size += size

    def add_deleted(self, item: Path, size: int) -> None:
        """Add deleted item to results"""
        self.deleted_items.append((item, size))
        self.total_deleted_size += size

    def add_error(self, message: str) -> None:
        """Add error message to results"""
        self.errors.append(message)


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


def archive_item(item: Path, source_base: Path, dest_base: Path, dry_run: bool) -> bool:
    """
    Archive file or directory to destination preserving structure.

    Args:
        item: Path to file or directory to archive
        source_base: Base path for source (to calculate relative path)
        dest_base: Base path for destination archive
        dry_run: If True, don't actually copy files

    Returns:
        True if successful, False otherwise
    """
    try:
        # Calculate relative path to preserve directory structure
        relative_path = item.relative_to(source_base)
        dest_path = dest_base / relative_path

        if dry_run:
            # In dry-run mode, just return success without copying
            return True

        # Create parent directories if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if item.is_file():
            # Copy file with metadata
            shutil.copy2(item, dest_path)
        else:
            # Copy directory tree
            shutil.copytree(item, dest_path, dirs_exist_ok=True)

        return True
    except (OSError, shutil.Error):
        return False


def verify_archive(source: Path, dest: Path) -> bool:
    """
    Verify archive integrity by comparing sizes and file counts.

    Args:
        source: Original source path
        dest: Archived destination path

    Returns:
        True if archive is valid, False otherwise
    """
    # Check if destination exists
    if not dest.exists():
        return False

    try:
        # For files, compare sizes
        if source.is_file():
            return source.stat().st_size == dest.stat().st_size

        # For directories, compare total sizes and file counts
        source_size = get_size(source)
        dest_size = get_size(dest)

        if source_size != dest_size:
            return False

        # Count files in both
        source_files = sum(1 for _ in source.rglob('*') if _.is_file())
        dest_files = sum(1 for _ in dest.rglob('*') if _.is_file())

        return source_files == dest_files
    except (OSError, PermissionError):
        return False


def delete_item(item: Path, dry_run: bool) -> bool:
    """
    Delete file or directory.

    Args:
        item: Path to file or directory to delete
        dry_run: If True, don't actually delete

    Returns:
        True if successful, False otherwise
    """
    if dry_run:
        # In dry-run mode, just return success without deleting
        return True

    try:
        if item.is_file():
            item.unlink()
        else:
            shutil.rmtree(item)
        return True
    except (OSError, shutil.Error):
        return False


def run_cleanup(config: CleanupConfig, dry_run: bool) -> CleanupResults:
    """
    Run cleanup operation.

    Args:
        config: Cleanup configuration
        dry_run: If True, preview without executing

    Returns:
        Results of cleanup operation
    """
    results = CleanupResults()

    # Process archive directories
    for dir_name in config.archive_dirs:
        dir_path = config.claude_dir / dir_name

        if not dir_path.exists():
            continue

        old_items = find_old_items(dir_path, config.cutoff_date)

        for item in old_items:
            size = get_size(item)

            # Archive item
            if archive_item(item, dir_path, config.archive_dir / dir_name, dry_run):
                # Verify archive
                archived_path = config.archive_dir / dir_name / item.name
                if dry_run or verify_archive(item, archived_path):
                    # Delete original
                    if delete_item(item, dry_run):
                        results.add_archived(item, size)
                    else:
                        results.add_error(f'Failed to delete {item} after archiving')
                else:
                    results.add_error(f'Archive verification failed for {item}')
            else:
                results.add_error(f'Failed to archive {item}')

    # Process delete-only directories
    for dir_name in config.delete_only_dirs:
        dir_path = config.claude_dir / dir_name

        if not dir_path.exists():
            continue

        old_items = find_old_items(dir_path, config.cutoff_date)

        for item in old_items:
            size = get_size(item)

            if delete_item(item, dry_run):
                results.add_deleted(item, size)
            else:
                results.add_error(f'Failed to delete {item}')

    return results


def format_results(results: CleanupResults, config: CleanupConfig, dry_run: bool) -> str:
    """
    Format cleanup results as human-readable output.

    Args:
        results: Cleanup results
        config: Cleanup configuration
        dry_run: Whether this was a dry-run

    Returns:
        Formatted output string
    """
    lines = []

    # Header
    if dry_run:
        lines.append('Claude Data Cleanup - DRY RUN MODE')
        lines.append('=' * 50)
    else:
        lines.append('Claude Data Cleanup - COMPLETE')
        lines.append('=' * 50)

    lines.append(f'Cutoff date: {config.cutoff_date.strftime("%Y-%m-%d")} ({config.retention_days} days ago)')
    lines.append('')

    # Archived items
    if results.archived_items:
        if dry_run:
            lines.append(f'WILL ARCHIVE TO: {config.archive_dir}')
        else:
            lines.append(f'ARCHIVED TO: {config.archive_dir}')

        for item, size in results.archived_items[:10]:  # Show first 10
            mtime = datetime.fromtimestamp(item.stat().st_mtime) if item.exists() else datetime.now()
            lines.append(f'  {item.name} ({format_size(size)}, modified {mtime.strftime("%Y-%m-%d")})')

        if len(results.archived_items) > 10:
            lines.append(f'  ... ({len(results.archived_items) - 10} more items)')
        lines.append('')

    # Deleted items
    if results.deleted_items:
        if dry_run:
            lines.append('WILL DELETE (no archive):')
        else:
            lines.append('DELETED (no archive):')

        for item, size in results.deleted_items[:10]:
            lines.append(f'  {item.name} ({format_size(size)})')

        if len(results.deleted_items) > 10:
            lines.append(f'  ... ({len(results.deleted_items) - 10} more items)')
        lines.append('')

    # Summary
    lines.append('SUMMARY:')
    lines.append(f'  Archive: {format_size(results.total_archived_size)} ({len(results.archived_items)} items)')
    lines.append(f'  Delete: {format_size(results.total_deleted_size)} ({len(results.deleted_items)} items)')
    total_size = results.total_archived_size + results.total_deleted_size
    lines.append(f'  Total space {"to reclaim" if dry_run else "reclaimed"}: {format_size(total_size)}')

    # Errors
    if results.errors:
        lines.append('')
        lines.append('ERRORS:')
        for error in results.errors:
            lines.append(f'  {error}')

    # Footer
    if dry_run:
        lines.append('')
        lines.append('Run with --execute to perform cleanup.')

    return '\n'.join(lines)


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
