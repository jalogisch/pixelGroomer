"""EXIF module custom implementation."""
from pathlib import Path


class ExifModule:
    """Custom implementation for the EXIF module."""
    
    def validate(self, params: dict) -> list[str]:
        """Validate EXIF parameters."""
        errors = []
        
        directory = params.get('directory', '')
        if not directory:
            errors.append("Directory is required")
        else:
            dir_path = Path(directory).expanduser()
            if not dir_path.exists():
                errors.append(f"Directory does not exist: {directory}")
        
        # Validate GPS format if provided
        gps = params.get('gps', '')
        if gps:
            try:
                parts = gps.split(',')
                if len(parts) != 2:
                    raise ValueError("Invalid format")
                lat, lon = float(parts[0]), float(parts[1])
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    errors.append("GPS coordinates out of range")
            except ValueError:
                errors.append("GPS must be in format: latitude,longitude (e.g., 51.875222,9.648111)")
        
        return errors
