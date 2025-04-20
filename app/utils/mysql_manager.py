import mysql.connector
import subprocess
import os
import logging

class MySQLManager:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        
    def get_connection(self, database=None):
        """Get a MySQL connection"""
        try:
            conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=database
            )
            return conn
        except Exception as e:
            logging.error(f"MySQL connection error: {str(e)}")
            raise
    
    def get_status(self):
        """Check if MySQL is running"""
        try:
            conn = self.get_connection()
            conn.close()
            return True
        except:
            return False
    
    def list_databases(self):
        """List all databases"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SHOW DATABASES")
            databases = [row['Database'] for row in cursor.fetchall() 
                        if row['Database'] not in ['information_schema', 'performance_schema', 'mysql', 'sys']]
            cursor.close()
            conn.close()
            return databases
        except Exception as e:
            logging.error(f"Error listing MySQL databases: {str(e)}")
            return []
    
    def list_users(self):
        """List all users"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT User, Host FROM mysql.user")
            users = [f"{row['User']}@{row['Host']}" for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return users
        except Exception as e:
            logging.error(f"Error listing MySQL users: {str(e)}")
            return []
    
    def create_database(self, db_name):
        """Create a new database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE `{db_name}`")
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error creating MySQL database: {str(e)}")
            return False
    
    def delete_database(self, db_name):
        """Delete a database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"DROP DATABASE `{db_name}`")
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error deleting MySQL database: {str(e)}")
            return False
    
    def create_user(self, username, password, host='%'):
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"CREATE USER '{username}'@'{host}' IDENTIFIED BY '{password}'")
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error creating MySQL user: {str(e)}")
            return False
    
    def grant_privileges(self, username, db_name, host='%'):
        """Grant privileges to a user on a database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{username}'@'{host}'")
            cursor.execute("FLUSH PRIVILEGES")
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error granting MySQL privileges: {str(e)}")
            return False
    
    def delete_user(self, username, host='%'):
        """Delete a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"DROP USER '{username}'@'{host}'")
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error deleting MySQL user: {str(e)}")
            return False
    
    def change_password(self, username, new_password, host='%'):
        """Change user password"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"ALTER USER '{username}'@'{host}' IDENTIFIED BY '{new_password}'")
            cursor.execute("FLUSH PRIVILEGES")
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error changing MySQL password: {str(e)}")
            return False
    
    def backup_database(self, db_name, backup_path):
        """Backup a database to a file"""
        try:
            cmd = [
                'mysqldump',
                f'--host={self.host}',
                f'--port={self.port}',
                f'--user={self.user}',
                f'--password={self.password}',
                '--add-drop-database',
                '--databases',
                db_name
            ]
            
            with open(backup_path, 'wb') as f:
                subprocess.run(cmd, stdout=f, check=True)
            
            return True
        except Exception as e:
            logging.error(f"Error backing up MySQL database: {str(e)}")
            return False
    
    def restore_database(self, backup_path):
        """Restore a database from a backup file"""
        try:
            cmd = [
                'mysql',
                f'--host={self.host}',
                f'--port={self.port}',
                f'--user={self.user}',
                f'--password={self.password}'
            ]
            
            with open(backup_path, 'rb') as f:
                subprocess.run(cmd, stdin=f, check=True)
            
            return True
        except Exception as e:
            logging.error(f"Error restoring MySQL database: {str(e)}")
            return False 