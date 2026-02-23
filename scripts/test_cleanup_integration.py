#!/usr/bin/env python3
"""Integration tests for cleanup script"""
import os
import sys
import tempfile
import time
from pathlib import Path

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
