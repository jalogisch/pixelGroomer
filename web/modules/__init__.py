"""Workflow module loader."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .base import WorkflowModule

# Cache for loaded modules
_modules: dict[str, "WorkflowModule"] = {}


def get_modules_dir() -> Path:
    """Get the modules directory path."""
    return Path(__file__).parent


def load_modules() -> dict[str, "WorkflowModule"]:
    """Load all available modules."""
    global _modules
    
    if _modules:
        return _modules
    
    from .base import WorkflowModule
    
    modules_dir = get_modules_dir()
    
    for module_dir in modules_dir.iterdir():
        if not module_dir.is_dir():
            continue
        
        if module_dir.name.startswith('_'):
            continue
        
        yaml_path = module_dir / 'module.yaml'
        if not yaml_path.exists():
            continue
        
        try:
            module = WorkflowModule.from_yaml(yaml_path)
            _modules[module.id] = module
        except Exception as e:
            print(f"Error loading module {module_dir.name}: {e}")
    
    return _modules


def get_all_modules() -> list["WorkflowModule"]:
    """Get all modules sorted by order."""
    modules = load_modules()
    return sorted(modules.values(), key=lambda m: m.order)


def get_module(module_id: str) -> "Optional[WorkflowModule]":
    """Get a specific module by ID."""
    modules = load_modules()
    return modules.get(module_id)


def reload_modules():
    """Reload all modules (useful for development)."""
    global _modules
    _modules = {}
    return load_modules()
