"""
Integration tests for pg-verify script.
"""

import os
import subprocess
from pathlib import Path

import pytest

from tests.conftest import requires_pillow
from tests.fixtures.photo_factory import create_jpeg


class TestPgVerifyGenerate:
    """Tests for pg-verify --generate mode."""
    
    @requires_pillow
    def test_generate_creates_checksum_file(self, run_script, tmp_path: Path, test_env):
        """pg-verify --generate creates .checksums file."""
        photo_dir = tmp_path / 'photos'
        photo_dir.mkdir()
        
        # Create some photos
        for i in range(3):
            create_jpeg(photo_dir / f'photo_{i}.jpg')
        
        result = run_script('pg-verify', str(photo_dir), '--generate')
        
        assert result.returncode == 0
        
        # Check .checksums file exists
        checksum_file = photo_dir / '.checksums'
        assert checksum_file.exists()
        
        # Check format
        content = checksum_file.read_text()
        lines = [l for l in content.split('\n') if l.strip()]
        assert len(lines) == 3  # One per photo
        
        # Each line should have format: <hash>  <filename>
        for line in lines:
            assert '  ' in line  # Two spaces between hash and filename
    
    @requires_pillow
    def test_generate_recursive(self, run_script, tmp_path: Path, test_env):
        """pg-verify --generate processes subdirectories."""
        base_dir = tmp_path / 'photos'
        sub_dir = base_dir / 'subdir'
        base_dir.mkdir()
        sub_dir.mkdir()
        
        create_jpeg(base_dir / 'top.jpg')
        create_jpeg(sub_dir / 'nested.jpg')
        
        result = run_script('pg-verify', str(base_dir), '--generate')
        
        assert result.returncode == 0
        
        # Both directories should have .checksums
        assert (base_dir / '.checksums').exists()
        assert (sub_dir / '.checksums').exists()
    
    @requires_pillow
    def test_generate_no_recursive(self, run_script, tmp_path: Path, test_env):
        """pg-verify --generate --no-recursive only processes top level."""
        base_dir = tmp_path / 'photos'
        sub_dir = base_dir / 'subdir'
        base_dir.mkdir()
        sub_dir.mkdir()
        
        create_jpeg(base_dir / 'top.jpg')
        create_jpeg(sub_dir / 'nested.jpg')
        
        result = run_script('pg-verify', str(base_dir), '--generate', '--no-recursive')
        
        assert result.returncode == 0
        
        # Only top level should have .checksums
        assert (base_dir / '.checksums').exists()
        assert not (sub_dir / '.checksums').exists()


class TestPgVerifyCheck:
    """Tests for pg-verify --check mode."""
    
    @requires_pillow
    def test_check_valid_files(self, run_script, tmp_path: Path, test_env):
        """pg-verify --check passes for unmodified files."""
        photo_dir = tmp_path / 'photos'
        photo_dir.mkdir()
        
        photos = [create_jpeg(photo_dir / f'photo_{i}.jpg') for i in range(3)]
        
        # Generate checksums first
        run_script('pg-verify', str(photo_dir), '--generate')
        
        # Check should pass
        result = run_script('pg-verify', str(photo_dir), '--check')
        
        # Check both stdout and stderr for success indicators
        output = result.stdout.lower() + result.stderr.lower()
        assert 'verified' in output or 'ok' in output or 'success' in output
    
    @requires_pillow
    def test_check_detects_modified(self, run_script, tmp_path: Path, test_env):
        """pg-verify --check detects modified files."""
        photo_dir = tmp_path / 'photos'
        photo_dir.mkdir()
        
        photo = create_jpeg(photo_dir / 'test.jpg')
        
        # Generate checksums
        run_script('pg-verify', str(photo_dir), '--generate')
        
        # Modify the file
        with open(photo, 'ab') as f:
            f.write(b'corrupted data')
        
        # Check should fail
        result = run_script('pg-verify', str(photo_dir), '--check')
        
        assert result.returncode != 0
        # Check both stdout and stderr for failure indicators
        output = result.stdout.lower() + result.stderr.lower()
        assert 'mismatch' in output or 'failed' in output
    
    @requires_pillow
    def test_check_detects_missing(self, run_script, tmp_path: Path, test_env):
        """pg-verify --check detects missing files."""
        photo_dir = tmp_path / 'photos'
        photo_dir.mkdir()
        
        photo = create_jpeg(photo_dir / 'test.jpg')
        
        # Generate checksums
        run_script('pg-verify', str(photo_dir), '--generate')
        
        # Delete the file
        photo.unlink()
        
        # Check should report missing
        result = run_script('pg-verify', str(photo_dir), '--check')
        
        assert result.returncode != 0
        output = result.stdout.lower() + result.stderr.lower()
        assert 'missing' in output or 'failed' in output
    
    @requires_pillow
    def test_check_no_checksum_file(self, run_script, tmp_path: Path, test_env):
        """pg-verify --check handles missing .checksums file."""
        photo_dir = tmp_path / 'photos'
        photo_dir.mkdir()
        
        create_jpeg(photo_dir / 'test.jpg')
        
        # Don't generate checksums
        result = run_script('pg-verify', str(photo_dir), '--check')
        
        # Should handle gracefully (might warn or skip)
        assert result.returncode == 0  # No checksums to verify


class TestPgVerifyUpdate:
    """Tests for pg-verify --update mode."""
    
    @requires_pillow
    def test_update_adds_new_files(self, run_script, tmp_path: Path, test_env):
        """pg-verify --update adds checksums for new files."""
        photo_dir = tmp_path / 'photos'
        photo_dir.mkdir()
        
        # Create initial photos and generate checksums
        create_jpeg(photo_dir / 'initial.jpg')
        run_script('pg-verify', str(photo_dir), '--generate')
        
        # Add a new photo
        create_jpeg(photo_dir / 'new_photo.jpg')
        
        # Update should add the new file
        result = run_script('pg-verify', str(photo_dir), '--update')
        
        assert result.returncode == 0
        
        # Check .checksums has both files
        checksum_file = photo_dir / '.checksums'
        content = checksum_file.read_text()
        
        assert 'initial.jpg' in content
        assert 'new_photo.jpg' in content
    
    @requires_pillow
    def test_update_preserves_existing(self, run_script, tmp_path: Path, test_env):
        """pg-verify --update keeps existing checksums."""
        photo_dir = tmp_path / 'photos'
        photo_dir.mkdir()
        
        create_jpeg(photo_dir / 'existing.jpg')
        run_script('pg-verify', str(photo_dir), '--generate')
        
        # Get original checksum
        checksum_file = photo_dir / '.checksums'
        original_content = checksum_file.read_text()
        original_hash = original_content.split()[0]
        
        # Add new file and update
        create_jpeg(photo_dir / 'new.jpg')
        run_script('pg-verify', str(photo_dir), '--update')
        
        # Existing checksum should be unchanged
        updated_content = checksum_file.read_text()
        assert original_hash in updated_content


class TestPgVerifyHelp:
    """Tests for pg-verify help and usage."""
    
    def test_help_flag(self, run_script):
        """pg-verify --help shows usage information."""
        result = run_script('pg-verify', '--help')
        
        assert result.returncode == 0
        assert 'USAGE' in result.stdout or 'usage' in result.stdout.lower()
        assert '--generate' in result.stdout
        assert '--check' in result.stdout
        assert '--update' in result.stdout
    
    def test_no_mode_shows_error(self, run_script, tmp_path: Path):
        """pg-verify requires a mode flag."""
        photo_dir = tmp_path / 'photos'
        photo_dir.mkdir()
        
        result = run_script('pg-verify', str(photo_dir))
        
        assert result.returncode != 0
        assert 'mode' in result.stderr.lower() or 'required' in result.stderr.lower()


class TestPgVerifyVerbose:
    """Tests for pg-verify verbose output."""
    
    @requires_pillow
    def test_verbose_shows_details(self, run_script, tmp_path: Path, test_env):
        """pg-verify --verbose shows detailed output."""
        photo_dir = tmp_path / 'photos'
        photo_dir.mkdir()
        
        create_jpeg(photo_dir / 'verbose_test.jpg')
        run_script('pg-verify', str(photo_dir), '--generate')
        
        # Modify to cause failure
        with open(photo_dir / 'verbose_test.jpg', 'ab') as f:
            f.write(b'modified')
        
        result = run_script('pg-verify', str(photo_dir), '--check', '--verbose')
        
        # Verbose should show more details
        # Even if check fails, we should see detailed output


class TestPgVerifyEdgeCases:
    """Edge case tests for pg-verify."""
    
    def test_nonexistent_directory(self, run_script):
        """pg-verify handles nonexistent directory."""
        result = run_script('pg-verify', '/nonexistent/path', '--generate')
        
        assert result.returncode != 0
    
    @requires_pillow
    def test_empty_directory(self, run_script, tmp_path: Path, test_env):
        """pg-verify handles empty directory."""
        empty_dir = tmp_path / 'empty'
        empty_dir.mkdir()
        
        result = run_script('pg-verify', str(empty_dir), '--generate')
        
        # Should complete without error
        assert result.returncode == 0
    
    @requires_pillow
    def test_filename_with_spaces(self, run_script, tmp_path: Path, test_env):
        """pg-verify handles filenames with spaces."""
        photo_dir = tmp_path / 'photos'
        photo_dir.mkdir()
        
        create_jpeg(photo_dir / 'My Photo Name.jpg')
        
        result = run_script('pg-verify', str(photo_dir), '--generate')
        
        assert result.returncode == 0
        
        # Verify file is in checksums
        checksum_file = photo_dir / '.checksums'
        content = checksum_file.read_text()
        assert 'My Photo Name.jpg' in content
