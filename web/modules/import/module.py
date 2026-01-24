"""Import module custom implementation."""
from pathlib import Path


class ImportModule:
    """Custom implementation for the import module."""
    
    def validate(self, params: dict) -> list[str]:
        """Validate import parameters."""
        errors = []
        
        source = params.get('source', '')
        if not source:
            errors.append("Source directory is required")
        else:
            source_path = Path(source).expanduser()
            if not source_path.exists():
                errors.append(f"Source directory does not exist: {source}")
            elif not source_path.is_dir():
                errors.append(f"Source is not a directory: {source}")
        
        return errors
