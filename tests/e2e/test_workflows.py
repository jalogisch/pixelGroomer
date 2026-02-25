"""
End-to-end workflow tests.
Tests complete real-world usage scenarios.
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime

import pytest

from tests.conftest import requires_exiftool, requires_pillow, requires_imagemagick
from tests.fixtures.photo_factory import (
    create_jpeg_with_date,
    create_sd_card_structure,
    create_import_yaml,
    create_raw_like,
    get_exif,
    set_exif,
)


class TestFullImportWorkflow:
    """Complete import-to-share workflow tests."""
    
    @requires_exiftool
    @requires_pillow
    def test_wedding_photographer_workflow(
        self, run_script, tmp_path: Path, test_env
    ):
        """
        Simulate a wedding photographer's workflow:
        1. Import photos from SD card with event name
        2. Review and tag with location
        3. Create curated album
        4. Export album for client
        5. Verify integrity
        """
        archive_dir = test_env['PHOTO_LIBRARY']
        album_dir = test_env['ALBUM_DIR']
        client_export = tmp_path / 'client_delivery'
        client_export.mkdir()
        
        # Create mock SD card with wedding photos
        sd_card = tmp_path / 'SD_CARD'
        sd_card.mkdir()
        dcim = sd_card / 'DCIM' / '100CANON'
        dcim.mkdir(parents=True)
        
        wedding_date = datetime(2026, 1, 24, 14, 0, 0)
        for i in range(10):
            create_jpeg_with_date(
                dcim / f'IMG_{1000 + i:04d}.JPG',
                date=datetime(
                    wedding_date.year, wedding_date.month, wedding_date.day,
                    wedding_date.hour + (i // 3), i % 60, 0
                ),
                camera='Canon EOS R5'
            )
        
        # Step 1: Import with event name
        result = run_script(
            'pg-import', str(sd_card),
            '--event', 'Smith_Wedding',
            '--author', 'Pro Photographer',
            '--no-delete'
        )
        assert result.returncode == 0
        
        # Find imported files
        imported = list(Path(archive_dir).rglob('*.jpg')) + list(Path(archive_dir).rglob('*.JPG'))
        assert len(imported) == 10, f"Expected 10 files, got {len(imported)}"
        
        # Step 2: Add location to all photos
        result = run_script(
            'pg-exif', str(archive_dir),
            '--location', 'Berlin, Charlottenburg Palace'
        )
        assert result.returncode == 0
        
        # Step 3: Create curated album (select best photos)
        best_photos = imported[:5]  # First 5 as "best"
        
        run_script('pg-album', 'create', 'Smith_Wedding_Highlights')
        result = run_script(
            'pg-album', 'add', 'Smith_Wedding_Highlights',
            *[str(p) for p in best_photos]
        )
        assert result.returncode == 0
        
        # Step 4: Export for client
        result = run_script(
            'pg-album', 'export', 'Smith_Wedding_Highlights',
            '--to', str(client_export)
        )
        assert result.returncode == 0
        
        # Step 5: Verify export integrity
        run_script('pg-verify', str(client_export), '--generate')
        result = run_script('pg-verify', str(client_export), '--check')
        assert result.returncode == 0
        
        # Verify exported files have correct metadata
        # Exclude .checksums file from count
        exported = [f for f in client_export.iterdir() if f.name != '.checksums']
        assert len(exported) == 5
        
        for f in exported:
            author = get_exif(f, 'Artist')
            location = get_exif(f, 'XMP:Location')
            event = get_exif(f, 'XMP:Event')
            
            assert author == 'Pro Photographer'
            assert 'Berlin' in location or 'Charlottenburg' in location
            assert event == 'Smith_Wedding'


class TestMultiDayEvent:
    """Tests for multi-day event workflows."""
    
    @requires_exiftool
    @requires_pillow
    def test_conference_multi_day_import(
        self, run_script, tmp_path: Path, test_env
    ):
        """
        Simulate importing photos from a multi-day conference:
        - Day 1: 5 photos
        - Day 2: 5 photos
        - Day 3: 5 photos
        All organized correctly by date.
        """
        archive_dir = test_env['PHOTO_LIBRARY']
        
        # Create SD card with photos across 3 days
        sd_card = tmp_path / 'SD_CARD'
        dcim = sd_card / 'DCIM' / '100CANON'
        dcim.mkdir(parents=True)
        
        photo_index = 0
        for day in range(3):
            date = datetime(2026, 1, 24 + day, 10, 0, 0)
            for i in range(5):
                create_jpeg_with_date(
                    dcim / f'IMG_{1000 + photo_index:04d}.JPG',
                    date=datetime(date.year, date.month, date.day, 10 + i, 0, 0)
                )
                photo_index += 1
        
        # Import all photos
        result = run_script(
            'pg-import', str(sd_card),
            '--event', 'TechConference2026',
            '--no-delete'
        )
        assert result.returncode == 0
        
        # Verify photos are organized by date
        archive_path = Path(archive_dir)
        date_dirs = [d for d in archive_path.iterdir() if d.is_dir()]
        
        # Should have 3 date directories
        assert len(date_dirs) == 3, f"Expected 3 date folders, got {len(date_dirs)}"
        
        # Check each day has 5 photos
        for date_dir in date_dirs:
            photos = list(date_dir.glob('*.jpg')) + list(date_dir.glob('*.JPG'))
            assert len(photos) == 5, f"Expected 5 photos in {date_dir}, got {len(photos)}"


class TestMixedFileTypes:
    """Tests for handling mixed RAW and JPG files."""
    
    @requires_exiftool
    @requires_pillow
    def test_raw_plus_jpg_import(
        self, run_script, tmp_path: Path, test_env
    ):
        """
        Simulate importing both RAW and JPG files:
        - Camera saves RAW+JPG pairs
        - Both should be imported and organized
        """
        archive_dir = test_env['PHOTO_LIBRARY']
        
        # Create SD card with RAW+JPG pairs
        sd_card = tmp_path / 'SD_CARD'
        dcim = sd_card / 'DCIM' / '100CANON'
        dcim.mkdir(parents=True)
        
        date = datetime(2026, 1, 24, 14, 0, 0)
        for i in range(3):
            # Create JPG
            create_jpeg_with_date(
                dcim / f'IMG_{1000 + i:04d}.JPG',
                date=date
            )
            # Create matching "RAW" file
            create_raw_like(dcim / f'IMG_{1000 + i:04d}.CR3')
        
        # Import
        result = run_script(
            'pg-import', str(sd_card),
            '--event', 'MixedTest',
            '--no-delete'
        )
        assert result.returncode == 0
        
        # Verify both types were imported
        archive_path = Path(archive_dir)
        jpgs = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        raws = list(archive_path.rglob('*.cr3')) + list(archive_path.rglob('*.CR3'))
        
        assert len(jpgs) == 3, f"Expected 3 JPGs, got {len(jpgs)}"
        assert len(raws) == 3, f"Expected 3 RAWs, got {len(raws)}"

    @requires_exiftool
    @requires_pillow
    def test_raw_plus_jpg_import_with_split_by_type(
        self, run_script, tmp_path: Path, test_env
    ):
        """
        With --split-by-type, 3 RAW+JPG pairs go to raw/ and jpg/ with paired names.
        """
        archive_dir = test_env['PHOTO_LIBRARY']
        sd_card = tmp_path / 'SD_CARD'
        dcim = sd_card / 'DCIM' / '100CANON'
        dcim.mkdir(parents=True)
        date = datetime(2026, 1, 24, 14, 0, 0)
        date_str = date.strftime('%Y:%m:%d %H:%M:%S')
        for i in range(3):
            create_jpeg_with_date(
                dcim / f'IMG_{1000 + i:04d}.JPG',
                date=date
            )
            raw_path = create_raw_like(dcim / f'IMG_{1000 + i:04d}.CR3')
            set_exif(raw_path, DateTimeOriginal=date_str, CreateDate=date_str)
        result = run_script(
            'pg-import', str(sd_card),
            '--event', 'MixedTest',
            '--no-delete',
            '--split-by-type'
        )
        assert result.returncode == 0
        archive_path = Path(archive_dir)
        date_dirs = [x for x in archive_path.iterdir() if x.is_dir()]
        assert len(date_dirs) == 1
        raw_dir = date_dirs[0] / 'raw'
        jpg_dir = date_dirs[0] / 'jpg'
        assert raw_dir.is_dir() and jpg_dir.is_dir()
        raws = sorted(raw_dir.glob('*.*'))
        jpgs = sorted(jpg_dir.glob('*.*'))
        assert len(raws) == 3 and len(jpgs) == 3
        for i in range(3):
            assert raws[i].stem == jpgs[i].stem, f"pair {i} should have same base name"


class TestImportYamlWorkflow:
    """Tests for .import.yaml based workflows."""
    
    @requires_exiftool
    @requires_pillow
    def test_yaml_driven_import(
        self, run_script, tmp_path: Path, test_env
    ):
        """
        Simulate workflow where .import.yaml is prepared on SD card:
        - Photographer creates .import.yaml before shoot
        - Import uses YAML values without prompts
        """
        archive_dir = test_env['PHOTO_LIBRARY']
        
        # Create SD card with .import.yaml
        sd_card = tmp_path / 'SD_CARD'
        dcim = sd_card / 'DCIM' / '100CANON'
        dcim.mkdir(parents=True)
        
        # Create .import.yaml in SD root
        create_import_yaml(
            sd_card,
            event='Corporate_Headshots',
            location='NYC Office',
            author='Studio Team',
            tags=['corporate', 'headshots', '2026']
        )
        
        # Create photos
        for i in range(5):
            create_jpeg_with_date(
                dcim / f'IMG_{1000 + i:04d}.JPG',
                date=datetime(2026, 1, 24, 10 + i, 0, 0)
            )
        
        # Import - should use YAML values
        result = run_script(
            'pg-import', str(sd_card),
            '--no-delete'
        )
        assert result.returncode == 0
        
        # Verify imported files have YAML-specified metadata
        imported = list(Path(archive_dir).rglob('*.jpg')) + list(Path(archive_dir).rglob('*.JPG'))
        assert len(imported) == 5
        
        # Files should be named with event from YAML
        for f in imported:
            assert 'Corporate_Headshots' in f.name


class TestBackupVerifyWorkflow:
    """Tests for backup and verification workflows."""
    
    @requires_exiftool
    @requires_pillow
    def test_archive_integrity_workflow(
        self, run_script, tmp_path: Path, test_env
    ):
        """
        Simulate archive integrity maintenance workflow:
        1. Import photos
        2. Generate checksums
        3. Later: verify integrity
        4. Add new photos
        5. Update checksums
        6. Re-verify
        """
        test_env['GENERATE_CHECKSUMS'] = 'true'
        archive_dir = test_env['PHOTO_LIBRARY']
        
        # Step 1: Initial import
        sd_card1 = tmp_path / 'SD1'
        dcim1 = sd_card1 / 'DCIM' / '100CANON'
        dcim1.mkdir(parents=True)
        
        for i in range(3):
            create_jpeg_with_date(
                dcim1 / f'IMG_{1000 + i:04d}.JPG',
                date=datetime(2026, 1, 24, 10 + i, 0, 0)
            )
        
        run_script(
            'pg-import', str(sd_card1),
            '--event', 'Batch1',
            '--no-delete',
            env=test_env
        )
        
        # Step 2: Generate checksums (might already be done by import)
        run_script('pg-verify', archive_dir, '--generate')
        
        # Step 3: Verify integrity
        result = run_script('pg-verify', archive_dir, '--check')
        assert result.returncode == 0
        
        # Step 4: Second import (simulating adding more photos later)
        sd_card2 = tmp_path / 'SD2'
        dcim2 = sd_card2 / 'DCIM' / '100CANON'
        dcim2.mkdir(parents=True)
        
        for i in range(3):
            create_jpeg_with_date(
                dcim2 / f'IMG_{2000 + i:04d}.JPG',
                date=datetime(2026, 1, 25, 10 + i, 0, 0)  # Next day
            )
        
        run_script(
            'pg-import', str(sd_card2),
            '--event', 'Batch2',
            '--no-delete',
            env=test_env
        )
        
        # Step 5: Update checksums
        result = run_script('pg-verify', archive_dir, '--update')
        assert result.returncode == 0
        
        # Step 6: Final verification
        result = run_script('pg-verify', archive_dir, '--check')
        assert result.returncode == 0


class TestAlbumManagementWorkflow:
    """Tests for album creation and management workflows."""
    
    @requires_exiftool
    @requires_pillow
    def test_create_multiple_albums_from_import(
        self, run_script, tmp_path: Path, test_env
    ):
        """
        Simulate creating multiple albums from single import:
        - Import large batch
        - Create "all photos" album
        - Create "favorites" album (subset)
        - Create "portfolio" album (different subset)
        """
        archive_dir = test_env['PHOTO_LIBRARY']
        album_dir = test_env['ALBUM_DIR']
        
        # Create and import photos
        sd_card = tmp_path / 'SD_CARD'
        dcim = sd_card / 'DCIM' / '100CANON'
        dcim.mkdir(parents=True)
        
        for i in range(15):
            create_jpeg_with_date(
                dcim / f'IMG_{1000 + i:04d}.JPG',
                date=datetime(2026, 1, 24, 10 + (i // 3), i % 60, 0)
            )
        
        run_script(
            'pg-import', str(sd_card),
            '--event', 'PhotoShoot',
            '--no-delete'
        )
        
        imported = list(Path(archive_dir).rglob('*.jpg')) + list(Path(archive_dir).rglob('*.JPG'))
        assert len(imported) == 15
        
        # Create "all photos" album
        run_script('pg-album', 'create', 'PhotoShoot_All')
        run_script('pg-album', 'add', 'PhotoShoot_All', *[str(f) for f in imported])
        
        # Create "favorites" album (first 5)
        run_script('pg-album', 'create', 'PhotoShoot_Favorites')
        run_script('pg-album', 'add', 'PhotoShoot_Favorites', *[str(f) for f in imported[:5]])
        
        # Create "portfolio" album (every 3rd photo)
        run_script('pg-album', 'create', 'PhotoShoot_Portfolio')
        run_script('pg-album', 'add', 'PhotoShoot_Portfolio', *[str(f) for f in imported[::3]])
        
        # Verify album counts
        result = run_script('pg-album', 'list')
        assert result.returncode == 0
        assert 'PhotoShoot_All' in result.stdout
        assert 'PhotoShoot_Favorites' in result.stdout
        assert 'PhotoShoot_Portfolio' in result.stdout
        
        # Verify album contents
        all_album = Path(album_dir) / 'PhotoShoot_All'
        favorites_album = Path(album_dir) / 'PhotoShoot_Favorites'
        portfolio_album = Path(album_dir) / 'PhotoShoot_Portfolio'
        
        assert len(list(all_album.iterdir())) == 15
        assert len(list(favorites_album.iterdir())) == 5
        assert len(list(portfolio_album.iterdir())) == 5  # Every 3rd of 15
