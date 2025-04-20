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

check_command() {
    if command -v $1 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Display banner
echo "================================================================="
echo "                NEXDB - Database Manager Installation            "
echo "================================================================="
echo "This script will install NEXDB and configure it for your system."
echo

# Check if running as root
if [ "$EUID" -ne 0 ] && [ "$(uname)" != "Darwin" ]; then
    print_warning "Not running as root. You may need sudo for some operations."
    echo "Continue anyway? (y/n) [n]: "
    read CONTINUE
    CONTINUE=${CONTINUE:-n}
    
    if [ "$CONTINUE" != "y" ]; then
        print_message "Please run this script with sudo for a complete installation."
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

# Check and install Python if needed
if ! check_command python3; then
    print_message "Installing Python 3..."
    
    case $OS_TYPE in
        debian)
            apt-get update
            apt-get install -y python3 python3-pip python3-venv
            ;;
        redhat)
            yum install -y python3 python3-pip
            ;;
        arch)
            pacman -S --noconfirm python python-pip
            ;;
        macos)
            if check_command brew; then
                brew install python
            else
                print_error "Homebrew is not installed. Please install Python 3 manually."
                exit 1
            fi
            ;;
        *)
            print_error "Please install Python 3 manually."
            exit 1
            ;;
    esac
else
    print_message "Python 3 is already installed."
fi

# Verify Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_message "Python version: $PYTHON_VERSION"

# Check if version is at least 3.7
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
    print_error "Python 3.7 or higher is required. Found $PYTHON_VERSION"
    exit 1
fi

# Setup installation directory
INSTALL_DIR="/opt/nexdb"
if [ "$OS_TYPE" == "macos" ]; then
    INSTALL_DIR="$HOME/nexdb"
fi

# Check if application already exists
if [ -d "$INSTALL_DIR" ]; then
    print_warning "NEXDB is already installed at $INSTALL_DIR"
    echo "Do you want to reinstall? This will preserve your database but reinstall the application. (y/n) [n]: "
    read REINSTALL
    REINSTALL=${REINSTALL:-n}
    
    if [ "$REINSTALL" != "y" ]; then
        print_message "Installation cancelled. Your existing installation has not been modified."
        exit 0
    fi
    
    print_message "Reinstalling NEXDB..."
else
    print_message "Creating installation directory at $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
    if [ $? -ne 0 ]; then
        print_error "Failed to create installation directory. Check permissions."
        exit 1
    fi
fi

# Copy application files
CURRENT_DIR=$(pwd)
print_message "Copying application files..."
cp -r "$CURRENT_DIR"/* "$INSTALL_DIR"/ || {
    print_error "Failed to copy application files."
    exit 1
}

# Create virtual environment
print_message "Setting up Python virtual environment..."
cd "$INSTALL_DIR" || {
    print_error "Failed to change to installation directory."
    exit 1
}

python3 -m venv venv || {
    print_error "Failed to create virtual environment."
    exit 1
}

# Activate virtual environment and install dependencies
if [ "$OS_TYPE" == "macos" ] || [ "$OS_TYPE" == "unknown" ]; then
    source venv/bin/activate
else
    source venv/bin/activate
fi

print_message "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt || {
    print_error "Failed to install dependencies."
    exit 1
}

# Create instance directory for database and backups
mkdir -p "$INSTALL_DIR/instance/backups"

# Initialize the database
print_message "Initializing database..."
python -m flask init-db || {
    print_error "Failed to initialize database."
    exit 1
}

# Create .env file for configuration
print_message "Creating configuration file..."
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cat > "$INSTALL_DIR/.env" << EOF
# NEXDB Environment Configuration
SECRET_KEY=$(python -c 'import os; print(os.urandom(24).hex())')
DEBUG=False

# Database URL (SQLite by default)
DATABASE_URL=sqlite:///${INSTALL_DIR}/instance/nexdb.db

# Backup directory
BACKUP_DIR=${INSTALL_DIR}/instance/backups

# MySQL settings (change as needed)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=

# PostgreSQL settings (change as needed)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=

# AWS S3 settings (for backups)
AWS_ACCESS_KEY=
AWS_SECRET_KEY=
AWS_BUCKET_NAME=
AWS_REGION=us-east-1
EOF
    print_message "Created default .env configuration file."
else
    print_message "Configuration file already exists, keeping existing configuration."
fi

# Set up service if not on macOS
if [ "$OS_TYPE" != "macos" ]; then
    print_message "Setting up systemd service..."
    
    # Create systemd service file
    SERVICE_FILE="/etc/systemd/system/nexdb.service"
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=NEXDB Database Manager
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=${INSTALL_DIR}
ExecStart=${INSTALL_DIR}/venv/bin/gunicorn --bind 0.0.0.0:5000 'app:create_app()'
Restart=always
Environment="PATH=${INSTALL_DIR}/venv/bin"
Environment="PYTHONPATH=${INSTALL_DIR}"

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable nexdb.service
    systemctl start nexdb.service
    
    print_message "NEXDB service installed and started."
    print_message "You can check the status with: systemctl status nexdb"
else
    print_message "Creating launch script..."
    
    # Create launch script for macOS
    cat > "$INSTALL_DIR/start.sh" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
source venv/bin/activate
exec gunicorn --bind 0.0.0.0:5000 "app:create_app()"
EOF
    
    chmod +x "$INSTALL_DIR/start.sh"
    
    print_message "You can start NEXDB by running: $INSTALL_DIR/start.sh"
fi

print_message "Installation complete!"
print_message "NEXDB is now available at: http://localhost:5000"
print_message "Admin credentials are saved in: $INSTALL_DIR/instance/admin_credentials.txt"

# Display saved credentials if the file exists
CREDS_FILE="$INSTALL_DIR/instance/admin_credentials.txt"
if [ -f "$CREDS_FILE" ]; then
    echo "-----------------------------------------------------------------"
    cat "$CREDS_FILE"
    echo "-----------------------------------------------------------------"
    echo "IMPORTANT: Save these credentials and delete the credentials file."
    echo "You can delete it with: rm $CREDS_FILE"
fi


