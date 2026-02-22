"""
Integration tests for pg-setup-darktable script.
"""

import pytest


class TestPgSetupDarktableBasic:
    """Basic functionality tests for pg-setup-darktable."""

    def test_help(self, run_script):
        """pg-setup-darktable --help shows usage."""
        result = run_script('pg-setup-darktable', '--help')
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert 'Usage' in output or 'usage' in output.lower()
        assert '--check' in output or 'check' in output.lower()

    def test_check(self, run_script):
        """pg-setup-darktable --check runs without error."""
        result = run_script('pg-setup-darktable', '--check')
        # Exit 0 if darktable found, non-zero otherwise; must not crash
        assert result.returncode in (0, 1)
        output = result.stdout + result.stderr
        assert 'darktable' in output.lower() or 'check' in output.lower()
