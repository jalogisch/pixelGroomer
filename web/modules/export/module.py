"""Export module custom implementation."""
from pathlib import Path


class ExportModule:
    """Custom implementation for the export module."""
    
    def validate(self, params: dict) -> list[str]:
        """Validate export parameters."""
        errors = []
        
        source = params.get('source', '')
        if not source:
            errors.append("Source directory is required")
        else:
            source_path = Path(source).expanduser()
            if not source_path.exists():
                errors.append(f"Source directory does not exist: {source}")
        
        output = params.get('output', '')
        if not output:
            errors.append("Output directory is required")
        
        # Validate numeric parameters
        for field in ['max_size', 'resize', 'quality']:
            value = params.get(field)
            if value:
                try:
                    int(value)
                except ValueError:
                    errors.append(f"{field} must be a number")
        
        quality = params.get('quality')
        if quality:
            try:
                q = int(quality)
                if not (1 <= q <= 100):
                    errors.append("Quality must be between 1 and 100")
            except ValueError:
                pass
        
        return errors
