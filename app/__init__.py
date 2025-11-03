import os
import pymysql
from flask import Flask, g, current_app
from flask_login import LoginManager
from config import config

# Initialize Flask-Login
login_manager = LoginManager()

def get_db():
    """Get database connection from Flask g object or create new one"""
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['MYSQL_HOST'],
            port=current_app.config['MYSQL_PORT'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DATABASE'],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    """Initialize database tables"""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create analyses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                filename VARCHAR(255) NOT NULL,
                file_size INT,
                file_path VARCHAR(500),
                total_rows INT,
                total_columns INT,
                quality_score INT,
                results_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        db.commit()
        cursor.close()

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__,
                static_folder='../static',
                static_url_path='/static',
                template_folder='../templates')

    # Load configuration
    app.config.from_object(config[config_name])

    # Ensure instance and upload folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    # Register database teardown
    app.teardown_appcontext(close_db)

    # Initialize database tables
    try:
        init_db(app)
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")

    # Register blueprints
    from app.routes import auth, api, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(main.bp)

    return app
