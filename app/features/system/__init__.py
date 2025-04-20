from flask import Flask
from app.features.system.api.system_api import system_api
from app.features.system.api.services_api import services_api
from app.features.system.api.timezone_api import timezone_api
from app.features.system.routes.system_routes import system_routes

def register_blueprints(app: Flask):
    """Register system blueprints with the Flask application"""
    # Register the API blueprints
    app.register_blueprint(system_api)
    app.register_blueprint(services_api)
    app.register_blueprint(timezone_api)
    
    # Register the web routes blueprint
    app.register_blueprint(system_routes) 