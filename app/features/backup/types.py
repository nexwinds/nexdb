from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, TypedDict, Union, Literal, Any


class BackupFrequency(str, Enum):
    """Enum for backup frequency options"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


class BackupType(str, Enum):
    """Enum for database types"""
    MYSQL = "mysql"
    POSTGRES = "postgres"


class BackupFile(TypedDict):
    """Type definition for backup file information"""
    name: str
    size: float  # Size in MB
    date: datetime


class ScheduledBackup(TypedDict):
    """Type definition for scheduled backup job"""
    id: str
    name: str
    frequency: str
    db_type: str
    db_name: str
    upload_to_s3: bool
    last_run: Optional[datetime]


class BackupError(Exception):
    """Base exception for backup operations"""
    pass


class DatabaseBackupError(BackupError):
    """Exception for database backup failures"""
    pass


class S3BackupError(BackupError):
    """Exception for S3 backup operations"""
    pass


class BackupResponse(TypedDict):
    """Type definition for standardized backup API responses"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]]


class BackupPageProps(TypedDict):
    """Type definition for backup page props"""
    local_backups: List[BackupFile]
    s3_backups: List[BackupFile]
    mysql_dbs: List[str]
    postgres_dbs: List[str]
    scheduled_backups: List[ScheduledBackup]
    scheduler_status: bool
    aws_configured: bool 