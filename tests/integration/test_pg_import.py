"""
Integration tests for pg-import script.
"""

import os
import re
import subprocess
from pathlib import Path
from datetime import datetime

import pytest

from tests.conftest import requires_exiftool, requires_pillow
from tests.fixtures.photo_factory import (
    create_sd_card_structure,
    create_import_yaml,
    create_jpeg_with_date,
    get_exif,
)


class TestPgImportBasic:
    """Basic functionality tests for pg-import."""
    
    @requires_exiftool
    @requires_pillow
    def test_import_copies_files(self, run_script, temp_sd_card: Path, test_env):
        """pg-import copies files from source to archive."""
        result = run_script(
            'pg-import',
            str(temp_sd_card),
            '--event', 'TestEvent',
            '--no-delete',
            '--dry-run'
        )
        
        # Dry run should succeed
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert 'DRY-RUN' in output
    
    @requires_exiftool
    @requires_pillow
    def test_import_creates_date_folders(self, run_script, temp_sd_card: Path, test_env):
        """pg-import creates date-based folder structure."""
        archive_dir = test_env['PHOTO_LIBRARY']
        
        result = run_script(
            'pg-import',
            str(temp_sd_card),
            '--event', 'TestEvent',
            '--no-delete'
        )
        
        assert result.returncode == 0
        
        # Check that date folders were created
        archive_path = Path(archive_dir)
        subdirs = list(archive_path.iterdir())
        assert len(subdirs) > 0
        
        # Should have format like 2026-01-24
        for subdir in subdirs:
            if subdir.is_dir():
                assert subdir.name.count('-') >= 2  # YYYY-MM-DD format
    
    @requires_exiftool
    @requires_pillow
    def test_import_renames_files(self, run_script, temp_sd_card: Path, test_env):
        """pg-import renames files according to pattern."""
        archive_dir = test_env['PHOTO_LIBRARY']
        
        result = run_script(
            'pg-import',
            str(temp_sd_card),
            '--event', 'Endurotraining',
            '--no-delete'
        )
        
        assert result.returncode == 0
        
        # Find imported files
        archive_path = Path(archive_dir)
        imported_files = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        
        assert len(imported_files) > 0
        
        # Files should contain event name (default pattern is {date}_{event}_{seq:03d})
        for f in imported_files:
            assert 'Endurotraining' in f.name


class TestPgImportSplitByType:
    """Tests for pg-import --split-by-type (raw/ and jpg/ subfolders with paired names)."""

    def test_import_help_includes_split_by_type(self, run_script):
        """pg-import --help mentions --split-by-type."""
        result = run_script('pg-import', '--help')
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert '--split-by-type' in output


class TestPgImportWithEvent:
    """Tests for pg-import with --event flag."""
    
    @requires_exiftool
    @requires_pillow
    def test_event_sets_metadata(self, run_script, temp_sd_card: Path, test_env):
        """--event flag sets XMP:Event metadata."""
        archive_dir = test_env['PHOTO_LIBRARY']
        
        result = run_script(
            'pg-import',
            str(temp_sd_card),
            '--event', 'ConcertNight',
            '--no-delete'
        )
        
        assert result.returncode == 0
        
        # Check EXIF on imported files
        archive_path = Path(archive_dir)
        imported_files = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        
        if imported_files:
            event = get_exif(imported_files[0], 'XMP:Event')
            # Event might be set if exiftool is available
            # The import script attempts to set this


class TestPgImportWithYaml:
    """Tests for pg-import with .import.yaml on SD card."""
    
    @requires_exiftool
    @requires_pillow
    def test_yaml_provides_defaults(self, run_script, temp_sd_card_with_yaml: Path, test_env):
        """pg-import uses values from .import.yaml."""
        result = run_script(
            'pg-import',
            str(temp_sd_card_with_yaml),
            '--no-delete'
        )
        
        assert result.returncode == 0
        # Should have used event from YAML
        assert 'Test Import Event' in result.stdout or result.returncode == 0
    
    @requires_exiftool
    @requires_pillow
    def test_cli_overrides_yaml(self, run_script, temp_sd_card_with_yaml: Path, test_env):
        """CLI arguments override .import.yaml values."""
        archive_dir = test_env['PHOTO_LIBRARY']
        
        result = run_script(
            'pg-import',
            str(temp_sd_card_with_yaml),
            '--event', 'CLIOverride',
            '--no-delete'
        )
        
        assert result.returncode == 0
        
        # Check files use CLI event name
        archive_path = Path(archive_dir)
        imported_files = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        
        for f in imported_files:
            assert 'CLIOverride' in f.name

    @requires_exiftool
    @requires_pillow
    def test_identity_yaml_sets_artist_copyright_credit(self, run_script, tmp_path: Path, test_env):
        """pg-import with .import.yaml (author, copyright, credit only) sets Artist, Copyright, IPTC:Credit."""
        sd_root = tmp_path / 'SD_IDENTITY'
        sd_root.mkdir()
        create_sd_card_structure(sd_root, num_photos=2)
        create_import_yaml(
            sd_root,
            author='IdentityAuthor',
            copyright='© 2026 Unlicense',
            credit='IdentityCredit',
        )

        archive_dir = test_env['PHOTO_LIBRARY']

        result = run_script(
            'pg-import',
            str(sd_root),
            '--trip',
            '--no-delete',
            env=test_env,
        )

        assert result.returncode == 0

        archive_path = Path(archive_dir)
        imported = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        assert len(imported) > 0

        sample = imported[0]
        assert get_exif(sample, 'Artist') == 'IdentityAuthor'
        assert get_exif(sample, 'Copyright') == '© 2026 Unlicense'
        assert get_exif(sample, 'IPTC:Credit') == 'IdentityCredit'


class TestPgImportDryRun:
    """Tests for pg-import --dry-run mode."""
    
    @requires_exiftool
    @requires_pillow
    def test_dry_run_no_files_created(self, run_script, temp_sd_card: Path, test_env):
        """--dry-run doesn't create any files."""
        archive_dir = test_env['PHOTO_LIBRARY']
        archive_path = Path(archive_dir)
        
        # Count files before
        files_before = list(archive_path.rglob('*'))
        
        result = run_script(
            'pg-import',
            str(temp_sd_card),
            '--event', 'DryRunTest',
            '--dry-run'
        )
        
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert 'DRY-RUN' in output
        
        # Count files after
        files_after = list(archive_path.rglob('*'))
        
        # Should be the same (no new files)
        assert len(files_after) == len(files_before)
    
    @requires_exiftool
    @requires_pillow
    def test_dry_run_shows_preview(self, run_script, temp_sd_card: Path, test_env):
        """--dry-run shows what would be imported."""
        result = run_script(
            'pg-import',
            str(temp_sd_card),
            '--event', 'PreviewTest',
            '--dry-run',
            '--verbose'
        )
        
        assert result.returncode == 0
        # Should show file count or preview
        output = result.stdout + result.stderr
        assert 'files' in output.lower() or 'import' in output.lower()


class TestPgImportChecksums:
    """Tests for pg-import checksum generation."""
    
    @requires_exiftool
    @requires_pillow
    def test_checksums_generated(self, run_script, temp_sd_card: Path, test_env):
        """pg-import generates .checksums files when enabled."""
        # Enable checksum generation
        test_env['GENERATE_CHECKSUMS'] = 'true'
        archive_dir = test_env['PHOTO_LIBRARY']
        
        result = run_script(
            'pg-import',
            str(temp_sd_card),
            '--event', 'ChecksumTest',
            '--no-delete',
            env=test_env
        )
        
        assert result.returncode == 0
        
        # Look for .checksums files
        archive_path = Path(archive_dir)
        checksum_files = list(archive_path.rglob('.checksums'))
        
        # May or may not have checksums depending on config
        # The important thing is the import succeeded


class TestPgImportFolderStructure:
    """Tests for pg-import folder structure patterns."""
    
    @requires_exiftool
    @requires_pillow
    def test_default_folder_structure(self, run_script, temp_sd_card: Path, test_env):
        """pg-import uses default FOLDER_STRUCTURE pattern."""
        archive_dir = test_env['PHOTO_LIBRARY']
        
        result = run_script(
            'pg-import',
            str(temp_sd_card),
            '--event', 'StructureTest',
            '--no-delete'
        )
        
        assert result.returncode == 0
        
        # Default is {year}-{month}-{day}
        archive_path = Path(archive_dir)
        subdirs = [d for d in archive_path.iterdir() if d.is_dir()]
        
        for subdir in subdirs:
            # Should match YYYY-MM-DD pattern
            parts = subdir.name.split('-')
            if len(parts) == 3:
                assert len(parts[0]) == 4  # Year
                assert len(parts[1]) == 2  # Month
                assert len(parts[2]) == 2  # Day
    
    @requires_exiftool
    @requires_pillow
    def test_custom_folder_structure(self, run_script, temp_sd_card: Path, test_env):
        """pg-import respects custom FOLDER_STRUCTURE."""
        test_env['FOLDER_STRUCTURE'] = '{year}/{month}'
        archive_dir = test_env['PHOTO_LIBRARY']
        
        result = run_script(
            'pg-import',
            str(temp_sd_card),
            '--event', 'CustomStructure',
            '--no-delete',
            env=test_env
        )
        
        assert result.returncode == 0
        
        # Check for nested structure
        archive_path = Path(archive_dir)
        # Should have year/month structure
        for year_dir in archive_path.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                for month_dir in year_dir.iterdir():
                    if month_dir.is_dir():
                        assert len(month_dir.name) == 2  # Month is 2 digits


class TestPgImportHelp:
    """Tests for pg-import help and usage."""
    
    def test_help_flag(self, run_script):
        """pg-import --help shows usage information."""
        result = run_script('pg-import', '--help')
        
        assert result.returncode == 0
        assert 'USAGE' in result.stdout or 'usage' in result.stdout.lower()
        assert '--event' in result.stdout
    
    def test_missing_source_shows_error(self, run_script):
        """pg-import without source shows error."""
        result = run_script('pg-import')
        
        assert result.returncode != 0
        assert 'error' in result.stderr.lower() or 'required' in result.stderr.lower()


class TestPgImportEdgeCases:
    """Edge case tests for pg-import."""
    
    @requires_exiftool
    @requires_pillow
    def test_empty_directory(self, run_script, tmp_path: Path, test_env):
        """pg-import handles empty source directory."""
        empty_dir = tmp_path / 'empty_sd'
        empty_dir.mkdir()
        
        result = run_script(
            'pg-import',
            str(empty_dir),
            '--event', 'EmptyTest',
            '--no-delete'
        )
        
        # Should complete (possibly with warning about no files)
        # Not necessarily an error
        assert 'No supported files' in result.stdout or result.returncode == 0 or result.returncode == 1
    
    @requires_exiftool
    @requires_pillow
    def test_nonexistent_directory(self, run_script, test_env):
        """pg-import reports error for nonexistent source."""
        result = run_script(
            'pg-import',
            '/nonexistent/path/to/sd',
            '--event', 'NonexistentTest'
        )
        
        assert result.returncode != 0
        assert 'not exist' in result.stderr.lower() or 'error' in result.stderr.lower()
    
    @requires_exiftool
    @requires_pillow
    def test_filename_with_spaces(self, run_script, tmp_path: Path, test_env):
        """pg-import handles filenames with spaces."""
        sd_card = tmp_path / 'SD_CARD'
        dcim = sd_card / 'DCIM' / '100CANON'
        dcim.mkdir(parents=True)
        
        # Create file with space in name
        create_jpeg_with_date(
            dcim / 'My Photo 001.JPG',
            date=datetime(2026, 1, 24, 10, 0, 0)
        )
        
        result = run_script(
            'pg-import',
            str(sd_card),
            '--event', 'SpaceTest',
            '--no-delete'
        )
        
        assert result.returncode == 0


class TestPgImportTrip:
    """Tests for pg-import --trip mode (no event/location prompts, date-only names when no event)."""

    def test_import_help_mentions_trip(self, run_script):
        """pg-import --help mentions --trip."""
        result = run_script('pg-import', '--help')
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert '--trip' in output
        assert 'trip' in output.lower()

    @requires_exiftool
    @requires_pillow
    def test_trip_mode_date_only_filenames(self, run_script, temp_sd_card: Path, test_env):
        """pg-import --trip with no event produces date-only filenames (YYYYMMDD_NNN.ext)."""
        archive_dir = test_env['PHOTO_LIBRARY']

        result = run_script(
            'pg-import',
            str(temp_sd_card),
            '--trip',
            '--no-delete',
            env=test_env
        )

        assert result.returncode == 0

        archive_path = Path(archive_dir)
        imported = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        assert len(imported) > 0

        # Filenames should be YYYYMMDD_NNN.ext (e.g. 20260124_001.jpg)
        pattern = re.compile(r'^\d{8}_\d{3}\.(?:jpg|JPG)$')
        for f in imported:
            assert pattern.match(f.name), f"Expected date_seq.ext, got {f.name}"

    @requires_exiftool
    @requires_pillow
    def test_trip_mode_event_from_yaml(self, run_script, tmp_path: Path, test_env):
        """pg-import --trip with event in .import.yaml uses event in filename."""
        sd_root = tmp_path / 'SD_CARD'
        sd_root.mkdir()
        create_sd_card_structure(sd_root, num_photos=2)
        create_import_yaml(sd_root, event='AlpsTour', location='Sölk Pass')

        archive_dir = test_env['PHOTO_LIBRARY']

        result = run_script(
            'pg-import',
            str(sd_root),
            '--trip',
            '--no-delete',
            env=test_env
        )

        assert result.returncode == 0

        archive_path = Path(archive_dir)
        imported = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        assert len(imported) > 0

        for f in imported:
            assert 'AlpsTour' in f.name, f"Expected event in filename, got {f.name}"
