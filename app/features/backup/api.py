from flask import Blueprint, jsonify, request, current_app, send_file
from typing import Dict, Any, List, Optional, Tuple, Union
import os
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required
from http import HTTPStatus

from app.features.backup.services.backup_service import get_backup_service
from app.features.backup.types import BackupFrequency, BackupResponse, S3BackupError, BackupError, BackupType
from app.features.database.services.mysql_service import MySQLService
from app.features.database.services.postgres_service import PostgresService


backup_api = Blueprint('backup_api', __name__, url_prefix='/api/backups')


@backup_api.route('', methods=['GET'])
@jwt_required()
def get_backups() -> Tuple[Dict[str, Any], int]:
    """Get all backups (local and S3)"""
    try:
        service = get_backup_service()
        
        # Get local and S3 backups
        local_backups = service.list_local_backups()
        s3_backups = service.list_s3_backups() if service.is_s3_configured() else []
        
        response: BackupResponse = {
            'success': True,
            'message': 'Backups retrieved successfully',
            'data': {
                'local_backups': local_backups,
                's3_backups': s3_backups,
                'aws_configured': service.is_s3_configured()
            }
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to retrieve backups: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@backup_api.route('/databases', methods=['GET'])
@jwt_required()
def get_databases() -> Tuple[Dict[str, Any], int]:
    """Get available databases for backup"""
    try:
        mysql_service = MySQLService()
        postgres_service = PostgresService()
        
        mysql_dbs = mysql_service.list_databases()
        postgres_dbs = postgres_service.list_databases()
        
        response: BackupResponse = {
            'success': True,
            'message': 'Databases retrieved successfully',
            'data': {
                'mysql_dbs': mysql_dbs,
                'postgres_dbs': postgres_dbs
            }
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to retrieve databases: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@backup_api.route('/scheduled', methods=['GET'])
@jwt_required()
def get_scheduled_backups() -> Tuple[Dict[str, Any], int]:
    """Get all scheduled backup jobs"""
    try:
        service = get_backup_service()
        scheduled_backups = service.get_scheduled_backups()
        
        response: BackupResponse = {
            'success': True,
            'message': 'Scheduled backups retrieved successfully',
            'data': {
                'scheduled_backups': scheduled_backups,
                'scheduler_status': service.scheduler_running
            }
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to retrieve scheduled backups: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@backup_api.route('', methods=['POST'])
@jwt_required()
def create_backup() -> Tuple[Dict[str, Any], int]:
    """Create a new backup"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'data': None
            }), HTTPStatus.BAD_REQUEST
        
        db_type = data.get('db_type')
        db_name = data.get('db_name')
        upload_to_s3 = data.get('upload_to_s3', False)
        
        # Validate inputs
        if not db_type or not db_name:
            return jsonify({
                'success': False,
                'message': 'Database type and name are required',
                'data': None
            }), HTTPStatus.BAD_REQUEST
        
        # Validate db_type
        if db_type not in [BackupType.MYSQL, BackupType.POSTGRES]:
            return jsonify({
                'success': False,
                'message': f'Invalid database type: {db_type}',
                'data': None
            }), HTTPStatus.BAD_REQUEST
        
        # Create backup
        service = get_backup_service()
        backup_file = service.create_backup(db_type, db_name)
        
        # Upload to S3 if requested
        s3_key = None
        if upload_to_s3:
            try:
                s3_key = service.upload_to_s3(backup_file)
            except S3BackupError as e:
                # Just log the error but continue as the local backup succeeded
                current_app.logger.warning(f"S3 upload failed: {str(e)}")
        
        response: BackupResponse = {
            'success': True,
            'message': 'Backup created successfully',
            'data': {
                'backup_file': os.path.basename(backup_file),
                's3_key': s3_key
            }
        }
        
        return jsonify(response), HTTPStatus.CREATED
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to create backup: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@backup_api.route('/s3/<path:object_name>', methods=['GET'])
@jwt_required()
def download_from_s3(object_name: str) -> Union[Tuple[Dict[str, Any], int], Any]:
    """Download a backup from S3"""
    try:
        service = get_backup_service()
        local_path = service.download_from_s3(object_name)
        
        # Send file as attachment
        return send_file(
            local_path,
            as_attachment=True,
            download_name=os.path.basename(local_path)
        )
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to download from S3: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@backup_api.route('/local/<path:backup_file>', methods=['DELETE'])
@jwt_required()
def delete_local_backup(backup_file: str) -> Tuple[Dict[str, Any], int]:
    """Delete a local backup file"""
    try:
        # Ensure the filename is secure
        backup_file = secure_filename(backup_file)
        
        service = get_backup_service()
        service.delete_local_backup(backup_file)
        
        response: BackupResponse = {
            'success': True,
            'message': f'Local backup {backup_file} deleted successfully',
            'data': None
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to delete local backup: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@backup_api.route('/s3/<path:object_name>', methods=['DELETE'])
@jwt_required()
def delete_s3_backup(object_name: str) -> Tuple[Dict[str, Any], int]:
    """Delete a backup from S3"""
    try:
        service = get_backup_service()
        service.delete_from_s3(object_name)
        
        response: BackupResponse = {
            'success': True,
            'message': f'S3 backup {object_name} deleted successfully',
            'data': None
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to delete S3 backup: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@backup_api.route('/s3', methods=['POST'])
@jwt_required()
def upload_to_s3() -> Tuple[Dict[str, Any], int]:
    """Upload a local backup to S3"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'data': None
            }), HTTPStatus.BAD_REQUEST
        
        backup_file = data.get('backup_file')
        
        # Validate inputs
        if not backup_file:
            return jsonify({
                'success': False,
                'message': 'Backup file name is required',
                'data': None
            }), HTTPStatus.BAD_REQUEST
        
        # Ensure the filename is secure
        backup_file = secure_filename(backup_file)
        
        # Get full path
        backup_path = os.path.join(current_app.config['BACKUP_DIR'], backup_file)
        
        # Upload to S3
        service = get_backup_service()
        s3_key = service.upload_to_s3(backup_path)
        
        response: BackupResponse = {
            'success': True,
            'message': f'Backup {backup_file} uploaded to S3 successfully',
            'data': {
                's3_key': s3_key
            }
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to upload to S3: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@backup_api.route('/scheduled', methods=['POST'])
@jwt_required()
def schedule_backup() -> Tuple[Dict[str, Any], int]:
    """Schedule a backup job"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'data': None
            }), HTTPStatus.BAD_REQUEST
        
        db_type = data.get('db_type')
        db_name = data.get('db_name')
        frequency = data.get('frequency')
        upload_to_s3 = data.get('upload_to_s3', False)
        
        # Validate inputs
        if not db_type or not db_name or not frequency:
            return jsonify({
                'success': False,
                'message': 'Database type, name, and frequency are required',
                'data': None
            }), HTTPStatus.BAD_REQUEST
        
        # Validate db_type
        if db_type not in [BackupType.MYSQL, BackupType.POSTGRES]:
            return jsonify({
                'success': False,
                'message': f'Invalid database type: {db_type}',
                'data': None
            }), HTTPStatus.BAD_REQUEST
        
        # Validate frequency
        try:
            frequency_enum = BackupFrequency(frequency)
        except ValueError:
            return jsonify({
                'success': False,
                'message': f'Invalid frequency: {frequency}',
                'data': None
            }), HTTPStatus.BAD_REQUEST
        
        # Schedule backup
        service = get_backup_service()
        job_id, job_info = service.schedule_backup(db_type, db_name, frequency_enum, upload_to_s3)
        
        response: BackupResponse = {
            'success': True,
            'message': f'{frequency} backup scheduled for {db_name}',
            'data': {
                'job_id': job_id,
                'job_info': job_info
            }
        }
        
        return jsonify(response), HTTPStatus.CREATED
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to schedule backup: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@backup_api.route('/scheduled/<job_id>', methods=['DELETE'])
@jwt_required()
def cancel_scheduled_backup(job_id: str) -> Tuple[Dict[str, Any], int]:
    """Cancel a scheduled backup job"""
    try:
        service = get_backup_service()
        name = service.cancel_scheduled_backup(job_id)
        
        response: BackupResponse = {
            'success': True,
            'message': f'Scheduled backup for {name} cancelled successfully',
            'data': None
        }
        
        return jsonify(response), HTTPStatus.OK
    
    except ValueError as e:
        response = {
            'success': False,
            'message': str(e),
            'data': None
        }
        return jsonify(response), HTTPStatus.NOT_FOUND
    
    except Exception as e:
        response = {
            'success': False,
            'message': f'Failed to cancel scheduled backup: {str(e)}',
            'data': None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR 