"""Tests for cleanup_claude_data.py"""
import os
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
