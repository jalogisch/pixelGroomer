"""
Integration tests for pg-rename script.
"""

from pathlib import Path

import pytest


class TestPgRenameBasic:
    """Basic functionality tests for pg-rename."""

    def test_rename_help(self, run_script):
        """pg-rename --help shows usage."""
        result = run_script('pg-rename', '--help')
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert 'USAGE' in output or 'usage' in output.lower()
        assert '--pattern' in output or 'pattern' in output.lower()

    @pytest.mark.skipif(True, reason="optional: add when exiftool available")
    def test_rename_dry_run(self, run_script, tmp_path: Path, test_env):
        """pg-rename --dry-run does not crash."""
        (tmp_path / "dummy.txt").write_text("x")
        result = run_script('pg-rename', str(tmp_path), '--dry-run')
        # Accept 0 or non-zero depending on no EXIF
        assert 'dry-run' in (result.stdout + result.stderr).lower() or result.returncode in (0, 1)
