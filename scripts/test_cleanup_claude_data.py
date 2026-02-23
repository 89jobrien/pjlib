"""Tests for cleanup_claude_data.py"""
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cleanup_claude_data import (
    CleanupConfig,
    CleanupResults,
    find_old_items,
    find_temp_files,
    format_results,
    parse_args,
    run_cleanup,
)


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


# Task 8: Cleanup Results Dataclass
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


# Task 9: Main Cleanup Orchestration
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


# Task 10: Output Formatting and Reporting
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


# Task 12: Handle Temp Files and Patterns
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
