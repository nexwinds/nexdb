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
echo "This script will remove NEXDB from your system."
echo

# Check if running as root
if [ "$EUID" -ne 0 ] && [ "$(uname)" != "Darwin" ]; then
    print_warning "Not running as root. You may need sudo for some operations."
    echo "Continue anyway? (y/n) [n]: "
    read CONTINUE
    CONTINUE=${CONTINUE:-n}
    
    if [ "$CONTINUE" != "y" ]; then
        print_message "Please run this script with sudo for a complete uninstallation."
        exit 1
    fi
fi

# Detect OS type
if [ "$(uname)" == "Darwin" ]; then
    OS_TYPE="macos"
elif [ -f /etc/debian_version ]; then
    OS_TYPE="debian"
elif [ -f /etc/redhat-release ]; then
    OS_TYPE="redhat"
elif [ -f /etc/arch-release ]; then
    OS_TYPE="arch"
else
    OS_TYPE="unknown"
    print_warning "Could not determine OS type. Some features may not work correctly."
fi

print_message "Detected OS type: $OS_TYPE"

# Setup installation directory
INSTALL_DIR="/opt/nexdb"
if [ "$OS_TYPE" == "macos" ]; then
    INSTALL_DIR="$HOME/nexdb"
fi

# Check if application exists
if [ ! -d "$INSTALL_DIR" ]; then
    print_warning "NEXDB is not installed at $INSTALL_DIR"
    echo "Do you want to specify a different installation directory? (y/n) [n]: "
    read SPECIFY_DIR
    SPECIFY_DIR=${SPECIFY_DIR:-n}
    
    if [ "$SPECIFY_DIR" == "y" ]; then
        echo "Enter the installation directory: "
        read CUSTOM_DIR
        if [ -d "$CUSTOM_DIR" ]; then
            INSTALL_DIR="$CUSTOM_DIR"
            print_message "Using installation directory: $INSTALL_DIR"
        else
            print_error "Directory $CUSTOM_DIR does not exist."
            exit 1
        fi
    else
        print_error "NEXDB is not installed. Nothing to uninstall."
        exit 1
    fi
fi

# Prompt for confirmation
echo "This will remove NEXDB from your system."
echo "Installation directory: $INSTALL_DIR"
echo 
echo "Do you want to remove the database and backups as well? (y/n) [n]: "
read REMOVE_DATA
REMOVE_DATA=${REMOVE_DATA:-n}

echo "Are you sure you want to uninstall NEXDB? (y/n) [n]: "
read CONFIRM
CONFIRM=${CONFIRM:-n}

if [ "$CONFIRM" != "y" ]; then
    print_message "Uninstallation cancelled."
    exit 0
fi

# Stop and remove service if not on macOS
if [ "$OS_TYPE" != "macos" ]; then
    print_message "Stopping NEXDB service..."
    if systemctl is-active --quiet nexdb.service; then
        systemctl stop nexdb.service
        print_message "NEXDB service stopped."
    else
        print_warning "NEXDB service is not running."
    fi
    
    print_message "Disabling NEXDB service..."
    if systemctl is-enabled --quiet nexdb.service; then
        systemctl disable nexdb.service
        print_message "NEXDB service disabled."
    else
        print_warning "NEXDB service is not enabled."
    fi
    
    print_message "Removing NEXDB service file..."
    if [ -f "/etc/systemd/system/nexdb.service" ]; then
        rm /etc/systemd/system/nexdb.service
        systemctl daemon-reload
        print_message "NEXDB service file removed."
    else
        print_warning "NEXDB service file not found."
    fi
fi

# Backup data if requested
if [ "$REMOVE_DATA" != "y" ]; then
    BACKUP_DIR="/tmp/nexdb_backup_$(date +%Y%m%d%H%M%S)"
    print_message "Creating backup of database and configuration at $BACKUP_DIR..."
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if [ -d "$INSTALL_DIR/instance" ]; then
        cp -r "$INSTALL_DIR/instance" "$BACKUP_DIR/"
        print_message "Database and backups saved to $BACKUP_DIR/instance."
    fi
    
    # Backup configuration
    if [ -f "$INSTALL_DIR/.env" ]; then
        cp "$INSTALL_DIR/.env" "$BACKUP_DIR/"
        print_message "Configuration saved to $BACKUP_DIR/.env."
    fi
fi

# Remove installation directory
print_message "Removing NEXDB installation directory..."
if [ "$REMOVE_DATA" == "y" ]; then
    rm -rf "$INSTALL_DIR"
    print_message "NEXDB completely removed from $INSTALL_DIR"
else
    # Remove everything except instance directory
    find "$INSTALL_DIR" -mindepth 1 -maxdepth 1 -not -name "instance" -exec rm -rf {} \;
    print_message "NEXDB removed from $INSTALL_DIR (database and backups preserved)"
    print_message "Your data is still available at $INSTALL_DIR/instance"
fi

print_message "Uninstallation complete!"
if [ "$REMOVE_DATA" != "y" ]; then
    print_message "A backup of your data has been created at $BACKUP_DIR"
fi 