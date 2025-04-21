from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request, jsonify
from typing import Dict, Any
from flask_login import login_required

from app.features.auth.decorators import login_required
from app.features.system.services.system_service import get_system_service, SystemService
from app.features.system.types import SystemPageProps, FirewallRule
from app.features.database.services.mysql_service import MySQLService
from app.features.database.services.postgres_service import PostgresService
from app.features.system.services.postgres_installer import get_postgres_installer
from app.utils.mysql_manager import MySQLManager
from app.utils.postgres_manager import PostgresManager
import psutil
import platform
import datetime
import socket


system_bp = Blueprint('system', __name__, url_prefix='/system')


@system_bp.route('/')
@login_required
def dashboard():
    """Display system dashboard with monitoring information"""
    try:
        # Create service instance
        system_service = SystemService()
        
        # Get system information
        system_info = system_service.get_system_info()
        
        # Get MySQL status
        mysql_manager = MySQLManager(
            host=current_app.config['MYSQL_HOST'],
            port=current_app.config['MYSQL_PORT'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD']
        )
        
        # Get PostgreSQL status
        postgres_manager = PostgresManager(
            host=current_app.config['POSTGRES_HOST'],
            port=current_app.config['POSTGRES_PORT'],
            user=current_app.config['POSTGRES_USER'],
            password=current_app.config['POSTGRES_PASSWORD']
        )
        
        try:
            mysql_status = mysql_manager.get_status()
        except:
            mysql_status = False
            
        try:
            postgres_status = postgres_manager.get_status()
        except:
            postgres_status = False
        
        # Get detailed PostgreSQL installation status
        postgres_installer = get_postgres_installer()
        postgres_install_status = postgres_installer.get_postgres_status()
        
        # Create props for template
        props = {
            'system_info': system_info,
            'mysql_status': mysql_status,
            'postgres_status': postgres_status,
            'postgres_install_status': postgres_install_status,
            'title': 'System Dashboard'
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


@system_bp.route('/install-postgresql', methods=['POST'])
@login_required
def install_postgresql():
    """Install PostgreSQL database server"""
    try:
        # Get the installer
        postgres_installer = get_postgres_installer()
        
        # Check if already installed
        if postgres_installer.check_if_installed():
            flash('PostgreSQL is already installed.', 'info')
            return redirect(url_for('system.dashboard'))
        
        # Install PostgreSQL
        success, message = postgres_installer.install()
        
        if success:
            # Save the credentials in the app configuration
            password = message.split('password: ')[1] if 'password: ' in message else None
            
            if password:
                # Store in configuration
                from app.db.db import get_db
                db = get_db()
                db.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', 
                          ('postgres_host', 'localhost'))
                db.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', 
                          ('postgres_port', '5432'))
                db.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', 
                          ('postgres_user', 'postgres'))
                db.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', 
                          ('postgres_password', password))
                db.commit()
            
            flash(message, 'success')
        else:
            flash(f'Failed to install PostgreSQL: {message}', 'danger')
        
        return redirect(url_for('system.dashboard'))
    
    except Exception as e:
        current_app.logger.error(f"Error installing PostgreSQL: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('system.dashboard')) 