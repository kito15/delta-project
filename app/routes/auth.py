from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, current_user
from app import login_manager
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.get_by_id(int(user_id))

@bp.route('/login', methods=['GET'])
def login():
    """Render login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('login.html')

@bp.route('/login', methods=['POST'])
def login_post():
    """Handle login form submission"""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')
    remember = data.get('remember', False)

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400

    # Find user by email
    user = User.get_by_email(email)

    if not user or not user.check_password(password):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    # Log in user
    login_user(user, remember=remember)

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200

@bp.route('/signup', methods=['POST'])
def signup():
    """Handle user registration"""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    # Validate email format
    if '@' not in email or '.' not in email:
        return jsonify({'success': False, 'message': 'Invalid email format'}), 400

    # Check if user already exists
    if User.get_by_email(email):
        return jsonify({'success': False, 'message': 'Email already registered'}), 409

    if User.get_by_username(username):
        return jsonify({'success': False, 'message': 'Username already taken'}), 409

    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)
    user.save()

    # Log in user automatically
    login_user(user)

    return jsonify({
        'success': True,
        'message': 'Registration successful',
        'user': user.to_dict()
    }), 201

@bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

@bp.route('/profile', methods=['GET'])
def profile():
    """Get current user profile"""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401

    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    }), 200
