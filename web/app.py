"""Flask Application Factory for PixelGroomer Web."""
import os
from flask import Flask

from config import config


def create_app(config_name: str = None) -> Flask:
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Ensure data directories exist
    app.config['DATA_DIR'].mkdir(parents=True, exist_ok=True)
    app.config['THUMBNAIL_DIR'].mkdir(parents=True, exist_ok=True)
    (app.config['DATA_DIR'] / 'workflows').mkdir(parents=True, exist_ok=True)
    
    # Register blueprints
    from routes.workflow import workflow_bp
    from routes.album import album_bp
    from routes.api import api_bp
    
    app.register_blueprint(workflow_bp)
    app.register_blueprint(album_bp)
    app.register_blueprint(api_bp)
    
    # Register template context
    @app.context_processor
    def inject_theme():
        from flask import session
        return {
            'current_theme': session.get('theme', app.config['DEFAULT_THEME']),
            'themes': app.config['THEMES'],
        }
    
    # Register index route
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('workflow.index'))
    
    return app


# For flask run command
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
