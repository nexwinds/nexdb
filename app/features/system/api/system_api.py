from flask import Blueprint, jsonify, request
from flask_login import login_required
import logging

from app.features.system.services.system_service import get_system_service

# Create blueprint
system_api = Blueprint('system_api', __name__, url_prefix='/api/system')
logger = logging.getLogger(__name__)

@system_api.route('/info', methods=['GET'])
@login_required
def get_system_info():
    """API endpoint to get system information"""
    try:
        service = get_system_service()
        return jsonify({
            "success": True,
            "data": service.get_system_info()
        })
    except Exception as e:
        logger.error(f"Error in system info API: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@system_api.route('/usage', methods=['GET'])
@login_required
def get_system_usage():
    """API endpoint to get system resource usage"""
    try:
        service = get_system_service()
        return jsonify({
            "success": True,
            "data": service.get_system_usage()
        })
    except Exception as e:
        logger.error(f"Error in system usage API: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@system_api.route('/network', methods=['GET'])
@login_required
def get_network_stats():
    """API endpoint to get network statistics"""
    try:
        service = get_system_service()
        return jsonify({
            "success": True,
            "data": service.get_network_stats()
        })
    except Exception as e:
        logger.error(f"Error in network stats API: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@system_api.route('/disk', methods=['GET'])
@login_required
def get_disk_io_stats():
    """API endpoint to get disk I/O statistics"""
    try:
        service = get_system_service()
        return jsonify({
            "success": True,
            "data": service.get_disk_io_stats()
        })
    except Exception as e:
        logger.error(f"Error in disk I/O stats API: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@system_api.route('/timezone', methods=['GET'])
@login_required
def get_timezone_info():
    """API endpoint to get timezone information"""
    try:
        service = get_system_service()
        return jsonify({
            "success": True,
            "data": service.get_timezone_info()
        })
    except Exception as e:
        logger.error(f"Error in timezone info API: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@system_api.route('/processes', methods=['GET'])
@login_required
def get_processes():
    """API endpoint to get list of running processes"""
    try:
        service = get_system_service()
        limit = request.args.get('limit', default=10, type=int)
        return jsonify({
            "success": True,
            "data": service.get_processes(limit=limit)
        })
    except Exception as e:
        logger.error(f"Error in processes API: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@system_api.route('/dashboard-data', methods=['GET'])
@login_required
def get_dashboard_data():
    """API endpoint to get all dashboard data in one call"""
    try:
        service = get_system_service()
        limit = request.args.get('limit', default=10, type=int)
        
        return jsonify({
            "success": True,
            "data": {
                "system_info": service.get_system_info(),
                "system_usage": service.get_system_usage(),
                "network_stats": service.get_network_stats(),
                "disk_io_stats": service.get_disk_io_stats(),
                "timezone_info": service.get_timezone_info(),
                "processes": service.get_processes(limit=limit)
            }
        })
    except Exception as e:
        logger.error(f"Error in dashboard data API: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500 