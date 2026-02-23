"""Tests for cleanup_claude_data.py"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cleanup_claude_data import CleanupConfig, parse_args


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
