"""Base class for workflow modules."""
import importlib.util
import subprocess
from pathlib import Path
from typing import Any

import yaml


class WorkflowModule:
    """Base class for workflow modules.
    
    A module is defined by:
    - module.yaml: Configuration and parameter definitions
    - module.py: Custom logic implementation (optional)
    """
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str = '',
        icon: str = 'settings',
        order: int = 100,
        parameters: list[dict] = None,
        outputs: list[dict] = None,
        script: str = None,
        module_dir: Path = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.order = order
        self.parameters = parameters or []
        self.outputs = outputs or []
        self.script = script or f'pg-{id}'
        self.module_dir = module_dir
        
        # Load custom module class if available
        self._custom_module = None
        if module_dir:
            self._load_custom_module()
    
    def _load_custom_module(self):
        """Load custom module implementation from module.py."""
        module_py = self.module_dir / 'module.py'
        
        if not module_py.exists():
            return
        
        try:
            spec = importlib.util.spec_from_file_location(
                f"modules.{self.id}.module",
                module_py
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for a class that extends WorkflowModule or has execute method
                for name in dir(module):
                    obj = getattr(module, name)
                    if isinstance(obj, type) and name != 'WorkflowModule':
                        if hasattr(obj, 'execute') or hasattr(obj, 'validate'):
                            self._custom_module = obj()
                            break
        except Exception as e:
            print(f"Error loading custom module {self.id}: {e}")
    
    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "WorkflowModule":
        """Load a module from a YAML configuration file."""
        with open(yaml_path) as f:
            config = yaml.safe_load(f)
        
        return cls(
            id=config['id'],
            name=config['name'],
            description=config.get('description', ''),
            icon=config.get('icon', 'settings'),
            order=config.get('order', 100),
            parameters=config.get('parameters', []),
            outputs=config.get('outputs', []),
            script=config.get('script'),
            module_dir=yaml_path.parent,
        )
    
    def get_form_schema(self) -> list[dict]:
        """Get the form schema for UI rendering."""
        return self.parameters
    
    def validate(self, params: dict) -> list[str]:
        """Validate parameters. Returns list of error messages."""
        # Use custom validation if available
        if self._custom_module and hasattr(self._custom_module, 'validate'):
            return self._custom_module.validate(params)
        
        errors = []
        
        for param in self.parameters:
            param_id = param['id']
            value = params.get(param_id)
            
            # Check required fields
            if param.get('required', False):
                if value is None or value == '':
                    errors.append(f"{param['label']} is required")
            
            # Type-specific validation
            if value:
                param_type = param.get('type', 'text')
                
                if param_type == 'number':
                    try:
                        float(value)
                    except ValueError:
                        errors.append(f"{param['label']} must be a number")
                
                elif param_type == 'path':
                    path = Path(value).expanduser()
                    if param.get('must_exist', False) and not path.exists():
                        errors.append(f"{param['label']}: Path does not exist")
        
        return errors
    
    def get_command(self, params: dict) -> str:
        """Get the command that would be executed (for dry run)."""
        args = self._build_args(params)
        return f"{self.script} {' '.join(args)}"
    
    def _build_args(self, params: dict) -> list[str]:
        """Build command line arguments from parameters."""
        args = []
        
        for param in self.parameters:
            param_id = param['id']
            value = params.get(param_id)
            
            if value is None or value == '':
                continue
            
            cli_flag = param.get('cli_flag', f'--{param_id.replace("_", "-")}')
            
            param_type = param.get('type', 'text')
            
            if param_type == 'boolean':
                if value in (True, 'true', '1', 'yes'):
                    args.append(cli_flag)
            elif param_type == 'positional':
                args.insert(0, str(value))
            else:
                args.extend([cli_flag, str(value)])
        
        return args
    
    def execute(self, params: dict, context: dict) -> dict:
        """Execute the module with the given parameters."""
        # Use custom execution if available
        if self._custom_module and hasattr(self._custom_module, 'execute'):
            return self._custom_module.execute(params, context)
        
        # Default: run the associated script
        return self.run_script(params)
    
    def run_script(self, params: dict) -> dict:
        """Run the module's script with the given parameters."""
        from flask import current_app
        
        pixelgroomer_root = current_app.config['PIXELGROOMER_ROOT']
        script_path = pixelgroomer_root / 'bin' / self.script
        
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        args = self._build_args(params)
        venv_activate = pixelgroomer_root / '.venv' / 'bin' / 'activate'
        
        cmd = f'source "{venv_activate}" && "{script_path}" {" ".join(args)}'
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(pixelgroomer_root),
        )
        
        output = {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
        }
        
        # Parse outputs if defined
        for output_def in self.outputs:
            output_id = output_def['id']
            # Output parsing would need to be customized per module
            output[output_id] = None
        
        return output
