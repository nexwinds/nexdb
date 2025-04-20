"""
Backup feature module for NEXDB.
Provides functionality for database backups to AWS S3.
"""
from flask import Blueprint

def register_blueprints(app):
    """Register backup feature blueprints with the Flask app."""
    from app.features.backup.controllers import backup_controller
    
    backup_bp = Blueprint('backup', __name__, url_prefix='/backup')
    backup_bp.register_blueprint(backup_controller.blueprint)
    
    app.register_blueprint(backup_bp) 