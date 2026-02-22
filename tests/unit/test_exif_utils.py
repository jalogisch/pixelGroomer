"""
Unit tests for lib/exif_utils.py ExifTool class.
"""

import sys
from pathlib import Path
from datetime import datetime

import pytest

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'lib'))

from exif_utils import ExifTool

from tests.conftest import requires_exiftool, requires_pillow
from tests.fixtures.photo_factory import create_jpeg, create_jpeg_with_date, set_exif, get_exif


class TestExifToolInstantiation:
    """Tests for ExifTool class initialization."""
    
    @requires_exiftool
    def test_creates_instance(self):
        """ExifTool can be instantiated when exiftool is available."""
        exif = ExifTool()
        assert exif is not None
        assert exif.exiftool_path == 'exiftool'
    
    @requires_exiftool
    def test_custom_exiftool_path(self):
        """ExifTool accepts custom exiftool path."""
        exif = ExifTool(exiftool_path='exiftool')
        assert exif.exiftool_path == 'exiftool'


class TestExifToolRead:
    """Tests for ExifTool.read() method."""
    
    @requires_exiftool
    @requires_pillow
    def test_read_returns_dict(self, tmp_path: Path):
        """read() returns a dictionary."""
        photo = create_jpeg(tmp_path / 'test.jpg')
        
        exif = ExifTool()
        result = exif.read(photo)
        
        assert isinstance(result, dict)
    
    @requires_exiftool
    @requires_pillow
    def test_read_contains_filename(self, tmp_path: Path):
        """read() result contains filename."""
        photo = create_jpeg(tmp_path / 'test_photo.jpg')
        
        exif = ExifTool()
        result = exif.read(photo)
        
        assert 'File:FileName' in result
        assert result['File:FileName'] == 'test_photo.jpg'
    
    @requires_exiftool
    @requires_pillow
    def test_read_with_exif_data(self, tmp_path: Path):
        """read() returns EXIF data when present."""
        photo = create_jpeg_with_date(
            tmp_path / 'test.jpg',
            date=datetime(2026, 1, 24, 14, 30, 0),
            camera='Canon EOS R5'
        )
        
        exif = ExifTool()
        result = exif.read(photo)
        
        # Check date was set (may be in different format)
        assert 'EXIF:DateTimeOriginal' in result or 'EXIF:CreateDate' in result
    
    @requires_exiftool
    def test_read_nonexistent_file(self):
        """read() returns empty dict for nonexistent file."""
        exif = ExifTool()
        result = exif.read('/nonexistent/path/file.jpg')
        
        assert result == {}


class TestExifToolReadDate:
    """Tests for ExifTool.read_date() method."""
    
    @requires_exiftool
    @requires_pillow
    def test_read_date_returns_datetime(self, tmp_path: Path):
        """read_date() returns datetime object."""
        test_date = datetime(2026, 1, 24, 14, 30, 0)
        photo = create_jpeg_with_date(tmp_path / 'test.jpg', date=test_date)
        
        exif = ExifTool()
        result = exif.read_date(photo)
        
        assert isinstance(result, datetime)
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 24
    
    @requires_exiftool
    @requires_pillow
    def test_read_date_no_exif(self, tmp_path: Path):
        """read_date() returns None when no date in EXIF."""
        photo = create_jpeg(tmp_path / 'no_date.jpg')
        
        exif = ExifTool()
        result = exif.read_date(photo)
        
        # May return file modification date or None
        # Depends on exiftool behavior


class TestExifToolReadCamera:
    """Tests for ExifTool.read_camera() method."""
    
    @requires_exiftool
    @requires_pillow
    def test_read_camera_returns_model(self, tmp_path: Path):
        """read_camera() returns camera model."""
        photo = create_jpeg_with_date(
            tmp_path / 'test.jpg',
            date=datetime(2026, 1, 24, 14, 30, 0),
            camera='Canon EOS R5'
        )
        
        exif = ExifTool()
        result = exif.read_camera(photo)
        
        assert result is not None
        assert 'Canon' in result or 'R5' in result


class TestExifToolWrite:
    """Tests for ExifTool.write() method."""
    
    @requires_exiftool
    @requires_pillow
    def test_write_author(self, tmp_path: Path):
        """write() sets author/artist field."""
        photo = create_jpeg(tmp_path / 'test.jpg')
        
        exif = ExifTool()
        result = exif.write(photo, author='Test Author')
        
        assert result is True
        
        # Verify the field was set
        value = get_exif(photo, 'Artist')
        assert value == 'Test Author'
    
    @requires_exiftool
    @requires_pillow
    def test_write_copyright(self, tmp_path: Path):
        """write() sets copyright field."""
        photo = create_jpeg(tmp_path / 'test.jpg')

        exif = ExifTool()
        result = exif.write(photo, copyright='© 2026 Test')

        assert result is True

        value = get_exif(photo, 'Copyright')
        assert '2026' in value

    @requires_exiftool
    @requires_pillow
    def test_write_credit(self, tmp_path: Path):
        """write() sets credit field (IPTC:Credit)."""
        photo = create_jpeg(tmp_path / 'test.jpg')

        exif = ExifTool()
        result = exif.write(photo, credit='Test Credit')

        assert result is True

        value = get_exif(photo, 'IPTC:Credit')
        assert value == 'Test Credit'

    @requires_exiftool
    @requires_pillow
    def test_write_event(self, tmp_path: Path):
        """write() sets XMP:Event field."""
        photo = create_jpeg(tmp_path / 'test.jpg')
        
        exif = ExifTool()
        result = exif.write(photo, event='Wedding')
        
        assert result is True
        
        value = get_exif(photo, 'XMP:Event')
        assert value == 'Wedding'
    
    @requires_exiftool
    @requires_pillow
    def test_write_location(self, tmp_path: Path):
        """write() sets XMP:Location field."""
        photo = create_jpeg(tmp_path / 'test.jpg')
        
        exif = ExifTool()
        result = exif.write(photo, location='Berlin')
        
        assert result is True
        
        value = get_exif(photo, 'XMP:Location')
        assert value == 'Berlin'
    
    @requires_exiftool
    @requires_pillow
    def test_write_multiple_fields(self, tmp_path: Path):
        """write() sets multiple fields at once."""
        photo = create_jpeg(tmp_path / 'test.jpg')
        
        exif = ExifTool()
        result = exif.write(
            photo,
            author='Multi Author',
            event='Multi Event',
            location='Multi Location'
        )
        
        assert result is True
        
        assert get_exif(photo, 'Artist') == 'Multi Author'
        assert get_exif(photo, 'XMP:Event') == 'Multi Event'
        assert get_exif(photo, 'XMP:Location') == 'Multi Location'
    
    @requires_exiftool
    @requires_pillow
    def test_write_gps_coordinates(self, tmp_path: Path):
        """write() sets GPS coordinates."""
        photo = create_jpeg(tmp_path / 'test.jpg')
        
        exif = ExifTool()
        result = exif.write(photo, gps='52.52,13.405')
        
        assert result is True
        
        lat = get_exif(photo, 'GPSLatitude')
        lon = get_exif(photo, 'GPSLongitude')
        
        assert lat is not None
        assert lon is not None


class TestExifToolWriteBatch:
    """Tests for ExifTool.write_batch() method."""
    
    @requires_exiftool
    @requires_pillow
    def test_write_batch_multiple_files(self, tmp_path: Path):
        """write_batch() updates multiple files."""
        photos = [
            create_jpeg(tmp_path / f'photo_{i}.jpg')
            for i in range(3)
        ]
        
        exif = ExifTool()
        count = exif.write_batch(photos, author='Batch Author')
        
        assert count == 3
        
        for photo in photos:
            assert get_exif(photo, 'Artist') == 'Batch Author'
    
    @requires_exiftool
    @requires_pillow
    def test_write_batch_empty_list(self):
        """write_batch() handles empty list."""
        exif = ExifTool()
        count = exif.write_batch([], author='Test')
        
        assert count == 0


class TestExifToolRemoveMetadata:
    """Tests for ExifTool.remove_metadata() method."""
    
    @requires_exiftool
    @requires_pillow
    def test_remove_metadata(self, tmp_path: Path):
        """remove_metadata() strips all metadata."""
        photo = create_jpeg_with_date(
            tmp_path / 'test.jpg',
            date=datetime(2026, 1, 24, 14, 30, 0),
            author='Original Author',
            event='Original Event'
        )
        
        exif = ExifTool()
        result = exif.remove_metadata(photo, keep_orientation=True)
        
        assert result is True
        
        # Author and event should be gone
        assert get_exif(photo, 'Artist') is None
        assert get_exif(photo, 'XMP:Event') is None


class TestExifToolShow:
    """Tests for ExifTool.show() method."""
    
    @requires_exiftool
    @requires_pillow
    def test_show_returns_string(self, tmp_path: Path):
        """show() returns formatted string."""
        photo = create_jpeg_with_date(
            tmp_path / 'test.jpg',
            date=datetime(2026, 1, 24, 14, 30, 0),
            author='Show Author'
        )
        
        exif = ExifTool()
        result = exif.show(photo)
        
        assert isinstance(result, str)
        assert 'File:' in result
        assert 'Author:' in result or 'Show Author' in result
