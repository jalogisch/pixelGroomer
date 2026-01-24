"""Photo library service."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from PIL import Image


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
        
        # Skip RAW files for now (would need dcraw or similar)
        if full_path.suffix.lower() in self.RAW_EXTENSIONS:
            return None
        
        # Generate thumbnail path
        thumb_name = photo_path.replace('/', '_').replace('\\', '_') + '.jpg'
        thumb_path = self.thumbnail_dir / thumb_name
        
        # Check if thumbnail exists and is up to date
        if thumb_path.exists():
            if thumb_path.stat().st_mtime >= full_path.stat().st_mtime:
                return thumb_path
        
        # Generate thumbnail
        try:
            with Image.open(full_path) as img:
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                img.save(thumb_path, 'JPEG', quality=85)
            
            return thumb_path
        except Exception:
            return None
    
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
