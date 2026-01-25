"""Workflow planner routes."""
from flask import Blueprint, render_template, request, session, current_app, jsonify

workflow_bp = Blueprint('workflow', __name__, url_prefix='/workflow')


@workflow_bp.route('/')
def index():
    """Render the workflow planner page."""
    from modules import get_all_modules
    
    modules = get_all_modules()
    workflow_steps = session.get('workflow_steps', [])
    
    # Resolve template variables for display
    resolved_steps = _resolve_step_values(workflow_steps)
    
    return render_template(
        'workflow/index.html',
        modules=modules,
        workflow_steps=resolved_steps,
    )


def _resolve_step_values(steps: list) -> list:
    """Resolve template variables in step parameters for display."""
    import os
    
    config_values = {
        'PHOTO_LIBRARY': current_app.config.get('PHOTO_LIBRARY', '~/Pictures/PhotoLibrary'),
        'ALBUM_DIR': current_app.config.get('ALBUM_DIR', '~/Pictures/Albums'),
        'DEFAULT_AUTHOR': os.environ.get('DEFAULT_AUTHOR', ''),
    }
    
    # Runtime placeholders that are resolved during execution
    runtime_placeholders = {
        '{SOURCE}': 'replaced with each source directory at runtime',
    }
    
    resolved = []
    for step in steps:
        resolved_step = {
            'id': step['id'],
            'module_id': step['module_id'],
            'module_name': step['module_name'],
            'params': {},
        }
        
        for key, value in step.get('params', {}).items():
            if not value:
                continue
            
            str_value = str(value)
            resolved_value = str_value
            explanation = None
            
            # Check for config template variables {{VAR}}
            if '{{' in str_value and '}}' in str_value:
                for var_name, var_value in config_values.items():
                    placeholder = '{{' + var_name + '}}'
                    if placeholder in str_value:
                        if var_value:
                            resolved_value = str_value.replace(placeholder, var_value)
                        else:
                            explanation = f"from config: {var_name}"
            
            # Check for runtime placeholders {VAR}
            for placeholder, desc in runtime_placeholders.items():
                if placeholder in str_value:
                    explanation = desc
            
            resolved_step['params'][key] = {
                'value': resolved_value,
                'original': str_value if resolved_value != str_value else None,
                'explanation': explanation,
            }
        
        resolved.append(resolved_step)
    
    return resolved


@workflow_bp.route('/new')
def new_workflow():
    """Start a new workflow."""
    session['workflow_steps'] = []
    session['workflow_name'] = ''
    return index()


@workflow_bp.route('/load/<workflow_id>')
def load_workflow(workflow_id: str):
    """Load a saved workflow."""
    from services.workflow import WorkflowService
    
    service = WorkflowService(current_app.config)
    workflow = service.load(workflow_id)
    
    if workflow:
        session['workflow_steps'] = workflow.get('steps', [])
        session['workflow_name'] = workflow.get('name', '')
    
    return index()
