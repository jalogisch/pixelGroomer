"""
Shared pytest fixtures for PixelGroomer tests.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Generator, Dict, Any

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'lib'))

from tests.fixtures.photo_factory import (
    create_jpeg,
    create_jpeg_with_date,
    create_sd_card_structure,
    create_import_yaml,
    has_exiftool,
    HAS_PILLOW,
)


# =============================================================================
# Skip markers for optional dependencies
# =============================================================================

def has_darktable() -> bool:
    """Check if darktable-cli is available."""
    return shutil.which('darktable-cli') is not None


def has_imagemagick() -> bool:
    """Check if ImageMagick convert is available."""
    return shutil.which('convert') is not None


# Conditional skip decorators
requires_exiftool = pytest.mark.skipif(
    not has_exiftool(),
    reason="exiftool not installed"
)

requires_pillow = pytest.mark.skipif(
    not HAS_PILLOW,
    reason="Pillow not installed"
)

requires_darktable = pytest.mark.skipif(
    not has_darktable(),
    reason="darktable-cli not installed"
)

requires_imagemagick = pytest.mark.skipif(
    not has_imagemagick(),
    reason="ImageMagick not installed"
)


# =============================================================================
# Path fixtures
# =============================================================================

@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def bin_dir(project_root: Path) -> Path:
    """Return the bin/ directory containing scripts."""
    return project_root / 'bin'


@pytest.fixture
def lib_dir(project_root: Path) -> Path:
    """Return the lib/ directory containing modules."""
    return project_root / 'lib'


# =============================================================================
# Environment fixtures
# =============================================================================

@pytest.fixture
def non_interactive_env() -> Dict[str, str]:
    """Environment variables for non-interactive mode."""
    env = os.environ.copy()
    env['PG_NON_INTERACTIVE'] = '1'
    return env


@pytest.fixture
def test_env(tmp_path: Path, project_root: Path) -> Dict[str, str]:
    """
    Complete test environment with isolated directories.
    
    Sets up:
    - PHOTO_LIBRARY: temp archive directory
    - ALBUM_DIR: temp albums directory
    - EXPORT_DIR: temp export directory
    - PG_NON_INTERACTIVE: enabled
    - PIXELGROOMER_ROOT: project root
    """
    archive = tmp_path / 'PhotoLibrary'
    albums = tmp_path / 'Albums'
    export = tmp_path / 'Export'
    
    archive.mkdir()
    albums.mkdir()
    export.mkdir()
    
    env = os.environ.copy()
    env['PHOTO_LIBRARY'] = str(archive)
    env['ALBUM_DIR'] = str(albums)
    env['EXPORT_DIR'] = str(export)
    env['PG_NON_INTERACTIVE'] = '1'
    env['PIXELGROOMER_ROOT'] = str(project_root)
    env['GENERATE_CHECKSUMS'] = 'false'  # Speed up tests
    env['CONFIRM_DELETE'] = 'false'
    
    return env


# =============================================================================
# Directory fixtures
# =============================================================================

@pytest.fixture
def temp_archive(tmp_path: Path) -> Path:
    """Create a temporary photo archive directory."""
    archive = tmp_path / 'PhotoLibrary'
    archive.mkdir()
    return archive


@pytest.fixture
def temp_albums(tmp_path: Path) -> Path:
    """Create a temporary albums directory."""
    albums = tmp_path / 'Albums'
    albums.mkdir()
    return albums


@pytest.fixture
def temp_export(tmp_path: Path) -> Path:
    """Create a temporary export directory."""
    export = tmp_path / 'Export'
    export.mkdir()
    return export


# =============================================================================
# Sample photo fixtures
# =============================================================================

@pytest.fixture
def sample_jpeg(tmp_path: Path) -> Path:
    """Create a single sample JPEG file."""
    photo = tmp_path / 'sample.jpg'
    create_jpeg(photo)
    return photo


@pytest.fixture
def sample_jpeg_with_exif(tmp_path: Path) -> Path:
    """Create a sample JPEG with standard EXIF data."""
    photo = tmp_path / 'sample_exif.jpg'
    create_jpeg_with_date(
        photo,
        date=datetime(2026, 1, 24, 14, 30, 0),
        event='Test Event',
        author='Test Author',
        camera='Canon EOS R5'
    )
    return photo


@pytest.fixture
def sample_photos(tmp_path: Path) -> list:
    """Create multiple sample photos with different dates."""
    photos = []
    base_date = datetime(2026, 1, 24, 10, 0, 0)
    
    for i in range(5):
        photo_date = datetime(
            base_date.year,
            base_date.month,
            base_date.day + (i // 3),  # Spread across days
            base_date.hour + (i % 3),
            base_date.minute,
            base_date.second
        )
        
        photo = tmp_path / f'photo_{i:03d}.jpg'
        create_jpeg_with_date(photo, date=photo_date)
        photos.append(photo)
    
    return photos


# =============================================================================
# SD Card simulation fixtures
# =============================================================================

@pytest.fixture
def temp_sd_card(tmp_path: Path) -> Path:
    """
    Create a mock SD card with sample photos.
    
    Structure:
        SD_CARD/
        └── DCIM/
            └── 100CANON/
                ├── IMG_1000.JPG
                ├── IMG_1001.JPG
                └── IMG_1002.JPG
    """
    sd_root = tmp_path / 'SD_CARD'
    sd_root.mkdir()
    create_sd_card_structure(sd_root, num_photos=3)
    return sd_root


@pytest.fixture
def temp_sd_card_with_yaml(tmp_path: Path) -> Path:
    """
    Create a mock SD card with sample photos and .import.yaml.
    """
    sd_root = tmp_path / 'SD_CARD'
    sd_root.mkdir()
    create_sd_card_structure(sd_root, num_photos=3)
    create_import_yaml(
        sd_root,
        event='Test Import Event',
        location='Test Location',
        author='YAML Author'
    )
    return sd_root


# =============================================================================
# Script runner fixtures
# =============================================================================

@pytest.fixture
def run_script(bin_dir: Path, test_env: Dict[str, str]):
    """
    Factory fixture for running pg-* scripts.
    
    Usage:
        result = run_script('pg-import', '/path/to/sd', '--event', 'Wedding')
    """
    def _run(script_name: str, *args, env: Dict[str, str] = None, 
             check: bool = False, timeout: int = 30) -> subprocess.CompletedProcess:
        script_path = bin_dir / script_name
        
        merged_env = test_env.copy()
        if env:
            merged_env.update(env)
        
        cmd = [str(script_path)] + list(str(a) for a in args)
        
        return subprocess.run(
            cmd,
            env=merged_env,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout
        )
    
    return _run


@pytest.fixture
def run_python(project_root: Path):
    """
    Factory fixture for running Python code in the project venv.
    
    Usage:
        result = run_python('print("hello")')
    """
    venv_python = project_root / '.venv' / 'bin' / 'python'
    
    def _run(code: str, check: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(venv_python), '-c', code],
            capture_output=True,
            text=True,
            check=check
        )
    
    return _run


# =============================================================================
# Cleanup fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def cleanup_env():
    """Ensure environment is clean after each test."""
    yield
    # Any cleanup needed after tests


# =============================================================================
# Test data helpers
# =============================================================================

@pytest.fixture
def date_20260124() -> datetime:
    """Standard test date."""
    return datetime(2026, 1, 24, 14, 30, 0)


@pytest.fixture
def date_20260125() -> datetime:
    """Second test date."""
    return datetime(2026, 1, 25, 10, 0, 0)
