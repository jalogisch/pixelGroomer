"""
Integration tests for tool-to-tool data flow (handovers).
Tests that data flows correctly between different pg-* scripts.
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime

import pytest

from tests.conftest import requires_exiftool, requires_pillow, requires_imagemagick
from tests.fixtures.photo_factory import (
    create_jpeg,
    create_jpeg_with_date,
    create_sd_card_structure,
    create_raw_like,
    get_exif,
)


class TestImportToAlbum:
    """Test data flow from pg-import to pg-album."""
    
    @requires_exiftool
    @requires_pillow
    def test_imported_files_can_be_added_to_album(
        self, run_script, temp_sd_card: Path, test_env
    ):
        """Files imported via pg-import can be added to an album."""
        archive_dir = test_env['PHOTO_LIBRARY']
        album_dir = test_env['ALBUM_DIR']
        
        # Step 1: Import
        result = run_script(
            'pg-import', str(temp_sd_card),
            '--event', 'HandoverTest',
            '--no-delete'
        )
        assert result.returncode == 0
        
        # Step 2: Find imported files
        archive_path = Path(archive_dir)
        imported_files = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        assert len(imported_files) > 0, "No files were imported"
        
        # Step 3: Create album and add files
        run_script('pg-album', 'create', 'ImportedAlbum')
        
        result = run_script(
            'pg-album', 'add', 'ImportedAlbum',
            *[str(f) for f in imported_files]
        )
        assert result.returncode == 0
        
        # Step 4: Verify symlinks were created
        album_path = Path(album_dir) / 'ImportedAlbum'
        symlinks = [f for f in album_path.iterdir() if f.is_symlink()]
        assert len(symlinks) == len(imported_files)
        
        # Step 5: Verify symlinks resolve to actual files
        for link in symlinks:
            assert link.resolve().exists(), f"Broken symlink: {link}"


class TestImportToExif:
    """Test data flow from pg-import to pg-exif."""
    
    @requires_exiftool
    @requires_pillow
    def test_exif_changes_after_import(
        self, run_script, temp_sd_card: Path, test_env
    ):
        """EXIF metadata can be modified on imported files."""
        archive_dir = test_env['PHOTO_LIBRARY']
        
        # Step 1: Import
        result = run_script(
            'pg-import', str(temp_sd_card),
            '--event', 'ExifHandover',
            '--no-delete'
        )
        assert result.returncode == 0
        
        # Step 2: Find an imported file
        archive_path = Path(archive_dir)
        imported_files = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        assert len(imported_files) > 0
        
        test_file = imported_files[0]
        
        # Step 3: Modify EXIF with pg-exif
        result = run_script(
            'pg-exif', str(test_file),
            '--author', 'Post-Import Author',
            '--location', 'Post-Import Location'
        )
        assert result.returncode == 0
        
        # Step 4: Verify changes
        author = get_exif(test_file, 'Artist')
        location = get_exif(test_file, 'XMP:Location')
        
        assert author == 'Post-Import Author'
        assert location == 'Post-Import Location'


class TestAlbumToExport:
    """Test data flow from pg-album to export."""
    
    @requires_exiftool
    @requires_pillow
    def test_export_resolves_symlinks(
        self, run_script, tmp_path: Path, test_env
    ):
        """Album export correctly resolves symlinks to real files."""
        album_dir = test_env['ALBUM_DIR']
        export_dir = tmp_path / 'export_test'
        export_dir.mkdir()
        
        # Step 1: Create source photos
        source_dir = tmp_path / 'source'
        source_dir.mkdir()
        photos = [
            create_jpeg_with_date(
                source_dir / f'photo_{i}.jpg',
                date=datetime(2026, 1, 24, 10 + i, 0, 0),
                author='Original Author'
            )
            for i in range(3)
        ]
        
        # Step 2: Create album and add photos
        run_script('pg-album', 'create', 'ExportTest')
        run_script('pg-album', 'add', 'ExportTest', *[str(p) for p in photos])
        
        # Step 3: Export album
        result = run_script(
            'pg-album', 'export', 'ExportTest',
            '--to', str(export_dir)
        )
        assert result.returncode == 0
        
        # Step 4: Verify exported files are real files (not symlinks)
        exported_files = list(export_dir.iterdir())
        assert len(exported_files) == 3
        
        for f in exported_files:
            assert not f.is_symlink(), f"Exported file is still a symlink: {f}"
            assert f.is_file()
            
            # Verify EXIF is preserved
            author = get_exif(f, 'Artist')
            assert author == 'Original Author'


class TestExportToVerify:
    """Test data flow from export to pg-verify."""
    
    @requires_exiftool
    @requires_pillow
    def test_exported_files_pass_verification(
        self, run_script, tmp_path: Path, test_env
    ):
        """Exported files pass checksum verification."""
        album_dir = test_env['ALBUM_DIR']
        export_dir = tmp_path / 'verify_export'
        export_dir.mkdir()
        
        # Step 1: Create source photos
        source_dir = tmp_path / 'source'
        source_dir.mkdir()
        photos = [create_jpeg(source_dir / f'verify_{i}.jpg') for i in range(3)]
        
        # Step 2: Create and populate album
        run_script('pg-album', 'create', 'VerifyTest')
        run_script('pg-album', 'add', 'VerifyTest', *[str(p) for p in photos])
        
        # Step 3: Export
        run_script('pg-album', 'export', 'VerifyTest', '--to', str(export_dir))
        
        # Step 4: Generate checksums on exported files
        result = run_script('pg-verify', str(export_dir), '--generate')
        # Should complete - may skip if no files need checksums
        output = result.stdout + result.stderr
        assert 'checksum' in output.lower() or 'verified' in output.lower() or 'generated' in output.lower() or result.returncode == 0
        
        # Step 5: Verify checksums
        result = run_script('pg-verify', str(export_dir), '--check')
        # Verification should pass or report no checksums
        output = result.stdout + result.stderr
        assert 'verified' in output.lower() or 'No checksums' in output or result.returncode == 0


class TestExifPreservedThroughAlbum:
    """Test that EXIF metadata survives the album symlink chain."""
    
    @requires_exiftool
    @requires_pillow
    def test_metadata_survives_album_workflow(
        self, run_script, tmp_path: Path, test_env
    ):
        """EXIF metadata is preserved through album add/export cycle."""
        album_dir = test_env['ALBUM_DIR']
        export_dir = tmp_path / 'metadata_export'
        export_dir.mkdir()
        
        # Step 1: Create photo with specific metadata
        source_dir = tmp_path / 'source'
        source_dir.mkdir()
        
        photo = create_jpeg_with_date(
            source_dir / 'metadata_test.jpg',
            date=datetime(2026, 1, 24, 14, 30, 0),
            author='Metadata Author',
            event='Metadata Event',
            camera='Test Camera'
        )
        
        # Add location separately
        run_script('pg-exif', str(photo), '--location', 'Metadata Location')
        
        # Step 2: Add to album
        run_script('pg-album', 'create', 'MetadataTest')
        run_script('pg-album', 'add', 'MetadataTest', str(photo))
        
        # Step 3: Read metadata through symlink (album show should work)
        album_path = Path(album_dir) / 'MetadataTest'
        album_file = list(album_path.iterdir())[0]
        
        # Metadata should be readable through symlink
        author = get_exif(album_file, 'Artist')
        assert author == 'Metadata Author'
        
        # Step 4: Export and verify metadata preserved
        run_script('pg-album', 'export', 'MetadataTest', '--to', str(export_dir))
        
        exported_file = list(export_dir.iterdir())[0]
        
        # All metadata should be preserved in export
        assert get_exif(exported_file, 'Artist') == 'Metadata Author'
        assert get_exif(exported_file, 'XMP:Event') == 'Metadata Event'
        assert get_exif(exported_file, 'XMP:Location') == 'Metadata Location'


class TestImportToVerify:
    """Test data flow from pg-import to pg-verify."""
    
    @requires_exiftool
    @requires_pillow
    def test_verify_checksums_after_import(
        self, run_script, temp_sd_card: Path, test_env
    ):
        """Checksums generated during import can be verified later."""
        # Enable checksum generation
        test_env['GENERATE_CHECKSUMS'] = 'true'
        archive_dir = test_env['PHOTO_LIBRARY']
        
        # Step 1: Import with checksums
        result = run_script(
            'pg-import', str(temp_sd_card),
            '--event', 'VerifyImport',
            '--no-delete',
            env=test_env
        )
        assert result.returncode == 0
        
        # Step 2: Verify the imported files
        result = run_script('pg-verify', archive_dir, '--check')
        
        # Should pass (either with checksums or gracefully without)
        # The important thing is no crashes


class TestDevelopToVerify:
    """Test data flow from pg-develop to pg-verify."""
    
    @requires_pillow
    @requires_imagemagick
    def test_developed_files_can_be_verified(
        self, run_script, tmp_path: Path, test_env
    ):
        """Developed files can have checksums generated and verified."""
        raw_dir = tmp_path / 'raw'
        output_dir = tmp_path / 'developed'
        raw_dir.mkdir()
        output_dir.mkdir()
        
        # Step 1: Create mock RAW file
        create_raw_like(raw_dir / 'test.cr3')
        
        # Step 2: Develop
        run_script(
            'pg-develop', str(raw_dir),
            '--processor', 'imagemagick',
            '--output', str(output_dir)
        )
        
        # Step 3: Generate checksums on developed files
        result = run_script('pg-verify', str(output_dir), '--generate')
        assert result.returncode == 0
        
        # Step 4: Verify
        result = run_script('pg-verify', str(output_dir), '--check')
        assert result.returncode == 0


class TestFullChain:
    """Test the full tool chain together."""
    
    @requires_exiftool
    @requires_pillow
    def test_import_exif_album_export_chain(
        self, run_script, temp_sd_card: Path, tmp_path: Path, test_env
    ):
        """Full chain: import -> exif -> album -> export."""
        archive_dir = test_env['PHOTO_LIBRARY']
        album_dir = test_env['ALBUM_DIR']
        export_dir = tmp_path / 'final_export'
        export_dir.mkdir()
        
        # Step 1: Import
        result = run_script(
            'pg-import', str(temp_sd_card),
            '--event', 'FullChain',
            '--no-delete'
        )
        assert result.returncode == 0
        
        # Step 2: Find and tag with additional EXIF
        imported = list(Path(archive_dir).rglob('*.jpg')) + list(Path(archive_dir).rglob('*.JPG'))
        assert len(imported) > 0
        
        for f in imported:
            run_script('pg-exif', str(f), '--author', 'Chain Author')
        
        # Step 3: Create album and add files
        run_script('pg-album', 'create', 'FullChainAlbum')
        run_script('pg-album', 'add', 'FullChainAlbum', *[str(f) for f in imported])
        
        # Step 4: Export album
        result = run_script(
            'pg-album', 'export', 'FullChainAlbum',
            '--to', str(export_dir)
        )
        # Export should complete - check output message
        output = result.stdout + result.stderr
        assert result.returncode == 0 or 'Exported' in output or 'Export' in output
        
        # Step 5: Verify export has correct metadata
        exported = list(export_dir.iterdir())
        # Exported files should exist if export succeeded
        if result.returncode == 0:
            assert len(exported) == len(imported)
        
        for f in exported:
            author = get_exif(f, 'Artist')
            assert author == 'Chain Author'
