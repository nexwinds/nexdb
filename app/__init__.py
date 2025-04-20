from flask import Flask, request, abort
from config import Config
import os
import logging
from datetime import datetime

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up database
    from app.db.models import db
    db.init_app(app)
    
    # Ensure instance path exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Ensure backup directory exists
    os.makedirs(app.config.get('BACKUP_DIR', os.path.join(app.instance_path, 'backups')), exist_ok=True)
    
    # Register auth blueprint
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    # Register blueprints with a more streamlined approach
    from app.routes.dashboard import dashboard_bp
    from app.routes.mysql import mysql_bp
    from app.routes.postgres import postgres_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(mysql_bp)
    app.register_blueprint(postgres_bp)
    
    # Simplified feature modules registration
    from app.features.backup import register_blueprints as register_backup
    from app.features.database import register_blueprints as register_database
    
    register_backup(app)
    register_database(app)
    
    # IP restriction middleware
    @app.before_request
    def check_ip():
        if app.config.get('ALLOWED_IPS') and request.remote_addr not in app.config['ALLOWED_IPS']:
            abort(403)  # Forbidden
    
    # Template context processor
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # Initialize database on startup if it doesn't exist
    with app.app_context():
        if not os.path.exists(os.path.join(app.instance_path, 'nexdb.db')):
            from app.db.init_db import init_db
            app.logger.info("No database found. Initializing database...")
            init_db(app)
    
    # Cleanup on shutdown
    @app.teardown_appcontext
    def shutdown_services(exception=None):
        """Clean up resources when the application shuts down"""
        from app.features.backup.services.backup_service import get_backup_service
        try:
            backup_service = get_backup_service()
            backup_service.shutdown()
        except Exception as e:
            app.logger.error(f"Error shutting down backup service: {str(e)}")
    
    return app 