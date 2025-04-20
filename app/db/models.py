"""
SQLite database models for NEXDB.
Contains models for user authentication and configuration.
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # 2FA fields
    totp_secret = db.Column(db.String(32), nullable=True)
    totp_enabled = db.Column(db.Boolean, default=False)
    backup_codes = db.Column(db.Text, nullable=True)  # JSON-encoded list of unused backup codes
    
    def set_password(self, password):
        """Set the password hash."""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check the password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Config(db.Model):
    """Configuration model for storing application settings."""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(200), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Config {self.key}>'

class BackupSchedule(db.Model):
    """Backup schedule model for storing automated backup schedules."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    db_type = db.Column(db.String(20), nullable=False)  # mysql or postgres
    db_name = db.Column(db.String(80), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly
    time = db.Column(db.Time, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=True)  # 0-6 (Monday-Sunday)
    day_of_month = db.Column(db.Integer, nullable=True)  # 1-31
    backup_type = db.Column(db.String(20), nullable=False)  # local or s3
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_run = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<BackupSchedule {self.name}>'

class BackupLog(db.Model):
    """Backup log model for tracking backup operations."""
    id = db.Column(db.Integer, primary_key=True)
    backup_name = db.Column(db.String(200), nullable=False)
    db_type = db.Column(db.String(20), nullable=False)
    db_name = db.Column(db.String(80), nullable=False)
    backup_type = db.Column(db.String(20), nullable=False)  # local or s3
    status = db.Column(db.String(20), nullable=False)  # success, failed
    message = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)  # in bytes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    schedule_id = db.Column(db.Integer, db.ForeignKey('backup_schedule.id'), nullable=True)
    
    def __repr__(self):
        return f'<BackupLog {self.backup_name}>' 