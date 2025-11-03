import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me-in-production'

    # Create instance directory if it doesn't exist
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Railway MySQL Database Configuration
    # Try Railway internal network first, then public URL, fallback to SQLite for local dev
    MYSQL_INTERNAL_URL = os.environ.get('MYSQL_INTERNAL_URL') or \
        'mysql+pymysql://root:RnFHqvEHjFeBlWzCAYELkVAyRRqgv1kq@mysql.railway.internal:3306/railway'
    MYSQL_PUBLIC_URL = os.environ.get('MYSQL_PUBLIC_URL') or \
        'mysql+pymysql://root:RnFHqvEHjFeBlWzCAYELkVAyRRqgv1kq@trolley.proxy.railway.net:48667/railway'
    
    # Use environment variable first, then try Railway URLs, fallback to SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        MYSQL_PUBLIC_URL
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20
    }

    # File upload settings
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 52428800))  # 50MB
    UPLOAD_FOLDER = os.path.join(basedir, os.environ.get('UPLOAD_FOLDER', 'uploads'))
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'csv').split(','))

    # Session settings
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 3600))
    PERMANENT_SESSION_LIFETIME = SESSION_TIMEOUT
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    # Use SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(Config.instance_path, 'purity.db')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    
    # Force MySQL in production - NEVER use SQLite
    # Priority: DATABASE_URL env var > MYSQL_INTERNAL_URL > MYSQL_PUBLIC_URL (hardcoded)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        os.environ.get('MYSQL_INTERNAL_URL') or \
        'mysql+pymysql://root:RnFHqvEHjFeBlWzCAYELkVAyRRqgv1kq@mysql.railway.internal:3306/railway'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

