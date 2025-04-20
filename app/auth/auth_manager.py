"""
Authentication manager for NEXDB.
Handles user authentication and session management.
"""
import logging
import json
import pyotp
import secrets
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, flash, g, request, current_app
from app.db.models import db, User

logger = logging.getLogger(__name__)

def login_required(f):
    """
    Decorator to require login for a route.
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # Check if 2FA is required but not completed
        if session.get('2fa_required') and not session.get('2fa_completed'):
            flash('Two-factor authentication is required', 'warning')
            return redirect(url_for('auth.verify_2fa', next=request.url))
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to require admin privileges for a route.
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # Check if 2FA is required but not completed
        if session.get('2fa_required') and not session.get('2fa_completed'):
            flash('Two-factor authentication is required', 'warning')
            return redirect(url_for('auth.verify_2fa', next=request.url))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def authenticate_user(username, password):
    """
    Authenticate a user with username and password.
    
    Args:
        username: The username
        password: The password
    
    Returns:
        User object if authentication is successful, None otherwise
    """
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        logger.warning(f"Failed login attempt for username: {username}")
        return None
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    logger.info(f"User {username} logged in successfully")
    return user

def verify_totp(user, totp_code):
    """
    Verify a TOTP code for a user.
    
    Args:
        user: User object
        totp_code: TOTP code to verify
    
    Returns:
        True if the code is valid, False otherwise
    """
    if not user.totp_secret or not user.totp_enabled:
        return False
    
    totp = pyotp.TOTP(user.totp_secret)
    return totp.verify(totp_code)

def verify_backup_code(user, backup_code):
    """
    Verify a backup code for a user.
    
    Args:
        user: User object
        backup_code: Backup code to verify
    
    Returns:
        True if the code is valid, False otherwise
    """
    if not user.backup_codes:
        return False
    
    try:
        backup_codes = json.loads(user.backup_codes)
        if backup_code in backup_codes:
            # Remove the used backup code
            backup_codes.remove(backup_code)
            user.backup_codes = json.dumps(backup_codes)
            db.session.commit()
            return True
    except (json.JSONDecodeError, TypeError):
        pass
    
    return False

def setup_totp(user):
    """
    Set up TOTP for a user.
    
    Args:
        user: User object
    
    Returns:
        Dict with secret, QR code provisioning URI, and backup codes
    """
    # Generate a new TOTP secret
    secret = pyotp.random_base32()
    user.totp_secret = secret
    
    # Generate backup codes
    backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
    user.backup_codes = json.dumps(backup_codes)
    
    db.session.commit()
    
    # Create the provisioning URI for the QR code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user.username,
        issuer_name="NEXDB"
    )
    
    return {
        'secret': secret,
        'provisioning_uri': provisioning_uri,
        'backup_codes': backup_codes
    }

def enable_totp(user, totp_code):
    """
    Enable TOTP for a user after verification.
    
    Args:
        user: User object
        totp_code: TOTP code to verify
    
    Returns:
        True if the code is valid and TOTP was enabled, False otherwise
    """
    if not user.totp_secret:
        return False
    
    totp = pyotp.TOTP(user.totp_secret)
    if totp.verify(totp_code):
        user.totp_enabled = True
        db.session.commit()
        return True
    
    return False

def disable_totp(user):
    """
    Disable TOTP for a user.
    
    Args:
        user: User object
    """
    user.totp_enabled = False
    user.totp_secret = None
    user.backup_codes = None
    db.session.commit()

def change_password(user, current_password, new_password):
    """
    Change a user's password.
    
    Args:
        user: User object
        current_password: Current password
        new_password: New password
    
    Returns:
        True if password change is successful, False otherwise
    """
    if not user.check_password(current_password):
        logger.warning(f"Failed password change attempt for user ID: {user.id}")
        return False
    
    user.set_password(new_password)
    db.session.commit()
    
    logger.info(f"Password changed for user ID: {user.id}")
    return True

def create_user(username, password, email=None, is_admin=False):
    """
    Create a new user.
    
    Args:
        username: The username
        password: The password
        email: The email (optional)
        is_admin: Whether the user is an admin
    
    Returns:
        User object if creation is successful, None otherwise
    """
    # Check if username exists
    if User.query.filter_by(username=username).first():
        logger.warning(f"Attempted to create user with existing username: {username}")
        return None
    
    # Check if email exists (if provided)
    if email and User.query.filter_by(email=email).first():
        logger.warning(f"Attempted to create user with existing email: {email}")
        return None
    
    # Create new user
    user = User(
        username=username,
        email=email,
        is_admin=is_admin
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    logger.info(f"Created new user: {username}")
    return user

def delete_user(user_id):
    """
    Delete a user.
    
    Args:
        user_id: ID of the user to delete
    
    Returns:
        True if deletion is successful, False otherwise
    """
    # Prevent deleting the last admin
    if User.query.filter_by(is_admin=True).count() <= 1:
        admin_to_delete = User.query.get(user_id)
        if admin_to_delete and admin_to_delete.is_admin:
            logger.warning("Attempted to delete the last admin user")
            return False
    
    user = User.query.get(user_id)
    if not user:
        logger.warning(f"Attempted to delete non-existent user ID: {user_id}")
        return False
    
    db.session.delete(user)
    db.session.commit()
    
    logger.info(f"Deleted user ID: {user_id}")
    return True 