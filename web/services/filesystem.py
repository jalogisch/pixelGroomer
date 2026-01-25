"""Filesystem service for path browsing and drive detection."""
from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional


class FilesystemService:
    """Service for browsing filesystem and detecting drives."""
    
    # Common mount points by OS
    MOUNT_POINTS = {
        'Darwin': ['/Volumes'],  # macOS
        'Linux': ['/media', '/mnt', '/run/media'],
    }
    
    # Directories to hide in browser
    HIDDEN_DIRS = {'.', '..', '.Spotlight-V100', '.fseventsd', '.Trashes', '$RECYCLE.BIN'}
    
    def __init__(self, config: dict):
        self.config = config
        self.system = platform.system()
    
    def get_drives(self) -> list[dict]:
        """Get list of mounted drives/volumes.
        
        Returns list of dicts with: name, path, type (usb/internal/network)
        """
        drives = []
        
        if self.system == 'Darwin':
            drives = self._get_macos_drives()
        elif self.system == 'Linux':
            drives = self._get_linux_drives()
        
        return drives
    
    def _get_macos_drives(self) -> list[dict]:
        """Get mounted volumes on macOS."""
        drives = []
        volumes_path = Path('/Volumes')
        
        if not volumes_path.exists():
            return drives
        
        for volume in volumes_path.iterdir():
            if volume.name.startswith('.'):
                continue
            
            drive_type = self._detect_drive_type_macos(volume)
            
            drives.append({
                'name': volume.name,
                'path': str(volume),
                'type': drive_type,
                'icon': self._get_drive_icon(drive_type),
            })
        
        return sorted(drives, key=lambda d: (d['type'] != 'usb', d['name']))
    
    def _detect_drive_type_macos(self, volume: Path) -> str:
        """Detect drive type on macOS using diskutil."""
        try:
            result = subprocess.run(
                ['diskutil', 'info', str(volume)],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout.lower()
            
            if 'usb' in output or 'external' in output:
                return 'usb'
            elif 'network' in output or 'afp' in output or 'smb' in output:
                return 'network'
            else:
                return 'internal'
        except Exception:
            return 'unknown'
    
    def _get_linux_drives(self) -> list[dict]:
        """Get mounted drives on Linux."""
        drives = []
        
        # Check common mount points
        for mount_base in self.MOUNT_POINTS.get('Linux', []):
            mount_path = Path(mount_base)
            if not mount_path.exists():
                continue
            
            # For /media and /run/media, check user subdirectories
            if mount_base in ['/media', '/run/media']:
                for user_dir in mount_path.iterdir():
                    if user_dir.is_dir():
                        for volume in user_dir.iterdir():
                            if volume.is_dir() and not volume.name.startswith('.'):
                                drives.append({
                                    'name': volume.name,
                                    'path': str(volume),
                                    'type': 'usb',
                                    'icon': self._get_drive_icon('usb'),
                                })
            else:
                for volume in mount_path.iterdir():
                    if volume.is_dir() and not volume.name.startswith('.'):
                        drives.append({
                            'name': volume.name,
                            'path': str(volume),
                            'type': 'external',
                            'icon': self._get_drive_icon('external'),
                        })
        
        return sorted(drives, key=lambda d: d['name'])
    
    def _get_drive_icon(self, drive_type: str) -> str:
        """Get icon name for drive type."""
        icons = {
            'usb': 'usb',
            'internal': 'hdd',
            'network': 'network',
            'external': 'external',
            'unknown': 'folder',
        }
        return icons.get(drive_type, 'folder')
    
    def list_directory(self, path: str, show_hidden: bool = False) -> Optional[dict]:
        """List contents of a directory.
        
        Returns dict with: path, parent, directories, files
        Returns None if path doesn't exist or isn't accessible.
        """
        dir_path = Path(path).expanduser().resolve()
        
        if not dir_path.exists() or not dir_path.is_dir():
            return None
        
        try:
            items = list(dir_path.iterdir())
        except PermissionError:
            return None
        
        directories = []
        files = []
        
        for item in sorted(items, key=lambda x: x.name.lower()):
            # Skip hidden items unless requested
            if not show_hidden and item.name.startswith('.'):
                continue
            
            # Skip system directories
            if item.name in self.HIDDEN_DIRS:
                continue
            
            if item.is_dir():
                directories.append({
                    'name': item.name,
                    'path': str(item),
                })
            elif item.is_file():
                files.append({
                    'name': item.name,
                    'path': str(item),
                    'size': item.stat().st_size,
                })
        
        # Get parent directory
        parent = str(dir_path.parent) if dir_path.parent != dir_path else None
        
        return {
            'path': str(dir_path),
            'name': dir_path.name or str(dir_path),
            'parent': parent,
            'directories': directories,
            'files': files,
        }
    
    def get_quick_paths(self) -> list[dict]:
        """Get list of quick access paths (home, common directories)."""
        paths = []
        home = Path.home()
        
        # Home directory
        paths.append({
            'name': 'Home',
            'path': str(home),
            'icon': 'home',
        })
        
        # Common directories
        common_dirs = [
            ('Pictures', home / 'Pictures'),
            ('Desktop', home / 'Desktop'),
            ('Downloads', home / 'Downloads'),
            ('Documents', home / 'Documents'),
        ]
        
        for name, path in common_dirs:
            if path.exists():
                paths.append({
                    'name': name,
                    'path': str(path),
                    'icon': 'folder',
                })
        
        # Photo library from config
        library_path = self.config.get('PHOTO_LIBRARY')
        if library_path:
            lib_path = Path(library_path)
            if lib_path.exists():
                paths.append({
                    'name': 'Photo Library',
                    'path': str(lib_path),
                    'icon': 'image',
                })
        
        return paths
