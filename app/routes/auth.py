from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from functools import wraps
from passlib.hash import pbkdf2_sha256

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check credentials
        if (username == current_app.config['ADMIN_USERNAME'] and 
            pbkdf2_sha256.verify(password, current_app.config['ADMIN_PASSWORD_HASH'])):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('auth.login'))

# Index route redirects to dashboard if logged in, otherwise to login
@auth_bp.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login')) 