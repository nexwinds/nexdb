from typing import TypedDict, Optional, List

class SystemInfo(TypedDict):
    """System information type definition"""
    os: str
    hostname: str
    platform: str
    architecture: str
    python_version: str
    uptime: str

class SystemUsage(TypedDict):
    """System resource usage type definition"""
    cpu_percent: float
    memory_percent: float
    memory_used: str
    memory_total: str
    disk_percent: float
    disk_used: str
    disk_total: str

class NetworkStats(TypedDict):
    """Network statistics type definition"""
    bytes_sent: str
    bytes_recv: str
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int

class DiskIOStats(TypedDict):
    """Disk I/O statistics type definition"""
    read_count: int
    write_count: int
    read_bytes: str
    write_bytes: str

class TimezoneInfo(TypedDict):
    """Timezone information type definition"""
    timezone: str
    current_time: str

class ProcessInfo(TypedDict):
    """Process information type definition"""
    pid: int
    name: str
    username: str
    status: str
    cpu_percent: float
    memory_percent: float
    created_time: str
    command: str 