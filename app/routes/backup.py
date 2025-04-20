from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, send_file
from app.routes.auth import login_required
from app.utils.backup_manager import BackupManager
from app.utils.mysql_manager import MySQLManager
from app.utils.postgres_manager import PostgresManager
import os
import json
import threading
import schedule
import time
from datetime import datetime, timedelta
import uuid
from apscheduler.schedulers.background import BackgroundScheduler

backup_bp = Blueprint('backup', __name__, url_prefix='/backup')

# Dictionary to store scheduled backup jobs
scheduled_backups = {}
# Background scheduler for running backup jobs
scheduler = BackgroundScheduler()
scheduler.start()

@backup_bp.route('/')
@login_required
def index():
    """Display backup management dashboard"""
    # Get backup directories from config
    backup_dir = current_app.config['BACKUP_DIR']
    
    # Initialize managers
    mysql_mgr = MySQLManager(current_app.config)
    postgres_mgr = PostgresManager(current_app.config)
    backup_mgr = BackupManager(current_app.config)
    
    # Get available databases
    mysql_dbs = mysql_mgr.get_databases()
    postgres_dbs = postgres_mgr.get_databases()
    
    # Get local backups
    local_backups = []
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.endswith('.sql') or filename.endswith('.dump'):
                file_path = os.path.join(backup_dir, filename)
                file_size = round(os.path.getsize(file_path) / (1024 * 1024), 2)  # Convert to MB
                file_date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                local_backups.append({
                    'name': filename,
                    'size': file_size,
                    'date': file_date
                })
    
    # Get S3 backups
    s3_backups = []
    if current_app.config.get('AWS_ACCESS_KEY') and current_app.config.get('AWS_SECRET_KEY'):
        try:
            s3_files = backup_mgr.list_s3_backups()
            for s3_file in s3_files:
                s3_backups.append({
                    'name': s3_file['Key'],
                    'size': round(s3_file['Size'] / (1024 * 1024), 2),  # Convert to MB
                    'date': s3_file['LastModified']
                })
        except Exception as e:
            flash(f'Error listing S3 backups: {str(e)}', 'danger')
    
    return render_template(
        'backup/index.html',
        local_backups=sorted(local_backups, key=lambda x: x['date'], reverse=True),
        s3_backups=sorted(s3_backups, key=lambda x: x['date'], reverse=True),
        mysql_dbs=mysql_dbs,
        postgres_dbs=postgres_dbs,
        scheduled_backups=list(scheduled_backups.values()),
        scheduler_status=scheduler.running
    )

@backup_bp.route('/backup', methods=['POST'])
@login_required
def backup_and_upload():
    """Create a backup and optionally upload to S3"""
    db_type = request.form.get('db_type')
    db_name = request.form.get('db_name')
    upload_to_s3 = 'upload_to_s3' in request.form
    
    if not db_type or not db_name:
        flash('Database type and name are required', 'danger')
        return redirect(url_for('backup.index'))
    
    # Initialize appropriate manager
    if db_type == 'mysql':
        db_mgr = MySQLManager(current_app.config)
    elif db_type == 'postgres':
        db_mgr = PostgresManager(current_app.config)
    else:
        flash('Invalid database type', 'danger')
        return redirect(url_for('backup.index'))
    
    try:
        # Create backup
        backup_file = db_mgr.backup_database(db_name)
        flash(f'Successfully created backup: {os.path.basename(backup_file)}', 'success')
        
        # Upload to S3 if requested
        if upload_to_s3:
            if not current_app.config.get('AWS_ACCESS_KEY') or not current_app.config.get('AWS_SECRET_KEY'):
                flash('AWS credentials not configured for S3 upload', 'warning')
            else:
                backup_mgr = BackupManager(current_app.config)
                s3_key = backup_mgr.upload_to_s3(backup_file)
                flash(f'Successfully uploaded backup to S3: {s3_key}', 'success')
    
    except Exception as e:
        flash(f'Error creating backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))

@backup_bp.route('/upload', methods=['POST'])
@login_required
def upload_to_s3():
    """Upload an existing local backup to S3"""
    backup_file = request.form.get('backup_file')
    
    if not backup_file:
        flash('Backup file name is required', 'danger')
        return redirect(url_for('backup.index'))
    
    if not current_app.config.get('AWS_ACCESS_KEY') or not current_app.config.get('AWS_SECRET_KEY'):
        flash('AWS credentials not configured for S3 upload', 'warning')
        return redirect(url_for('backup.index'))
    
    try:
        backup_path = os.path.join(current_app.config['BACKUP_DIR'], backup_file)
        if not os.path.exists(backup_path):
            flash(f'Backup file not found: {backup_file}', 'danger')
            return redirect(url_for('backup.index'))
        
        backup_mgr = BackupManager(current_app.config)
        s3_key = backup_mgr.upload_to_s3(backup_path)
        flash(f'Successfully uploaded backup to S3: {s3_key}', 'success')
    
    except Exception as e:
        flash(f'Error uploading to S3: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))

@backup_bp.route('/download', methods=['POST'])
@login_required
def download_from_s3():
    """Download a backup from S3 to local storage"""
    s3_object = request.form.get('s3_object')
    
    if not s3_object:
        flash('S3 object key is required', 'danger')
        return redirect(url_for('backup.index'))
    
    if not current_app.config.get('AWS_ACCESS_KEY') or not current_app.config.get('AWS_SECRET_KEY'):
        flash('AWS credentials not configured for S3 download', 'warning')
        return redirect(url_for('backup.index'))
    
    try:
        backup_mgr = BackupManager(current_app.config)
        local_path = backup_mgr.download_from_s3(s3_object)
        flash(f'Successfully downloaded backup from S3: {os.path.basename(local_path)}', 'success')
    
    except Exception as e:
        flash(f'Error downloading from S3: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))

@backup_bp.route('/delete-local', methods=['POST'])
@login_required
def delete_local_backup():
    """Delete a local backup file"""
    backup_file = request.form.get('backup_file')
    confirm = request.form.get('confirm')
    
    if not backup_file:
        flash('Backup file name is required', 'danger')
        return redirect(url_for('backup.index'))
    
    if not confirm or confirm != backup_file:
        flash('Confirmation does not match backup file name', 'danger')
        return redirect(url_for('backup.index'))
    
    try:
        backup_path = os.path.join(current_app.config['BACKUP_DIR'], backup_file)
        if not os.path.exists(backup_path):
            flash(f'Backup file not found: {backup_file}', 'danger')
            return redirect(url_for('backup.index'))
        
        os.remove(backup_path)
        flash(f'Successfully deleted local backup: {backup_file}', 'success')
    
    except Exception as e:
        flash(f'Error deleting local backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))

@backup_bp.route('/delete-s3', methods=['POST'])
@login_required
def delete_s3_backup():
    """Delete a backup from S3"""
    s3_object = request.form.get('s3_object')
    confirm = request.form.get('confirm')
    
    if not s3_object:
        flash('S3 object key is required', 'danger')
        return redirect(url_for('backup.index'))
    
    if not confirm or confirm != s3_object:
        flash('Confirmation does not match S3 object key', 'danger')
        return redirect(url_for('backup.index'))
    
    if not current_app.config.get('AWS_ACCESS_KEY') or not current_app.config.get('AWS_SECRET_KEY'):
        flash('AWS credentials not configured for S3 operations', 'warning')
        return redirect(url_for('backup.index'))
    
    try:
        backup_mgr = BackupManager(current_app.config)
        backup_mgr.delete_from_s3(s3_object)
        flash(f'Successfully deleted S3 backup: {s3_object}', 'success')
    
    except Exception as e:
        flash(f'Error deleting S3 backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))

@backup_bp.route('/schedule', methods=['POST'])
@login_required
def schedule_backup():
    """Schedule a regular backup job"""
    db_type = request.form.get('db_type')
    db_name = request.form.get('db_name')
    frequency = request.form.get('frequency')
    upload_to_s3 = 'upload_to_s3' in request.form
    
    if not db_type or not db_name or not frequency:
        flash('Database type, name, and frequency are required', 'danger')
        return redirect(url_for('backup.index'))
    
    try:
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        
        # Add job based on frequency
        if frequency == 'hourly':
            job = scheduler.add_job(
                perform_backup,
                'interval', 
                hours=1,
                args=[db_type, db_name, upload_to_s3, job_id]
            )
        elif frequency == 'daily':
            job = scheduler.add_job(
                perform_backup,
                'cron', 
                hour=0, 
                minute=0,
                args=[db_type, db_name, upload_to_s3, job_id]
            )
        elif frequency == 'weekly':
            job = scheduler.add_job(
                perform_backup,
                'cron', 
                day_of_week='mon', 
                hour=0, 
                minute=0,
                args=[db_type, db_name, upload_to_s3, job_id]
            )
        else:
            flash('Invalid backup frequency', 'danger')
            return redirect(url_for('backup.index'))
        
        # Store job in our dictionary
        scheduled_backups[job_id] = {
            'id': job_id,
            'name': f"{db_name} ({db_type})",
            'frequency': frequency,
            'db_type': db_type,
            'db_name': db_name,
            'upload_to_s3': upload_to_s3,
            'job': job
        }
        
        flash(f'Successfully scheduled {frequency} backup for {db_name}', 'success')
    
    except Exception as e:
        flash(f'Error scheduling backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))

@backup_bp.route('/cancel-schedule', methods=['POST'])
@login_required
def cancel_scheduled_backup():
    """Cancel a scheduled backup job"""
    job_id = request.form.get('job_id')
    
    if not job_id or job_id not in scheduled_backups:
        flash('Invalid backup job ID', 'danger')
        return redirect(url_for('backup.index'))
    
    try:
        # Remove job from scheduler
        job_info = scheduled_backups[job_id]
        job_info['job'].remove()
        
        # Remove from our dictionary
        del scheduled_backups[job_id]
        
        flash(f'Successfully cancelled scheduled backup for {job_info["name"]}', 'success')
    
    except Exception as e:
        flash(f'Error cancelling scheduled backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))

def perform_backup(db_type, db_name, upload_to_s3, job_id):
    """
    Perform a backup operation with the given parameters
    This function is called by the scheduler
    """
    with current_app.app_context():
        try:
            # Get the appropriate manager for database type
            if db_type == 'mysql':
                db_mgr = MySQLManager(current_app.config)
            elif db_type == 'postgres':
                db_mgr = PostgresManager(current_app.config)
            else:
                raise ValueError(f"Invalid database type: {db_type}")
            
            # Create backup
            backup_file = db_mgr.backup_database(db_name)
            current_app.logger.info(f"Scheduled backup created: {backup_file}")
            
            # Upload to S3 if requested
            if upload_to_s3:
                if current_app.config.get('AWS_ACCESS_KEY') and current_app.config.get('AWS_SECRET_KEY'):
                    backup_mgr = BackupManager(current_app.config)
                    s3_key = backup_mgr.upload_to_s3(backup_file)
                    current_app.logger.info(f"Scheduled backup uploaded to S3: {s3_key}")
                else:
                    current_app.logger.warning("AWS credentials not configured for S3 upload")
            
            # Update the last run time in the job info
            if job_id in scheduled_backups:
                scheduled_backups[job_id]['last_run'] = datetime.datetime.now()
        
        except Exception as e:
            current_app.logger.error(f"Error in scheduled backup: {str(e)}")

@backup_bp.teardown_app_request
def shutdown_scheduler(exception=None):
    """Ensure the scheduler shuts down with the application"""
    if exception:
        current_app.logger.error(f"Error during request: {str(exception)}") 