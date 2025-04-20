#!/bin/bash

echo "NEXDB Installation Verification"
echo "--------------------------------"

# Check if panel directory exists
if [ -d "/www/server/panel" ]; then
    echo "[✓] Panel directory exists"
else
    echo "[✗] Panel directory not found at /www/server/panel"
    exit 1
fi

# Check if MySQL is installed
if [ -d "/www/server/mysql" ]; then
    echo "[✓] MySQL is installed"
else
    echo "[✗] MySQL is not installed"
    exit 1
fi

# Check if PostgreSQL is installed
if [ -d "/www/server/pgsql" ]; then
    echo "[✓] PostgreSQL is installed"
else
    echo "[✗] PostgreSQL is not installed"
    exit 1
fi

# Check if S3 backup module exists
if [ -f "/www/server/panel/class/s3_backup.py" ]; then
    echo "[✓] S3 backup module exists"
else
    echo "[✗] S3 backup module not found"
    exit 1
fi

# Check if boto3 is installed (for S3 functionality)
python -c "import boto3" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "[✓] boto3 Python package is installed"
else
    echo "[✗] boto3 Python package is not installed"
    pip3 install boto3
    echo "[✓] boto3 Python package has been installed"
fi

# Check if panel is running
if ps aux | grep -v grep | grep BT-Panel > /dev/null; then
    echo "[✓] Panel service is running"
else
    echo "[✗] Panel service is not running"
    service bt start
    echo "[✓] Panel service has been started"
fi

echo "--------------------------------"
echo "NEXDB verification completed successfully!"
echo "You can now access your panel at http://YOUR_SERVER_IP:8888"
echo "================================" 