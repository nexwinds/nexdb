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
echo "                NEXDB - Database Manager Installation            "
echo "================================================================="
echo "This script will install NEXDB and configure it for your system."
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root. Please use sudo."
    exit 1
fi

# Check if OS is Ubuntu 24 or higher
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$ID" != "ubuntu" ]; then
        print_error "This script is only compatible with Ubuntu."
        exit 1
    fi
    
    UBUNTU_VERSION=$(echo $VERSION_ID | cut -d. -f1)
    if [ "$UBUNTU_VERSION" -lt 24 ]; then
        print_error "This script requires Ubuntu 24 or higher. Found: $VERSION_ID"
        exit 1
    fi
else
    print_error "Could not determine OS version. This script is only compatible with Ubuntu 24+."
    exit 1
fi

print_message "Detected compatible Ubuntu version: $VERSION_ID"

# Check if this is a new VPS installation
if [ -d "/opt/nexdb" ]; then
    print_error "NEXDB is already installed. This script is intended for new installations only."
    exit 1
fi

# Check if MySQL is already installed
if command -v mysql &> /dev/null; then
    print_warning "MySQL is already installed on this system."
    echo "Do you want to continue with the existing MySQL installation? (y/n) [y]: "
    read CONTINUE_MYSQL
    CONTINUE_MYSQL=${CONTINUE_MYSQL:-y}
    
    if [ "$CONTINUE_MYSQL" != "y" ]; then
        print_error "Installation aborted. Please remove MySQL first or use a fresh VPS."
        exit 1
    fi
fi

# Install required packages
print_message "Installing required packages..."
apt-get update
apt-get install -y python3 python3-pip python3-venv wget curl gnupg lsb-release

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_message "Python version: $PYTHON_VERSION"

# Check if version is at least 3.7
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
    print_error "Python 3.7 or higher is required. Found $PYTHON_VERSION"
    exit 1
fi

# Install MySQL 8
print_message "Installing MySQL 8..."
apt-get install -y mysql-server-8.0

# Secure MySQL installation
print_message "Securing MySQL installation..."
# Generate a random password for MySQL root user
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 12)

# Set MySQL root password
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}';"
mysql -u root -p${MYSQL_ROOT_PASSWORD} -e "DELETE FROM mysql.user WHERE User='';"
mysql -u root -p${MYSQL_ROOT_PASSWORD} -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -u root -p${MYSQL_ROOT_PASSWORD} -e "DROP DATABASE IF EXISTS test;"
mysql -u root -p${MYSQL_ROOT_PASSWORD} -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
mysql -u root -p${MYSQL_ROOT_PASSWORD} -e "FLUSH PRIVILEGES;"

print_message "MySQL root password set to: ${MYSQL_ROOT_PASSWORD}"
print_message "Please save this password in a secure location."

# Setup installation directory
INSTALL_DIR="/opt/nexdb"
print_message "Creating installation directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

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
source venv/bin/activate

print_message "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt || {
    print_error "Failed to install dependencies."
    exit 1
}

# Create instance directory for database and backups
mkdir -p "$INSTALL_DIR/instance/backups"

# Generate admin credentials
ADMIN_USERNAME="admin"
ADMIN_PASSWORD=$(openssl rand -base64 12)

# Store MySQL credentials in SQLite configuration
print_message "Initializing database and configuration..."
python -m flask init-db || {
    print_error "Failed to initialize database."
    exit 1
}

# Create admin account
python -m flask create-admin --username "$ADMIN_USERNAME" --password "$ADMIN_PASSWORD" || {
    print_error "Failed to create admin account."
    exit 1
}

# Store MySQL credentials in SQLite
python -m flask store-config --key "mysql_host" --value "localhost"
python -m flask store-config --key "mysql_port" --value "3306"
python -m flask store-config --key "mysql_user" --value "root"
python -m flask store-config --key "mysql_password" --value "${MYSQL_ROOT_PASSWORD}"

# Set up systemd service
print_message "Setting up systemd service..."

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/nexdb.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=NEXDB Database Manager
After=network.target mysql.service

[Service]
User=root
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

print_message "Installation complete!"
print_message "NEXDB is now available at: http://$(hostname -I | awk '{print $1}'):5000"
print_message "Admin credentials:"
echo "-----------------------------------------------------------------"
echo "Username: $ADMIN_USERNAME"
echo "Password: $ADMIN_PASSWORD"
echo "-----------------------------------------------------------------"
echo "MySQL Root Password: $MYSQL_ROOT_PASSWORD"
echo "-----------------------------------------------------------------"
echo "IMPORTANT: Save these credentials in a secure location!"
echo "You can manage MySQL credentials and install PostgreSQL through the dashboard."


