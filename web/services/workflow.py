"""Workflow engine service."""
from __future__ import annotations

import json
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class WorkflowService:
    """Service for managing and executing workflows."""
    
    def __init__(self, config: dict):
        self.config = config
        self.data_dir = config['DATA_DIR'] / 'workflows'
        self.examples_dir = config['DATA_DIR'] / 'examples'
        self.pixelgroomer_root = config['PIXELGROOMER_ROOT']
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, name: str, steps: list[dict]) -> str:
        """Save a workflow and return its ID."""
        workflow_id = str(uuid.uuid4())[:8]
        
        workflow = {
            'id': workflow_id,
            'name': name,
            'steps': steps,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        
        filepath = self.data_dir / f'{workflow_id}.json'
        with open(filepath, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        return workflow_id
    
    def load(self, workflow_id: str) -> Optional[dict]:
        """Load a workflow by ID."""
        filepath = self.data_dir / f'{workflow_id}.json'
        
        if not filepath.exists():
            return None
        
        with open(filepath) as f:
            return json.load(f)
    
    def list_workflows(self) -> list[dict]:
        """List all saved workflows."""
        workflows = []
        
        for filepath in self.data_dir.glob('*.json'):
            with open(filepath) as f:
                workflow = json.load(f)
                workflows.append({
                    'id': workflow['id'],
                    'name': workflow['name'],
                    'steps_count': len(workflow['steps']),
                    'updated_at': workflow.get('updated_at', ''),
                })
        
        # Sort by updated date, newest first
        workflows.sort(key=lambda w: w['updated_at'], reverse=True)
        return workflows
    
    def delete(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        filepath = self.data_dir / f'{workflow_id}.json'
        
        if filepath.exists():
            filepath.unlink()
            return True
        
        return False
    
    def list_examples(self) -> list[dict]:
        """List all example workflows."""
        examples = []
        
        if not self.examples_dir.exists():
            return examples
        
        for filepath in self.examples_dir.glob('*.json'):
            try:
                with open(filepath) as f:
                    workflow = json.load(f)
                    examples.append({
                        'id': workflow['id'],
                        'name': workflow['name'],
                        'description': workflow.get('description', ''),
                        'category': workflow.get('category', 'general'),
                        'steps_count': len(workflow.get('steps', [])),
                    })
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Sort by category then name
        examples.sort(key=lambda e: (e['category'], e['name']))
        return examples
    
    def load_example(self, example_id: str) -> Optional[dict]:
        """Load an example workflow by ID."""
        if not self.examples_dir.exists():
            return None
        
        for filepath in self.examples_dir.glob('*.json'):
            try:
                with open(filepath) as f:
                    workflow = json.load(f)
                    if workflow.get('id') == example_id:
                        return workflow
            except (json.JSONDecodeError, KeyError):
                continue
        
        return None
    
    def execute(self, steps: list[dict], dry_run: bool = False) -> dict:
        """Execute a workflow."""
        from modules import get_module
        
        results = {
            'success': True,
            'steps': [],
            'errors': [],
            'dry_run': dry_run,
        }
        
        context = {}
        
        for step in steps:
            module_id = step['module_id']
            params = step.get('params', {})
            
            module = get_module(module_id)
            if not module:
                results['errors'].append(f"Module not found: {module_id}")
                results['success'] = False
                break
            
            # Validate parameters
            errors = module.validate(params)
            if errors:
                results['errors'].extend(errors)
                results['success'] = False
                break
            
            step_result = {
                'step_id': step['id'],
                'module_id': module_id,
                'module_name': module.name,
                'status': 'pending',
            }
            
            if dry_run:
                step_result['status'] = 'skipped (dry run)'
                step_result['command'] = module.get_command(params)
            else:
                try:
                    output = module.execute(params, context)
                    step_result['status'] = 'success'
                    step_result['output'] = output
                    
                    # Update context with outputs for next steps
                    context.update(output)
                except Exception as e:
                    step_result['status'] = 'error'
                    step_result['error'] = str(e)
                    results['success'] = False
                    results['errors'].append(f"Step {step['id']}: {e}")
            
            results['steps'].append(step_result)
            
            if not results['success']:
                break
        
        return results
    
    def run_script(self, script_name: str, args: list[str]) -> dict:
        """Run a pg-* script and return the result."""
        script_path = self.pixelgroomer_root / 'bin' / script_name
        
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        # Activate venv and run script
        venv_activate = self.pixelgroomer_root / '.venv' / 'bin' / 'activate'
        
        cmd = f'source "{venv_activate}" && "{script_path}" {" ".join(args)}'
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(self.pixelgroomer_root),
        )
        
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0,
        }
