"""Workflow planner routes."""
from flask import Blueprint, render_template, request, session, current_app, jsonify

workflow_bp = Blueprint('workflow', __name__, url_prefix='/workflow')


@workflow_bp.route('/')
def index():
    """Render the workflow planner page."""
    from modules import get_all_modules
    
    modules = get_all_modules()
    workflow_steps = session.get('workflow_steps', [])
    
    return render_template(
        'workflow/index.html',
        modules=modules,
        workflow_steps=workflow_steps,
    )


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
