from typing import TypedDict, Optional, List, Dict, Any

class SystemInfo(TypedDict):
    """Type definition for system information"""
    os: str
    hostname: str
    cpu_cores: int
    memory_gb: float
    cloud_provider: Optional[str]
    region: Optional[str]
    ipv4: Optional[str]
    ipv6: Optional[str]


class SystemUsage(TypedDict):
    """Type definition for system usage metrics"""
    cpu_percent: float
    memory_percent: float
    memory_used: float
    memory_total: float
    disk_percent: float
    disk_used: float
    disk_total: float
    load_avg: List[float]


class NetworkStats(TypedDict):
    """Type definition for network traffic statistics"""
    upload_speed: float  # MB/s
    download_speed: float  # MB/s
    total_sent: float  # GB
    total_received: float  # GB


class DiskIO(TypedDict):
    """Type definition for disk I/O statistics"""
    read_speed: float  # MB/s
    write_speed: float  # MB/s
    total_read: float  # GB
    total_written: float  # GB


class TimezoneInfo(TypedDict):
    """Type definition for timezone information"""
    timezone: str
    current_time: str


class FirewallRule(TypedDict):
    """Type definition for firewall rule"""
    id: str
    type: str  # TCP, UDP, etc.
    port_range: str
    ip_version: str  # IPv4, IPv6
    source: str


class SystemPageProps(TypedDict):
    """Type definition for system dashboard page props"""
    system_info: SystemInfo
    system_usage: SystemUsage
    network_stats: NetworkStats
    disk_io: DiskIO
    timezone_info: TimezoneInfo
    firewall_rules: List[FirewallRule] 