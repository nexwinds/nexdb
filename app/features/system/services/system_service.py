import os
import platform
import socket
import psutil
import logging
import re
import json
import time
import urllib.request
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from flask import current_app
from functools import lru_cache

from app.features.system.types import SystemInfo, SystemUsage
from app.features.system.types.system_types import (
    NetworkStats, 
    DiskIOStats,
    TimezoneInfo,
    ProcessInfo
)

logger = logging.getLogger(__name__)

class SystemService:
    """Service for collecting system information and metrics"""
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get all data needed for the system dashboard
        
        Returns:
            Dict containing system_info, system_usage, processes, and timestamp
        """
        try:
            return {
                'system_info': self.get_system_info(),
                'system_usage': self.get_system_usage(),
                'disk_usage': self.get_disk_usage(),
                'network_stats': self.get_network_stats(),
                'processes': self.get_processes(limit=10),
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error collecting dashboard data: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def get_system_info(self) -> Dict[str, str]:
        """
        Get basic system information
        
        Returns:
            Dict with system information details
        """
        try:
            uname = platform.uname()
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            
            return {
                'os': f"{uname.system} {uname.release}",
                'hostname': uname.node,
                'kernel': uname.version,
                'arch': uname.machine,
                'processor': uname.processor,
                'python_version': platform.python_version(),
                'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
                'uptime': str(uptime).split('.')[0],  # Remove microseconds
            }
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {'error': str(e)}
    
    def get_system_usage(self) -> Dict[str, Any]:
        """
        Get CPU, memory and swap usage information
        
        Returns:
            Dict with CPU and memory usage metrics
        """
        try:
            # Get CPU info
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            
            # Get memory info
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'per_cpu': psutil.cpu_percent(interval=0.5, percpu=True),
                    'count': cpu_count,
                    'freq_current': cpu_freq.current if cpu_freq else None,
                    'freq_max': cpu_freq.max if cpu_freq else None,
                },
                'memory': {
                    'total': self._format_bytes(memory.total),
                    'used': self._format_bytes(memory.used),
                    'free': self._format_bytes(memory.free),
                    'percent': memory.percent,
                    'total_bytes': memory.total,
                    'used_bytes': memory.used,
                },
                'swap': {
                    'total': self._format_bytes(swap.total),
                    'used': self._format_bytes(swap.used),
                    'free': self._format_bytes(swap.free),
                    'percent': swap.percent,
                    'total_bytes': swap.total,
                    'used_bytes': swap.used,
                }
            }
        except Exception as e:
            logger.error(f"Error getting system usage: {str(e)}")
            return {'error': str(e)}
    
    def get_disk_usage(self) -> List[Dict[str, Any]]:
        """
        Get disk usage for all partitions
        
        Returns:
            List of dictionaries with disk usage metrics
        """
        try:
            disks = []
            for partition in psutil.disk_partitions(all=False):
                if os.name == 'nt' and ('cdrom' in partition.opts or partition.fstype == ''):
                    # Skip CD-ROM drives on Windows
                    continue
                    
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': self._format_bytes(usage.total),
                        'used': self._format_bytes(usage.used),
                        'free': self._format_bytes(usage.free),
                        'percent': usage.percent,
                        'total_bytes': usage.total,
                        'used_bytes': usage.used,
                    })
                except PermissionError:
                    # This can happen if the disk isn't ready
                    continue
            
            return disks
        except Exception as e:
            logger.error(f"Error getting disk usage: {str(e)}")
            return [{'error': str(e)}]
    
    def get_network_stats(self) -> Dict[str, Any]:
        """
        Get network statistics
        
        Returns:
            Dict with network interface statistics
        """
        try:
            # Get network IO counters
            net_io = psutil.net_io_counters(pernic=True)
            
            # Get network interfaces
            net_if = psutil.net_if_addrs()
            
            # Get network connections
            net_connections = {
                'total': len(psutil.net_connections()),
                'established': len([conn for conn in psutil.net_connections() 
                                  if conn.status == 'ESTABLISHED']),
                'listening': len([conn for conn in psutil.net_connections()
                                if conn.status == 'LISTEN']),
                'time_wait': len([conn for conn in psutil.net_connections()
                                if conn.status == 'TIME_WAIT']),
            }
            
            network_stats = {
                'interfaces': {},
                'connections': net_connections
            }
            
            for interface, stats in net_io.items():
                if interface in net_if:
                    addresses = []
                    for addr in net_if[interface]:
                        if addr.family == psutil.AF_LINK:
                            mac = addr.address
                        elif addr.family == socket.AF_INET:
                            addresses.append({
                                'addr': addr.address,
                                'netmask': addr.netmask,
                                'broadcast': addr.broadcast,
                                'family': 'IPv4'
                            })
                        elif addr.family == socket.AF_INET6:
                            addresses.append({
                                'addr': addr.address,
                                'netmask': addr.netmask,
                                'family': 'IPv6'
                            })
                    
                    network_stats['interfaces'][interface] = {
                        'bytes_sent': stats.bytes_sent,
                        'bytes_recv': stats.bytes_recv,
                        'packets_sent': stats.packets_sent,
                        'packets_recv': stats.packets_recv,
                        'errin': stats.errin,
                        'errout': stats.errout,
                        'dropin': stats.dropin,
                        'dropout': stats.dropout,
                        'bytes_sent_formatted': self._format_bytes(stats.bytes_sent),
                        'bytes_recv_formatted': self._format_bytes(stats.bytes_recv),
                        'addresses': addresses,
                        'mac': mac if 'mac' in locals() else None
                    }
            
            return network_stats
        except Exception as e:
            logger.error(f"Error getting network stats: {str(e)}")
            return {'error': str(e)}
    
    def get_processes(self, sort_by: str = 'memory', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get information about running processes
        
        Args:
            sort_by: Field to sort by ('memory', 'cpu', 'pid', 'name')
            limit: Maximum number of processes to return
            
        Returns:
            List of dictionaries with process information
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 
                                           'memory_percent', 'create_time', 'status']):
                try:
                    # Get process info and convert to dictionary
                    proc_info = proc.info
                    
                    # Add formatted memory usage
                    try:
                        memory_info = proc.memory_info()
                        proc_info['memory_info'] = {
                            'rss': self._format_bytes(memory_info.rss),
                            'rss_bytes': memory_info.rss,
                            'vms': self._format_bytes(memory_info.vms),
                            'vms_bytes': memory_info.vms
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_info['memory_info'] = {'rss': 'N/A', 'vms': 'N/A'}
                    
                    # Add formatted create time
                    try:
                        create_time = datetime.datetime.fromtimestamp(proc_info['create_time'])
                        proc_info['created'] = create_time.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        proc_info['created'] = 'N/A'
                    
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort processes
            if sort_by == 'memory':
                processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
            elif sort_by == 'cpu':
                processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            elif sort_by == 'pid':
                processes.sort(key=lambda x: x.get('pid', 0))
            elif sort_by == 'name':
                processes.sort(key=lambda x: x.get('name', '').lower())
            
            # Limit the number of processes
            return processes[:limit]
        except Exception as e:
            logger.error(f"Error getting process information: {str(e)}")
            return [{'error': str(e)}]
    
    def _format_bytes(self, bytes_value: int) -> str:
        """
        Format bytes to human-readable string
        
        Args:
            bytes_value: Size in bytes
            
        Returns:
            Formatted string with appropriate unit
        """
        if bytes_value is None:
            return "N/A"
            
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if bytes_value < 1024.0 or unit == 'PB':
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0


# Singleton instance
_system_service_instance = None

@lru_cache(maxsize=1)
def get_system_service() -> SystemService:
    """Factory function to get system service instance"""
    global _system_service_instance
    if _system_service_instance is None:
        _system_service_instance = SystemService()
    return _system_service_instance 