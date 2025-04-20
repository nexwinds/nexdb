"""
Authentication routes for NEXDB.
Handles login, logout, and password management.
"""
import json
import qrcode
import io
import base64
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.auth.auth_manager import (
    authenticate_user, change_password, create_user, login_required, admin_required,
    setup_totp, verify_totp, enable_totp, disable_totp, verify_backup_code
)
from app.db.models import User, db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    # Redirect if already logged in
    if 'user_id' in session and session.get('2fa_completed', False):
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next_url = request.form.get('next')
        
        if not username or not password:
            flash('Username and password are required', 'warning')
            return render_template('auth/login.html')
        
        user = authenticate_user(username, password)
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            # Check if 2FA is enabled for the user
            if user.totp_enabled:
                session['2fa_required'] = True
                session['2fa_completed'] = False
                
                if next_url and next_url.startswith('/'):
                    session['next_url'] = next_url
                
                flash('Please complete two-factor authentication', 'info')
                return redirect(url_for('auth.verify_2fa'))
            else:
                session['2fa_required'] = False
                session['2fa_completed'] = True
                flash(f'Welcome back, {user.username}!', 'success')
                
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    """Handle 2FA verification."""
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))
    
    if session.get('2fa_completed', False):
        return redirect(url_for('dashboard.index'))
    
    user = User.query.get(session['user_id'])
    if not user or not user.totp_enabled:
        session['2fa_required'] = False
        session['2fa_completed'] = True
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        code_type = request.form.get('code_type', 'totp')
        code = request.form.get('code')
        
        if not code:
            flash('Authentication code is required', 'warning')
            return render_template('auth/verify_2fa.html')
        
        verified = False
        if code_type == 'totp':
            verified = verify_totp(user, code)
        elif code_type == 'backup':
            verified = verify_backup_code(user, code)
        
        if verified:
            session['2fa_completed'] = True
            next_url = session.pop('next_url', None)
            
            flash('Two-factor authentication successful', 'success')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid authentication code', 'danger')
    
    return render_template('auth/verify_2fa.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Handle user profile and password changes."""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not current_password or not new_password or not confirm_password:
                flash('All password fields are required', 'warning')
                return redirect(url_for('auth.profile'))
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'warning')
                return redirect(url_for('auth.profile'))
            
            if len(new_password) < 8:
                flash('Password must be at least 8 characters long', 'warning')
                return redirect(url_for('auth.profile'))
            
            if change_password(user, current_password, new_password):
                flash('Password changed successfully', 'success')
                return redirect(url_for('auth.profile'))
            else:
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('auth.profile'))
        
        elif action == 'update_profile':
            email = request.form.get('email')
            
            # Check if email is already taken by another user
            if email and email != user.email:
                existing_user = User.query.filter_by(email=email).first()
                if existing_user and existing_user.id != user.id:
                    flash('Email address is already in use', 'warning')
                    return redirect(url_for('auth.profile'))
            
            user.email = email
            db.session.commit()
            flash('Profile updated successfully', 'success')
    
    # Check if 2FA is set up
    backup_codes = []
    if user.backup_codes:
        try:
            backup_codes = json.loads(user.backup_codes)
        except (json.JSONDecodeError, TypeError):
            backup_codes = []
    
    return render_template('auth/profile.html', user=user, backup_codes=backup_codes)

@auth_bp.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    """Handle 2FA setup."""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    # If 2FA is already enabled, redirect to profile
    if user.totp_enabled:
        flash('Two-factor authentication is already enabled', 'info')
        return redirect(url_for('auth.profile'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        
        if not code:
            flash('Verification code is required', 'warning')
            return redirect(url_for('auth.setup_2fa'))
        
        if enable_totp(user, code):
            flash('Two-factor authentication enabled successfully', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Invalid verification code', 'danger')
            return redirect(url_for('auth.setup_2fa'))
    
    # Generate new TOTP setup
    totp_setup = setup_totp(user)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(totp_setup['provisioning_uri'])
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert the image to a data URL
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    qr_code_data_url = f"data:image/png;base64,{img_str}"
    
    return render_template(
        'auth/setup_2fa.html',
        secret=totp_setup['secret'],
        qr_code=qr_code_data_url,
        backup_codes=totp_setup['backup_codes']
    )

@auth_bp.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    """Handle 2FA disabling."""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    # If 2FA is not enabled, redirect to profile
    if not user.totp_enabled:
        flash('Two-factor authentication is not enabled', 'info')
        return redirect(url_for('auth.profile'))
    
    # Require password confirmation
    password = request.form.get('password')
    
    if not password:
        flash('Password is required', 'warning')
        return redirect(url_for('auth.profile'))
    
    if not user.check_password(password):
        flash('Incorrect password', 'danger')
        return redirect(url_for('auth.profile'))
    
    disable_totp(user)
    flash('Two-factor authentication disabled successfully', 'success')
    return redirect(url_for('auth.profile'))

@auth_bp.route('/users', methods=['GET'])
@admin_required
def users():
    """List all users (admin only)."""
    users_list = User.query.all()
    return render_template('auth/users.html', users=users_list)

@auth_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user_route():
    """Create a new user (admin only)."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        is_admin = request.form.get('is_admin') == 'on'
        
        if not username or not password or not confirm_password:
            flash('Username and password are required', 'warning')
            return redirect(url_for('auth.create_user_route'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'warning')
            return redirect(url_for('auth.create_user_route'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'warning')
            return redirect(url_for('auth.create_user_route'))
        
        user = create_user(username, password, email, is_admin)
        
        if user:
            flash(f'User {username} created successfully', 'success')
            return redirect(url_for('auth.users'))
        else:
            flash('Username or email already exists', 'danger')
    
    return render_template('auth/create_user.html')

@auth_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user_route(user_id):
    """Delete a user (admin only)."""
    # Prevent self-deletion
    if user_id == session.get('user_id'):
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('auth.users'))
    
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.users'))
    
    username = user.username
    
    from app.auth.auth_manager import delete_user
    if delete_user(user_id):
        flash(f'User {username} deleted successfully', 'success')
    else:
        flash('Cannot delete the last admin user', 'danger')
    
    return redirect(url_for('auth.users')) 