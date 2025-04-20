import subprocess
import os
import logging
import pymysql
from typing import List, Dict, Any, Optional, Tuple
from flask import current_app
from werkzeug.utils import secure_filename

from app.features.database.types import DatabaseError


class MySQLService:
    """Service for managing MySQL databases"""
    
    def __init__(self):
        """Initialize the MySQL service with config from the app"""
        self.host = current_app.config.get('MYSQL_HOST', 'localhost')
        self.port = current_app.config.get('MYSQL_PORT', 3306)
        self.user = current_app.config.get('MYSQL_USER', 'root')
        self.password = current_app.config.get('MYSQL_PASSWORD', '')
    
    def get_connection(self, database: str = '') -> pymysql.connections.Connection:
        """Get a MySQL connection"""
        try:
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=database if database else None
            )
            return conn
        except Exception as e:
            logging.error(f"MySQL connection error: {str(e)}")
            raise DatabaseError(f"Failed to connect to MySQL: {str(e)}")
    
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
        """Check if MySQL is running"""
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
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall() 
                        if row[0] not in ('information_schema', 'performance_schema', 'mysql', 'sys')]
            cursor.close()
            conn.close()
            return databases
        except Exception as e:
            logging.error(f"Error listing MySQL databases: {str(e)}")
            return []
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all MySQL users"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT User, Host FROM mysql.user")
            users = [{'user': row[0], 'host': row[1]} for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return users
        except Exception as e:
            logging.error(f"Error listing MySQL users: {str(e)}")
            return []
    
    def create_database(self, db_name: str) -> bool:
        """Create a new database"""
        try:
            # Sanitize db_name to prevent SQL injection
            db_name = db_name.replace('`', '').replace('\\', '').replace('/', '')
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error creating MySQL database: {str(e)}")
            raise DatabaseError(f"Failed to create database: {str(e)}")
    
    def delete_database(self, db_name: str) -> bool:
        """Delete a database"""
        try:
            # Sanitize db_name to prevent SQL injection
            db_name = db_name.replace('`', '').replace('\\', '').replace('/', '')
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error deleting MySQL database: {str(e)}")
            raise DatabaseError(f"Failed to delete database: {str(e)}")
    
    def create_user(self, username: str, password: str, host: str = '%') -> bool:
        """Create a new user"""
        try:
            # Sanitize inputs
            username = username.replace('`', '').replace('\\', '').replace('/', '')
            host = host.replace('`', '').replace('\\', '').replace('/', '')
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if MySQL 8.0+ (different user creation syntax)
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
            if int(version.split('.')[0]) >= 8:
                cursor.execute(f"CREATE USER IF NOT EXISTS '{username}'@'{host}' IDENTIFIED BY %s", (password,))
            else:
                cursor.execute(f"CREATE USER IF NOT EXISTS '{username}'@'{host}' IDENTIFIED BY PASSWORD(%s)", (password,))
                
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error creating MySQL user: {str(e)}")
            raise DatabaseError(f"Failed to create user: {str(e)}")
    
    def grant_privileges(self, username: str, db_name: str, host: str = '%') -> bool:
        """Grant privileges to a user on a database"""
        try:
            # Sanitize inputs
            username = username.replace('`', '').replace('\\', '').replace('/', '')
            db_name = db_name.replace('`', '').replace('\\', '').replace('/', '')
            host = host.replace('`', '').replace('\\', '').replace('/', '')
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{username}'@'{host}'")
            cursor.execute("FLUSH PRIVILEGES")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error granting MySQL privileges: {str(e)}")
            raise DatabaseError(f"Failed to grant privileges: {str(e)}")
    
    def delete_user(self, username: str, host: str = '%') -> bool:
        """Delete a user"""
        try:
            # Sanitize inputs
            username = username.replace('`', '').replace('\\', '').replace('/', '')
            host = host.replace('`', '').replace('\\', '').replace('/', '')
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"DROP USER IF EXISTS '{username}'@'{host}'")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error deleting MySQL user: {str(e)}")
            raise DatabaseError(f"Failed to delete user: {str(e)}")
    
    def change_password(self, username: str, new_password: str, host: str = '%') -> bool:
        """Change user password"""
        try:
            # Sanitize inputs
            username = username.replace('`', '').replace('\\', '').replace('/', '')
            host = host.replace('`', '').replace('\\', '').replace('/', '')
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if MySQL 8.0+ (different password change syntax)
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
            if int(version.split('.')[0]) >= 8:
                cursor.execute(f"ALTER USER '{username}'@'{host}' IDENTIFIED BY %s", (new_password,))
            else:
                cursor.execute(f"SET PASSWORD FOR '{username}'@'{host}' = PASSWORD(%s)", (new_password,))
                
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error changing MySQL password: {str(e)}")
            raise DatabaseError(f"Failed to change password: {str(e)}")
    
    def backup_database(self, db_name: str, backup_path: Optional[str] = None) -> str:
        """Backup a database to a file"""
        try:
            # Check if mysqldump is available
            if not self.check_binary_exists('mysqldump'):
                raise DatabaseError("mysqldump binary not found. Please install MySQL client tools.")
            
            # Sanitize db_name
            db_name = secure_filename(db_name)
            
            # Generate backup path if not provided
            if backup_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{db_name}_{timestamp}.sql"
                backup_path = os.path.join(current_app.config['BACKUP_DIR'], filename)
            
            # Build command with proper escaping
            cmd = [
                'mysqldump',
                f'--host={self.host}',
                f'--port={str(self.port)}',
                f'--user={self.user}',
                '--add-drop-database',
                '--databases',
                db_name
            ]
            
            # Use environment for password to avoid it showing in process list
            env = os.environ.copy()
            env['MYSQL_PWD'] = self.password
            
            # Run the backup command
            with open(backup_path, 'wb') as f:
                process = subprocess.run(
                    cmd,
                    stdout=f,
                    env=env,
                    check=True
                )
            
            return backup_path
        except subprocess.SubprocessError as e:
            logging.error(f"Error executing mysqldump: {str(e)}")
            raise DatabaseError(f"Backup failed: {str(e)}")
        except Exception as e:
            logging.error(f"Error backing up MySQL database: {str(e)}")
            raise DatabaseError(f"Backup failed: {str(e)}")
    
    def restore_database(self, backup_path: str, db_name: Optional[str] = None) -> bool:
        """Restore a database from a backup file"""
        try:
            # Check if mysql client is available
            if not self.check_binary_exists('mysql'):
                raise DatabaseError("mysql binary not found. Please install MySQL client tools.")
            
            # Ensure the backup file exists
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Build command
            cmd = [
                'mysql',
                f'--host={self.host}',
                f'--port={str(self.port)}',
                f'--user={self.user}'
            ]
            
            # Add database name if specified
            if db_name:
                # First ensure database exists
                self.create_database(db_name)
                cmd.append(db_name)
            
            # Use environment for password to avoid it showing in process list
            env = os.environ.copy()
            env['MYSQL_PWD'] = self.password
            
            # Run the restore command
            with open(backup_path, 'rb') as f:
                process = subprocess.run(
                    cmd,
                    stdin=f,
                    env=env,
                    check=True
                )
            
            return True
        except subprocess.SubprocessError as e:
            logging.error(f"Error executing mysql: {str(e)}")
            raise DatabaseError(f"Restore failed: {str(e)}")
        except Exception as e:
            logging.error(f"Error restoring MySQL database: {str(e)}")
            raise DatabaseError(f"Restore failed: {str(e)}") 