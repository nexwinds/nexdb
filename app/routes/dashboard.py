from flask import Blueprint, render_template, current_app
from app.routes.auth import login_required
from app.utils.mysql_manager import MySQLManager
from app.utils.postgres_manager import PostgresManager
import os
import psutil
import shutil

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Get database status
    mysql_manager = MySQLManager(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )
    
    postgres_manager = PostgresManager(
        host=current_app.config['POSTGRES_HOST'],
        port=current_app.config['POSTGRES_PORT'],
        user=current_app.config['POSTGRES_USER'],
        password=current_app.config['POSTGRES_PASSWORD']
    )
    
    try:
        mysql_status = mysql_manager.get_status()
        mysql_dbs = mysql_manager.list_databases()
        mysql_users = mysql_manager.list_users()
    except Exception as e:
        mysql_status = False
        mysql_dbs = []
        mysql_users = []
    
    try:
        postgres_status = postgres_manager.get_status()
        postgres_dbs = postgres_manager.list_databases()
        postgres_users = postgres_manager.list_users()
    except Exception as e:
        postgres_status = False
        postgres_dbs = []
        postgres_users = []
    
    # Get system information
    system_info = {
        'disk_total': round(shutil.disk_usage('/').total / (1024**3), 2),  # GB
        'disk_used': round(shutil.disk_usage('/').used / (1024**3), 2),    # GB
        'disk_free': round(shutil.disk_usage('/').free / (1024**3), 2),    # GB
        'memory_total': round(psutil.virtual_memory().total / (1024**3), 2),  # GB
        'memory_used': round(psutil.virtual_memory().used / (1024**3), 2),    # GB
        'cpu_percent': psutil.cpu_percent()
    }
    
    # Get backup info
    backup_dir = current_app.config['BACKUP_DIR']
    backups = []
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if os.path.isfile(os.path.join(backup_dir, filename)):
                backups.append({
                    'name': filename,
                    'size': round(os.path.getsize(os.path.join(backup_dir, filename)) / (1024**2), 2),  # MB
                    'date': os.path.getmtime(os.path.join(backup_dir, filename))
                })
    
    return render_template('dashboard/index.html', 
                          mysql_status=mysql_status,
                          mysql_dbs=mysql_dbs,
                          mysql_users=mysql_users,
                          postgres_status=postgres_status,
                          postgres_dbs=postgres_dbs,
                          postgres_users=postgres_users,
                          system_info=system_info,
                          backups=sorted(backups, key=lambda x: x['date'], reverse=True)[:5])  # Show only 5 most recent backups 