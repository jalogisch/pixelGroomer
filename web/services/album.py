"""Album management service."""
import json
import subprocess
from pathlib import Path
from typing import Any


class AlbumService:
    """Service for managing photo albums."""
    
    def __init__(self, config: dict):
        self.config = config
        self.album_dir = Path(config['ALBUM_DIR'])
        self.pixelgroomer_root = config['PIXELGROOMER_ROOT']
        self.albums_file = config['DATA_DIR'] / 'albums.json'
        
        self._albums = self._load_albums()
    
    def _load_albums(self) -> dict:
        """Load albums data from file."""
        if self.albums_file.exists():
            with open(self.albums_file) as f:
                return json.load(f)
        return {'albums': {}}
    
    def _save_albums(self):
        """Save albums data to file."""
        self.albums_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.albums_file, 'w') as f:
            json.dump(self._albums, f, indent=2)
    
    def list_albums(self) -> list[dict]:
        """List all albums."""
        albums = []
        
        for name, data in self._albums.get('albums', {}).items():
            albums.append({
                'name': name,
                'photo_count': len(data.get('photos', [])),
                'description': data.get('description', ''),
            })
        
        albums.sort(key=lambda a: a['name'])
        return albums
    
    def create_album(self, name: str, description: str = '') -> bool:
        """Create a new album."""
        if name in self._albums.get('albums', {}):
            return False
        
        if 'albums' not in self._albums:
            self._albums['albums'] = {}
        
        self._albums['albums'][name] = {
            'photos': [],
            'description': description,
            'export_config': {},
        }
        
        self._save_albums()
        
        # Also create via pg-album if available
        self._run_pg_album('create', name)
        
        return True
    
    def delete_album(self, name: str) -> bool:
        """Delete an album."""
        if name not in self._albums.get('albums', {}):
            return False
        
        del self._albums['albums'][name]
        self._save_albums()
        
        return True
    
    def add_to_album(self, album_name: str, photo_path: str) -> bool:
        """Add a photo to an album."""
        if album_name not in self._albums.get('albums', {}):
            return False
        
        photos = self._albums['albums'][album_name].get('photos', [])
        
        if photo_path not in photos:
            photos.append(photo_path)
            self._albums['albums'][album_name]['photos'] = photos
            self._save_albums()
        
        return True
    
    def remove_from_album(self, album_name: str, photo_path: str) -> bool:
        """Remove a photo from an album."""
        if album_name not in self._albums.get('albums', {}):
            return False
        
        photos = self._albums['albums'][album_name].get('photos', [])
        
        if photo_path in photos:
            photos.remove(photo_path)
            self._albums['albums'][album_name]['photos'] = photos
            self._save_albums()
            return True
        
        return False
    
    def is_in_album(self, album_name: str, photo_path: str) -> bool:
        """Check if a photo is in an album."""
        if album_name not in self._albums.get('albums', {}):
            return False
        
        photos = self._albums['albums'][album_name].get('photos', [])
        return photo_path in photos
    
    def get_photo_albums(self, photo_path: str) -> list[str]:
        """Get list of albums a photo is in."""
        albums = []
        
        for name, data in self._albums.get('albums', {}).items():
            if photo_path in data.get('photos', []):
                albums.append(name)
        
        return albums
    
    def get_album_photos(self, album_name: str) -> list[str]:
        """Get list of photos in an album."""
        if album_name not in self._albums.get('albums', {}):
            return []
        
        return self._albums['albums'][album_name].get('photos', [])
    
    def save_export_config(self, album_name: str, config: dict) -> bool:
        """Save export configuration for an album."""
        if album_name not in self._albums.get('albums', {}):
            return False
        
        self._albums['albums'][album_name]['export_config'] = config
        self._save_albums()
        return True
    
    def get_export_config(self, album_name: str) -> dict:
        """Get export configuration for an album."""
        if album_name not in self._albums.get('albums', {}):
            return {}
        
        return self._albums['albums'][album_name].get('export_config', {})
    
    def export_album(
        self,
        album_name: str,
        output_dir: str = '',
        watermark: str = '',
        max_size_kb: int = 2048,
        resize_px: int = 2048,
    ) -> dict:
        """Export an album to a directory."""
        result = {
            'success': False,
            'message': '',
            'exported_count': 0,
        }
        
        if album_name not in self._albums.get('albums', {}):
            result['message'] = f'Album not found: {album_name}'
            return result
        
        photos = self.get_album_photos(album_name)
        
        if not photos:
            result['message'] = 'Album is empty'
            return result
        
        if not output_dir:
            output_dir = str(Path.home() / 'Desktop' / f'{album_name}_export')
        
        # Save export config
        self.save_export_config(album_name, {
            'output_dir': output_dir,
            'watermark': watermark,
            'max_size_kb': max_size_kb,
            'resize_px': resize_px,
        })
        
        # Run pg-album export
        args = ['export', album_name, '--to', output_dir]
        
        # Note: pg-album export doesn't support all these options yet
        # This would need to be extended or we use a custom export
        
        pg_result = self._run_pg_album(*args)
        
        if pg_result.get('success'):
            result['success'] = True
            result['message'] = f'Exported {len(photos)} photos to {output_dir}'
            result['exported_count'] = len(photos)
        else:
            result['message'] = pg_result.get('stderr', 'Export failed')
        
        return result
    
    def _run_pg_album(self, *args) -> dict:
        """Run the pg-album script."""
        script_path = self.pixelgroomer_root / 'bin' / 'pg-album'
        
        if not script_path.exists():
            return {'success': False, 'stderr': 'pg-album script not found'}
        
        venv_activate = self.pixelgroomer_root / '.venv' / 'bin' / 'activate'
        
        cmd = f'source "{venv_activate}" && "{script_path}" {" ".join(str(a) for a in args)}'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(self.pixelgroomer_root),
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
            }
        except Exception as e:
            return {'success': False, 'stderr': str(e)}
