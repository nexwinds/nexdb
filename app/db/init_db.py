"""
Database initialization for NEXDB.
Creates tables and initial data if they don't exist.
"""
import os
import random
import string
import logging
from datetime import datetime
from pathlib import Path

from app.db.models import db, User, Config

logger = logging.getLogger(__name__)

def generate_secure_username(length=8):
    """Generate a secure random username."""
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def generate_secure_password(length=32):
    """Generate a secure random password."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(chars, k=length))

def save_credentials_to_file(username, password, filepath):
    """Save generated credentials to a file."""
    try:
        with open(filepath, 'w') as f:
            f.write(f"NEXDB Admin Credentials (created {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
            f.write("=" * 60 + "\n")
            f.write(f"Username: {username}\n")
            f.write(f"Password: {password}\n")
            f.write("=" * 60 + "\n")
            f.write("IMPORTANT: Please save these credentials securely and delete this file once noted.\n")
        os.chmod(filepath, 0o600)  # Set secure permissions (owner read/write only)
        return True
    except Exception as e:
        logger.error(f"Failed to save credentials: {str(e)}")
        return False

def init_db(app, force=False):
    """
    Initialize the database and create initial data.
    
    Args:
        app: Flask application instance
        force: If True, recreate all tables even if they exist
    """
    with app.app_context():
        if force:
            db.drop_all()
            logger.info("Dropped all existing tables")
        
        # Create tables if they don't exist
        db.create_all()
        logger.info("Created database tables")
        
        # Check if admin user exists
        admin_exists = User.query.filter_by(is_admin=True).first()
        
        if not admin_exists:
            # Generate secure credentials
            username = generate_secure_username()
            password = generate_secure_password()
            
            # Create admin user
            admin = User(
                username=username,
                is_admin=True
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            logger.info(f"Created admin user: {username}")
            
            # Save credentials to file
            creds_dir = Path(app.config.get('INSTANCE_PATH', app.instance_path))
            creds_dir.mkdir(exist_ok=True)
            creds_file = creds_dir / 'admin_credentials.txt'
            
            if save_credentials_to_file(username, password, creds_file):
                logger.info(f"Saved admin credentials to {creds_file}")
                print(f"\n{'='*60}")
                print(f"Admin account created:")
                print(f"Username: {username}")
                print(f"Password: {password}")
                print(f"These credentials have been saved to: {creds_file}")
                print(f"{'='*60}\n")
            else:
                print("\nWARNING: Failed to save credentials to file. Please note them now:")
                print(f"Username: {username}")
                print(f"Password: {password}\n")
        
        # Add default configurations if they don't exist
        default_configs = {
            "backup_retention_days": {
                "value": "30", 
                "description": "Number of days to retain local backups"
            },
            "s3_backup_prefix": {
                "value": "nexdb-backups", 
                "description": "Prefix for S3 backup files"
            },
            "default_mysql_charset": {
                "value": "utf8mb4", 
                "description": "Default character set for MySQL databases"
            },
            "default_mysql_collation": {
                "value": "utf8mb4_unicode_ci", 
                "description": "Default collation for MySQL databases"
            }
        }
        
        for key, data in default_configs.items():
            if not Config.query.filter_by(key=key).first():
                config = Config(
                    key=key,
                    value=data["value"],
                    description=data["description"]
                )
                db.session.add(config)
        
        db.session.commit()
        logger.info("Database initialization complete")

if __name__ == "__main__":
    # Allow running as standalone script for maintenance/setup
    from flask import Flask
    from config import Config as AppConfig
    
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    db.init_app(app)
    
    import sys
    force = "--force" in sys.argv
    
    init_db(app, force=force)
    print("Database initialization complete") 