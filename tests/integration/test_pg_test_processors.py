"""
Integration tests for pg-test-processors script.
"""

import pytest


class TestPgTestProcessorsBasic:
    """Basic functionality tests for pg-test-processors."""

    def test_help(self, run_script):
        """pg-test-processors --help shows usage."""
        result = run_script('pg-test-processors', '--help')
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert 'USAGE' in output or 'usage' in output.lower()
        assert 'darktable' in output.lower() or 'imagemagick' in output.lower()
