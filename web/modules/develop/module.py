"""Develop module custom implementation."""
from pathlib import Path


class DevelopModule:
    """Custom implementation for the develop module."""
    
    def validate(self, params: dict) -> list[str]:
        """Validate develop parameters."""
        errors = []
        
        source = params.get('source', '')
        if not source:
            errors.append("Source is required")
        else:
            source_path = Path(source).expanduser()
            if not source_path.exists():
                errors.append(f"Source does not exist: {source}")
        
        # Validate quality
        quality = params.get('quality', 95)
        if quality:
            try:
                q = int(quality)
                if not (1 <= q <= 100):
                    errors.append("Quality must be between 1 and 100")
            except ValueError:
                errors.append("Quality must be a number")
        
        return errors
