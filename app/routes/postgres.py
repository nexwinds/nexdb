from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.routes.auth import login_required
from app.utils.postgres_manager import PostgresManager
import os
from datetime import datetime

postgres_bp = Blueprint('postgres', __name__, url_prefix='/postgres')

@postgres_bp.route('/')
@login_required
def index():
    postgres_manager = PostgresManager(
        host=current_app.config['POSTGRES_HOST'],
        port=current_app.config['POSTGRES_PORT'],
        user=current_app.config['POSTGRES_USER'],
        password=current_app.config['POSTGRES_PASSWORD']
    )
    
    try:
        databases = postgres_manager.list_databases()
        users = postgres_manager.list_users()
        status = postgres_manager.get_status()
    except Exception as e:
        databases = []
        users = []
        status = False
        flash(f"Error connecting to PostgreSQL: {str(e)}", "danger")
    
    return render_template('postgres/index.html', 
                          databases=databases, 
                          users=users, 
                          status=status)

@postgres_bp.route('/create_database', methods=['GET', 'POST'])
@login_required
def create_database():
    if request.method == 'POST':
        db_name = request.form.get('db_name')
        create_user = request.form.get('create_user') == 'on'
        user_name = request.form.get('user_name')
        user_password = request.form.get('user_password')
        
        postgres_manager = PostgresManager(
            host=current_app.config['POSTGRES_HOST'],
            port=current_app.config['POSTGRES_PORT'],
            user=current_app.config['POSTGRES_USER'],
            password=current_app.config['POSTGRES_PASSWORD']
        )
        
        # Create database
        if postgres_manager.create_database(db_name):
            flash(f"Database '{db_name}' created successfully", "success")
            
            # Optionally create user and grant permissions
            if create_user and user_name and user_password:
                if postgres_manager.create_user(user_name, user_password):
                    flash(f"User '{user_name}' created successfully", "success")
                    
                    if postgres_manager.grant_privileges(user_name, db_name):
                        flash(f"Privileges granted to '{user_name}' on '{db_name}'", "success")
                    else:
                        flash(f"Failed to grant privileges to '{user_name}'", "danger")
                else:
                    flash(f"Failed to create user '{user_name}'", "danger")
        else:
            flash(f"Failed to create database '{db_name}'", "danger")
        
        return redirect(url_for('postgres.index'))
    
    return render_template('postgres/create_database.html')

@postgres_bp.route('/delete_database/<db_name>', methods=['POST'])
@login_required
def delete_database(db_name):
    confirm = request.form.get('confirm')
    
    if confirm != db_name:
        flash("Database name confirmation does not match", "danger")
        return redirect(url_for('postgres.index'))
    
    postgres_manager = PostgresManager(
        host=current_app.config['POSTGRES_HOST'],
        port=current_app.config['POSTGRES_PORT'],
        user=current_app.config['POSTGRES_USER'],
        password=current_app.config['POSTGRES_PASSWORD']
    )
    
    if postgres_manager.delete_database(db_name):
        flash(f"Database '{db_name}' deleted successfully", "success")
    else:
        flash(f"Failed to delete database '{db_name}'", "danger")
    
    return redirect(url_for('postgres.index'))

@postgres_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_password = request.form.get('user_password')
        
        postgres_manager = PostgresManager(
            host=current_app.config['POSTGRES_HOST'],
            port=current_app.config['POSTGRES_PORT'],
            user=current_app.config['POSTGRES_USER'],
            password=current_app.config['POSTGRES_PASSWORD']
        )
        
        if postgres_manager.create_user(user_name, user_password):
            flash(f"User '{user_name}' created successfully", "success")
        else:
            flash(f"Failed to create user '{user_name}'", "danger")
        
        return redirect(url_for('postgres.index'))
    
    return render_template('postgres/create_user.html')

@postgres_bp.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    user_name = request.form.get('user_name')
    
    postgres_manager = PostgresManager(
        host=current_app.config['POSTGRES_HOST'],
        port=current_app.config['POSTGRES_PORT'],
        user=current_app.config['POSTGRES_USER'],
        password=current_app.config['POSTGRES_PASSWORD']
    )
    
    if postgres_manager.delete_user(user_name):
        flash(f"User '{user_name}' deleted successfully", "success")
    else:
        flash(f"Failed to delete user '{user_name}'", "danger")
    
    return redirect(url_for('postgres.index'))

@postgres_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    user_name = request.form.get('user_name')
    new_password = request.form.get('new_password')
    
    postgres_manager = PostgresManager(
        host=current_app.config['POSTGRES_HOST'],
        port=current_app.config['POSTGRES_PORT'],
        user=current_app.config['POSTGRES_USER'],
        password=current_app.config['POSTGRES_PASSWORD']
    )
    
    if postgres_manager.change_password(user_name, new_password):
        flash(f"Password for '{user_name}' changed successfully", "success")
    else:
        flash(f"Failed to change password for '{user_name}'", "danger")
    
    return redirect(url_for('postgres.index'))

@postgres_bp.route('/backup/<db_name>', methods=['POST'])
@login_required
def backup_database(db_name):
    postgres_manager = PostgresManager(
        host=current_app.config['POSTGRES_HOST'],
        port=current_app.config['POSTGRES_PORT'],
        user=current_app.config['POSTGRES_USER'],
        password=current_app.config['POSTGRES_PASSWORD']
    )
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"postgres_{db_name}_{timestamp}.dump"
    backup_path = os.path.join(current_app.config['BACKUP_DIR'], backup_filename)
    
    if postgres_manager.backup_database(db_name, backup_path):
        flash(f"Database '{db_name}' backed up successfully", "success")
    else:
        flash(f"Failed to backup database '{db_name}'", "danger")
    
    return redirect(url_for('postgres.index'))

@postgres_bp.route('/restore', methods=['POST'])
@login_required
def restore_database():
    backup_file = request.form.get('backup_file')
    db_name = request.form.get('db_name')
    
    postgres_manager = PostgresManager(
        host=current_app.config['POSTGRES_HOST'],
        port=current_app.config['POSTGRES_PORT'],
        user=current_app.config['POSTGRES_USER'],
        password=current_app.config['POSTGRES_PASSWORD']
    )
    
    backup_path = os.path.join(current_app.config['BACKUP_DIR'], backup_file)
    
    if not os.path.exists(backup_path):
        flash(f"Backup file not found: {backup_file}", "danger")
        return redirect(url_for('postgres.index'))
    
    if postgres_manager.restore_database(db_name, backup_path):
        flash(f"Database '{db_name}' restored successfully", "success")
    else:
        flash(f"Failed to restore database '{db_name}'", "danger")
    
    return redirect(url_for('postgres.index')) 