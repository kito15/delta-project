import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__,
                static_folder='static',
                static_url_path='/static',
                template_folder='templates')

    # Load configuration
    app.config.from_object(config[config_name])

    # Ensure instance and upload folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    # Register blueprints
    from app.routes import auth, api, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(main.bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

