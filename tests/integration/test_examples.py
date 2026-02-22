"""
Integration tests for example workflow scripts (examples/*.sh).
"""

import subprocess
from pathlib import Path

import pytest

from tests.conftest import project_root


class TestExampleScriptsHelp:
    """Example scripts must run with --help and show usage."""

    def test_holiday_import_help(self, project_root: Path):
        """holiday-import.sh --help exits 0 and shows usage."""
        script = project_root / "examples" / "holiday-import.sh"
        if not script.exists():
            pytest.skip("holiday-import.sh not found")
        result = subprocess.run(
            [str(script), "--help"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=10,
        )
        assert result.returncode == 0
        out = result.stdout + result.stderr
        assert "Usage" in out or "usage" in out.lower()
        assert "holiday" in out.lower() or "trip" in out.lower()

    def test_adventure_camp_workflow_help(self, project_root: Path):
        """adventure-camp-workflow.sh --help exits 0 and shows usage."""
        script = project_root / "examples" / "adventure-camp-workflow.sh"
        if not script.exists():
            pytest.skip("adventure-camp-workflow.sh not found")
        result = subprocess.run(
            [str(script), "--help"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=10,
        )
        assert result.returncode == 0
        out = result.stdout + result.stderr
        assert "Usage" in out or "usage" in out.lower()
        assert "Adventure" in out or "adventure" in out
