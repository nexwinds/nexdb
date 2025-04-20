"""
Configuration settings for NEXDB.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file if it exists
env_file = os.path.join(basedir, '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)

# Application configuration
class Config:
    """Application configuration."""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DEBUG = os.environ.get('DEBUG') == 'True'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'nexdb.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    
    # Backup settings
    BACKUP_DIR = os.environ.get('BACKUP_DIR') or os.path.join(basedir, 'instance', 'backups')
    
    # Security settings
    ALLOWED_IPS = os.environ.get('ALLOWED_IPS', '').split(',') if os.environ.get('ALLOWED_IPS') else []
    
    # MySQL settings
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    
    # PostgreSQL settings
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT', 5432))
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')
    
    # AWS S3 settings
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', '')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', '')
    AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME', '')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Authentication settings
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH', '') # Will be set during installation
    
    # IP Allowlist (comma-separated list of IPs)
    ALLOWED_IPS = os.environ.get('ALLOWED_IPS', '').split(',') if os.environ.get('ALLOWED_IPS') else []
    
    # Backup directory
    BACKUP_DIR = os.environ.get('BACKUP_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')) 