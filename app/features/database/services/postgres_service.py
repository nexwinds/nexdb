import subprocess
import os
import logging
import psycopg2
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

from app.features.database.types import DatabaseError


class PostgresService:
    """Service for managing PostgreSQL databases"""
    
    def __init__(self):
        """Initialize the PostgreSQL service with config from the app"""
        self.host = current_app.config.get('POSTGRES_HOST', 'localhost')
        self.port = current_app.config.get('POSTGRES_PORT', 5432)
        self.user = current_app.config.get('POSTGRES_USER', 'postgres')
        self.password = current_app.config.get('POSTGRES_PASSWORD', '')
    
    def get_connection(self, database: str = "postgres") -> psycopg2.extensions.connection:
        """Get a PostgreSQL connection"""
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=database
            )
            return conn
        except Exception as e:
            logging.error(f"PostgreSQL connection error: {str(e)}")
            raise DatabaseError(f"Failed to connect to PostgreSQL: {str(e)}")
    
    def check_binary_exists(self, binary: str) -> bool:
        """Check if a binary exists in PATH"""
        try:
            subprocess.run(['which', binary], 
                           check=True, 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
            return True
        except subprocess.SubprocessError:
            return False
    
    def get_status(self) -> bool:
        """Check if PostgreSQL is running"""
        try:
            conn = self.get_connection()
            conn.close()
            return True
        except:
            return False
    
    def list_databases(self) -> List[str]:
        """List all databases"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres'")
            databases = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return databases
        except Exception as e:
            logging.error(f"Error listing PostgreSQL databases: {str(e)}")
            return []
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT rolname FROM pg_roles WHERE rolcanlogin = true")
            users = [{'user': row[0], 'host': None} for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return users
        except Exception as e:
            logging.error(f"Error listing PostgreSQL users: {str(e)}")
            return []
    
    def create_database(self, db_name: str) -> bool:
        """Create a new database"""
        try:
            # Sanitize db_name to prevent SQL injection
            db_name = db_name.replace('"', '').replace('\\', '').replace('/', '')
            
            conn = self.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error creating PostgreSQL database: {str(e)}")
            raise DatabaseError(f"Failed to create database: {str(e)}")
    
    def delete_database(self, db_name: str) -> bool:
        """Delete a database"""
        try:
            # Sanitize db_name to prevent SQL injection
            db_name = db_name.replace('"', '').replace('\\', '').replace('/', '')
            
            conn = self.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error deleting PostgreSQL database: {str(e)}")
            raise DatabaseError(f"Failed to delete database: {str(e)}")
    
    def create_user(self, username: str, password: str) -> bool:
        """Create a new user"""
        try:
            # Sanitize username to prevent SQL injection
            username = username.replace('"', '').replace('\\', '').replace('/', '')
            
            conn = self.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f'CREATE USER "{username}" WITH PASSWORD %s', (password,))
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error creating PostgreSQL user: {str(e)}")
            raise DatabaseError(f"Failed to create user: {str(e)}")
    
    def grant_privileges(self, username: str, db_name: str) -> bool:
        """Grant privileges to a user on a database"""
        try:
            # Sanitize inputs to prevent SQL injection
            username = username.replace('"', '').replace('\\', '').replace('/', '')
            db_name = db_name.replace('"', '').replace('\\', '').replace('/', '')
            
            conn = self.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f'GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO "{username}"')
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error granting PostgreSQL privileges: {str(e)}")
            raise DatabaseError(f"Failed to grant privileges: {str(e)}")
    
    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        try:
            # Sanitize username to prevent SQL injection
            username = username.replace('"', '').replace('\\', '').replace('/', '')
            
            conn = self.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f'DROP USER IF EXISTS "{username}"')
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error deleting PostgreSQL user: {str(e)}")
            raise DatabaseError(f"Failed to delete user: {str(e)}")
    
    def change_password(self, username: str, new_password: str) -> bool:
        """Change user password"""
        try:
            # Sanitize username to prevent SQL injection
            username = username.replace('"', '').replace('\\', '').replace('/', '')
            
            conn = self.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f'ALTER USER "{username}" WITH PASSWORD %s', (new_password,))
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error changing PostgreSQL password: {str(e)}")
            raise DatabaseError(f"Failed to change password: {str(e)}")
    
    def backup_database(self, db_name: str, backup_path: Optional[str] = None) -> str:
        """Backup a database to a file"""
        try:
            # Check if pg_dump is available
            if not self.check_binary_exists('pg_dump'):
                raise DatabaseError("pg_dump binary not found. Please install PostgreSQL client tools.")
            
            # Sanitize db_name
            db_name = secure_filename(db_name)
            
            # Generate backup path if not provided
            if backup_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{db_name}_{timestamp}.dump"
                backup_path = os.path.join(current_app.config['BACKUP_DIR'], filename)
            
            # Set environment variables for pg_dump
            env = os.environ.copy()
            env['PGPASSWORD'] = self.password
            
            # Build command with proper escaping
            cmd = [
                'pg_dump',
                f'--host={self.host}',
                f'--port={str(self.port)}',
                f'--username={self.user}',
                '--format=custom',
                f'--file={backup_path}',
                db_name
            ]
            
            # Run the backup command
            process = subprocess.run(
                cmd,
                env=env,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return backup_path
        except subprocess.SubprocessError as e:
            logging.error(f"Error executing pg_dump: {str(e)}")
            raise DatabaseError(f"Backup failed: {str(e)}")
        except Exception as e:
            logging.error(f"Error backing up PostgreSQL database: {str(e)}")
            raise DatabaseError(f"Backup failed: {str(e)}")
    
    def restore_database(self, backup_path: str, db_name: str) -> bool:
        """Restore a database from a backup file"""
        try:
            # Check if pg_restore is available
            if not self.check_binary_exists('pg_restore'):
                raise DatabaseError("pg_restore binary not found. Please install PostgreSQL client tools.")
            
            # Ensure the backup file exists
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Sanitize db_name
            db_name = secure_filename(db_name)
            
            # Make sure database exists
            self.create_database(db_name)
            
            # Set environment variables for pg_restore
            env = os.environ.copy()
            env['PGPASSWORD'] = self.password
            
            # Build command
            cmd = [
                'pg_restore',
                f'--host={self.host}',
                f'--port={str(self.port)}',
                f'--username={self.user}',
                '--dbname=' + db_name,
                '--clean',
                backup_path
            ]
            
            # Run the restore command
            process = subprocess.run(
                cmd,
                env=env,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return True
        except subprocess.SubprocessError as e:
            logging.error(f"Error executing pg_restore: {str(e)}")
            raise DatabaseError(f"Restore failed: {str(e)}")
        except Exception as e:
            logging.error(f"Error restoring PostgreSQL database: {str(e)}")
            raise DatabaseError(f"Restore failed: {str(e)}") 