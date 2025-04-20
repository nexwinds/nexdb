from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.routes.auth import login_required
from app.utils.mysql_manager import MySQLManager
import os
from datetime import datetime

mysql_bp = Blueprint('mysql', __name__, url_prefix='/mysql')

@mysql_bp.route('/')
@login_required
def index():
    mysql_manager = MySQLManager(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )
    
    try:
        databases = mysql_manager.list_databases()
        users = mysql_manager.list_users()
        status = mysql_manager.get_status()
    except Exception as e:
        databases = []
        users = []
        status = False
        flash(f"Error connecting to MySQL: {str(e)}", "danger")
    
    return render_template('mysql/index.html', 
                          databases=databases, 
                          users=users, 
                          status=status)

@mysql_bp.route('/create_database', methods=['GET', 'POST'])
@login_required
def create_database():
    if request.method == 'POST':
        db_name = request.form.get('db_name')
        create_user = request.form.get('create_user') == 'on'
        user_name = request.form.get('user_name')
        user_password = request.form.get('user_password')
        
        mysql_manager = MySQLManager(
            host=current_app.config['MYSQL_HOST'],
            port=current_app.config['MYSQL_PORT'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD']
        )
        
        # Create database
        if mysql_manager.create_database(db_name):
            flash(f"Database '{db_name}' created successfully", "success")
            
            # Optionally create user and grant permissions
            if create_user and user_name and user_password:
                if mysql_manager.create_user(user_name, user_password):
                    flash(f"User '{user_name}' created successfully", "success")
                    
                    if mysql_manager.grant_privileges(user_name, db_name):
                        flash(f"Privileges granted to '{user_name}' on '{db_name}'", "success")
                    else:
                        flash(f"Failed to grant privileges to '{user_name}'", "danger")
                else:
                    flash(f"Failed to create user '{user_name}'", "danger")
        else:
            flash(f"Failed to create database '{db_name}'", "danger")
        
        return redirect(url_for('mysql.index'))
    
    return render_template('mysql/create_database.html')

@mysql_bp.route('/delete_database/<db_name>', methods=['POST'])
@login_required
def delete_database(db_name):
    confirm = request.form.get('confirm')
    
    if confirm != db_name:
        flash("Database name confirmation does not match", "danger")
        return redirect(url_for('mysql.index'))
    
    mysql_manager = MySQLManager(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )
    
    if mysql_manager.delete_database(db_name):
        flash(f"Database '{db_name}' deleted successfully", "success")
    else:
        flash(f"Failed to delete database '{db_name}'", "danger")
    
    return redirect(url_for('mysql.index'))

@mysql_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_password = request.form.get('user_password')
        host = request.form.get('host', '%')
        
        mysql_manager = MySQLManager(
            host=current_app.config['MYSQL_HOST'],
            port=current_app.config['MYSQL_PORT'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD']
        )
        
        if mysql_manager.create_user(user_name, user_password, host):
            flash(f"User '{user_name}@{host}' created successfully", "success")
        else:
            flash(f"Failed to create user '{user_name}@{host}'", "danger")
        
        return redirect(url_for('mysql.index'))
    
    return render_template('mysql/create_user.html')

@mysql_bp.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    user_info = request.form.get('user_info')
    
    if '@' not in user_info:
        flash("Invalid user format", "danger")
        return redirect(url_for('mysql.index'))
    
    user_name, host = user_info.split('@', 1)
    
    mysql_manager = MySQLManager(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )
    
    if mysql_manager.delete_user(user_name, host):
        flash(f"User '{user_info}' deleted successfully", "success")
    else:
        flash(f"Failed to delete user '{user_info}'", "danger")
    
    return redirect(url_for('mysql.index'))

@mysql_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    user_info = request.form.get('user_info')
    new_password = request.form.get('new_password')
    
    if '@' not in user_info:
        flash("Invalid user format", "danger")
        return redirect(url_for('mysql.index'))
    
    user_name, host = user_info.split('@', 1)
    
    mysql_manager = MySQLManager(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )
    
    if mysql_manager.change_password(user_name, new_password, host):
        flash(f"Password for '{user_info}' changed successfully", "success")
    else:
        flash(f"Failed to change password for '{user_info}'", "danger")
    
    return redirect(url_for('mysql.index'))

@mysql_bp.route('/backup/<db_name>', methods=['POST'])
@login_required
def backup_database(db_name):
    mysql_manager = MySQLManager(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"mysql_{db_name}_{timestamp}.sql"
    backup_path = os.path.join(current_app.config['BACKUP_DIR'], backup_filename)
    
    if mysql_manager.backup_database(db_name, backup_path):
        flash(f"Database '{db_name}' backed up successfully", "success")
    else:
        flash(f"Failed to backup database '{db_name}'", "danger")
    
    return redirect(url_for('mysql.index'))

@mysql_bp.route('/restore', methods=['POST'])
@login_required
def restore_database():
    backup_file = request.form.get('backup_file')
    
    mysql_manager = MySQLManager(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )
    
    backup_path = os.path.join(current_app.config['BACKUP_DIR'], backup_file)
    
    if not os.path.exists(backup_path):
        flash(f"Backup file not found: {backup_file}", "danger")
        return redirect(url_for('mysql.index'))
    
    if mysql_manager.restore_database(backup_path):
        flash("Database restored successfully", "success")
    else:
        flash("Failed to restore database", "danger")
    
    return redirect(url_for('mysql.index')) 