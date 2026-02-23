# Directory Cleanup Script Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python script to reclaim ~750MB from ~/.claude by archiving old session data to iCloud and deleting temporary files

**Architecture:** CLI tool with dry-run mode, age-based filtering (7-day retention), archive-then-delete workflow for valuable data, direct deletion for regenerable data

**Tech Stack:** Python 3.12+, pathlib, shutil, dataclasses, argparse (stdlib only)

---

## Task 1: Project Setup and CLI Argument Parsing

**Files:**
- Create: `scripts/cleanup_claude_data.py`
- Create: `scripts/test_cleanup_claude_data.py`

**Step 1: Write failing test for CLI argument parsing**

```python
# scripts/test_cleanup_claude_data.py
"""Tests for cleanup_claude_data.py"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from cleanup_claude_data import parse_args


def test_parse_args_defaults():
    """Test default argument values"""
    args = parse_args(['--dry-run'])
    assert args.dry_run is True
    assert args.execute is False
    assert args.days == 7


def test_parse_args_execute_mode():
    """Test execute mode flag"""
    args = parse_args(['--execute'])
    assert args.execute is True
    assert args.dry_run is False


def test_parse_args_custom_days():
    """Test custom retention days"""
    args = parse_args(['--days', '14'])
    assert args.days == 14
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_parse_args_defaults -v`

Expected: FAIL with "cannot import name 'parse_args'"

**Step 3: Write minimal implementation for CLI parsing**

```python
# scripts/cleanup_claude_data.py
#!/usr/bin/env python3
"""
Claude workspace cleanup script.

Reclaims disk space by archiving old session data to iCloud
and deleting temporary files based on configurable retention policy.
"""
import argparse
from pathlib import Path
from typing import NamedTuple


class Args(NamedTuple):
    """Parsed CLI arguments"""
    dry_run: bool
    execute: bool
    days: int


def parse_args(argv: list[str] | None = None) -> Args:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Clean up Claude workspace by archiving old data and removing temp files'
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Preview changes without executing (default)'
    )
    mode_group.add_argument(
        '--execute',
        action='store_true',
        help='Actually perform cleanup operations'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Retention period in days (default: 7)'
    )

    parsed = parser.parse_args(argv)

    return Args(
        dry_run=not parsed.execute,
        execute=parsed.execute,
        days=parsed.days
    )


def main() -> int:
    """Main entry point"""
    args = parse_args()
    print(f"Args: dry_run={args.dry_run}, execute={args.execute}, days={args.days}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py -v`

Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add scripts/cleanup_claude_data.py scripts/test_cleanup_claude_data.py
git commit -m "feat: add CLI argument parsing for cleanup script"
```

---

## Task 2: Configuration and Data Models

**Files:**
- Modify: `scripts/cleanup_claude_data.py`
- Modify: `scripts/test_cleanup_claude_data.py`

**Step 1: Write failing test for configuration dataclass**

```python
# scripts/test_cleanup_claude_data.py (add to existing file)
from datetime import datetime, timedelta
from cleanup_claude_data import CleanupConfig


def test_cleanup_config_creation():
    """Test cleanup configuration with default paths"""
    config = CleanupConfig(
        claude_dir=Path.home() / '.claude',
        archive_dir=Path.home() / 'Documents' / 'claude-archives' / '2026-02-23',
        retention_days=7
    )

    assert config.claude_dir == Path.home() / '.claude'
    assert config.archive_dir.parent.name == 'claude-archives'
    assert config.retention_days == 7
    assert config.cutoff_date < datetime.now()


def test_cleanup_config_cutoff_calculation():
    """Test cutoff date calculation"""
    config = CleanupConfig(
        claude_dir=Path.home() / '.claude',
        archive_dir=Path.home() / 'Documents' / 'claude-archives' / '2026-02-23',
        retention_days=7
    )

    expected_cutoff = datetime.now() - timedelta(days=7)
    # Allow 1 second tolerance for test execution time
    assert abs((config.cutoff_date - expected_cutoff).total_seconds()) < 1
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_cleanup_config_creation -v`

Expected: FAIL with "cannot import name 'CleanupConfig'"

**Step 3: Write minimal implementation for configuration**

```python
# scripts/cleanup_claude_data.py (add after imports)
from dataclasses import dataclass
from datetime import datetime, timedelta


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
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_cleanup_config_creation scripts/test_cleanup_claude_data.py::test_cleanup_config_cutoff_calculation -v`

Expected: Both tests PASS

**Step 5: Commit**

```bash
git add scripts/cleanup_claude_data.py scripts/test_cleanup_claude_data.py
git commit -m "feat: add cleanup configuration dataclass"
```

---

## Task 3: File Discovery and Age Filtering

**Files:**
- Modify: `scripts/cleanup_claude_data.py`
- Modify: `scripts/test_cleanup_claude_data.py`

**Step 1: Write failing test for file discovery**

```python
# scripts/test_cleanup_claude_data.py (add to existing file)
import tempfile
import os
import time
from cleanup_claude_data import find_old_items


def test_find_old_items_by_age():
    """Test finding files older than cutoff date"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create old file (modified 10 days ago)
        old_file = tmp_path / 'old.txt'
        old_file.write_text('old content')
        old_time = time.time() - (10 * 24 * 60 * 60)  # 10 days ago
        os.utime(old_file, (old_time, old_time))

        # Create new file (modified 1 day ago)
        new_file = tmp_path / 'new.txt'
        new_file.write_text('new content')
        new_time = time.time() - (1 * 24 * 60 * 60)  # 1 day ago
        os.utime(new_file, (new_time, new_time))

        # Find items older than 7 days
        cutoff = datetime.now() - timedelta(days=7)
        old_items = find_old_items(tmp_path, cutoff)

        assert len(old_items) == 1
        assert old_items[0].name == 'old.txt'


def test_find_old_items_empty_directory():
    """Test handling of empty directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cutoff = datetime.now() - timedelta(days=7)
        old_items = find_old_items(Path(tmpdir), cutoff)
        assert len(old_items) == 0
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_find_old_items_by_age -v`

Expected: FAIL with "cannot import name 'find_old_items'"

**Step 3: Write minimal implementation for file discovery**

```python
# scripts/cleanup_claude_data.py (add after CleanupConfig)


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
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_find_old_items_by_age scripts/test_cleanup_claude_data.py::test_find_old_items_empty_directory -v`

Expected: Both tests PASS

**Step 5: Commit**

```bash
git add scripts/cleanup_claude_data.py scripts/test_cleanup_claude_data.py
git commit -m "feat: add file discovery by age"
```

---

## Task 4: Calculate Item Size

**Files:**
- Modify: `scripts/cleanup_claude_data.py`
- Modify: `scripts/test_cleanup_claude_data.py`

**Step 1: Write failing test for size calculation**

```python
# scripts/test_cleanup_claude_data.py (add to existing file)
from cleanup_claude_data import get_size, format_size


def test_get_size_file():
    """Test calculating size of a file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_file = tmp_path / 'test.txt'
        test_file.write_text('x' * 1024)  # 1KB file

        size = get_size(test_file)
        assert size == 1024


def test_get_size_directory():
    """Test calculating size of a directory recursively"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create nested structure
        (tmp_path / 'file1.txt').write_text('x' * 512)
        subdir = tmp_path / 'subdir'
        subdir.mkdir()
        (subdir / 'file2.txt').write_text('x' * 1024)

        size = get_size(tmp_path)
        assert size == 512 + 1024


def test_format_size():
    """Test human-readable size formatting"""
    assert format_size(0) == '0B'
    assert format_size(1024) == '1.0KB'
    assert format_size(1024 * 1024) == '1.0MB'
    assert format_size(1024 * 1024 * 1024) == '1.0GB'
    assert format_size(500) == '500B'
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_get_size_file -v`

Expected: FAIL with "cannot import name 'get_size'"

**Step 3: Write minimal implementation for size calculation**

```python
# scripts/cleanup_claude_data.py (add after find_old_items)


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
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_get_size_file scripts/test_cleanup_claude_data.py::test_get_size_directory scripts/test_cleanup_claude_data.py::test_format_size -v`

Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add scripts/cleanup_claude_data.py scripts/test_cleanup_claude_data.py
git commit -m "feat: add size calculation and formatting"
```

---

## Task 5: Archive Files to iCloud

**Files:**
- Modify: `scripts/cleanup_claude_data.py`
- Modify: `scripts/test_cleanup_claude_data.py`

**Step 1: Write failing test for archiving**

```python
# scripts/test_cleanup_claude_data.py (add to existing file)
from cleanup_claude_data import archive_item


def test_archive_item_file():
    """Test archiving a single file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create source file
        source = tmp_path / 'source' / 'file.txt'
        source.parent.mkdir()
        source.write_text('test content')

        # Archive to destination
        dest_base = tmp_path / 'archive'
        archive_item(source, tmp_path / 'source', dest_base, dry_run=False)

        # Verify archive exists
        archived = dest_base / 'file.txt'
        assert archived.exists()
        assert archived.read_text() == 'test content'


def test_archive_item_directory():
    """Test archiving a directory with contents"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create source directory
        source = tmp_path / 'source' / 'mydir'
        source.mkdir(parents=True)
        (source / 'file1.txt').write_text('content1')
        (source / 'subdir').mkdir()
        (source / 'subdir' / 'file2.txt').write_text('content2')

        # Archive to destination
        dest_base = tmp_path / 'archive'
        archive_item(source, tmp_path / 'source', dest_base, dry_run=False)

        # Verify structure preserved
        archived = dest_base / 'mydir'
        assert archived.exists()
        assert (archived / 'file1.txt').read_text() == 'content1'
        assert (archived / 'subdir' / 'file2.txt').read_text() == 'content2'


def test_archive_item_dry_run():
    """Test dry-run mode doesn't create files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        source = tmp_path / 'source' / 'file.txt'
        source.parent.mkdir()
        source.write_text('test')

        dest_base = tmp_path / 'archive'
        archive_item(source, tmp_path / 'source', dest_base, dry_run=True)

        # Verify nothing created in dry-run
        assert not dest_base.exists()
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_archive_item_file -v`

Expected: FAIL with "cannot import name 'archive_item'"

**Step 3: Write minimal implementation for archiving**

```python
# scripts/cleanup_claude_data.py (add after format_size)
import shutil


def archive_item(
    item: Path,
    source_base: Path,
    dest_base: Path,
    dry_run: bool
) -> bool:
    """
    Archive a file or directory to destination.

    Args:
        item: Item to archive
        source_base: Base directory for source (for relative path calculation)
        dest_base: Base directory for archive destination
        dry_run: If True, don't actually copy files

    Returns:
        True if successful, False otherwise
    """
    if dry_run:
        return True

    try:
        # Calculate relative path to preserve structure
        rel_path = item.relative_to(source_base)
        dest = dest_base / rel_path

        # Create parent directory
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Copy file or directory
        if item.is_file():
            shutil.copy2(item, dest)
        else:
            shutil.copytree(item, dest, dirs_exist_ok=True)

        return True
    except (OSError, shutil.Error):
        return False
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_archive_item_file scripts/test_cleanup_claude_data.py::test_archive_item_directory scripts/test_cleanup_claude_data.py::test_archive_item_dry_run -v`

Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add scripts/cleanup_claude_data.py scripts/test_cleanup_claude_data.py
git commit -m "feat: add archive functionality"
```

---

## Task 6: Verify Archive Integrity

**Files:**
- Modify: `scripts/cleanup_claude_data.py`
- Modify: `scripts/test_cleanup_claude_data.py`

**Step 1: Write failing test for verification**

```python
# scripts/test_cleanup_claude_data.py (add to existing file)
from cleanup_claude_data import verify_archive


def test_verify_archive_success():
    """Test verification succeeds for valid archive"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create source and destination
        source = tmp_path / 'source' / 'file.txt'
        source.parent.mkdir()
        source.write_text('x' * 1024)

        dest = tmp_path / 'dest' / 'file.txt'
        dest.parent.mkdir()
        shutil.copy2(source, dest)

        # Verify should succeed
        assert verify_archive(source, dest) is True


def test_verify_archive_size_mismatch():
    """Test verification fails when sizes don't match"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        source = tmp_path / 'source' / 'file.txt'
        source.parent.mkdir()
        source.write_text('x' * 1024)

        dest = tmp_path / 'dest' / 'file.txt'
        dest.parent.mkdir()
        dest.write_text('x' * 512)  # Different size

        # Verify should fail
        assert verify_archive(source, dest) is False


def test_verify_archive_missing_destination():
    """Test verification fails when destination doesn't exist"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        source = tmp_path / 'source' / 'file.txt'
        source.parent.mkdir()
        source.write_text('test')

        dest = tmp_path / 'dest' / 'file.txt'

        # Verify should fail (dest doesn't exist)
        assert verify_archive(source, dest) is False
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_verify_archive_success -v`

Expected: FAIL with "cannot import name 'verify_archive'"

**Step 3: Write minimal implementation for verification**

```python
# scripts/cleanup_claude_data.py (add after archive_item)


def verify_archive(source: Path, dest: Path) -> bool:
    """
    Verify archive was copied successfully.

    Args:
        source: Original item
        dest: Archived item

    Returns:
        True if verification passes, False otherwise
    """
    if not dest.exists():
        return False

    # Compare sizes
    source_size = get_size(source)
    dest_size = get_size(dest)

    if source_size != dest_size:
        return False

    # For directories, compare file counts
    if source.is_dir():
        source_files = list(source.rglob('*'))
        dest_files = list(dest.rglob('*'))

        if len(source_files) != len(dest_files):
            return False

    return True
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_verify_archive_success scripts/test_cleanup_claude_data.py::test_verify_archive_size_mismatch scripts/test_cleanup_claude_data.py::test_verify_archive_missing_destination -v`

Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add scripts/cleanup_claude_data.py scripts/test_cleanup_claude_data.py
git commit -m "feat: add archive verification"
```

---

## Task 7: Delete Items

**Files:**
- Modify: `scripts/cleanup_claude_data.py`
- Modify: `scripts/test_cleanup_claude_data.py`

**Step 1: Write failing test for deletion**

```python
# scripts/test_cleanup_claude_data.py (add to existing file)
from cleanup_claude_data import delete_item


def test_delete_item_file():
    """Test deleting a file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')

        assert test_file.exists()
        assert delete_item(test_file, dry_run=False) is True
        assert not test_file.exists()


def test_delete_item_directory():
    """Test deleting a directory and contents"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        test_dir = tmp_path / 'testdir'
        test_dir.mkdir()
        (test_dir / 'file.txt').write_text('content')
        (test_dir / 'subdir').mkdir()

        assert test_dir.exists()
        assert delete_item(test_dir, dry_run=False) is True
        assert not test_dir.exists()


def test_delete_item_dry_run():
    """Test dry-run mode doesn't delete"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')

        assert delete_item(test_file, dry_run=True) is True
        assert test_file.exists()  # Still exists in dry-run
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_delete_item_file -v`

Expected: FAIL with "cannot import name 'delete_item'"

**Step 3: Write minimal implementation for deletion**

```python
# scripts/cleanup_claude_data.py (add after verify_archive)


def delete_item(item: Path, dry_run: bool) -> bool:
    """
    Delete a file or directory.

    Args:
        item: Item to delete
        dry_run: If True, don't actually delete

    Returns:
        True if successful, False otherwise
    """
    if dry_run:
        return True

    try:
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
        return True
    except (OSError, shutil.Error):
        return False
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_delete_item_file scripts/test_cleanup_claude_data.py::test_delete_item_directory scripts/test_cleanup_claude_data.py::test_delete_item_dry_run -v`

Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add scripts/cleanup_claude_data.py scripts/test_cleanup_claude_data.py
git commit -m "feat: add delete functionality"
```

---

## Task 8: Cleanup Results Dataclass

**Files:**
- Modify: `scripts/cleanup_claude_data.py`
- Modify: `scripts/test_cleanup_claude_data.py`

**Step 1: Write failing test for results tracking**

```python
# scripts/test_cleanup_claude_data.py (add to existing file)
from cleanup_claude_data import CleanupResults


def test_cleanup_results_init():
    """Test cleanup results initialization"""
    results = CleanupResults()

    assert results.archived_items == []
    assert results.deleted_items == []
    assert results.errors == []
    assert results.total_archived_size == 0
    assert results.total_deleted_size == 0


def test_cleanup_results_add_archived():
    """Test adding archived item"""
    results = CleanupResults()
    results.add_archived(Path('/test/file.txt'), 1024)

    assert len(results.archived_items) == 1
    assert results.archived_items[0][0] == Path('/test/file.txt')
    assert results.archived_items[0][1] == 1024
    assert results.total_archived_size == 1024


def test_cleanup_results_add_deleted():
    """Test adding deleted item"""
    results = CleanupResults()
    results.add_deleted(Path('/test/file.txt'), 512)

    assert len(results.deleted_items) == 1
    assert results.total_deleted_size == 512


def test_cleanup_results_add_error():
    """Test adding error"""
    results = CleanupResults()
    results.add_error('Test error message')

    assert len(results.errors) == 1
    assert results.errors[0] == 'Test error message'
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_cleanup_results_init -v`

Expected: FAIL with "cannot import name 'CleanupResults'"

**Step 3: Write minimal implementation for results**

```python
# scripts/cleanup_claude_data.py (add after CleanupConfig)


@dataclass
class CleanupResults:
    """Results of cleanup operation"""
    archived_items: list[tuple[Path, int]] = None
    deleted_items: list[tuple[Path, int]] = None
    errors: list[str] = None
    total_archived_size: int = 0
    total_deleted_size: int = 0

    def __post_init__(self):
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
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py -k "cleanup_results" -v`

Expected: All 4 tests PASS

**Step 5: Commit**

```bash
git add scripts/cleanup_claude_data.py scripts/test_cleanup_claude_data.py
git commit -m "feat: add cleanup results tracking"
```

---

## Task 9: Main Cleanup Orchestration

**Files:**
- Modify: `scripts/cleanup_claude_data.py`
- Modify: `scripts/test_cleanup_claude_data.py`

**Step 1: Write failing test for cleanup orchestration**

```python
# scripts/test_cleanup_claude_data.py (add to existing file)
from cleanup_claude_data import run_cleanup


def test_run_cleanup_archive_workflow():
    """Test end-to-end archive workflow"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Setup claude_dir with old project
        claude_dir = tmp_path / '.claude'
        projects_dir = claude_dir / 'projects'
        projects_dir.mkdir(parents=True)

        old_project = projects_dir / 'old-project'
        old_project.mkdir()
        (old_project / 'file.txt').write_text('x' * 1024)

        # Make it old (10 days)
        old_time = time.time() - (10 * 24 * 60 * 60)
        os.utime(old_project, (old_time, old_time))

        # Setup archive destination
        archive_base = tmp_path / 'Documents' / 'claude-archives'
        archive_dir = archive_base / '2026-02-23'

        # Create config
        config = CleanupConfig(
            claude_dir=claude_dir,
            archive_dir=archive_dir,
            retention_days=7
        )

        # Run cleanup
        results = run_cleanup(config, dry_run=False)

        # Verify archived
        assert len(results.archived_items) == 1
        assert results.total_archived_size > 0

        # Verify source deleted
        assert not old_project.exists()

        # Verify archive exists
        archived = archive_dir / 'projects' / 'old-project'
        assert archived.exists()


def test_run_cleanup_delete_workflow():
    """Test end-to-end delete workflow"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Setup claude_dir with old debug data
        claude_dir = tmp_path / '.claude'
        debug_dir = claude_dir / 'debug'
        debug_dir.mkdir(parents=True)

        old_file = debug_dir / 'old.log'
        old_file.write_text('x' * 512)

        # Make it old
        old_time = time.time() - (10 * 24 * 60 * 60)
        os.utime(old_file, (old_time, old_time))

        archive_dir = tmp_path / 'Documents' / 'claude-archives' / '2026-02-23'

        config = CleanupConfig(
            claude_dir=claude_dir,
            archive_dir=archive_dir,
            retention_days=7
        )

        results = run_cleanup(config, dry_run=False)

        # Verify deleted
        assert len(results.deleted_items) == 1
        assert not old_file.exists()

        # Verify NOT archived
        assert not (archive_dir / 'debug').exists()
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_run_cleanup_archive_workflow -v`

Expected: FAIL with "cannot import name 'run_cleanup'"

**Step 3: Write minimal implementation for cleanup orchestration**

```python
# scripts/cleanup_claude_data.py (add after delete_item)


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
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_run_cleanup_archive_workflow scripts/test_cleanup_claude_data.py::test_run_cleanup_delete_workflow -v`

Expected: Both tests PASS

**Step 5: Commit**

```bash
git add scripts/cleanup_claude_data.py scripts/test_cleanup_claude_data.py
git commit -m "feat: add cleanup orchestration"
```

---

## Task 10: Output Formatting and Reporting

**Files:**
- Modify: `scripts/cleanup_claude_data.py`
- Modify: `scripts/test_cleanup_claude_data.py`

**Step 1: Write failing test for output formatting**

```python
# scripts/test_cleanup_claude_data.py (add to existing file)
from cleanup_claude_data import format_results


def test_format_results_dry_run():
    """Test formatting dry-run results"""
    results = CleanupResults()
    results.add_archived(Path('/claude/projects/old'), 100 * 1024 * 1024)
    results.add_deleted(Path('/claude/debug/old.log'), 50 * 1024 * 1024)

    config = CleanupConfig(
        claude_dir=Path.home() / '.claude',
        archive_dir=Path.home() / 'Documents' / 'claude-archives' / '2026-02-23',
        retention_days=7
    )

    output = format_results(results, config, dry_run=True)

    assert 'DRY RUN MODE' in output
    assert 'WILL ARCHIVE' in output
    assert 'WILL DELETE' in output
    assert '100.0MB' in output
    assert '50.0MB' in output
    assert 'Run with --execute' in output


def test_format_results_execute():
    """Test formatting execute results"""
    results = CleanupResults()
    results.add_archived(Path('/claude/projects/old'), 100 * 1024 * 1024)

    config = CleanupConfig(
        claude_dir=Path.home() / '.claude',
        archive_dir=Path.home() / 'Documents' / 'claude-archives' / '2026-02-23',
        retention_days=7
    )

    output = format_results(results, config, dry_run=False)

    assert 'DRY RUN MODE' not in output
    assert 'ARCHIVED' in output or 'Archive' in output
    assert '100.0MB' in output
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_format_results_dry_run -v`

Expected: FAIL with "cannot import name 'format_results'"

**Step 3: Write minimal implementation for output formatting**

```python
# scripts/cleanup_claude_data.py (add after run_cleanup)


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
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_format_results_dry_run scripts/test_cleanup_claude_data.py::test_format_results_execute -v`

Expected: Both tests PASS

**Step 5: Commit**

```bash
git add scripts/cleanup_claude_data.py scripts/test_cleanup_claude_data.py
git commit -m "feat: add output formatting"
```

---

## Task 11: Integrate Main Entry Point

**Files:**
- Modify: `scripts/cleanup_claude_data.py`

**Step 1: Update main() function to orchestrate cleanup**

```python
# scripts/cleanup_claude_data.py (replace existing main function)


def main() -> int:
    """Main entry point"""
    args = parse_args()

    # Setup configuration
    today = datetime.now().strftime('%Y-%m-%d')
    claude_dir = Path.home() / '.claude'
    archive_dir = Path.home() / 'Documents' / 'claude-archives' / today

    config = CleanupConfig(
        claude_dir=claude_dir,
        archive_dir=archive_dir,
        retention_days=args.days
    )

    # Pre-flight checks
    if not claude_dir.exists():
        print(f'Error: Claude directory not found: {claude_dir}')
        return 1

    documents_dir = Path.home() / 'Documents'
    if not documents_dir.exists():
        print(f'Error: Documents directory not found: {documents_dir}')
        return 1

    # Create archive directory if executing
    if args.execute and not config.archive_dir.exists():
        config.archive_dir.mkdir(parents=True, exist_ok=True)

    # Run cleanup
    results = run_cleanup(config, dry_run=args.dry_run)

    # Display results
    output = format_results(results, config, dry_run=args.dry_run)
    print(output)

    # Return error code if there were errors
    return 1 if results.errors else 0
```

**Step 2: Test manually**

Run: `cd /Users/joe/.claude && python scripts/cleanup_claude_data.py --dry-run`

Expected: Output showing items to archive/delete

**Step 3: Commit**

```bash
git add scripts/cleanup_claude_data.py
git commit -m "feat: integrate main entry point"
```

---

## Task 12: Handle Temp Files and Patterns

**Files:**
- Modify: `scripts/cleanup_claude_data.py`
- Modify: `scripts/test_cleanup_claude_data.py`

**Step 1: Write failing test for temp file handling**

```python
# scripts/test_cleanup_claude_data.py (add to existing file)
from cleanup_claude_data import find_temp_files


def test_find_temp_files_paste_cache():
    """Test finding paste-cache files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        paste_cache = tmp_path / 'paste-cache'
        paste_cache.mkdir()
        (paste_cache / 'file1.txt').write_text('temp')
        (paste_cache / 'file2.txt').write_text('temp')

        temp_files = find_temp_files(tmp_path, ['paste-cache'])
        assert len(temp_files) >= 2


def test_find_temp_files_backup_pattern():
    """Test finding backup files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        (tmp_path / 'settings.json.backup').write_text('{}')
        (tmp_path / 'config.backup.20260222').write_text('{}')
        (tmp_path / 'normal.json').write_text('{}')

        temp_files = find_temp_files(tmp_path, ['*.backup*'])

        assert len(temp_files) == 2
        assert all('.backup' in f.name for f in temp_files)
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_find_temp_files_paste_cache -v`

Expected: FAIL with "cannot import name 'find_temp_files'"

**Step 3: Write minimal implementation for temp file finding**

```python
# scripts/cleanup_claude_data.py (add after find_old_items)
import fnmatch


def find_temp_files(directory: Path, patterns: list[str]) -> list[Path]:
    """
    Find files matching temporary file patterns.

    Args:
        directory: Directory to search
        patterns: List of patterns to match (supports glob patterns)

    Returns:
        List of matching paths
    """
    if not directory.exists():
        return []

    temp_files: list[Path] = []

    for pattern in patterns:
        if '/' not in pattern and '*' not in pattern:
            # Directory name pattern
            target = directory / pattern
            if target.exists():
                if target.is_dir():
                    temp_files.extend(target.rglob('*'))
                    temp_files.append(target)
                else:
                    temp_files.append(target)
        else:
            # Glob pattern
            for item in directory.rglob('*'):
                if fnmatch.fnmatch(item.name, pattern):
                    temp_files.append(item)

    return temp_files
```

**Step 4: Integrate temp file cleanup into run_cleanup**

```python
# scripts/cleanup_claude_data.py (modify run_cleanup, add after delete-only section)

    # Process temp files (delete entirely regardless of age)
    temp_files = find_temp_files(config.claude_dir, config.temp_patterns)

    for item in temp_files:
        if not item.exists():
            continue

        size = get_size(item)

        if delete_item(item, dry_run):
            results.add_deleted(item, size)
        else:
            results.add_error(f'Failed to delete temp file {item}')
```

**Step 5: Run tests to verify they pass**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_claude_data.py::test_find_temp_files_paste_cache scripts/test_cleanup_claude_data.py::test_find_temp_files_backup_pattern -v`

Expected: Both tests PASS

**Step 6: Commit**

```bash
git add scripts/cleanup_claude_data.py scripts/test_cleanup_claude_data.py
git commit -m "feat: add temp file handling"
```

---

## Task 13: Add Logging Support

**Files:**
- Modify: `scripts/cleanup_claude_data.py`

**Step 1: Add logging configuration**

```python
# scripts/cleanup_claude_data.py (add after imports)
import logging
from datetime import datetime


def setup_logging(claude_dir: Path, dry_run: bool) -> None:
    """
    Configure logging for cleanup operations.

    Args:
        claude_dir: Claude directory for log file location
        dry_run: Whether this is a dry-run
    """
    logs_dir = claude_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    log_file = logs_dir / f'cleanup-{timestamp}.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler() if not dry_run else logging.NullHandler()
        ]
    )

    logging.info(f'Cleanup started - dry_run={dry_run}')
```

**Step 2: Add logging calls throughout run_cleanup**

```python
# scripts/cleanup_claude_data.py (modify run_cleanup to add logging)

def run_cleanup(config: CleanupConfig, dry_run: bool) -> CleanupResults:
    """Run cleanup operation with logging"""
    results = CleanupResults()

    logging.info(f'Cutoff date: {config.cutoff_date}')
    logging.info(f'Archive directory: {config.archive_dir}')

    # Process archive directories
    for dir_name in config.archive_dirs:
        dir_path = config.claude_dir / dir_name
        logging.info(f'Processing archive directory: {dir_name}')

        if not dir_path.exists():
            logging.info(f'  Directory does not exist, skipping')
            continue

        old_items = find_old_items(dir_path, config.cutoff_date)
        logging.info(f'  Found {len(old_items)} old items')

        for item in old_items:
            size = get_size(item)
            logging.debug(f'  Archiving {item.name} ({format_size(size)})')

            # Archive item
            if archive_item(item, dir_path, config.archive_dir / dir_name, dry_run):
                archived_path = config.archive_dir / dir_name / item.name
                if dry_run or verify_archive(item, archived_path):
                    if delete_item(item, dry_run):
                        results.add_archived(item, size)
                        logging.info(f'  Archived: {item.name}')
                    else:
                        msg = f'Failed to delete {item} after archiving'
                        results.add_error(msg)
                        logging.error(f'  {msg}')
                else:
                    msg = f'Archive verification failed for {item}'
                    results.add_error(msg)
                    logging.error(f'  {msg}')
            else:
                msg = f'Failed to archive {item}'
                results.add_error(msg)
                logging.error(f'  {msg}')

    # Process delete-only directories
    for dir_name in config.delete_only_dirs:
        dir_path = config.claude_dir / dir_name
        logging.info(f'Processing delete-only directory: {dir_name}')

        if not dir_path.exists():
            logging.info(f'  Directory does not exist, skipping')
            continue

        old_items = find_old_items(dir_path, config.cutoff_date)
        logging.info(f'  Found {len(old_items)} old items')

        for item in old_items:
            size = get_size(item)
            logging.debug(f'  Deleting {item.name} ({format_size(size)})')

            if delete_item(item, dry_run):
                results.add_deleted(item, size)
                logging.info(f'  Deleted: {item.name}')
            else:
                msg = f'Failed to delete {item}'
                results.add_error(msg)
                logging.error(f'  {msg}')

    # Process temp files
    logging.info('Processing temp files')
    temp_files = find_temp_files(config.claude_dir, config.temp_patterns)
    logging.info(f'  Found {len(temp_files)} temp files')

    for item in temp_files:
        if not item.exists():
            continue

        size = get_size(item)

        if delete_item(item, dry_run):
            results.add_deleted(item, size)
            logging.info(f'  Deleted temp: {item.name}')
        else:
            msg = f'Failed to delete temp file {item}'
            results.add_error(msg)
            logging.error(f'  {msg}')

    logging.info(f'Cleanup complete - archived: {format_size(results.total_archived_size)}, '
                 f'deleted: {format_size(results.total_deleted_size)}')

    return results
```

**Step 3: Add logging setup to main()**

```python
# scripts/cleanup_claude_data.py (modify main to add logging setup)

def main() -> int:
    """Main entry point"""
    args = parse_args()

    # Setup configuration
    today = datetime.now().strftime('%Y-%m-%d')
    claude_dir = Path.home() / '.claude'
    archive_dir = Path.home() / 'Documents' / 'claude-archives' / today

    config = CleanupConfig(
        claude_dir=claude_dir,
        archive_dir=archive_dir,
        retention_days=args.days
    )

    # Setup logging
    setup_logging(claude_dir, args.dry_run)

    # ... rest of main() unchanged
```

**Step 4: Test logging works**

Run: `cd /Users/joe/.claude && python scripts/cleanup_claude_data.py --dry-run`

Check: `ls -l /Users/joe/.claude/logs/cleanup-*.log`

Expected: New log file created

**Step 5: Commit**

```bash
git add scripts/cleanup_claude_data.py
git commit -m "feat: add logging support"
```

---

## Task 14: Final Integration Testing

**Files:**
- Create: `scripts/test_cleanup_integration.py`

**Step 1: Write integration test**

```python
# scripts/test_cleanup_integration.py
"""Integration tests for cleanup script"""
import tempfile
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent))

from cleanup_claude_data import CleanupConfig, run_cleanup


def test_full_cleanup_workflow():
    """Test complete cleanup workflow with archive and delete"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Setup mock .claude directory structure
        claude_dir = tmp_path / '.claude'
        claude_dir.mkdir()

        # Create old projects (should be archived)
        projects_dir = claude_dir / 'projects'
        projects_dir.mkdir()
        old_project = projects_dir / 'old-project'
        old_project.mkdir()
        (old_project / 'code.py').write_text('old code')

        # Create new project (should be kept)
        new_project = projects_dir / 'new-project'
        new_project.mkdir()
        (new_project / 'code.py').write_text('new code')

        # Create old debug data (should be deleted)
        debug_dir = claude_dir / 'debug'
        debug_dir.mkdir()
        old_debug = debug_dir / 'old.log'
        old_debug.write_text('old debug log')

        # Create temp files (should be deleted)
        paste_cache = claude_dir / 'paste-cache'
        paste_cache.mkdir()
        (paste_cache / 'temp1.txt').write_text('temp')
        (paste_cache / 'temp2.txt').write_text('temp')

        backup_file = claude_dir / 'settings.json.backup'
        backup_file.write_text('{}')

        # Set old items to 10 days ago
        old_time = time.time() - (10 * 24 * 60 * 60)
        for item in [old_project, old_debug]:
            os.utime(item, (old_time, old_time))

        # Setup archive directory
        archive_dir = tmp_path / 'Documents' / 'claude-archives' / '2026-02-23'

        # Create config
        config = CleanupConfig(
            claude_dir=claude_dir,
            archive_dir=archive_dir,
            retention_days=7
        )

        # Run cleanup (execute mode)
        results = run_cleanup(config, dry_run=False)

        # Verify results
        assert len(results.archived_items) == 1  # old-project
        assert len(results.deleted_items) >= 3  # old.log, temp1, temp2, backup
        assert results.total_archived_size > 0
        assert results.total_deleted_size > 0

        # Verify old project archived and deleted locally
        assert not old_project.exists()
        archived_project = archive_dir / 'projects' / 'old-project'
        assert archived_project.exists()
        assert (archived_project / 'code.py').read_text() == 'old code'

        # Verify new project still exists
        assert new_project.exists()

        # Verify debug deleted (not archived)
        assert not old_debug.exists()
        assert not (archive_dir / 'debug').exists()

        # Verify temp files deleted
        assert not (paste_cache / 'temp1.txt').exists()
        assert not backup_file.exists()


def test_dry_run_changes_nothing():
    """Test dry-run mode doesn't modify filesystem"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        claude_dir = tmp_path / '.claude'
        projects_dir = claude_dir / 'projects'
        projects_dir.mkdir(parents=True)

        old_project = projects_dir / 'old'
        old_project.mkdir()

        old_time = time.time() - (10 * 24 * 60 * 60)
        os.utime(old_project, (old_time, old_time))

        archive_dir = tmp_path / 'Documents' / 'claude-archives' / '2026-02-23'

        config = CleanupConfig(
            claude_dir=claude_dir,
            archive_dir=archive_dir,
            retention_days=7
        )

        # Run in dry-run mode
        results = run_cleanup(config, dry_run=True)

        # Verify results show what would happen
        assert len(results.archived_items) == 1

        # Verify nothing actually changed
        assert old_project.exists()
        assert not archive_dir.exists()


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
```

**Step 2: Run integration tests**

Run: `cd /Users/joe/.claude && python -m pytest scripts/test_cleanup_integration.py -v`

Expected: All integration tests PASS

**Step 3: Commit**

```bash
git add scripts/test_cleanup_integration.py
git commit -m "test: add integration tests"
```

---

## Task 15: Documentation and Usage Examples

**Files:**
- Create: `scripts/README_CLEANUP.md`

**Step 1: Write documentation**

```markdown
# Claude Workspace Cleanup Script

Reclaims disk space from `~/.claude` by archiving old session data to iCloud Drive and deleting temporary files.

## Usage

### Preview (Dry-Run Mode - Default)

See what would be cleaned up without making changes:

```bash
python scripts/cleanup_claude_data.py
```

### Execute Cleanup

Actually perform the cleanup:

```bash
python scripts/cleanup_claude_data.py --execute
```

### Custom Retention Period

Keep last 14 days instead of default 7:

```bash
python scripts/cleanup_claude_data.py --days 14 --execute
```

## What Gets Cleaned

### Archived to iCloud (`~/Documents/claude-archives/YYYY-MM-DD/`)

- `projects/` - Session project contexts
- `transcripts/` - Session transcripts

Files older than retention period are copied to iCloud Drive, then deleted locally.

### Deleted Without Archive

- `plugins/` - Marketplace plugins (re-downloadable)
- `debug/` - Debug logs
- `shell-snapshots/` - Shell state captures
- `file-history/` - File version tracking
- `logs/` - Application logs

Files older than retention period are deleted directly.

### Deleted Entirely

- `paste-cache/` - All temporary clipboard data
- `*.backup*` - Backup files
- `.DS_Store` - macOS metadata files

## Safety Features

- **Dry-run by default** - Must use `--execute` to make changes
- **Archive verification** - Ensures copies succeeded before deleting
- **Detailed logging** - All operations logged to `logs/cleanup-YYYY-MM-DD-HHMMSS.log`
- **Error handling** - Continues on permission errors, reports failures

## Expected Results

Initial cleanup typically reclaims **~750MB** (varies based on usage).

## Logs

Detailed logs written to:

```
~/.claude/logs/cleanup-YYYY-MM-DD-HHMMSS.log
```

## Running Periodically

Recommended frequency: weekly or monthly

Each run creates a new timestamped archive in:

```
~/Documents/claude-archives/YYYY-MM-DD/
```

iCloud Drive automatically syncs these to the cloud.
```

**Step 2: Add to repository**

```bash
git add scripts/README_CLEANUP.md
git commit -m "docs: add cleanup script documentation"
```

---

## Testing & Validation Checklist

Before considering implementation complete:

- [ ] All unit tests pass: `pytest scripts/test_cleanup_claude_data.py -v`
- [ ] All integration tests pass: `pytest scripts/test_cleanup_integration.py -v`
- [ ] Dry-run mode works: `python scripts/cleanup_claude_data.py`
- [ ] Execute mode works on test data
- [ ] Logging creates files in `logs/cleanup-*.log`
- [ ] Archive verification catches corrupted copies
- [ ] Temp files are deleted regardless of age
- [ ] Recent files (< 7 days) are preserved
- [ ] iCloud sync works for archived data

## Post-Implementation Tasks

After implementation complete:

1. **Run initial cleanup**:
   ```bash
   python scripts/cleanup_claude_data.py          # Preview
   python scripts/cleanup_claude_data.py --execute # Execute
   ```

2. **Verify results**:
   - Check space reclaimed: `du -sh ~/.claude`
   - Verify archive exists: `ls ~/Documents/claude-archives/`
   - Check iCloud sync status

3. **Schedule periodic runs** (optional):
   - Add to cron or launchd for automated weekly cleanup
   - Or set calendar reminder to run manually monthly

4. **Monitor iCloud storage**:
   - Archives accumulate over time
   - Delete old archives from iCloud if never accessed
