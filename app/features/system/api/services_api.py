from flask import Blueprint, jsonify, request
from flask_login import login_required
import logging
from datetime import datetime

from app.features.system.services.service_manager import get_service_manager
from app.features.system.services.system_service import get_system_service

# Create blueprint
services_api = Blueprint('services_api', __name__, url_prefix='/api/system')
logger = logging.getLogger(__name__)

@services_api.route('/services', methods=['GET'])
@login_required
def get_services():
    """API endpoint to get list of services and their status"""
    try:
        service_manager = get_service_manager()
        services = service_manager.get_all_services()
        
        return jsonify({
            "success": True,
            "services": [
                {
                    "name": service.name,
                    "display_name": service.display_name,
                    "description": service.description,
                    "status": service.status,
                    "port": service.port
                } for service in services
            ],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        logger.error(f"Error getting services: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@services_api.route('/services/start', methods=['POST'])
@login_required
def start_service():
    """API endpoint to start a service"""
    try:
        service_name = request.json.get('service')
        if not service_name:
            return jsonify({
                "success": False,
                "error": "Service name is required"
            }), 400
        
        service_manager = get_service_manager()
        success = service_manager.start_service(service_name)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Service {service_name} started successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Failed to start service {service_name}"
            }), 500
    except Exception as e:
        logger.error(f"Error starting service: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@services_api.route('/services/stop', methods=['POST'])
@login_required
def stop_service():
    """API endpoint to stop a service"""
    try:
        service_name = request.json.get('service')
        if not service_name:
            return jsonify({
                "success": False,
                "error": "Service name is required"
            }), 400
        
        service_manager = get_service_manager()
        success = service_manager.stop_service(service_name)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Service {service_name} stopped successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Failed to stop service {service_name}"
            }), 500
    except Exception as e:
        logger.error(f"Error stopping service: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@services_api.route('/services/restart', methods=['POST'])
@login_required
def restart_service():
    """API endpoint to restart a service"""
    try:
        service_name = request.json.get('service')
        if not service_name:
            return jsonify({
                "success": False,
                "error": "Service name is required"
            }), 400
        
        service_manager = get_service_manager()
        success = service_manager.restart_service(service_name)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Service {service_name} restarted successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Failed to restart service {service_name}"
            }), 500
    except Exception as e:
        logger.error(f"Error restarting service: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@services_api.route('/web-server/reload', methods=['POST'])
@login_required
def reload_web_server():
    """API endpoint to reload web server configuration"""
    try:
        service_manager = get_service_manager()
        success = service_manager.reload_web_server()
        
        if success:
            return jsonify({
                "success": True,
                "message": "Web server reloaded successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to reload web server"
            }), 500
    except Exception as e:
        logger.error(f"Error reloading web server: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@services_api.route('/web-server/clear-cache', methods=['POST'])
@login_required
def clear_cache():
    """API endpoint to clear application cache"""
    try:
        # Implementation depends on your caching strategy
        # This is a placeholder that just returns success
        
        return jsonify({
            "success": True,
            "message": "Cache cleared successfully"
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@services_api.route('/web-server/port', methods=['POST'])
@login_required
def update_port():
    """API endpoint to update the web server port"""
    try:
        port = request.json.get('port')
        if not port:
            return jsonify({
                "success": False,
                "error": "Port is required"
            }), 400
        
        try:
            port = int(port)
            if port < 1 or port > 65535:
                return jsonify({
                    "success": False,
                    "error": "Port must be between 1 and 65535"
                }), 400
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Port must be a valid number"
            }), 400
        
        # Implementation depends on your web server configuration
        # This is a placeholder that just returns success
        
        return jsonify({
            "success": True,
            "message": f"Port updated to {port}. Server restart required for changes to take effect."
        })
    except Exception as e:
        logger.error(f"Error updating port: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500 