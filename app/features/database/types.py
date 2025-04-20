from typing import TypedDict, Dict, List, Optional, Any, Union


class DatabaseError(Exception):
    """Base exception for database operations"""
    pass


class DatabaseConnectionError(DatabaseError):
    """Exception for database connection failures"""
    pass


class DatabaseUser(TypedDict):
    """Type definition for database user information"""
    user: str
    host: Optional[str]


class DatabaseStats(TypedDict):
    """Type definition for database statistics"""
    name: str
    size: float  # Size in MB
    tables: int
    status: str 