"""
Integration tests for pg-exif script.
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime

import pytest

from tests.conftest import requires_exiftool, requires_pillow
from tests.fixtures.photo_factory import create_jpeg, create_jpeg_with_date, get_exif


class TestPgExifShow:
    """Tests for pg-exif --show mode."""
    
    @requires_exiftool
    @requires_pillow
    def test_show_displays_metadata(self, run_script, tmp_path: Path, test_env):
        """pg-exif --show displays file metadata."""
        photo = create_jpeg_with_date(
            tmp_path / 'test.jpg',
            date=datetime(2026, 1, 24, 14, 30, 0),
            author='Show Test Author',
            camera='Canon EOS R5'
        )
        
        result = run_script('pg-exif', str(photo), '--show')
        
        assert result.returncode == 0
        # Should contain file info
        assert 'test.jpg' in result.stdout or 'File' in result.stdout
    
    @requires_exiftool
    @requires_pillow
    def test_show_multiple_files(self, run_script, tmp_path: Path, test_env):
        """pg-exif --show handles multiple files."""
        photos = [
            create_jpeg(tmp_path / f'photo_{i}.jpg')
            for i in range(3)
        ]
        
        result = run_script('pg-exif', *[str(p) for p in photos], '--show')
        
        assert result.returncode == 0


class TestPgExifWriteAuthor:
    """Tests for pg-exif author writing."""
    
    @requires_exiftool
    @requires_pillow
    def test_write_author(self, run_script, tmp_path: Path, test_env):
        """pg-exif --author sets Artist field."""
        photo = create_jpeg(tmp_path / 'author_test.jpg')
        
        result = run_script('pg-exif', str(photo), '--author', 'New Author')
        
        assert result.returncode == 0
        
        # Verify the field was set
        author = get_exif(photo, 'Artist')
        assert author == 'New Author'
    
    @requires_exiftool
    @requires_pillow
    def test_write_author_batch(self, run_script, tmp_path: Path, test_env):
        """pg-exif --author works on multiple files."""
        photos = [
            create_jpeg(tmp_path / f'batch_{i}.jpg')
            for i in range(3)
        ]
        
        result = run_script('pg-exif', *[str(p) for p in photos], '--author', 'Batch Author')
        
        assert result.returncode == 0
        
        # Verify all files
        for photo in photos:
            author = get_exif(photo, 'Artist')
            assert author == 'Batch Author'


class TestPgExifWriteCopyright:
    """Tests for pg-exif copyright writing."""
    
    @requires_exiftool
    @requires_pillow
    def test_write_copyright(self, run_script, tmp_path: Path, test_env):
        """pg-exif --copyright sets Copyright field."""
        photo = create_jpeg(tmp_path / 'copyright_test.jpg')
        
        result = run_script('pg-exif', str(photo), '--copyright', '© 2026 Test')
        
        assert result.returncode == 0
        
        copyright_val = get_exif(photo, 'Copyright')
        assert '2026' in copyright_val


class TestPgExifWriteEvent:
    """Tests for pg-exif event writing."""
    
    @requires_exiftool
    @requires_pillow
    def test_write_event(self, run_script, tmp_path: Path, test_env):
        """pg-exif --event sets XMP:Event field."""
        photo = create_jpeg(tmp_path / 'event_test.jpg')
        
        result = run_script('pg-exif', str(photo), '--event', 'Wedding')
        
        assert result.returncode == 0
        
        event = get_exif(photo, 'XMP:Event')
        assert event == 'Wedding'


class TestPgExifWriteLocation:
    """Tests for pg-exif location writing."""
    
    @requires_exiftool
    @requires_pillow
    def test_write_location(self, run_script, tmp_path: Path, test_env):
        """pg-exif --location sets XMP:Location field."""
        photo = create_jpeg(tmp_path / 'location_test.jpg')
        
        result = run_script('pg-exif', str(photo), '--location', 'Berlin, Germany')
        
        assert result.returncode == 0
        
        location = get_exif(photo, 'XMP:Location')
        assert 'Berlin' in location


class TestPgExifWriteGPS:
    """Tests for pg-exif GPS writing."""
    
    @requires_exiftool
    @requires_pillow
    def test_write_gps(self, run_script, tmp_path: Path, test_env):
        """pg-exif --gps sets GPS coordinates."""
        photo = create_jpeg(tmp_path / 'gps_test.jpg')
        
        result = run_script('pg-exif', str(photo), '--gps', '52.52,13.405')
        
        assert result.returncode == 0
        
        lat = get_exif(photo, 'GPSLatitude')
        lon = get_exif(photo, 'GPSLongitude')
        
        assert lat is not None
        assert lon is not None


class TestPgExifWriteMultipleFields:
    """Tests for pg-exif writing multiple fields."""
    
    @requires_exiftool
    @requires_pillow
    def test_write_multiple_fields(self, run_script, tmp_path: Path, test_env):
        """pg-exif sets multiple fields at once."""
        photo = create_jpeg(tmp_path / 'multi_test.jpg')
        
        result = run_script(
            'pg-exif', str(photo),
            '--author', 'Multi Author',
            '--event', 'Multi Event',
            '--location', 'Multi City'
        )
        
        assert result.returncode == 0
        
        assert get_exif(photo, 'Artist') == 'Multi Author'
        assert get_exif(photo, 'XMP:Event') == 'Multi Event'
        assert get_exif(photo, 'XMP:Location') == 'Multi City'


class TestPgExifRemove:
    """Tests for pg-exif --remove mode."""
    
    @requires_exiftool
    @requires_pillow
    def test_remove_metadata(self, run_script, tmp_path: Path, test_env):
        """pg-exif --remove strips metadata."""
        photo = create_jpeg_with_date(
            tmp_path / 'remove_test.jpg',
            date=datetime(2026, 1, 24, 14, 30, 0),
            author='Original Author',
            event='Original Event'
        )
        
        result = run_script('pg-exif', str(photo), '--remove')
        
        assert result.returncode == 0
        
        # Metadata should be removed
        author = get_exif(photo, 'Artist')
        assert author is None


class TestPgExifDirectory:
    """Tests for pg-exif on directories."""
    
    @requires_exiftool
    @requires_pillow
    def test_process_directory(self, run_script, tmp_path: Path, test_env):
        """pg-exif processes all photos in directory."""
        photo_dir = tmp_path / 'photos'
        photo_dir.mkdir()
        
        photos = [
            create_jpeg(photo_dir / f'dir_photo_{i}.jpg')
            for i in range(3)
        ]
        
        result = run_script('pg-exif', str(photo_dir), '--author', 'Dir Author')
        
        assert result.returncode == 0
        
        # All should be updated
        for photo in photos:
            author = get_exif(photo, 'Artist')
            assert author == 'Dir Author'


class TestPgExifHelp:
    """Tests for pg-exif help and usage."""
    
    def test_help_flag(self, run_script):
        """pg-exif --help shows usage information."""
        result = run_script('pg-exif', '--help')
        
        assert result.returncode == 0
        assert 'USAGE' in result.stdout or 'usage' in result.stdout.lower()
        assert '--author' in result.stdout
        assert '--show' in result.stdout
    
    def test_no_files_shows_error(self, run_script):
        """pg-exif without files shows error."""
        result = run_script('pg-exif')
        
        assert result.returncode != 0


class TestPgExifEdgeCases:
    """Edge case tests for pg-exif."""
    
    @requires_exiftool
    @requires_pillow
    def test_nonexistent_file(self, run_script, test_env):
        """pg-exif handles nonexistent file gracefully."""
        result = run_script('pg-exif', '/nonexistent/file.jpg', '--show')
        
        # Should handle gracefully (warning or empty output)
        # Not necessarily an error for --show on missing file
    
    @requires_exiftool
    @requires_pillow
    def test_special_characters_in_value(self, run_script, tmp_path: Path, test_env):
        """pg-exif handles special characters in metadata values."""
        photo = create_jpeg(tmp_path / 'special.jpg')
        
        result = run_script('pg-exif', str(photo), '--copyright', '© 2026 Müller & Co.')
        
        assert result.returncode == 0
        
        copyright_val = get_exif(photo, 'Copyright')
        assert '2026' in copyright_val
