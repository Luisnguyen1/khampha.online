"""
Configuration management for khappha.online
Load settings from environment variables
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_APP = os.getenv('FLASK_APP', 'app.py')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'  # Use filesystem-based sessions
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_FILE_DIR = Path(__file__).parent / 'flask_session'
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days in seconds
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables!")
    
    # Database Configuration
    BASE_DIR = Path(__file__).parent
    DATABASE_PATH = BASE_DIR / os.getenv('DATABASE_PATH', 'data/travelmate.db')
    DATABASE_BACKUP = BASE_DIR / os.getenv('DATABASE_BACKUP', 'data/backups/')
    
    # File Upload Configuration
    UPLOAD_FOLDER = BASE_DIR / os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,pdf').split(','))
    
    # Cache Configuration
    CACHE_TTL_HOURS = int(os.getenv('CACHE_TTL_HOURS', 24))
    CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 1000))
    
    # AI Configuration
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-flash-2.0')
    GEMINI_TEMPERATURE = float(os.getenv('GEMINI_TEMPERATURE', 0.7))
    GEMINI_MAX_TOKENS = int(os.getenv('GEMINI_MAX_TOKENS', 8192))
    GEMINI_TIMEOUT = int(os.getenv('GEMINI_TIMEOUT', 240))
    
    # Search Configuration
    SEARCH_MAX_RESULTS = int(os.getenv('SEARCH_MAX_RESULTS', 10))
    SEARCH_TIMEOUT = int(os.getenv('SEARCH_TIMEOUT', 10))
    SEARCH_CACHE_ENABLED = os.getenv('SEARCH_CACHE_ENABLED', 'true').lower() == 'true'
    
    # Application Settings
    APP_NAME = os.getenv('APP_NAME', 'khappha.online')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    SESSION_TIMEOUT_HOURS = int(os.getenv('SESSION_TIMEOUT_HOURS', 24))
    MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', 50))
    
    # Development Settings
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'
    VERBOSE_LOGGING = os.getenv('VERBOSE_LOGGING', 'True').lower() == 'true'
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'fe30b4f590msh6817e6a304fb995p1382dejsn50ae5d7c997d')
    
    # Google Maps API Key
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'AIzaSyBC6GFXWXE6oJn79RlYACnUxgwD6zX0qJE')
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        # Create necessary directories
        Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        Config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        Config.DATABASE_BACKUP.mkdir(parents=True, exist_ok=True)
        Config.SESSION_FILE_DIR.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_PATH = Path(':memory:')  # Use in-memory database for tests


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
