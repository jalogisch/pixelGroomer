"""Photo library service."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Optional

from PIL import Image, ImageOps


class LibraryService:
    """Service for accessing the photo library."""
    
    # Supported image extensions
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    RAW_EXTENSIONS = {'.cr2', '.cr3', '.nef', '.arw', '.orf', '.rw2', '.dng', '.raf'}
    
    def __init__(self, config: dict):
        self.config = config
        self.library_path = Path(config['PHOTO_LIBRARY'])
        self.thumbnail_dir = config['THUMBNAIL_DIR']
        self.thumbnail_size = config['THUMBNAIL_SIZE']
        self.ratings_file = config['DATA_DIR'] / 'ratings.json'
        
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        self._ratings = self._load_ratings()
    
    def _load_ratings(self) -> dict:
        """Load ratings from file."""
        if self.ratings_file.exists():
            with open(self.ratings_file) as f:
                return json.load(f)
        return {}
    
    def _save_ratings(self):
        """Save ratings to file."""
        with open(self.ratings_file, 'w') as f:
            json.dump(self._ratings, f, indent=2)
    
    def get_folders(self) -> list[str]:
        """Get list of folders in the library."""
        if not self.library_path.exists():
            return []
        
        folders = []
        for item in sorted(self.library_path.iterdir(), reverse=True):
            if item.is_dir() and not item.name.startswith('.'):
                folders.append(item.name)
        
        return folders
    
    def get_photos(self, folder: str) -> list[str]:
        """Get list of photos in a folder."""
        folder_path = self.library_path / folder
        
        if not folder_path.exists():
            return []
        
        photos = []
        all_extensions = self.IMAGE_EXTENSIONS | self.RAW_EXTENSIONS
        
        for item in sorted(folder_path.iterdir()):
            if item.is_file() and item.suffix.lower() in all_extensions:
                photos.append(str(item.relative_to(self.library_path)))
        
        return photos
    
    def get_photo_info(self, photo_path: str) -> Optional[dict]:
        """Get information about a photo."""
        full_path = self.library_path / photo_path
        
        if not full_path.exists():
            return None
        
        stat = full_path.stat()
        
        info = {
            'path': photo_path,
            'name': full_path.name,
            'size': stat.st_size,
            'size_human': self._format_size(stat.st_size),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': full_path.suffix.lower(),
            'is_raw': full_path.suffix.lower() in self.RAW_EXTENSIONS,
            'rating': self._ratings.get(photo_path, 0),
        }
        
        # Try to get image dimensions for non-RAW files
        if full_path.suffix.lower() in self.IMAGE_EXTENSIONS:
            try:
                with Image.open(full_path) as img:
                    info['width'] = img.width
                    info['height'] = img.height
                    info['dimensions'] = f"{img.width} x {img.height}"
            except Exception:
                pass
        
        return info
    
    def _format_size(self, size: int) -> str:
        """Format file size for display."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def get_thumbnail(self, photo_path: str) -> Optional[Path]:
        """Get or generate a thumbnail for a photo."""
        full_path = self.library_path / photo_path
        
        if not full_path.exists():
            return None
        
        # Generate thumbnail path
        thumb_name = photo_path.replace('/', '_').replace('\\', '_') + '.jpg'
        thumb_path = self.thumbnail_dir / thumb_name
        
        # Check if thumbnail exists and is up to date
        if thumb_path.exists():
            if thumb_path.stat().st_mtime >= full_path.stat().st_mtime:
                return thumb_path
        
        # Handle RAW files
        if full_path.suffix.lower() in self.RAW_EXTENSIONS:
            return self._generate_raw_thumbnail(full_path, thumb_path)
        
        # Generate thumbnail for regular images
        return self._generate_thumbnail(full_path, thumb_path)
    
    def _generate_thumbnail(self, full_path: Path, thumb_path: Path) -> Optional[Path]:
        """Generate thumbnail for regular image files."""
        try:
            with Image.open(full_path) as img:
                # Apply EXIF orientation
                img = ImageOps.exif_transpose(img)
                
                # Create thumbnail
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                img.save(thumb_path, 'JPEG', quality=85)
            
            return thumb_path
        except Exception:
            return None
    
    def _generate_raw_thumbnail(self, full_path: Path, thumb_path: Path) -> Optional[Path]:
        """Generate thumbnail for RAW files.
        
        Tries multiple methods:
        1. Extract embedded JPEG preview using exiftool (fastest)
        2. Use dcraw to generate preview
        3. Use rawpy if available
        """
        # Method 1: Extract embedded preview with exiftool
        preview = self._extract_raw_preview_exiftool(full_path)
        if preview:
            try:
                img = Image.open(BytesIO(preview))
                img = ImageOps.exif_transpose(img)
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(thumb_path, 'JPEG', quality=85)
                return thumb_path
            except Exception:
                pass
        
        # Method 2: Try dcraw
        if self._generate_raw_thumbnail_dcraw(full_path, thumb_path):
            return thumb_path
        
        # Method 3: Try rawpy (if installed)
        if self._generate_raw_thumbnail_rawpy(full_path, thumb_path):
            return thumb_path
        
        return None
    
    def _extract_raw_preview_exiftool(self, raw_path: Path) -> Optional[bytes]:
        """Extract embedded JPEG preview from RAW using exiftool."""
        try:
            # exiftool -b -PreviewImage or -JpgFromRaw
            result = subprocess.run(
                ['exiftool', '-b', '-PreviewImage', str(raw_path)],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout and len(result.stdout) > 1000:
                return result.stdout
            
            # Try JpgFromRaw (used by some cameras)
            result = subprocess.run(
                ['exiftool', '-b', '-JpgFromRaw', str(raw_path)],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout and len(result.stdout) > 1000:
                return result.stdout
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def _generate_raw_thumbnail_dcraw(self, raw_path: Path, thumb_path: Path) -> bool:
        """Generate thumbnail using dcraw."""
        try:
            # dcraw -e extracts embedded thumbnail
            result = subprocess.run(
                ['dcraw', '-e', '-c', str(raw_path)],
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout:
                img = Image.open(BytesIO(result.stdout))
                img = ImageOps.exif_transpose(img)
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(thumb_path, 'JPEG', quality=85)
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        
        return False
    
    def _generate_raw_thumbnail_rawpy(self, raw_path: Path, thumb_path: Path) -> bool:
        """Generate thumbnail using rawpy library."""
        try:
            import rawpy
            with rawpy.imread(str(raw_path)) as raw:
                # Try to get embedded thumbnail first
                try:
                    thumb = raw.extract_thumb()
                    if thumb.format == rawpy.ThumbFormat.JPEG:
                        img = Image.open(BytesIO(thumb.data))
                    else:
                        img = Image.fromarray(thumb.data)
                except rawpy.LibRawNoThumbnailError:
                    # Generate from raw data (slower)
                    rgb = raw.postprocess(use_camera_wb=True, half_size=True)
                    img = Image.fromarray(rgb)
                
                img = ImageOps.exif_transpose(img)
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(thumb_path, 'JPEG', quality=85)
                return True
        except ImportError:
            pass  # rawpy not installed
        except Exception:
            pass
        
        return False
    
    def get_rating(self, photo_path: str) -> int:
        """Get the rating for a photo."""
        return self._ratings.get(photo_path, 0)
    
    def set_rating(self, photo_path: str, rating: int):
        """Set the rating for a photo."""
        rating = max(0, min(5, rating))
        
        if rating == 0:
            self._ratings.pop(photo_path, None)
        else:
            self._ratings[photo_path] = rating
        
        self._save_ratings()
