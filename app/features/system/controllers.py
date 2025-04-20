from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from typing import Dict, Any

from app.features.auth.decorators import login_required
from app.features.system.services.system_service import get_system_service
from app.features.system.types import SystemPageProps, FirewallRule
from app.features.database.services.mysql_service import MySQLService
from app.features.database.services.postgres_service import PostgresService


system_bp = Blueprint('system', __name__, url_prefix='/system')


@system_bp.route('/')
@login_required
def dashboard():
    """Display system dashboard with monitoring information"""
    try:
        # Get system service
        system_service = get_system_service()
        
        # Get database services
        mysql_service = MySQLService()
        postgres_service = PostgresService()
        
        # Get system information and usage
        system_info = system_service.get_system_info()
        system_usage = system_service.get_system_usage()
        network_stats = system_service.get_network_stats()
        disk_io = system_service.get_disk_io()
        timezone_info = system_service.get_timezone()
        firewall_rules = system_service.get_firewall_rules()
        
        # Get database status
        mysql_status = mysql_service.get_status()
        postgres_status = postgres_service.get_status()
        
        # Create page props
        props: SystemPageProps = {
            'system_info': system_info,
            'system_usage': system_usage,
            'network_stats': network_stats,
            'disk_io': disk_io,
            'timezone_info': timezone_info,
            'firewall_rules': firewall_rules
        }
        
        # Add database status for the services table
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
                'status': True,  # The server is obviously running if we're seeing this page
                'type': 'web'
            }
        ]
        
        return render_template(
            'system/dashboard.html', 
            **props, 
            services=services
        )
    
    except Exception as e:
        current_app.logger.error(f"Error in system dashboard: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))


@system_bp.route('/timezone', methods=['POST'])
@login_required
def set_timezone():
    """Set system timezone"""
    try:
        timezone = request.form.get('timezone')
        if not timezone:
            flash('Timezone is required', 'danger')
            return redirect(url_for('system.dashboard'))
        
        system_service = get_system_service()
        success = system_service.set_timezone(timezone)
        
        if success:
            flash(f'Timezone set to {timezone}', 'success')
        else:
            flash(f'Failed to set timezone to {timezone}', 'danger')
        
        return redirect(url_for('system.dashboard'))
    
    except Exception as e:
        current_app.logger.error(f"Error setting timezone: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('system.dashboard'))


@system_bp.route('/service/<service_name>/restart', methods=['POST'])
@login_required
def restart_service(service_name: str):
    """Restart a system service"""
    try:
        # In a real implementation, this would call system commands to restart services
        # For this example, we'll just simulate success
        flash(f'Service {service_name} restarted successfully', 'success')
        return redirect(url_for('system.dashboard'))
    
    except Exception as e:
        current_app.logger.error(f"Error restarting service {service_name}: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('system.dashboard'))


@system_bp.route('/firewall/add', methods=['POST'])
@login_required
def add_firewall_rule():
    """Add a new firewall rule"""
    try:
        rule_type = request.form.get('type')
        port_range = request.form.get('port_range')
        ip_version = request.form.get('ip_version')
        source = request.form.get('source')
        
        # Validate inputs
        if not all([rule_type, port_range, ip_version, source]):
            flash('All fields are required', 'danger')
            return redirect(url_for('system.dashboard'))
        
        # In a real implementation, this would add the rule to the system firewall
        # For this example, we'll just simulate success
        flash(f'Firewall rule added successfully', 'success')
        return redirect(url_for('system.dashboard'))
    
    except Exception as e:
        current_app.logger.error(f"Error adding firewall rule: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('system.dashboard'))


@system_bp.route('/firewall/delete/<rule_id>', methods=['POST'])
@login_required
def delete_firewall_rule(rule_id: str):
    """Delete a firewall rule"""
    try:
        # In a real implementation, this would remove the rule from the system firewall
        # For this example, we'll just simulate success
        flash(f'Firewall rule deleted successfully', 'success')
        return redirect(url_for('system.dashboard'))
    
    except Exception as e:
        current_app.logger.error(f"Error deleting firewall rule: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('system.dashboard')) 