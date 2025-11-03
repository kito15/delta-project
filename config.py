import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration"""
    SECRET_KEY = 'dev-secret-key-change-me-in-production'

    # Create instance directory if it doesn't exist
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Hardcoded MySQL connection parameters for Railway
    MYSQL_HOST = 'mysql.railway.internal'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'RnFHqvEhjFeBiWzCAYeLKVwyRRqgvlKq'
    MYSQL_DATABASE = 'railway'
    
    # Connection pool settings
    MYSQL_POOL_SIZE = 10
    MYSQL_POOL_MAX_OVERFLOW = 20
    MYSQL_POOL_TIMEOUT = 30
    MYSQL_POOL_RECYCLE = 300

    # File upload settings
    MAX_FILE_SIZE = 52428800  # 50MB
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'csv'}

    # Session settings
    SESSION_TIMEOUT = 3600
    PERMANENT_SESSION_LIFETIME = 3600
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Require HTTPS

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
