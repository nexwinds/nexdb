from flask import Blueprint, render_template, redirect, url_for, flash, current_app, jsonify, request
from flask_login import login_required
import logging
from app.features.system.services.system_service import get_system_service
from app.features.system.services.service_manager import get_service_manager
import pytz
from datetime import datetime

# Create blueprint
system_routes = Blueprint('system', __name__, url_prefix='/system')
logger = logging.getLogger(__name__)
system_service = get_system_service()

@system_routes.route('/', methods=['GET'])
@login_required
def index():
    """Main system dashboard view"""
    dashboard_data = system_service.get_dashboard_data()
    dashboard_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template('system/dashboard.html', **dashboard_data)

@system_routes.route('/services', methods=['GET'])
@login_required
def services():
    """Service management page"""
    try:
        # Get services list
        service_manager = get_service_manager()
        services = service_manager.get_all_services()
        
        # Get timezone information
        current_timezone = _get_current_timezone()
        now = datetime.now(pytz.timezone(current_timezone))
        server_time = now.strftime("%Y-%m-%d %H:%M:%S %Z")
        
        # Get list of timezones for the dropdown
        timezone_list = [
            {"value": tz, "label": tz.replace('_', ' ')}
            for tz in pytz.common_timezones
        ]
        
        # Mock data for UI display (replace with actual settings from your config)
        server_config = {
            'server_port': current_app.config.get('SERVER_PORT', 5000),
            'cloud_enabled': current_app.config.get('CLOUD_ENABLED', False),
            'cloud_provider': current_app.config.get('CLOUD_PROVIDER', 'aws'),
            'cloud_region': current_app.config.get('CLOUD_REGION', 'us-east-1'),
            'backup_config': {
                'frequency': current_app.config.get('BACKUP_FREQUENCY', 'daily'),
                'retention_days': current_app.config.get('BACKUP_RETENTION_DAYS', 7),
                'cloud_sync': current_app.config.get('BACKUP_CLOUD_SYNC', False)
            },
            'security_config': {
                'basic_auth_enabled': current_app.config.get('BASIC_AUTH_ENABLED', False),
                'basic_auth_username': current_app.config.get('BASIC_AUTH_USERNAME', 'admin'),
                'security_entrance': current_app.config.get('SECURITY_ENTRANCE', ''),
                'ipv6_enabled': current_app.config.get('IPV6_ENABLED', True),
                'allowed_ips': current_app.config.get('ALLOWED_IPS', [])
            },
            'firewall_rules': _get_firewall_rules()
        }
        
        return render_template(
            'system/services.html',
            services=services,
            current_timezone=current_timezone,
            server_time=server_time,
            timezones=timezone_list,
            server_port=server_config['server_port'],
            cloud_enabled=server_config['cloud_enabled'],
            cloud_provider=server_config['cloud_provider'],
            cloud_region=server_config['cloud_region'],
            cloud_regions=_get_cloud_regions(server_config['cloud_provider']),
            backup_config=server_config['backup_config'],
            security_config=server_config['security_config'],
            firewall_rules=server_config['firewall_rules'],
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as e:
        logger.error(f"Error rendering services page: {str(e)}")
        flash(f"Error loading services: {str(e)}", "error")
        return redirect(url_for('system.index'))

@system_routes.route('/monitor', methods=['GET'])
@login_required
def monitor():
    """Render the system monitoring page with real-time updates"""
    try:
        return render_template(
            'system/monitor.html',
            page_title="System Monitor"
        )
    except Exception as e:
        logger.error(f"Error rendering system monitor: {str(e)}")
        flash(f"Error loading system monitor: {str(e)}", "error")
        return redirect(url_for('system.index'))

@system_routes.route('/processes', methods=['GET'])
@login_required
def processes():
    """View all running processes"""
    processes = system_service.get_processes(sort_by='memory', limit=100)
    return render_template('system/processes.html', 
                          processes=processes,
                          timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@system_routes.route('/network', methods=['GET'])
@login_required
def network():
    """View detailed network information"""
    network_stats = system_service.get_network_stats()
    return render_template('system/network.html', 
                          network_stats=network_stats,
                          timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@system_routes.route('/disk', methods=['GET'])
@login_required
def disk():
    """View detailed disk information"""
    try:
        disk_io_stats = system_service.get_disk_io_stats()
        system_usage = system_service.get_system_usage()
        return render_template('system/disk.html', 
                            disk_io_stats=disk_io_stats,
                            disks=system_usage.get('disks', []),
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        logger.error(f"Error rendering disk page: {str(e)}")
        flash(f"Error loading disk information: {str(e)}", "error")
        return redirect(url_for('system.index'))

# API Endpoints for AJAX calls
@system_routes.route('/api/dashboard')
@login_required
def api_dashboard_data():
    """API endpoint to get dashboard data for real-time updates"""
    dashboard_data = system_service.get_dashboard_data()
    dashboard_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(dashboard_data)

@system_routes.route('/api/system-info')
@login_required
def api_system_info():
    """API endpoint to get system information"""
    system_info = system_service.get_system_info()
    return jsonify({
        'system_info': system_info,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@system_routes.route('/api/system-usage')
@login_required
def api_system_usage():
    """API endpoint to get system usage metrics"""
    system_usage = system_service.get_system_usage()
    return jsonify({
        'system_usage': system_usage,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@system_routes.route('/api/processes')
@login_required
def api_processes():
    """API endpoint to get list of processes"""
    sort_by = request.args.get('sort_by', 'memory')
    limit = request.args.get('limit', 50, type=int)
    processes = system_service.get_processes(sort_by=sort_by, limit=limit)
    return jsonify({
        'processes': processes,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@system_routes.route('/api/network')
@login_required
def api_network():
    """API endpoint to get network statistics"""
    network_stats = system_service.get_network_stats()
    return jsonify({
        'network_stats': network_stats,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@system_routes.route('/api/disk')
@login_required
def api_disk():
    """API endpoint to get disk I/O statistics"""
    try:
        disk_io_stats = system_service.get_disk_io_stats()
        system_usage = system_service.get_system_usage()
        return jsonify({
            'disk_io_stats': disk_io_stats,
            'disks': system_usage.get('disks', []),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        logger.error(f"Error getting disk stats: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }), 500

def _get_current_timezone() -> str:
    """Get current timezone from the system or app config"""
    try:
        # Try to get from app config first
        if 'TIMEZONE' in current_app.config:
            return current_app.config['TIMEZONE']
        
        # Fallback to system timezone
        import time
        return time.tzname[0]
    except Exception:
        # Default to UTC if all else fails
        return 'UTC'

def _get_cloud_regions(provider: str) -> list:
    """Get cloud regions for the given provider"""
    regions = []
    
    if provider == 'aws':
        regions = [
            {"value": "us-east-1", "label": "US East (N. Virginia)"},
            {"value": "us-east-2", "label": "US East (Ohio)"},
            {"value": "us-west-1", "label": "US West (N. California)"},
            {"value": "us-west-2", "label": "US West (Oregon)"},
            {"value": "eu-west-1", "label": "EU (Ireland)"},
            {"value": "eu-central-1", "label": "EU (Frankfurt)"},
            {"value": "ap-south-1", "label": "Asia Pacific (Mumbai)"},
            {"value": "ap-northeast-1", "label": "Asia Pacific (Tokyo)"},
            {"value": "ap-southeast-1", "label": "Asia Pacific (Singapore)"},
            {"value": "ap-southeast-2", "label": "Asia Pacific (Sydney)"},
            {"value": "sa-east-1", "label": "South America (São Paulo)"}
        ]
    elif provider == 'gcp':
        regions = [
            {"value": "us-central1", "label": "US Central (Iowa)"},
            {"value": "us-east1", "label": "US East (South Carolina)"},
            {"value": "us-east4", "label": "US East (Northern Virginia)"},
            {"value": "us-west1", "label": "US West (Oregon)"},
            {"value": "us-west2", "label": "US West (Los Angeles)"},
            {"value": "europe-west1", "label": "Europe West (Belgium)"},
            {"value": "europe-west2", "label": "Europe West (London)"},
            {"value": "asia-east1", "label": "Asia East (Taiwan)"},
            {"value": "asia-southeast1", "label": "Asia Southeast (Singapore)"}
        ]
    elif provider == 'azure':
        regions = [
            {"value": "eastus", "label": "East US"},
            {"value": "eastus2", "label": "East US 2"},
            {"value": "centralus", "label": "Central US"},
            {"value": "westus", "label": "West US"},
            {"value": "westus2", "label": "West US 2"},
            {"value": "northeurope", "label": "North Europe"},
            {"value": "westeurope", "label": "West Europe"},
            {"value": "eastasia", "label": "East Asia"},
            {"value": "southeastasia", "label": "Southeast Asia"}
        ]
    
    return regions

def _get_firewall_rules() -> list:
    """Get mock firewall rules for UI display"""
    # Replace with actual rules from your configuration or database
    return [
        {
            "id": 1,
            "type": "TCP",
            "port_range": "80",
            "ip_version": "IPv4",
            "source": "0.0.0.0/0"
        },
        {
            "id": 2,
            "type": "TCP",
            "port_range": "443",
            "ip_version": "IPv4",
            "source": "0.0.0.0/0"
        },
        {
            "id": 3,
            "type": "TCP",
            "port_range": "22",
            "ip_version": "IPv4",
            "source": "192.168.0.0/16"
        },
        {
            "id": 4,
            "type": "TCP",
            "port_range": "3306",
            "ip_version": "IPv4",
            "source": "127.0.0.1/32"
        }
    ]

# Register the blueprint
def register_blueprints(app):
    app.register_blueprint(system_routes)
    return app 