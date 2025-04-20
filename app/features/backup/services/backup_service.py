import boto3
import logging
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from flask import current_app
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.job import Job

from app.features.backup.types import (
    BackupFile, ScheduledBackup, BackupError, 
    S3BackupError, BackupFrequency
)
from app.features.database.services.mysql_service import MySQLService
from app.features.database.services.postgres_service import PostgresService


class BackupService:
    """Service for managing database backups and scheduled jobs"""
    
    def __init__(self):
        self._scheduler = BackgroundScheduler()
        self._scheduled_backups: Dict[str, Dict] = {}
        self._scheduler.start()
        
    @property
    def scheduler_running(self) -> bool:
        """Check if scheduler is running"""
        return self._scheduler.running
    
    def shutdown(self) -> None:
        """Shutdown the scheduler"""
        if self._scheduler.running:
            self._scheduler.shutdown()
    
    def get_s3_client(self) -> boto3.client:
        """Get an S3 client with configuration from app config"""
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
                aws_secret_access_key=current_app.config['AWS_SECRET_KEY'],
                region_name=current_app.config['AWS_REGION']
            )
            return s3_client
        except Exception as e:
            logging.error(f"Error creating S3 client: {str(e)}")
            raise S3BackupError(f"Failed to create S3 client: {str(e)}")
    
    def list_local_backups(self) -> List[BackupFile]:
        """List all local backup files"""
        backup_dir = current_app.config['BACKUP_DIR']
        backups: List[BackupFile] = []
        
        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                if filename.endswith('.sql') or filename.endswith('.dump'):
                    file_path = os.path.join(backup_dir, filename)
                    file_size = round(os.path.getsize(file_path) / (1024 * 1024), 2)  # MB
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    backups.append({
                        'name': filename,
                        'size': file_size,
                        'date': file_date
                    })
        
        # Sort by date, newest first
        return sorted(backups, key=lambda x: x['date'], reverse=True)
    
    def list_s3_backups(self) -> List[BackupFile]:
        """List all backups in the S3 bucket"""
        if not self._is_s3_configured():
            return []
            
        try:
            s3_client = self.get_s3_client()
            response = s3_client.list_objects_v2(Bucket=current_app.config['AWS_BUCKET_NAME'])
            
            if 'Contents' not in response:
                return []
            
            backups: List[BackupFile] = []
            for obj in response['Contents']:
                backups.append({
                    'name': obj['Key'],
                    'size': round(obj['Size'] / (1024**2), 2),  # MB
                    'date': obj['LastModified']
                })
            
            # Sort by date, newest first
            return sorted(backups, key=lambda x: x['date'], reverse=True)
        except Exception as e:
            logging.error(f"Error listing S3 backups: {str(e)}")
            raise S3BackupError(f"Failed to list S3 backups: {str(e)}")
    
    def create_backup(self, db_type: str, db_name: str) -> str:
        """Create a database backup"""
        # Get appropriate service based on db_type
        service = self._get_db_service(db_type)
        
        # Generate backup filename with timestamp and secure name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        secure_db_name = secure_filename(db_name)
        extension = '.sql' if db_type == 'mysql' else '.dump'
        filename = f"{secure_db_name}_{timestamp}{extension}"
        
        # Get full backup path
        backup_path = os.path.join(current_app.config['BACKUP_DIR'], filename)
        
        # Perform backup
        success = service.backup_database(db_name, backup_path)
        if not success:
            raise BackupError(f"Failed to create {db_type} backup for {db_name}")
        
        return backup_path
    
    def upload_to_s3(self, file_path: str, object_name: Optional[str] = None) -> str:
        """Upload a file to S3 bucket"""
        if not self._is_s3_configured():
            raise S3BackupError("AWS S3 credentials not configured")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Backup file not found: {file_path}")
            
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        try:
            s3_client = self.get_s3_client()
            s3_client.upload_file(
                file_path, 
                current_app.config['AWS_BUCKET_NAME'], 
                object_name
            )
            return object_name
        except Exception as e:
            logging.error(f"Error uploading to S3: {str(e)}")
            raise S3BackupError(f"Failed to upload to S3: {str(e)}")
    
    def download_from_s3(self, object_name: str) -> str:
        """Download a file from S3 bucket"""
        if not self._is_s3_configured():
            raise S3BackupError("AWS S3 credentials not configured")
            
        try:
            # Ensure object name doesn't contain path traversal
            secure_object_name = secure_filename(object_name)
            local_path = os.path.join(current_app.config['BACKUP_DIR'], secure_object_name)
            
            s3_client = self.get_s3_client()
            s3_client.download_file(
                current_app.config['AWS_BUCKET_NAME'], 
                object_name, 
                local_path
            )
            return local_path
        except Exception as e:
            logging.error(f"Error downloading from S3: {str(e)}")
            raise S3BackupError(f"Failed to download from S3: {str(e)}")
    
    def delete_local_backup(self, backup_file: str) -> bool:
        """Delete a local backup file safely"""
        try:
            # Secure the filename and build full path
            secure_name = secure_filename(backup_file)
            backup_path = os.path.join(current_app.config['BACKUP_DIR'], secure_name)
            
            # Verify path is within backup directory (prevent path traversal)
            real_backup_path = os.path.realpath(backup_path)
            real_backup_dir = os.path.realpath(current_app.config['BACKUP_DIR'])
            
            if not real_backup_path.startswith(real_backup_dir):
                raise BackupError("Invalid backup path")
            
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            os.remove(backup_path)
            return True
        except Exception as e:
            logging.error(f"Error deleting local backup: {str(e)}")
            raise BackupError(f"Failed to delete local backup: {str(e)}")
    
    def delete_from_s3(self, object_name: str) -> bool:
        """Delete a file from S3 bucket"""
        if not self._is_s3_configured():
            raise S3BackupError("AWS S3 credentials not configured")
            
        try:
            s3_client = self.get_s3_client()
            s3_client.delete_object(
                Bucket=current_app.config['AWS_BUCKET_NAME'],
                Key=object_name
            )
            return True
        except Exception as e:
            logging.error(f"Error deleting from S3: {str(e)}")
            raise S3BackupError(f"Failed to delete from S3: {str(e)}")
    
    def schedule_backup(self, 
                       db_type: str, 
                       db_name: str, 
                       frequency: BackupFrequency, 
                       upload_to_s3: bool) -> Tuple[str, ScheduledBackup]:
        """Schedule a regular backup job"""
        from uuid import uuid4
        
        # Validate database exists
        service = self._get_db_service(db_type)
        databases = service.list_databases()
        if db_name not in databases:
            raise BackupError(f"Database {db_name} not found")
        
        # Generate a unique job ID
        job_id = str(uuid4())
        
        # Add job based on frequency
        if frequency == BackupFrequency.HOURLY:
            job = self._scheduler.add_job(
                self._perform_scheduled_backup,
                'interval', 
                hours=1,
                args=[db_type, db_name, upload_to_s3, job_id]
            )
        elif frequency == BackupFrequency.DAILY:
            job = self._scheduler.add_job(
                self._perform_scheduled_backup,
                'cron', 
                hour=0, 
                minute=0,
                args=[db_type, db_name, upload_to_s3, job_id]
            )
        elif frequency == BackupFrequency.WEEKLY:
            job = self._scheduler.add_job(
                self._perform_scheduled_backup,
                'cron', 
                day_of_week='mon', 
                hour=0, 
                minute=0,
                args=[db_type, db_name, upload_to_s3, job_id]
            )
        else:
            raise ValueError(f"Invalid backup frequency: {frequency}")
        
        # Store job in our dictionary
        job_info: ScheduledBackup = {
            'id': job_id,
            'name': f"{db_name} ({db_type})",
            'frequency': frequency,
            'db_type': db_type,
            'db_name': db_name,
            'upload_to_s3': upload_to_s3,
            'last_run': None
        }
        
        self._scheduled_backups[job_id] = {
            **job_info,
            'job': job
        }
        
        return job_id, job_info
    
    def cancel_scheduled_backup(self, job_id: str) -> str:
        """Cancel a scheduled backup job"""
        if job_id not in self._scheduled_backups:
            raise ValueError(f"Invalid job ID: {job_id}")
        
        try:
            # Remove job from scheduler
            job_info = self._scheduled_backups[job_id]
            job_info['job'].remove()
            
            # Get name before removing from dictionary
            name = job_info['name']
            
            # Remove from our dictionary
            del self._scheduled_backups[job_id]
            
            return name
        except Exception as e:
            logging.error(f"Error cancelling scheduled backup: {str(e)}")
            raise BackupError(f"Failed to cancel scheduled backup: {str(e)}")
    
    def get_scheduled_backups(self) -> List[ScheduledBackup]:
        """Get all scheduled backup jobs"""
        # Convert to list of job info without the job object
        result: List[ScheduledBackup] = []
        for job_id, job_data in self._scheduled_backups.items():
            # Create a copy without the job object
            job_info = {k: v for k, v in job_data.items() if k != 'job'}
            result.append(job_info)  # type: ignore
        return result
    
    def is_s3_configured(self) -> bool:
        """Check if AWS S3 is configured"""
        return self._is_s3_configured()
    
    def _perform_scheduled_backup(self, db_type: str, db_name: str, upload_to_s3: bool, job_id: str) -> None:
        """
        Perform a backup operation with the given parameters
        This function is called by the scheduler
        """
        try:
            # Create backup
            backup_file = self.create_backup(db_type, db_name)
            current_app.logger.info(f"Scheduled backup created: {backup_file}")
            
            # Upload to S3 if requested
            if upload_to_s3 and self._is_s3_configured():
                s3_key = self.upload_to_s3(backup_file)
                current_app.logger.info(f"Scheduled backup uploaded to S3: {s3_key}")
            elif upload_to_s3:
                current_app.logger.warning("AWS credentials not configured for S3 upload")
            
            # Update the last run time in the job info
            if job_id in self._scheduled_backups:
                self._scheduled_backups[job_id]['last_run'] = datetime.now()
        
        except Exception as e:
            current_app.logger.error(f"Error in scheduled backup: {str(e)}")
    
    def _get_db_service(self, db_type: str) -> Union[MySQLService, PostgresService]:
        """Get the appropriate database service based on type"""
        if db_type == 'mysql':
            return MySQLService()
        elif db_type == 'postgres':
            return PostgresService()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _is_s3_configured(self) -> bool:
        """Check if AWS S3 credentials are configured"""
        return bool(
            current_app.config.get('AWS_ACCESS_KEY') and 
            current_app.config.get('AWS_SECRET_KEY') and
            current_app.config.get('AWS_BUCKET_NAME')
        )


# Create a singleton instance
_backup_service = None

def get_backup_service() -> BackupService:
    """Get the backup service singleton"""
    global _backup_service
    if _backup_service is None:
        _backup_service = BackupService()
    return _backup_service 