"""
Synthetic photo factory for test fixtures.
Creates minimal valid JPEG files with controllable EXIF metadata.
"""

import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Check if Pillow is available
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


def has_exiftool() -> bool:
    """Check if exiftool is available."""
    return shutil.which('exiftool') is not None


def create_jpeg(
    path: Path,
    width: int = 100,
    height: int = 100,
    color: tuple = (128, 128, 128),
    exif: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Create a minimal valid JPEG file.
    
    Args:
        path: Output path for the JPEG
        width: Image width in pixels
        height: Image height in pixels
        color: RGB tuple for fill color
        exif: Optional dict of EXIF fields to set
    
    Returns:
        Path to created file
    """
    if not HAS_PILLOW:
        raise RuntimeError("Pillow is required for creating test images")
    
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create a simple solid color image
    img = Image.new('RGB', (width, height), color)
    img.save(str(path), 'JPEG', quality=85)
    
    # Set EXIF data if provided
    if exif:
        set_exif(path, **exif)
    
    return path


def create_jpeg_with_date(
    path: Path,
    date: datetime,
    event: Optional[str] = None,
    author: Optional[str] = None,
    camera: Optional[str] = None
) -> Path:
    """
    Create a JPEG with specific date and optional metadata.
    
    Args:
        path: Output path
        date: DateTimeOriginal to set
        event: Optional event name
        author: Optional author/artist name
        camera: Optional camera model
    
    Returns:
        Path to created file
    """
    exif = {
        'DateTimeOriginal': date.strftime('%Y:%m:%d %H:%M:%S'),
        'CreateDate': date.strftime('%Y:%m:%d %H:%M:%S'),
    }
    
    if event:
        exif['Event'] = event
    if author:
        exif['Artist'] = author
    if camera:
        exif['Model'] = camera
    
    return create_jpeg(path, exif=exif)


def create_raw_like(path: Path, extension: str = 'cr3') -> Path:
    """
    Create a file that mimics a RAW file structure.
    
    For testing purposes, we create a JPEG and rename it.
    This allows testing file handling without actual RAW processing.
    
    Args:
        path: Output path (extension will be forced to given type)
        extension: RAW extension to use (cr2, cr3, nef, arw, etc.)
    
    Returns:
        Path to created file
    """
    path = Path(path)
    if path.suffix.lower() != f'.{extension.lower()}':
        path = path.with_suffix(f'.{extension}')
    
    # Create a JPEG internally (exiftool can still read/write metadata)
    create_jpeg(path)
    
    return path


def set_exif(path: Path, **kwargs) -> bool:
    """
    Set EXIF metadata on a file using exiftool.
    
    Args:
        path: Path to the image file
        **kwargs: EXIF field names and values
            Supported fields:
            - DateTimeOriginal: "YYYY:MM:DD HH:MM:SS"
            - CreateDate: "YYYY:MM:DD HH:MM:SS"
            - Artist: Author name
            - Copyright: Copyright notice
            - Event: XMP:Event
            - Location: XMP:Location
            - Model: Camera model
            - Make: Camera make
            - GPSLatitude/GPSLongitude: GPS coordinates
    
    Returns:
        True if successful
    """
    if not has_exiftool():
        raise RuntimeError("exiftool is required for setting EXIF metadata")
    
    args = ['exiftool', '-overwrite_original']
    
    # Map common field names to exiftool tags
    field_map = {
        'DateTimeOriginal': '-DateTimeOriginal',
        'CreateDate': '-CreateDate',
        'Artist': '-Artist',
        'Author': '-Artist',
        'Copyright': '-Copyright',
        'Event': '-XMP:Event',
        'Location': '-XMP:Location',
        'Model': '-Model',
        'Camera': '-Model',
        'Make': '-Make',
        'GPSLatitude': '-GPSLatitude',
        'GPSLongitude': '-GPSLongitude',
    }
    
    for field, value in kwargs.items():
        if field in field_map:
            args.append(f'{field_map[field]}={value}')
        else:
            # Use as-is for direct exiftool tags
            args.append(f'-{field}={value}')
    
    args.append(str(path))
    
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False


def get_exif(path: Path, field: str) -> Optional[str]:
    """
    Get a specific EXIF field value from a file.
    
    Args:
        path: Path to the image file
        field: EXIF field name (e.g., 'DateTimeOriginal', 'Artist')
    
    Returns:
        Field value or None if not found
    """
    if not has_exiftool():
        return None
    
    try:
        result = subprocess.run(
            ['exiftool', '-s3', f'-{field}', str(path)],
            capture_output=True,
            text=True,
            check=True
        )
        value = result.stdout.strip()
        return value if value else None
    except subprocess.CalledProcessError:
        return None


def create_sd_card_structure(base_path: Path, num_photos: int = 3) -> Path:
    """
    Create a mock SD card directory structure with sample photos.
    
    Args:
        base_path: Base directory for the SD card
        num_photos: Number of sample photos to create
    
    Returns:
        Path to DCIM directory
    """
    dcim = base_path / 'DCIM' / '100CANON'
    dcim.mkdir(parents=True, exist_ok=True)
    
    base_date = datetime(2026, 1, 24, 10, 0, 0)
    
    for i in range(num_photos):
        photo_date = datetime(
            base_date.year,
            base_date.month,
            base_date.day,
            base_date.hour + i,
            base_date.minute,
            base_date.second
        )
        
        create_jpeg_with_date(
            dcim / f'IMG_{1000 + i:04d}.JPG',
            date=photo_date,
            camera='Canon EOS R5'
        )
    
    return dcim


def create_import_yaml(path: Path, **kwargs) -> Path:
    """
    Create a .import.yaml file.
    
    Args:
        path: Directory to create the file in
        **kwargs: YAML fields (event, location, author, tags, etc.)
    
    Returns:
        Path to created YAML file
    """
    import yaml
    
    yaml_path = Path(path) / '.import.yaml'
    
    with open(yaml_path, 'w') as f:
        yaml.dump(kwargs, f, default_flow_style=False)
    
    return yaml_path
