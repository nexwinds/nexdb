from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from typing import Dict, Any
import os
from werkzeug.utils import secure_filename

from app.features.auth.decorators import login_required
from app.features.backup.services.backup_service import get_backup_service
from app.features.backup.types import BackupPageProps, BackupFrequency, BackupError, S3BackupError, BackupType
from app.features.database.services.mysql_service import MySQLService
from app.features.database.services.postgres_service import PostgresService


backup_bp = Blueprint('backup', __name__, url_prefix='/backup')


@backup_bp.route('/')
@login_required
def index():
    """Display backup management dashboard"""
    try:
        # Get services
        backup_service = get_backup_service()
        mysql_service = MySQLService()
        postgres_service = PostgresService()
        
        # Get data for view
        local_backups = backup_service.list_local_backups()
        mysql_dbs = mysql_service.list_databases()
        postgres_dbs = postgres_service.list_databases()
        scheduled_backups = backup_service.get_scheduled_backups()
        
        # Get S3 backups if S3 is configured
        s3_backups = []
        aws_configured = backup_service.is_s3_configured()
        if aws_configured:
            try:
                s3_backups = backup_service.list_s3_backups()
            except S3BackupError as e:
                flash(f'Error listing S3 backups: {str(e)}', 'danger')
        
        # Create page props
        props: BackupPageProps = {
            'local_backups': local_backups,
            's3_backups': s3_backups,
            'mysql_dbs': mysql_dbs,
            'postgres_dbs': postgres_dbs,
            'scheduled_backups': scheduled_backups,
            'scheduler_status': backup_service.scheduler_running,
            'aws_configured': aws_configured
        }
        
        return render_template('backup/index.html', **props)
    
    except Exception as e:
        current_app.logger.error(f"Error in backup index: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))


@backup_bp.route('/backup', methods=['POST'])
@login_required
def backup_and_upload():
    """Create a backup and optionally upload to S3"""
    try:
        # Get form data
        db_type = request.form.get('db_type')
        db_name = request.form.get('db_name')
        upload_to_s3 = 'upload_to_s3' in request.form
        
        # Validate inputs
        if not db_type or not db_name:
            flash('Database type and name are required', 'danger')
            return redirect(url_for('backup.index'))
        
        # Validate db_type
        if db_type not in [BackupType.MYSQL, BackupType.POSTGRES]:
            flash(f'Invalid database type: {db_type}', 'danger')
            return redirect(url_for('backup.index'))
        
        # Create backup
        backup_service = get_backup_service()
        backup_file = backup_service.create_backup(db_type, db_name)
        flash(f'Successfully created backup: {os.path.basename(backup_file)}', 'success')
        
        # Upload to S3 if requested
        if upload_to_s3:
            try:
                if not backup_service.is_s3_configured():
                    flash('AWS credentials not configured for S3 upload', 'warning')
                else:
                    s3_key = backup_service.upload_to_s3(backup_file)
                    flash(f'Successfully uploaded backup to S3: {s3_key}', 'success')
            except S3BackupError as e:
                flash(f'Error uploading to S3: {str(e)}', 'danger')
    
    except Exception as e:
        current_app.logger.error(f"Error creating backup: {str(e)}")
        flash(f'Error creating backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))


@backup_bp.route('/upload', methods=['POST'])
@login_required
def upload_to_s3():
    """Upload an existing local backup to S3"""
    try:
        # Get form data
        backup_file = request.form.get('backup_file')
        
        # Validate inputs
        if not backup_file:
            flash('Backup file name is required', 'danger')
            return redirect(url_for('backup.index'))
        
        # Get service
        backup_service = get_backup_service()
        
        # Check if S3 is configured
        if not backup_service.is_s3_configured():
            flash('AWS credentials not configured for S3 upload', 'warning')
            return redirect(url_for('backup.index'))
        
        # Secure filename and get full path
        secure_name = secure_filename(backup_file)
        backup_path = os.path.join(current_app.config['BACKUP_DIR'], secure_name)
        
        # Check if file exists
        if not os.path.exists(backup_path):
            flash(f'Backup file not found: {backup_file}', 'danger')
            return redirect(url_for('backup.index'))
        
        # Upload to S3
        s3_key = backup_service.upload_to_s3(backup_path)
        flash(f'Successfully uploaded backup to S3: {s3_key}', 'success')
    
    except Exception as e:
        current_app.logger.error(f"Error uploading to S3: {str(e)}")
        flash(f'Error uploading to S3: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))


@backup_bp.route('/download', methods=['POST'])
@login_required
def download_from_s3():
    """Download a backup from S3 to local storage"""
    try:
        # Get form data
        s3_object = request.form.get('s3_object')
        
        # Validate inputs
        if not s3_object:
            flash('S3 object key is required', 'danger')
            return redirect(url_for('backup.index'))
        
        # Get service
        backup_service = get_backup_service()
        
        # Check if S3 is configured
        if not backup_service.is_s3_configured():
            flash('AWS credentials not configured for S3 download', 'warning')
            return redirect(url_for('backup.index'))
        
        # Download from S3
        local_path = backup_service.download_from_s3(s3_object)
        flash(f'Successfully downloaded backup from S3: {os.path.basename(local_path)}', 'success')
    
    except Exception as e:
        current_app.logger.error(f"Error downloading from S3: {str(e)}")
        flash(f'Error downloading from S3: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))


@backup_bp.route('/delete-local', methods=['POST'])
@login_required
def delete_local_backup():
    """Delete a local backup file"""
    try:
        # Get form data
        backup_file = request.form.get('backup_file')
        confirm = request.form.get('confirm')
        
        # Validate inputs
        if not backup_file:
            flash('Backup file name is required', 'danger')
            return redirect(url_for('backup.index'))
        
        if not confirm or confirm != backup_file:
            flash('Confirmation does not match backup file name', 'danger')
            return redirect(url_for('backup.index'))
        
        # Delete the backup
        backup_service = get_backup_service()
        backup_service.delete_local_backup(backup_file)
        flash(f'Successfully deleted local backup: {backup_file}', 'success')
    
    except Exception as e:
        current_app.logger.error(f"Error deleting local backup: {str(e)}")
        flash(f'Error deleting local backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))


@backup_bp.route('/delete-s3', methods=['POST'])
@login_required
def delete_s3_backup():
    """Delete a backup from S3"""
    try:
        # Get form data
        s3_object = request.form.get('s3_object')
        confirm = request.form.get('confirm')
        
        # Validate inputs
        if not s3_object:
            flash('S3 object key is required', 'danger')
            return redirect(url_for('backup.index'))
        
        if not confirm or confirm != s3_object:
            flash('Confirmation does not match S3 object key', 'danger')
            return redirect(url_for('backup.index'))
        
        # Get service
        backup_service = get_backup_service()
        
        # Check if S3 is configured
        if not backup_service.is_s3_configured():
            flash('AWS credentials not configured for S3 operations', 'warning')
            return redirect(url_for('backup.index'))
        
        # Delete from S3
        backup_service.delete_from_s3(s3_object)
        flash(f'Successfully deleted S3 backup: {s3_object}', 'success')
    
    except Exception as e:
        current_app.logger.error(f"Error deleting S3 backup: {str(e)}")
        flash(f'Error deleting S3 backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))


@backup_bp.route('/schedule', methods=['POST'])
@login_required
def schedule_backup():
    """Schedule a regular backup job"""
    try:
        # Get form data
        db_type = request.form.get('db_type')
        db_name = request.form.get('db_name')
        frequency = request.form.get('frequency')
        upload_to_s3 = 'upload_to_s3' in request.form
        
        # Validate inputs
        if not db_type or not db_name or not frequency:
            flash('Database type, name, and frequency are required', 'danger')
            return redirect(url_for('backup.index'))
        
        # Validate db_type
        if db_type not in [BackupType.MYSQL, BackupType.POSTGRES]:
            flash(f'Invalid database type: {db_type}', 'danger')
            return redirect(url_for('backup.index'))
        
        # Validate frequency
        try:
            frequency_enum = BackupFrequency(frequency)
        except ValueError:
            flash(f'Invalid backup frequency: {frequency}', 'danger')
            return redirect(url_for('backup.index'))
        
        # Schedule the backup
        backup_service = get_backup_service()
        job_id, job_info = backup_service.schedule_backup(db_type, db_name, frequency_enum, upload_to_s3)
        flash(f'Successfully scheduled {frequency} backup for {db_name}', 'success')
    
    except Exception as e:
        current_app.logger.error(f"Error scheduling backup: {str(e)}")
        flash(f'Error scheduling backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))


@backup_bp.route('/cancel-schedule', methods=['POST'])
@login_required
def cancel_scheduled_backup():
    """Cancel a scheduled backup job"""
    try:
        # Get form data
        job_id = request.form.get('job_id')
        
        # Validate inputs
        if not job_id:
            flash('Job ID is required', 'danger')
            return redirect(url_for('backup.index'))
        
        # Cancel the scheduled backup
        backup_service = get_backup_service()
        name = backup_service.cancel_scheduled_backup(job_id)
        flash(f'Successfully cancelled scheduled backup for {name}', 'success')
    
    except ValueError as e:
        flash(f'Invalid backup job ID: {str(e)}', 'danger')
    except Exception as e:
        current_app.logger.error(f"Error cancelling scheduled backup: {str(e)}")
        flash(f'Error cancelling scheduled backup: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))


@backup_bp.teardown_app_request
def shutdown_scheduler(exception=None):
    """Ensure the scheduler shuts down with the application"""
    if exception:
        current_app.logger.error(f"Error during request: {str(exception)}")
    
    # Note: We don't actually shut down the scheduler here as it's a singleton
    # The scheduler will be properly shutdown when the app context terminates 