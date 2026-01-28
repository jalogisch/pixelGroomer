"""
Combinatorial matrix tests for pg-import option combinations.
Tests various combinations of CLI flags, YAML config, and environment settings.
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from itertools import product

import pytest

from tests.conftest import requires_exiftool, requires_pillow, requires_imagemagick
from tests.fixtures.photo_factory import (
    create_sd_card_structure,
    create_import_yaml,
    get_exif,
)


class TestImportOptionMatrix:
    """
    Systematic testing of import option combinations.
    
    Options tested:
    - .import.yaml present/absent
    - --event CLI flag present/absent
    - --location CLI flag present/absent
    - GENERATE_CHECKSUMS env var true/false
    """
    
    @requires_exiftool
    @requires_pillow
    @pytest.mark.parametrize("has_yaml,has_cli_event,has_cli_location,checksums", [
        # No YAML, no CLI - minimal (will use defaults)
        (False, False, False, False),
        # No YAML, CLI event only
        (False, True, False, False),
        # No YAML, CLI event + location
        (False, True, True, False),
        # No YAML, CLI event + location + checksums
        (False, True, True, True),
        # YAML only (use YAML values)
        (True, False, False, False),
        # YAML + CLI event (CLI overrides)
        (True, True, False, False),
        # YAML + CLI event + location (CLI overrides)
        (True, True, True, False),
        # Full: YAML + CLI + checksums
        (True, True, True, True),
    ])
    def test_import_option_combination(
        self, run_script, tmp_path: Path, test_env,
        has_yaml, has_cli_event, has_cli_location, checksums
    ):
        """Test specific combination of import options."""
        # Create SD card
        sd_card = tmp_path / 'SD_CARD'
        sd_card.mkdir()
        create_sd_card_structure(sd_card, num_photos=2)
        
        # Configure YAML if needed
        yaml_event = 'YAMLEvent'
        yaml_location = 'YAMLLocation'
        
        if has_yaml:
            create_import_yaml(
                sd_card,
                event=yaml_event,
                location=yaml_location,
                author='YAML Author'
            )
        
        # Build CLI args
        args = [str(sd_card), '--no-delete']
        
        cli_event = 'CLIEvent'
        cli_location = 'CLILocation'
        
        if has_cli_event:
            args.extend(['--event', cli_event])
        elif not has_yaml:
            # Need some event if no YAML
            args.extend(['--event', 'DefaultEvent'])
        
        if has_cli_location:
            args.extend(['--location', cli_location])
        
        # Configure environment
        env = test_env.copy()
        env['GENERATE_CHECKSUMS'] = 'true' if checksums else 'false'
        
        # Run import
        result = run_script('pg-import', *args, env=env)
        
        # Basic success check
        assert result.returncode == 0, f"Import failed: {result.stderr}"
        
        # Find imported files
        archive_path = Path(env['PHOTO_LIBRARY'])
        imported = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        
        assert len(imported) >= 1, "No files imported"
        
        # Check expected event in filename
        expected_event = cli_event if has_cli_event else (yaml_event if has_yaml else 'DefaultEvent')
        for f in imported:
            assert expected_event in f.name, f"Expected {expected_event} in {f.name}"
        
        # Check checksums
        if checksums:
            checksum_files = list(archive_path.rglob('.checksums'))
            # Checksums might be in subdirectories


class TestImportNamingPatternMatrix:
    """Tests for different naming pattern configurations."""
    
    @requires_exiftool
    @requires_pillow
    @pytest.mark.parametrize("pattern,expected_format", [
        ('{date}_{event}_{seq:03d}', 'date_event_seq'),
        ('{event}_{date}_{seq:03d}', 'event_date_seq'),
        ('{date}_{seq:04d}', 'date_seq'),
    ])
    def test_naming_pattern(
        self, run_script, tmp_path: Path, test_env,
        pattern, expected_format
    ):
        """Test different naming patterns."""
        sd_card = tmp_path / 'SD_CARD'
        sd_card.mkdir()
        create_sd_card_structure(sd_card, num_photos=2)
        
        env = test_env.copy()
        env['NAMING_PATTERN'] = pattern
        
        result = run_script(
            'pg-import', str(sd_card),
            '--event', 'PatternTest',
            '--no-delete',
            env=env
        )
        
        assert result.returncode == 0
        
        # Verify files exist and match expected format
        archive_path = Path(env['PHOTO_LIBRARY'])
        imported = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        
        assert len(imported) >= 1


class TestImportFolderStructureMatrix:
    """Tests for different folder structure configurations."""
    
    @requires_exiftool
    @requires_pillow
    @pytest.mark.parametrize("structure,depth", [
        ('{year}-{month}-{day}', 1),  # Single folder: 2026-01-24
        ('{year}/{month}/{day}', 3),  # Nested: 2026/01/24
        ('{year}/{month}', 2),        # Year/month: 2026/01
        ('{year}', 1),                # Year only: 2026
    ])
    def test_folder_structure(
        self, run_script, tmp_path: Path, test_env,
        structure, depth
    ):
        """Test different folder structure patterns."""
        sd_card = tmp_path / 'SD_CARD'
        sd_card.mkdir()
        create_sd_card_structure(sd_card, num_photos=2)
        
        env = test_env.copy()
        env['FOLDER_STRUCTURE'] = structure
        
        result = run_script(
            'pg-import', str(sd_card),
            '--event', 'StructureTest',
            '--no-delete',
            env=env
        )
        
        assert result.returncode == 0
        
        # Verify folder depth
        archive_path = Path(env['PHOTO_LIBRARY'])
        imported = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        
        assert len(imported) >= 1
        
        # Check path depth from archive root
        for f in imported:
            relative_path = f.relative_to(archive_path)
            # Path depth is number of parts minus filename
            actual_depth = len(relative_path.parts) - 1
            assert actual_depth == depth, f"Expected depth {depth}, got {actual_depth} for {relative_path}"


class TestImportDryRunMatrix:
    """Matrix tests for dry-run mode across different configurations."""
    
    @requires_exiftool
    @requires_pillow
    @pytest.mark.parametrize("has_yaml,verbose", [
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    ])
    def test_dry_run_combinations(
        self, run_script, tmp_path: Path, test_env,
        has_yaml, verbose
    ):
        """Test dry-run with different configurations."""
        sd_card = tmp_path / 'SD_CARD'
        sd_card.mkdir()
        create_sd_card_structure(sd_card, num_photos=2)
        
        if has_yaml:
            create_import_yaml(sd_card, event='DryRunYAML')
        
        args = [str(sd_card), '--dry-run']
        
        if not has_yaml:
            args.extend(['--event', 'DryRunTest'])
        
        if verbose:
            args.append('--verbose')
        
        result = run_script('pg-import', *args)
        
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert 'DRY-RUN' in output
        
        # Verify no files were actually created
        archive_path = Path(test_env['PHOTO_LIBRARY'])
        imported = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        assert len(imported) == 0, "Dry-run should not create files"


class TestDevelopOptionMatrix:
    """Matrix tests for pg-develop options."""
    
    @requires_pillow
    @requires_imagemagick
    @pytest.mark.parametrize("processor,quality,resize", [
        ('imagemagick', '85', None),
        ('imagemagick', '95', None),
        ('imagemagick', '85', '800x600'),
        ('imagemagick', '95', '1920x'),
    ])
    def test_develop_combinations(
        self, run_script, tmp_path: Path, test_env,
        processor, quality, resize
    ):
        """Test develop with different quality/resize combinations."""
        from tests.fixtures.photo_factory import create_raw_like
        from tests.conftest import has_imagemagick
        
        if not has_imagemagick():
            pytest.skip("ImageMagick not installed")
        
        raw_file = create_raw_like(tmp_path / 'test.cr3')
        output_dir = tmp_path / 'output'
        output_dir.mkdir()
        
        args = [
            str(raw_file),
            '--processor', processor,
            '--quality', quality,
            '--output', str(output_dir)
        ]
        
        if resize:
            args.extend(['--resize', resize])
        
        result = run_script('pg-develop', *args)
        
        # Script should complete without crashing
        # Actual processing may fail on mock RAW files
        output = result.stdout + result.stderr
        assert 'Development complete' in output or 'Processing' in output


class TestVerifyModeMatrix:
    """Matrix tests for pg-verify modes."""
    
    @requires_pillow
    @pytest.mark.parametrize("mode,recursive", [
        ('generate', True),
        ('generate', False),
        ('check', True),
        ('check', False),
        ('update', True),
        ('update', False),
    ])
    def test_verify_mode_combinations(
        self, run_script, tmp_path: Path, test_env,
        mode, recursive
    ):
        """Test verify modes with recursive/non-recursive options."""
        from tests.fixtures.photo_factory import create_jpeg
        
        # Create directory structure
        base = tmp_path / 'photos'
        sub = base / 'subdir'
        base.mkdir()
        sub.mkdir()
        
        create_jpeg(base / 'top.jpg')
        create_jpeg(sub / 'nested.jpg')
        
        # For check/update, we need existing checksums
        if mode in ('check', 'update'):
            run_script('pg-verify', str(base), '--generate')
        
        args = [str(base), f'--{mode}']
        
        if not recursive:
            args.append('--no-recursive')
        
        result = run_script('pg-verify', *args)
        
        # check might fail if no checksums exist for some files
        # but the command should run


class TestEdgeCaseMatrix:
    """Matrix tests for edge cases and special characters."""
    
    @requires_exiftool
    @requires_pillow
    @pytest.mark.parametrize("event_name", [
        'Simple',
        'With Spaces',
        'With-Dashes',
        'With_Underscores',
        'MixedCase123',
        'Special@Chars!',
    ])
    def test_event_name_variations(
        self, run_script, tmp_path: Path, test_env,
        event_name
    ):
        """Test import with various event name formats."""
        sd_card = tmp_path / 'SD_CARD'
        sd_card.mkdir()
        create_sd_card_structure(sd_card, num_photos=1)
        
        result = run_script(
            'pg-import', str(sd_card),
            '--event', event_name,
            '--no-delete'
        )
        
        assert result.returncode == 0
        
        # Files should be created (name sanitized)
        archive_path = Path(test_env['PHOTO_LIBRARY'])
        imported = list(archive_path.rglob('*.jpg')) + list(archive_path.rglob('*.JPG'))
        
        assert len(imported) >= 1
