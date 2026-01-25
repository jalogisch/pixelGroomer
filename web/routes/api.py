"""API routes for HTMX interactions."""
from flask import Blueprint, request, session, current_app, render_template, jsonify
from services.filesystem import FilesystemService

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ============================================================================
# Theme
# ============================================================================

@api_bp.route('/theme', methods=['POST'])
def set_theme():
    """Set the current theme."""
    theme = request.form.get('theme', current_app.config['DEFAULT_THEME'])
    session['theme'] = theme
    
    # Return the new theme stylesheet link for HTMX to swap
    return f'<link rel="stylesheet" href="/static/css/themes/{theme}.css" id="theme-css">'


# ============================================================================
# Workflow
# ============================================================================

@api_bp.route('/workflow/steps', methods=['GET'])
def get_workflow_steps():
    """Get current workflow steps."""
    steps = session.get('workflow_steps', [])
    return render_template('workflow/partials/steps.html', steps=steps)


@api_bp.route('/workflow/steps', methods=['POST'])
def add_workflow_step():
    """Add a step to the workflow."""
    from modules import get_module
    
    module_id = request.form.get('module_id')
    module = get_module(module_id)
    
    if not module:
        return 'Module not found', 404
    
    steps = session.get('workflow_steps', [])
    step = {
        'id': len(steps) + 1,
        'module_id': module_id,
        'module_name': module.name,
        'params': {},
    }
    steps.append(step)
    session['workflow_steps'] = steps
    
    return render_template('workflow/partials/steps.html', steps=steps)


@api_bp.route('/workflow/steps/<int:step_id>', methods=['DELETE'])
def remove_workflow_step(step_id: int):
    """Remove a step from the workflow."""
    steps = session.get('workflow_steps', [])
    steps = [s for s in steps if s['id'] != step_id]
    
    # Renumber steps
    for i, step in enumerate(steps):
        step['id'] = i + 1
    
    session['workflow_steps'] = steps
    return render_template('workflow/partials/steps.html', steps=steps)


@api_bp.route('/workflow/steps/<int:step_id>/params', methods=['POST'])
def update_step_params(step_id: int):
    """Update parameters for a workflow step."""
    steps = session.get('workflow_steps', [])
    
    for step in steps:
        if step['id'] == step_id:
            # Update params from form
            for key, value in request.form.items():
                if key != 'step_id':
                    step['params'][key] = value
            break
    
    session['workflow_steps'] = steps
    return '', 204


@api_bp.route('/workflow/module-form/<module_id>', methods=['GET'])
def get_module_form(module_id: str):
    """Get the form for a module."""
    from modules import get_module
    
    module = get_module(module_id)
    if not module:
        return 'Module not found', 404
    
    step_id = request.args.get('step_id', 0)
    
    # Get inherited values from previous workflow steps
    inherited_params = _get_inherited_params(module)
    
    # Resolve template variables in defaults (e.g. {{PHOTO_LIBRARY}})
    params = _resolve_defaults(module, inherited_params)
    
    return render_template(
        'components/module_form.html',
        module=module,
        step_id=step_id,
        params=params,
    )


def _get_inherited_params(module) -> dict:
    """Get parameter values inherited from previous workflow steps."""
    steps = session.get('workflow_steps', [])
    inherited = {}
    
    # Build a map of all outputs from previous steps
    outputs = {}
    for step in steps:
        params = step.get('params', {})
        # Map common output patterns
        if 'destination' in params:
            outputs['target_directory'] = params['destination']
        if 'output' in params:
            outputs['output_directory'] = params['output']
        if 'directory' in params:
            outputs['target_directory'] = params['directory']
        if 'source' in params and 'target_directory' not in outputs:
            outputs['target_directory'] = params['source']
    
    # Check which module parameters can inherit values
    for param in module.parameters:
        inherit_from = param.get('inherit_from')
        if inherit_from and inherit_from in outputs:
            inherited[param['id']] = outputs[inherit_from]
    
    return inherited


def _resolve_defaults(module, inherited_params: dict) -> dict:
    """Resolve template variables in parameter defaults."""
    params = dict(inherited_params)
    
    for param in module.parameters:
        param_id = param['id']
        
        # Skip if already inherited
        if param_id in params:
            continue
        
        default = param.get('default', '')
        if not default:
            continue
        
        # Resolve {{VARIABLE}} placeholders
        if '{{' in str(default):
            if '{{PHOTO_LIBRARY}}' in default:
                params[param_id] = default.replace(
                    '{{PHOTO_LIBRARY}}', 
                    current_app.config.get('PHOTO_LIBRARY', '')
                )
            elif '{{DEFAULT_AUTHOR}}' in default:
                # Read from .env or use empty
                import os
                params[param_id] = default.replace(
                    '{{DEFAULT_AUTHOR}}',
                    os.environ.get('DEFAULT_AUTHOR', '')
                )
    
    return params


@api_bp.route('/workflow/save', methods=['POST'])
def save_workflow():
    """Save the current workflow."""
    from services.workflow import WorkflowService
    
    name = request.form.get('name', 'Untitled Workflow')
    steps = session.get('workflow_steps', [])
    
    service = WorkflowService(current_app.config)
    workflow_id = service.save(name, steps)
    
    session['workflow_name'] = name
    
    return render_template(
        'workflow/partials/save_status.html',
        success=True,
        workflow_id=workflow_id,
        message=f'Workflow "{name}" saved',
    )


@api_bp.route('/workflow/execute', methods=['POST'])
def execute_workflow():
    """Execute the current workflow."""
    from services.workflow import WorkflowService
    
    steps = session.get('workflow_steps', [])
    dry_run = request.form.get('dry_run', 'false') == 'true'
    
    service = WorkflowService(current_app.config)
    result = service.execute(steps, dry_run=dry_run)
    
    return render_template(
        'workflow/partials/execution_result.html',
        result=result,
    )


# ============================================================================
# Photos
# ============================================================================

def _get_library_config():
    """Get config with custom library path from session if set."""
    config = dict(current_app.config)
    custom_path = session.get('album_library_path')
    if custom_path and Path(custom_path).exists():
        config['PHOTO_LIBRARY'] = custom_path
    return config


@api_bp.route('/photos/<path:folder>')
def get_photos(folder: str):
    """Get photos in a folder."""
    from services.library import LibraryService
    
    library = LibraryService(_get_library_config())
    photos = library.get_photos(folder)
    
    return render_template(
        'album/partials/photo_grid.html',
        photos=photos,
        folder=folder,
    )


@api_bp.route('/photos/thumbnail/<path:photo_path>')
def get_thumbnail(photo_path: str):
    """Get or generate a thumbnail for a photo."""
    from services.library import LibraryService
    from flask import send_file
    
    library = LibraryService(_get_library_config())
    thumbnail_path = library.get_thumbnail(photo_path)
    
    if thumbnail_path and thumbnail_path.exists():
        return send_file(thumbnail_path, mimetype='image/jpeg')
    
    # If no thumbnail, try to serve the original image directly for JPGs
    full_path = Path(library.library_path) / photo_path
    if full_path.exists() and full_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}:
        return send_file(full_path)
    
    return '', 404


@api_bp.route('/photos/<path:photo_path>/rate', methods=['POST'])
def rate_photo(photo_path: str):
    """Set the rating for a photo."""
    from services.library import LibraryService
    
    rating = int(request.form.get('rating', 0))
    rating = max(0, min(5, rating))
    
    library = LibraryService(_get_library_config())
    library.set_rating(photo_path, rating)
    
    return render_template(
        'components/rating.html',
        photo_path=photo_path,
        rating=rating,
    )


@api_bp.route('/photos/<path:photo_path>/album', methods=['POST'])
def toggle_photo_album(photo_path: str):
    """Add or remove a photo from an album."""
    from services.album import AlbumService
    
    album_name = request.form.get('album')
    action = request.form.get('action', 'toggle')
    
    service = AlbumService(current_app.config)
    
    if action == 'add':
        service.add_to_album(album_name, photo_path)
    elif action == 'remove':
        service.remove_from_album(album_name, photo_path)
    else:  # toggle
        if service.is_in_album(album_name, photo_path):
            service.remove_from_album(album_name, photo_path)
        else:
            service.add_to_album(album_name, photo_path)
    
    # Return updated album checkboxes
    albums = service.list_albums()
    photo_albums = service.get_photo_albums(photo_path)
    
    return render_template(
        'album/partials/album_checkboxes.html',
        photo_path=photo_path,
        albums=albums,
        photo_albums=photo_albums,
    )


# ============================================================================
# Albums
# ============================================================================

@api_bp.route('/albums', methods=['GET'])
def list_albums():
    """List all albums."""
    from services.album import AlbumService
    
    service = AlbumService(current_app.config)
    albums = service.list_albums()
    
    return render_template(
        'album/partials/album_list.html',
        albums=albums,
    )


@api_bp.route('/albums', methods=['POST'])
def create_album():
    """Create a new album."""
    from services.album import AlbumService
    
    name = request.form.get('name', '').strip()
    if not name:
        return 'Album name required', 400
    
    service = AlbumService(current_app.config)
    service.create_album(name)
    
    albums = service.list_albums()
    return render_template(
        'album/partials/album_list.html',
        albums=albums,
    )


@api_bp.route('/albums/<album_name>/export', methods=['POST'])
def export_album(album_name: str):
    """Export an album."""
    from services.album import AlbumService
    
    output_dir = request.form.get('output_dir', '')
    watermark = request.form.get('watermark', '')
    max_size = int(request.form.get('max_size', 2048))
    resize = int(request.form.get('resize', 2048))
    
    service = AlbumService(current_app.config)
    result = service.export_album(
        album_name,
        output_dir=output_dir,
        watermark=watermark,
        max_size_kb=max_size,
        resize_px=resize,
    )
    
    return render_template(
        'album/partials/export_result.html',
        result=result,
    )


# ============================================================================
# Filesystem Browser
# ============================================================================

@api_bp.route('/filesystem/drives', methods=['GET'])
def get_drives():
    """Get list of mounted drives/volumes."""
    service = FilesystemService(current_app.config)
    drives = service.get_drives()
    quick_paths = service.get_quick_paths()
    
    return render_template(
        'components/path_picker_drives.html',
        drives=drives,
        quick_paths=quick_paths,
    )


@api_bp.route('/filesystem/browse', methods=['GET'])
def browse_directory():
    """Browse a directory."""
    path = request.args.get('path', '')
    target_input = request.args.get('target', '')
    mode = request.args.get('mode', 'directory')  # 'directory' or 'file'
    
    service = FilesystemService(current_app.config)
    
    # Default to home if no path
    if not path:
        path = str(Path.home())
    
    # Expand ~ in path
    path = str(Path(path).expanduser())
    
    contents = service.list_directory(path)
    drives = service.get_drives()
    quick_paths = service.get_quick_paths()
    
    if contents is None:
        # Path not accessible, go to home
        contents = service.list_directory(str(Path.home()))
    
    return render_template(
        'components/path_picker_browser.html',
        contents=contents,
        drives=drives,
        quick_paths=quick_paths,
        target_input=target_input,
        mode=mode,
    )


@api_bp.route('/filesystem/mkdir', methods=['POST'])
def create_directory():
    """Create a new directory."""
    base_path = request.form.get('path', '')
    folder_name = request.form.get('name', '').strip()
    
    if not base_path or not folder_name:
        return jsonify({'success': False, 'error': 'Path and name required'})
    
    # Validate folder name (no path separators, no dots at start)
    if '/' in folder_name or '\\' in folder_name or folder_name.startswith('.'):
        return jsonify({'success': False, 'error': 'Invalid folder name'})
    
    try:
        new_path = Path(base_path).expanduser() / folder_name
        new_path.mkdir(parents=False, exist_ok=False)
        return jsonify({'success': True, 'path': str(new_path)})
    except FileExistsError:
        return jsonify({'success': False, 'error': 'Folder already exists'})
    except PermissionError:
        return jsonify({'success': False, 'error': 'Permission denied'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


from pathlib import Path
