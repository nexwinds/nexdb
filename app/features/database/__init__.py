"""
Database feature module for NEXDB.
Provides MySQL and PostgreSQL database management.
"""

from flask import Blueprint

def register_blueprints(app):
    # Import controllers
    from app.features.database.controllers import mysql_controller, postgres_controller, db_explorer
    
    # Create and register blueprints
    db_bp = Blueprint('database', __name__, url_prefix='/database')
    
    # Register sub-routes
    db_bp.register_blueprint(mysql_controller.blueprint, url_prefix='/mysql')
    db_bp.register_blueprint(postgres_controller.blueprint, url_prefix='/postgres')
    db_bp.register_blueprint(db_explorer.blueprint, url_prefix='/explorer')
    
    # Register main blueprint
    app.register_blueprint(db_bp) 