"""Flask application configuration."""
import os
from pathlib import Path


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    WEB_DIR = Path(__file__).parent
    DATA_DIR = WEB_DIR / 'data'
    MODULES_DIR = WEB_DIR / 'modules'
    
    # PixelGroomer integration
    PIXELGROOMER_ROOT = BASE_DIR
    PHOTO_LIBRARY = os.environ.get('PHOTO_LIBRARY', str(Path.home() / 'Pictures' / 'PhotoLibrary'))
    ALBUM_DIR = os.environ.get('ALBUM_DIR', str(Path.home() / 'Pictures' / 'Albums'))
    
    # Thumbnails
    THUMBNAIL_SIZE = (400, 400)
    THUMBNAIL_DIR = DATA_DIR / 'thumbnails'
    
    # Default theme
    DEFAULT_THEME = 'eui-light'
    
    # Available themes
    THEMES = [
        {'id': 'eui-light', 'name': 'EUI Light'},
        {'id': 'eui-dark', 'name': 'EUI Dark'},
        {'id': 'solarized-light', 'name': 'Solarized Light'},
        {'id': 'solarized-dark', 'name': 'Solarized Dark'},
    ]


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


# Config mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
