from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def landing():
    """Landing page - redirect to login or dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def index():
    """Main dashboard page"""
    return render_template('index.html')

