"""Tests for cleanup_claude_data.py"""
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cleanup_claude_data import CleanupConfig, find_old_items, parse_args


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


def test_get_size_file():
    """Test calculating size of a file"""
    from cleanup_claude_data import get_size

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_file = tmp_path / 'test.txt'
        test_file.write_text('x' * 1024)  # 1KB file

        size = get_size(test_file)
        assert size == 1024


def test_get_size_directory():
    """Test calculating size of a directory recursively"""
    from cleanup_claude_data import get_size

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
    from cleanup_claude_data import format_size

    assert format_size(0) == '0B'
    assert format_size(1024) == '1.0KB'
    assert format_size(1024 * 1024) == '1.0MB'
    assert format_size(1024 * 1024 * 1024) == '1.0GB'
    assert format_size(500) == '500B'


# Task 5: Archive Files to iCloud
def test_archive_item_file():
    """Test archiving a single file with directory structure preservation"""
    from cleanup_claude_data import archive_item

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        source_base = tmp_path / 'source'
        dest_base = tmp_path / 'dest'

        # Create source structure
        source_dir = source_base / 'projects'
        source_dir.mkdir(parents=True)
        test_file = source_dir / 'test.txt'
        test_file.write_text('test content')

        # Archive the file
        result = archive_item(test_file, source_base, dest_base, dry_run=False)

        assert result is True
        # Check destination preserves structure
        dest_file = dest_base / 'projects' / 'test.txt'
        assert dest_file.exists()
        assert dest_file.read_text() == 'test content'


def test_archive_item_directory():
    """Test archiving a directory recursively"""
    from cleanup_claude_data import archive_item

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        source_base = tmp_path / 'source'
        dest_base = tmp_path / 'dest'

        # Create source directory structure
        source_dir = source_base / 'projects' / 'my-project'
        source_dir.mkdir(parents=True)
        (source_dir / 'file1.txt').write_text('content1')
        subdir = source_dir / 'subdir'
        subdir.mkdir()
        (subdir / 'file2.txt').write_text('content2')

        # Archive the directory
        result = archive_item(source_dir, source_base, dest_base, dry_run=False)

        assert result is True
        # Check destination preserves full structure
        dest_dir = dest_base / 'projects' / 'my-project'
        assert dest_dir.exists()
        assert (dest_dir / 'file1.txt').read_text() == 'content1'
        assert (dest_dir / 'subdir' / 'file2.txt').read_text() == 'content2'


def test_archive_item_dry_run():
    """Test archive dry-run mode doesn't copy files"""
    from cleanup_claude_data import archive_item

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        source_base = tmp_path / 'source'
        dest_base = tmp_path / 'dest'

        source_dir = source_base / 'projects'
        source_dir.mkdir(parents=True)
        test_file = source_dir / 'test.txt'
        test_file.write_text('test content')

        # Archive in dry-run mode
        result = archive_item(test_file, source_base, dest_base, dry_run=True)

        assert result is True
        # Destination should not exist
        dest_file = dest_base / 'projects' / 'test.txt'
        assert not dest_file.exists()


# Task 6: Verify Archive Integrity
def test_verify_archive_success():
    """Test successful archive verification"""
    from cleanup_claude_data import verify_archive

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create matching source and destination
        source = tmp_path / 'source' / 'test.txt'
        source.parent.mkdir(parents=True)
        source.write_text('x' * 1024)

        dest = tmp_path / 'dest' / 'test.txt'
        dest.parent.mkdir(parents=True)
        shutil.copy2(source, dest)

        # Verify should succeed
        assert verify_archive(source, dest) is True


def test_verify_archive_size_mismatch():
    """Test verification fails on size mismatch"""
    from cleanup_claude_data import verify_archive

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        source = tmp_path / 'source' / 'test.txt'
        source.parent.mkdir(parents=True)
        source.write_text('x' * 1024)

        dest = tmp_path / 'dest' / 'test.txt'
        dest.parent.mkdir(parents=True)
        dest.write_text('x' * 512)  # Different size

        # Verify should fail
        assert verify_archive(source, dest) is False


def test_verify_archive_missing_destination():
    """Test verification fails when destination doesn't exist"""
    from cleanup_claude_data import verify_archive

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        source = tmp_path / 'source' / 'test.txt'
        source.parent.mkdir(parents=True)
        source.write_text('test content')

        dest = tmp_path / 'dest' / 'test.txt'  # Doesn't exist

        # Verify should fail
        assert verify_archive(source, dest) is False


# Task 7: Delete Items
def test_delete_item_file():
    """Test deleting a file"""
    from cleanup_claude_data import delete_item

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')

        assert test_file.exists()
        result = delete_item(test_file, dry_run=False)

        assert result is True
        assert not test_file.exists()


def test_delete_item_directory():
    """Test deleting a directory recursively"""
    from cleanup_claude_data import delete_item

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_dir = tmp_path / 'test_dir'
        test_dir.mkdir()
        (test_dir / 'file1.txt').write_text('content1')
        subdir = test_dir / 'subdir'
        subdir.mkdir()
        (subdir / 'file2.txt').write_text('content2')

        assert test_dir.exists()
        result = delete_item(test_dir, dry_run=False)

        assert result is True
        assert not test_dir.exists()


def test_delete_item_dry_run():
    """Test delete dry-run mode doesn't actually delete"""
    from cleanup_claude_data import delete_item

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')

        assert test_file.exists()
        result = delete_item(test_file, dry_run=True)

        assert result is True
        assert test_file.exists()  # Should still exist in dry-run
