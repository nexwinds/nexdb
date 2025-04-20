import subprocess
import socket
import shutil
import logging
import platform
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ServiceInfo:
    """Service information class"""
    name: str
    status: str
    display_name: str
    description: str
    port: Optional[int] = None

class ServiceManager:
    """Service manager for handling database and system services"""
    
    def __init__(self):
        self._os_type = platform.system().lower()
        self._is_windows = self._os_type == 'windows'
        self._is_linux = self._os_type == 'linux'
        self._is_mac = self._os_type == 'darwin'
    
    def get_all_services(self) -> List[ServiceInfo]:
        """
        Get a list of all managed services with their status
        
        Returns:
            List of ServiceInfo objects
        """
        services = []
        
        # Database services
        services.append(self.get_service_info('mysql'))
        services.append(self.get_service_info('postgresql'))
        
        # Web server
        if self._is_linux:
            services.append(self.get_service_info('nginx'))
            services.append(self.get_service_info('apache2'))
        elif self._is_windows:
            services.append(self.get_service_info('nginx'))
            services.append(self.get_service_info('Apache2.4'))
        
        # Filter out None values (services that don't exist)
        return [s for s in services if s is not None]
    
    def get_service_info(self, service_name: str) -> Optional[ServiceInfo]:
        """
        Get information about a specific service
        
        Args:
            service_name: Name of the service
            
        Returns:
            ServiceInfo object if service exists, None otherwise
        """
        display_name_map = {
            'mysql': 'MySQL Database',
            'postgresql': 'PostgreSQL Database',
            'nginx': 'Nginx Web Server',
            'apache2': 'Apache Web Server',
            'Apache2.4': 'Apache Web Server'
        }
        
        description_map = {
            'mysql': 'MySQL open source relational database',
            'postgresql': 'PostgreSQL open source relational database',
            'nginx': 'Nginx web server and reverse proxy',
            'apache2': 'Apache HTTP server',
            'Apache2.4': 'Apache HTTP server'
        }
        
        port_map = {
            'mysql': 3306,
            'postgresql': 5432,
            'nginx': 80,
            'apache2': 80,
            'Apache2.4': 80
        }
        
        # Check if service exists
        if not self._service_exists(service_name):
            return None
        
        # Get status
        status = self._get_service_status(service_name)
        
        # Create and return ServiceInfo
        return ServiceInfo(
            name=service_name,
            status=status,
            display_name=display_name_map.get(service_name, service_name),
            description=description_map.get(service_name, ''),
            port=port_map.get(service_name)
        )
    
    def start_service(self, service_name: str) -> bool:
        """
        Start a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self._is_linux:
                subprocess.run(['sudo', 'systemctl', 'start', service_name], 
                             check=True, capture_output=True)
            elif self._is_windows:
                subprocess.run(['net', 'start', service_name], 
                             check=True, capture_output=True, shell=True)
            elif self._is_mac:
                if service_name == 'mysql':
                    subprocess.run(['brew', 'services', 'start', 'mysql'], 
                                 check=True, capture_output=True)
                elif service_name == 'postgresql':
                    subprocess.run(['brew', 'services', 'start', 'postgresql'], 
                                 check=True, capture_output=True)
            
            logger.info(f"Started service: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error starting service {service_name}: {str(e)}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """
        Stop a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self._is_linux:
                subprocess.run(['sudo', 'systemctl', 'stop', service_name], 
                             check=True, capture_output=True)
            elif self._is_windows:
                subprocess.run(['net', 'stop', service_name], 
                             check=True, capture_output=True, shell=True)
            elif self._is_mac:
                if service_name == 'mysql':
                    subprocess.run(['brew', 'services', 'stop', 'mysql'], 
                                 check=True, capture_output=True)
                elif service_name == 'postgresql':
                    subprocess.run(['brew', 'services', 'stop', 'postgresql'], 
                                 check=True, capture_output=True)
            
            logger.info(f"Stopped service: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error stopping service {service_name}: {str(e)}")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """
        Restart a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self._is_linux:
                subprocess.run(['sudo', 'systemctl', 'restart', service_name], 
                             check=True, capture_output=True)
            elif self._is_windows:
                subprocess.run(['net', 'stop', service_name], 
                             check=True, capture_output=True, shell=True)
                subprocess.run(['net', 'start', service_name], 
                             check=True, capture_output=True, shell=True)
            elif self._is_mac:
                if service_name == 'mysql':
                    subprocess.run(['brew', 'services', 'restart', 'mysql'], 
                                 check=True, capture_output=True)
                elif service_name == 'postgresql':
                    subprocess.run(['brew', 'services', 'restart', 'postgresql'], 
                                 check=True, capture_output=True)
            
            logger.info(f"Restarted service: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error restarting service {service_name}: {str(e)}")
            return False
    
    def reload_web_server(self) -> bool:
        """
        Reload web server configuration
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self._is_linux:
                # Check which web server is running
                if self._get_service_status('nginx') == 'running':
                    subprocess.run(['sudo', 'systemctl', 'reload', 'nginx'], 
                                 check=True, capture_output=True)
                elif self._get_service_status('apache2') == 'running':
                    subprocess.run(['sudo', 'systemctl', 'reload', 'apache2'], 
                                 check=True, capture_output=True)
            elif self._is_windows:
                # Check which web server is running
                if self._get_service_status('nginx') == 'running':
                    self.restart_service('nginx')
                elif self._get_service_status('Apache2.4') == 'running':
                    self.restart_service('Apache2.4')
            
            logger.info("Reloaded web server")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error reloading web server: {str(e)}")
            return False
    
    def _service_exists(self, service_name: str) -> bool:
        """
        Check if a service exists on the system
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if service exists, False otherwise
        """
        try:
            # For Linux, check if service file exists
            if self._is_linux:
                result = subprocess.run(['systemctl', 'list-unit-files', f'{service_name}.service'],
                                      capture_output=True, text=True)
                return service_name in result.stdout
            
            # For Windows, check if service is registered
            elif self._is_windows:
                result = subprocess.run(['sc', 'query', service_name],
                                      capture_output=True, text=True, shell=True)
                return 'FAILED 1060' not in result.stderr
            
            # For Mac, check using homebrew or executable presence
            elif self._is_mac:
                if service_name == 'mysql':
                    return shutil.which('mysql') is not None
                elif service_name == 'postgresql':
                    return shutil.which('psql') is not None
            
            return False
        except Exception as e:
            logger.error(f"Error checking if service {service_name} exists: {str(e)}")
            return False
    
    def _get_service_status(self, service_name: str) -> str:
        """
        Get the status of a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            Status string ('running', 'stopped', 'unknown')
        """
        try:
            # For Linux, use systemctl
            if self._is_linux:
                result = subprocess.run(['systemctl', 'is-active', service_name],
                                      capture_output=True, text=True)
                return 'running' if result.stdout.strip() == 'active' else 'stopped'
            
            # For Windows, use sc query
            elif self._is_windows:
                result = subprocess.run(['sc', 'query', service_name],
                                      capture_output=True, text=True, shell=True)
                return 'running' if 'RUNNING' in result.stdout else 'stopped'
            
            # For Mac, check port for common services
            elif self._is_mac:
                if service_name == 'mysql':
                    return 'running' if self._check_port_open(3306) else 'stopped'
                elif service_name == 'postgresql':
                    return 'running' if self._check_port_open(5432) else 'stopped'
            
            return 'unknown'
        except Exception as e:
            logger.error(f"Error getting status for service {service_name}: {str(e)}")
            return 'unknown'
    
    def _check_port_open(self, port: int) -> bool:
        """
        Check if a port is open (indicating a service is running)
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is open, False otherwise
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0


# Singleton instance
_service_manager = None

def get_service_manager() -> ServiceManager:
    """Get the service manager instance"""
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager()
    return _service_manager 