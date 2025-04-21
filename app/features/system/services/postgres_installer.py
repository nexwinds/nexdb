import subprocess
import logging
import os
import platform
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class PostgresInstaller:
    """Service for installing and configuring PostgreSQL"""
    
    def __init__(self):
        self._os_type = platform.system().lower()
        self._is_ubuntu = False
        
        # Check if we're on Ubuntu
        if self._os_type == 'linux':
            try:
                with open('/etc/os-release', 'r') as f:
                    content = f.read()
                    self._is_ubuntu = 'ubuntu' in content.lower()
            except Exception as e:
                logger.error(f"Error determining OS type: {str(e)}")
    
    def check_if_installed(self) -> bool:
        """Check if PostgreSQL is already installed"""
        try:
            # Check for PostgreSQL service
            if self._os_type == 'linux':
                result = subprocess.run(
                    ['systemctl', 'list-unit-files', 'postgresql*'],
                    capture_output=True, 
                    text=True
                )
                if 'postgresql' in result.stdout:
                    return True
                
                # Also check for postgres binary
                result = subprocess.run(
                    ['which', 'psql'], 
                    capture_output=True, 
                    text=True
                )
                return len(result.stdout.strip()) > 0
            else:
                # Not implemented for other OS
                return False
        except Exception as e:
            logger.error(f"Error checking PostgreSQL installation: {str(e)}")
            return False
    
    def install(self) -> Tuple[bool, str]:
        """
        Install PostgreSQL on Ubuntu
        
        Returns:
            Tuple[bool, str]: Success status and message
        """
        if not self._is_ubuntu:
            return False, "PostgreSQL installation is only supported on Ubuntu systems"
            
        if self.check_if_installed():
            return True, "PostgreSQL is already installed"
        
        try:
            # Update package lists
            update_cmd = ['apt-get', 'update']
            subprocess.run(update_cmd, check=True, capture_output=True)
            
            # Install PostgreSQL
            install_cmd = ['apt-get', 'install', '-y', 'postgresql', 'postgresql-contrib']
            subprocess.run(install_cmd, check=True, capture_output=True)
            
            # Ensure the service is started
            start_cmd = ['systemctl', 'start', 'postgresql']
            subprocess.run(start_cmd, check=True, capture_output=True)
            
            # Enable the service
            enable_cmd = ['systemctl', 'enable', 'postgresql']
            subprocess.run(enable_cmd, check=True, capture_output=True)
            
            # Set up a default password for postgres user
            password = self._generate_random_password()
            
            # Run commands as postgres user to set password
            set_pw_cmd = [
                'sudo', '-u', 'postgres', 'psql', '-c', 
                f"ALTER USER postgres WITH PASSWORD '{password}';"
            ]
            subprocess.run(set_pw_cmd, check=True, capture_output=True)
            
            return True, f"PostgreSQL installed successfully. Default username: postgres, password: {password}"
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to install PostgreSQL: {e.stderr.decode() if e.stderr else str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error during PostgreSQL installation: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _generate_random_password(self, length: int = 12) -> str:
        """Generate a random password"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def get_postgres_status(self) -> Dict[str, Any]:
        """
        Get detailed PostgreSQL status
        
        Returns:
            Dict with status information
        """
        status = {
            'installed': False,
            'running': False,
            'version': None,
            'message': ''
        }
        
        # First check if installed
        if not self.check_if_installed():
            status['message'] = 'PostgreSQL is not installed'
            return status
        
        status['installed'] = True
        
        try:
            # Check service status
            if self._os_type == 'linux':
                service_cmd = ['systemctl', 'is-active', 'postgresql']
                result = subprocess.run(service_cmd, capture_output=True, text=True)
                status['running'] = result.stdout.strip() == 'active'
            
            # Get version
            try:
                version_cmd = ['psql', '--version']
                result = subprocess.run(version_cmd, capture_output=True, text=True)
                version_output = result.stdout.strip()
                # Parse version from output like "psql (PostgreSQL) 12.9 (Ubuntu 12.9-0ubuntu0.20.04.1)"
                if version_output:
                    import re
                    match = re.search(r'(\d+\.\d+)', version_output)
                    if match:
                        status['version'] = match.group(1)
            except Exception as e:
                logger.warning(f"Could not determine PostgreSQL version: {str(e)}")
            
            status['message'] = 'PostgreSQL is installed and running' if status['running'] else 'PostgreSQL is installed but not running'
            
        except Exception as e:
            logger.error(f"Error getting PostgreSQL status: {str(e)}")
            status['message'] = f"Error checking PostgreSQL status: {str(e)}"
            
        return status


# Helper function to get an instance of the installer
def get_postgres_installer() -> PostgresInstaller:
    return PostgresInstaller() 