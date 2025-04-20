"""
Database utilities for NEXDB.
Contains helper functions for database operations.
"""
from flask import current_app
from app.utils.mysql_manager import MySQLManager
from app.utils.postgres_manager import PostgresManager

def get_mysql_manager():
    """
    Get a configured MySQL manager instance.
    
    Returns:
        MySQLManager: An initialized MySQL manager
    """
    return MySQLManager(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )

def get_postgres_manager():
    """
    Get a configured PostgreSQL manager instance.
    
    Returns:
        PostgresManager: An initialized PostgreSQL manager
    """
    return PostgresManager(
        host=current_app.config['POSTGRES_HOST'],
        port=current_app.config['POSTGRES_PORT'],
        user=current_app.config['POSTGRES_USER'],
        password=current_app.config['POSTGRES_PASSWORD']
    )

def format_db_size(size_bytes):
    """
    Format database size in bytes to human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string (e.g. '1.2 MB')
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB" 