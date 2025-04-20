from flask import Blueprint, jsonify, request
from flask_login import login_required
import logging
import pytz
from datetime import datetime
import subprocess
import platform
import os

# Create blueprint
timezone_api = Blueprint('timezone_api', __name__, url_prefix='/api/system')
logger = logging.getLogger(__name__)

@timezone_api.route('/timezone/list', methods=['GET'])
@login_required
def list_timezones():
    """API endpoint to get list of available timezones"""
    try:
        timezones = [
            {"value": tz, "label": tz.replace('_', ' ')}
            for tz in pytz.common_timezones
        ]
        
        return jsonify({
            "success": True,
            "timezones": timezones
        })
    except Exception as e:
        logger.error(f"Error listing timezones: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@timezone_api.route('/timezone', methods=['GET'])
@login_required
def get_timezone():
    """API endpoint to get current timezone information"""
    try:
        # Get current timezone
        current_timezone = _get_current_timezone()
        
        # Get current time in the timezone
        now = datetime.now(pytz.timezone(current_timezone))
        
        return jsonify({
            "success": True,
            "timezone": current_timezone,
            "server_time": now.strftime("%Y-%m-%d %H:%M:%S %Z%z"),
            "unix_timestamp": int(now.timestamp())
        })
    except Exception as e:
        logger.error(f"Error getting timezone info: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@timezone_api.route('/timezone', methods=['POST'])
@login_required
def set_timezone():
    """API endpoint to set system timezone"""
    try:
        timezone = request.json.get('timezone')
        if not timezone:
            return jsonify({
                "success": False,
                "error": "Timezone is required"
            }), 400
        
        # Validate timezone
        if timezone not in pytz.common_timezones:
            return jsonify({
                "success": False,
                "error": f"Invalid timezone: {timezone}"
            }), 400
        
        # Set the timezone
        success = _set_system_timezone(timezone)
        
        if success:
            # Get current time in the new timezone
            now = datetime.now(pytz.timezone(timezone))
            
            return jsonify({
                "success": True,
                "message": f"Timezone set to {timezone}",
                "timezone": timezone,
                "server_time": now.strftime("%Y-%m-%d %H:%M:%S %Z%z")
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Failed to set timezone to {timezone}"
            }), 500
    except Exception as e:
        logger.error(f"Error setting timezone: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def _get_current_timezone() -> str:
    """
    Get the current system timezone
    
    Returns:
        Timezone string (e.g., 'America/New_York')
    """
    try:
        os_name = platform.system().lower()
        
        if os_name == 'linux':
            # Try to get from timedatectl
            try:
                result = subprocess.run(['timedatectl', 'show', '--property=Timezone'], 
                                     capture_output=True, text=True, check=True)
                timezone = result.stdout.strip().split('=')[1]
                return timezone
            except (subprocess.SubprocessError, IndexError):
                # Fallback to /etc/timezone
                if os.path.exists('/etc/timezone'):
                    with open('/etc/timezone', 'r') as f:
                        return f.read().strip()
                
                # Fallback to Python's time module
                import time
                return time.tzname[0]
        
        elif os_name == 'windows':
            # On Windows, use the Registry
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SYSTEM\CurrentControlSet\Control\TimeZoneInformation")
            timezone = winreg.QueryValueEx(key, "TimeZoneKeyName")[0]
            winreg.CloseKey(key)
            return timezone
        
        elif os_name == 'darwin':  # macOS
            # On macOS, use systemsetup command
            result = subprocess.run(['systemsetup', '-gettimezone'], 
                                 capture_output=True, text=True, check=True)
            timezone = result.stdout.strip().split(': ')[1]
            return timezone
        
        # Fallback to local timezone from datetime
        return str(datetime.now(datetime.timezone.utc).astimezone().tzinfo)
    
    except Exception as e:
        logger.error(f"Error getting current timezone: {str(e)}")
        # Return a default timezone as fallback
        return 'UTC'

def _set_system_timezone(timezone: str) -> bool:
    """
    Set the system timezone
    
    Args:
        timezone: Timezone string (e.g., 'America/New_York')
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os_name = platform.system().lower()
        
        if os_name == 'linux':
            # Use timedatectl on Linux
            subprocess.run(['sudo', 'timedatectl', 'set-timezone', timezone], 
                         check=True, capture_output=True)
            return True
        
        elif os_name == 'windows':
            # On Windows, use tzutil
            subprocess.run(['tzutil', '/s', timezone], 
                         check=True, capture_output=True, shell=True)
            return True
        
        elif os_name == 'darwin':  # macOS
            # On macOS, use systemsetup command
            subprocess.run(['sudo', 'systemsetup', '-settimezone', timezone], 
                         check=True, capture_output=True)
            return True
        
        # For other OSes or if OS-specific method fails, set only in Flask app
        os.environ['TZ'] = timezone
        return True
    
    except Exception as e:
        logger.error(f"Error setting timezone to {timezone}: {str(e)}")
        return False 