import psycopg2
import subprocess
import os
import logging

class PostgresManager:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        
    def get_connection(self, database="postgres"):
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
            raise
    
    def get_status(self):
        """Check if PostgreSQL is running"""
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
            cursor = conn.cursor()
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres'")
            databases = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return databases
        except Exception as e:
            logging.error(f"Error listing PostgreSQL databases: {str(e)}")
            return []
    
    def list_users(self):
        """List all users"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT rolname FROM pg_roles WHERE rolcanlogin = true")
            users = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return users
        except Exception as e:
            logging.error(f"Error listing PostgreSQL users: {str(e)}")
            return []
    
    def create_database(self, db_name):
        """Create a new database"""
        try:
            conn = self.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE {db_name}")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error creating PostgreSQL database: {str(e)}")
            return False
    
    def delete_database(self, db_name):
        """Delete a database"""
        try:
            conn = self.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"DROP DATABASE {db_name}")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error deleting PostgreSQL database: {str(e)}")
            return False
    
    def create_user(self, username, password):
        """Create a new user"""
        try:
            conn = self.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"CREATE USER {username} WITH PASSWORD '{password}'")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error creating PostgreSQL user: {str(e)}")
            return False
    
    def grant_privileges(self, username, db_name):
        """Grant privileges to a user on a database"""
        try:
            conn = self.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {username}")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error granting PostgreSQL privileges: {str(e)}")
            return False
    
    def delete_user(self, username):
        """Delete a user"""
        try:
            conn = self.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"DROP USER {username}")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error deleting PostgreSQL user: {str(e)}")
            return False
    
    def change_password(self, username, new_password):
        """Change user password"""
        try:
            conn = self.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"ALTER USER {username} WITH PASSWORD '{new_password}'")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error changing PostgreSQL password: {str(e)}")
            return False
    
    def backup_database(self, db_name, backup_path):
        """Backup a database to a file"""
        try:
            # Set environment variables for pg_dump
            env = os.environ.copy()
            env['PGPASSWORD'] = self.password
            
            cmd = [
                'pg_dump',
                f'--host={self.host}',
                f'--port={self.port}',
                f'--username={self.user}',
                '--format=custom',
                f'--file={backup_path}',
                db_name
            ]
            
            subprocess.run(cmd, env=env, check=True)
            return True
        except Exception as e:
            logging.error(f"Error backing up PostgreSQL database: {str(e)}")
            return False
    
    def restore_database(self, db_name, backup_path):
        """Restore a database from a backup file"""
        try:
            # Set environment variables for pg_restore
            env = os.environ.copy()
            env['PGPASSWORD'] = self.password
            
            # First, make sure database exists
            self.create_database(db_name)
            
            cmd = [
                'pg_restore',
                f'--host={self.host}',
                f'--port={self.port}',
                f'--username={self.user}',
                '--dbname=' + db_name,
                '--clean',
                backup_path
            ]
            
            subprocess.run(cmd, env=env, check=True)
            return True
        except Exception as e:
            logging.error(f"Error restoring PostgreSQL database: {str(e)}")
            return False 