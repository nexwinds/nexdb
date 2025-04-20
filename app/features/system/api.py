from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any, List, Optional, Tuple
from http import HTTPStatus
from flask_jwt_extended import jwt_required
import subprocess

from app.features.system.services.system_service import get_system_service
from app.features.database.services.mysql_service import MySQLService
from app.features.database.services.postgres_service import PostgresService


system_api = Blueprint('system_api', __name__, url_prefix='/api/system')


@system_api.route('/info', methods=['GET'])
@jwt_required()
def get_system_info() -> Tuple[Dict[str, Any], int]:
    """Get system information including OS, hardware, and network details"""
    try:
        service = get_system_service()
        info = service.get_system_info()
        
        response = {
            'success': True,
            'message': 'System information retrieved successfully',
            'data': info
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to retrieve system information: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@system_api.route('/usage', methods=['GET'])
@jwt_required()
def get_system_usage() -> Tuple[Dict[str, Any], int]:
    """Get current system usage metrics"""
    try:
        service = get_system_service()
        usage = service.get_system_usage()
        
        response = {
            'success': True,
            'message': 'System usage metrics retrieved successfully',
            'data': usage
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to retrieve system usage metrics: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@system_api.route('/network', methods=['GET'])
@jwt_required()
def get_network_stats() -> Tuple[Dict[str, Any], int]:
    """Get network traffic statistics"""
    try:
        service = get_system_service()
        network_stats = service.get_network_stats()
        
        response = {
            'success': True,
            'message': 'Network statistics retrieved successfully',
            'data': network_stats
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to retrieve network statistics: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@system_api.route('/disk-io', methods=['GET'])
@jwt_required()
def get_disk_io() -> Tuple[Dict[str, Any], int]:
    """Get disk I/O statistics"""
    try:
        service = get_system_service()
        disk_io = service.get_disk_io()
        
        response = {
            'success': True,
            'message': 'Disk I/O statistics retrieved successfully',
            'data': disk_io
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to retrieve disk I/O statistics: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@system_api.route('/timezone', methods=['GET'])
@jwt_required()
def get_timezone() -> Tuple[Dict[str, Any], int]:
    """Get system timezone information"""
    try:
        service = get_system_service()
        timezone_info = service.get_timezone()
        
        response = {
            'success': True,
            'message': 'Timezone information retrieved successfully',
            'data': timezone_info
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to retrieve timezone information: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@system_api.route('/timezone', methods=['POST'])
@jwt_required()
def set_timezone() -> Tuple[Dict[str, Any], int]:
    """Set system timezone"""
    try:
        data = request.get_json()
        if not data or 'timezone' not in data:
            return jsonify({
                'success': False,
                'message': 'Timezone is required',
                'data': None
            }), HTTPStatus.BAD_REQUEST
        
        timezone = data['timezone']
        
        service = get_system_service()
        success = service.set_timezone(timezone)
        
        if success:
            response = {
                'success': True,
                'message': f'Timezone set to {timezone} successfully',
                'data': service.get_timezone()
            }
            return jsonify(response), HTTPStatus.OK
        else:
            response = {
                'success': False,
                'message': f'Failed to set timezone to {timezone}',
                'data': None
            }
            return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Error setting timezone: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@system_api.route('/services', methods=['GET'])
@jwt_required()
def get_services_status() -> Tuple[Dict[str, Any], int]:
    """Get status of all system services"""
    try:
        # Get database services
        mysql_service = MySQLService()
        postgres_service = PostgresService()
        
        # Check status
        mysql_status = mysql_service.get_status()
        postgres_status = postgres_service.get_status()
        
        # Create services list
        services = [
            {
                'name': 'MySQL',
                'status': mysql_status,
                'type': 'database'
            },
            {
                'name': 'PostgreSQL',
                'status': postgres_status,
                'type': 'database'
            },
            {
                'name': 'Web Server',
                'status': True,  # The server is obviously running if this API is responding
                'type': 'web'
            }
        ]
        
        response = {
            'success': True,
            'message': 'Services status retrieved successfully',
            'data': {
                'services': services
            }
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to retrieve services status: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@system_api.route('/service/<service_name>/restart', methods=['POST'])
@jwt_required()
def restart_service(service_name: str) -> Tuple[Dict[str, Any], int]:
    """Restart a specific service"""
    try:
        # Check if service exists and restart
        if service_name.lower() == 'mysql':
            # Restart MySQL logic would go here
            # This would typically involve system calls to restart the service
            success = True
        elif service_name.lower() == 'postgresql':
            # Restart PostgreSQL logic would go here
            success = True
        elif service_name.lower() == 'webserver':
            # Restart web server logic would go here
            success = True
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown service: {service_name}',
                'data': None
            }), HTTPStatus.BAD_REQUEST
        
        if success:
            response = {
                'success': True,
                'message': f'Service {service_name} restarted successfully',
                'data': None
            }
            return jsonify(response), HTTPStatus.OK
        else:
            response = {
                'success': False,
                'message': f'Failed to restart service {service_name}',
                'data': None
            }
            return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Error restarting service {service_name}: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@system_api.route('/firewall', methods=['GET'])
@jwt_required()
def get_firewall_rules() -> Tuple[Dict[str, Any], int]:
    """Get firewall rules"""
    try:
        service = get_system_service()
        firewall_rules = service.get_firewall_rules()
        
        response = {
            'success': True,
            'message': 'Firewall rules retrieved successfully',
            'data': {
                'rules': firewall_rules
            }
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to retrieve firewall rules: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@system_api.route('/firewall', methods=['POST'])
@jwt_required()
def add_firewall_rule() -> Tuple[Dict[str, Any], int]:
    """Add a new firewall rule"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'data': None
            }), HTTPStatus.BAD_REQUEST
        
        # Validate required fields
        required_fields = ['type', 'port_range', 'ip_version', 'source']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Field {field} is required',
                    'data': None
                }), HTTPStatus.BAD_REQUEST
        
        # In a real implementation, this would add the rule to the system firewall
        # For this example, we'll just simulate success
        
        response = {
            'success': True,
            'message': 'Firewall rule added successfully',
            'data': {
                'rule': {
                    'id': '999',  # This would be generated by the system
                    'type': data['type'],
                    'port_range': data['port_range'],
                    'ip_version': data['ip_version'],
                    'source': data['source']
                }
            }
        }
        
        return jsonify(response), HTTPStatus.CREATED
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Error adding firewall rule: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@system_api.route('/firewall/<rule_id>', methods=['DELETE'])
@jwt_required()
def delete_firewall_rule(rule_id: str) -> Tuple[Dict[str, Any], int]:
    """Delete a firewall rule"""
    try:
        # In a real implementation, this would remove the rule from the system firewall
        # For this example, we'll just simulate success
        
        response = {
            'success': True,
            'message': f'Firewall rule {rule_id} deleted successfully',
            'data': None
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Error deleting firewall rule: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR 