"""
Backup controller for NEXDB.
Provides endpoints for database backups and restoration.
"""
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, jsonify
from app.utils.backup_manager import BackupManager
from app.features.database.utils import get_mysql_manager, get_postgres_manager
from app.db.models import db, Config

blueprint = Blueprint('backup_controller', __name__)

@blueprint.route('/')
def index():
    """Display backup management dashboard"""
    # Get S3 config from database first, fall back to env vars
    s3_config = {
        'aws_access_key': get_config('AWS_ACCESS_KEY', ''),
        'aws_secret_key': get_config('AWS_SECRET_KEY', ''),
        'aws_bucket': get_config('AWS_BUCKET_NAME', ''),
        'aws_region': get_config('AWS_REGION', 'us-east-1')
    }
    
    backup_manager = BackupManager(
        backup_dir=current_app.config['BACKUP_DIR'],
        aws_access_key=s3_config['aws_access_key'],
        aws_secret_key=s3_config['aws_secret_key'],
        aws_bucket=s3_config['aws_bucket'],
        aws_region=s3_config['aws_region']
    )
    
    try:
        # Get local backups
        local_backups = backup_manager.list_local_backups()
        
        # Get S3 backups if credentials are configured
        if (s3_config['aws_access_key'] and 
            s3_config['aws_secret_key'] and 
            s3_config['aws_bucket']):
            s3_backups = backup_manager.list_s3_backups()
            s3_configured = True
        else:
            s3_backups = []
            s3_configured = False
            
        # Get databases for backup selection
        mysql_databases = []
        postgres_databases = []
        
        try:
            mysql_manager = get_mysql_manager()
            mysql_databases = mysql_manager.list_databases()
        except Exception as e:
            current_app.logger.error(f"Error getting MySQL databases: {str(e)}")
            
        try:
            postgres_manager = get_postgres_manager()
            postgres_databases = postgres_manager.list_databases()
        except Exception as e:
            current_app.logger.error(f"Error getting PostgreSQL databases: {str(e)}")
            
        # Get scheduled backups
        scheduled_backups = backup_manager.get_scheduled_backups()
        
    except Exception as e:
        flash(f"Error retrieving backup information: {str(e)}", "danger")
        local_backups = []
        s3_backups = []
        s3_configured = False
        mysql_databases = []
        postgres_databases = []
        scheduled_backups = []
    
    return render_template(
        'backup/index.html',
        local_backups=local_backups,
        s3_backups=s3_backups,
        s3_configured=s3_configured,
        s3_config=s3_config,
        mysql_databases=mysql_databases,
        postgres_databases=postgres_databases,
        scheduled_backups=scheduled_backups
    )

@blueprint.route('/create', methods=['POST'])
def create_backup():
    """Create a new database backup"""
    db_type = request.form.get('db_type')
    db_name = request.form.get('db_name')
    backup_type = request.form.get('backup_type', 'local')  # local or s3
    
    if not db_type or not db_name:
        flash("Database type and name are required", "danger")
        return redirect(url_for('backup.backup_controller.index'))
    
    # Get S3 config from database
    s3_config = {
        'aws_access_key': get_config('AWS_ACCESS_KEY', ''),
        'aws_secret_key': get_config('AWS_SECRET_KEY', ''),
        'aws_bucket': get_config('AWS_BUCKET_NAME', ''),
        'aws_region': get_config('AWS_REGION', 'us-east-1')
    }
    
    backup_manager = BackupManager(
        backup_dir=current_app.config['BACKUP_DIR'],
        aws_access_key=s3_config['aws_access_key'],
        aws_secret_key=s3_config['aws_secret_key'],
        aws_bucket=s3_config['aws_bucket'],
        aws_region=s3_config['aws_region']
    )
    
    try:
        if db_type == 'mysql':
            mysql_manager = get_mysql_manager()
            backup_file = backup_manager.backup_mysql_database(
                db_name,
                mysql_manager.host,
                mysql_manager.port,
                mysql_manager.user,
                mysql_manager.password
            )
        elif db_type == 'postgres':
            postgres_manager = get_postgres_manager()
            backup_file = backup_manager.backup_postgres_database(
                db_name,
                postgres_manager.host,
                postgres_manager.port,
                postgres_manager.user,
                postgres_manager.password
            )
        else:
            flash("Invalid database type", "danger")
            return redirect(url_for('backup.backup_controller.index'))
        
        # Upload to S3 if requested
        if backup_type == 's3':
            if (s3_config['aws_access_key'] and 
                s3_config['aws_secret_key'] and 
                s3_config['aws_bucket']):
                backup_manager.upload_to_s3(backup_file)
                flash(f"Database {db_name} backed up to S3 successfully", "success")
            else:
                flash("S3 credentials not configured", "danger")
                return redirect(url_for('backup.backup_controller.index'))
        else:
            flash(f"Database {db_name} backed up locally successfully", "success")
            
    except Exception as e:
        flash(f"Error creating backup: {str(e)}", "danger")
    
    return redirect(url_for('backup.backup_controller.index'))

@blueprint.route('/restore', methods=['POST'])
def restore_backup():
    """Restore a database from backup"""
    backup_file = request.form.get('backup_file')
    db_type = request.form.get('db_type')
    db_name = request.form.get('db_name')
    
    if not backup_file or not db_type or not db_name:
        flash("Backup file, database type, and name are required", "danger")
        return redirect(url_for('backup.backup_controller.index'))
    
    # Get S3 config from database
    s3_config = {
        'aws_access_key': get_config('AWS_ACCESS_KEY', ''),
        'aws_secret_key': get_config('AWS_SECRET_KEY', ''),
        'aws_bucket': get_config('AWS_BUCKET_NAME', ''),
        'aws_region': get_config('AWS_REGION', 'us-east-1')
    }
    
    backup_manager = BackupManager(
        backup_dir=current_app.config['BACKUP_DIR'],
        aws_access_key=s3_config['aws_access_key'],
        aws_secret_key=s3_config['aws_secret_key'],
        aws_bucket=s3_config['aws_bucket'],
        aws_region=s3_config['aws_region']
    )
    
    try:
        if db_type == 'mysql':
            mysql_manager = get_mysql_manager()
            backup_manager.restore_mysql_database(
                backup_file,
                db_name,
                mysql_manager.host,
                mysql_manager.port,
                mysql_manager.user,
                mysql_manager.password
            )
        elif db_type == 'postgres':
            postgres_manager = get_postgres_manager()
            backup_manager.restore_postgres_database(
                backup_file,
                db_name,
                postgres_manager.host,
                postgres_manager.port,
                postgres_manager.user,
                postgres_manager.password
            )
        else:
            flash("Invalid database type", "danger")
            return redirect(url_for('backup.backup_controller.index'))
            
        flash(f"Database {db_name} restored successfully", "success")
            
    except Exception as e:
        flash(f"Error restoring backup: {str(e)}", "danger")
    
    return redirect(url_for('backup.backup_controller.index'))

@blueprint.route('/config/s3', methods=['POST'])
def update_s3_config():
    """Update S3 configuration"""
    aws_access_key = request.form.get('aws_access_key', '')
    aws_secret_key = request.form.get('aws_secret_key', '')
    aws_bucket = request.form.get('aws_bucket', '')
    aws_region = request.form.get('aws_region', 'us-east-1')
    
    # Save to database
    set_config('AWS_ACCESS_KEY', aws_access_key, "AWS S3 Access Key")
    set_config('AWS_SECRET_KEY', aws_secret_key, "AWS S3 Secret Key")
    set_config('AWS_BUCKET_NAME', aws_bucket, "AWS S3 Bucket Name")
    set_config('AWS_REGION', aws_region, "AWS S3 Region")
    
    flash("S3 configuration updated successfully", "success")
    return redirect(url_for('backup.backup_controller.index'))

def get_config(key, default=None):
    """Get configuration value from database, falling back to environment variables."""
    config = Config.query.filter_by(key=key).first()
    if config and config.value:
        return config.value
    return current_app.config.get(key, default)

def set_config(key, value, description=None):
    """Set configuration value in database."""
    config = Config.query.filter_by(key=key).first()
    if config:
        config.value = value
        if description:
            config.description = description
    else:
        config = Config(
            key=key,
            value=value,
            description=description or f"Configuration for {key}"
        )
        db.session.add(config)
    
    db.session.commit()
    return config 