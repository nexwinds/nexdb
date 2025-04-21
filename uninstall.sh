#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

# Display banner
echo "================================================================="
echo "                NEXDB - Uninstallation Script                    "
echo "================================================================="
echo "This script will remove NEXDB from your system but preserve your databases."
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root. Please use sudo."
    exit 1
fi

# Check if NEXDB is installed
INSTALL_DIR="/opt/nexdb"
if [ ! -d "$INSTALL_DIR" ]; then
    print_error "NEXDB is not installed at $INSTALL_DIR. Nothing to uninstall."
    exit 1
fi

# Prompt for confirmation
echo "This will remove NEXDB from your system, but will preserve all your databases."
echo 
echo "Are you sure you want to uninstall NEXDB? (y/n) [n]: "
read CONFIRM
CONFIRM=${CONFIRM:-n}

if [ "$CONFIRM" != "y" ]; then
    print_message "Uninstallation cancelled."
    exit 0
fi

# Stop service
print_message "Stopping NEXDB service..."
if systemctl is-active --quiet nexdb.service; then
    systemctl stop nexdb.service
    print_message "NEXDB service stopped."
else
    print_warning "NEXDB service is not running."
fi

# Disable service
print_message "Disabling NEXDB service..."
if systemctl is-enabled --quiet nexdb.service; then
    systemctl disable nexdb.service
    print_message "NEXDB service disabled."
else
    print_warning "NEXDB service is not enabled."
fi

# Remove service file
print_message "Removing NEXDB service file..."
if [ -f "/etc/systemd/system/nexdb.service" ]; then
    rm /etc/systemd/system/nexdb.service
    systemctl daemon-reload
    print_message "NEXDB service file removed."
else
    print_warning "NEXDB service file not found."
fi

# Remove NEXDB installation directory
print_message "Removing NEXDB installation directory..."
rm -rf "$INSTALL_DIR"
print_message "NEXDB has been completely removed from $INSTALL_DIR"

print_message "Uninstallation complete!"
print_message "Your MySQL and other databases have been preserved." 