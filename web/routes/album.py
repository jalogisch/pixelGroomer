"""Album manager routes."""
from flask import Blueprint, render_template, request, current_app, session
from pathlib import Path

album_bp = Blueprint('album', __name__, url_prefix='/album')


def get_library_path():
    """Get the current library path from session or config."""
    custom_path = session.get('album_library_path')
    if custom_path and Path(custom_path).exists():
        return custom_path
    return current_app.config.get('PHOTO_LIBRARY', str(Path.home() / 'Pictures'))


@album_bp.route('/')
def index():
    """Render the album manager page."""
    from services.library import LibraryService
    from services.album import AlbumService
    
    # Get library path (custom or from config)
    library_path = get_library_path()
    
    # Create config with custom library path
    config = dict(current_app.config)
    config['PHOTO_LIBRARY'] = library_path
    
    library = LibraryService(config)
    album_service = AlbumService(current_app.config)
    
    # Get folder list
    folders = library.get_folders()
    
    # Get current folder from query param or first available
    current_folder = request.args.get('folder')
    if not current_folder and folders:
        current_folder = folders[0]
    
    # Get photos in folder
    photos = []
    current_index = 0
    if current_folder:
        photos = library.get_photos(current_folder)
        current_index = int(request.args.get('index', 0))
        current_index = max(0, min(current_index, len(photos) - 1))
    
    # Get albums
    albums = album_service.list_albums()
    
    return render_template(
        'album/index.html',
        folders=folders,
        current_folder=current_folder,
        photos=photos,
        current_index=current_index,
        albums=albums,
        library_path=library_path,
        default_library_path=current_app.config.get('PHOTO_LIBRARY', ''),
    )


@album_bp.route('/set-library', methods=['POST'])
def set_library():
    """Set the library path."""
    library_path = request.form.get('library_path', '').strip()
    
    if library_path:
        # Expand ~ and validate
        expanded = str(Path(library_path).expanduser())
        if Path(expanded).exists() and Path(expanded).is_dir():
            session['album_library_path'] = expanded
    
    # Redirect back to album page
    from flask import redirect, url_for
    return redirect(url_for('album.index'))


@album_bp.route('/browser')
def browser():
    """Image browser with navigation."""
    from services.library import LibraryService
    from services.album import AlbumService
    
    # Get library path (custom or from config)
    library_path = get_library_path()
    
    # Create config with custom library path
    config = dict(current_app.config)
    config['PHOTO_LIBRARY'] = library_path
    
    library = LibraryService(config)
    album_service = AlbumService(current_app.config)
    
    folder = request.args.get('folder', '')
    index = int(request.args.get('index', 0))
    
    photos = library.get_photos(folder) if folder else []
    index = max(0, min(index, len(photos) - 1)) if photos else 0
    
    current_photo = photos[index] if photos else None
    photo_info = library.get_photo_info(current_photo) if current_photo else None
    photo_albums = album_service.get_photo_albums(current_photo) if current_photo else []
    albums = album_service.list_albums()
    
    return render_template(
        'album/browser.html',
        folder=folder,
        photos=photos,
        current_index=index,
        current_photo=current_photo,
        photo_info=photo_info,
        photo_albums=photo_albums,
        albums=albums,
    )
