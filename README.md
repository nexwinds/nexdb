# NEXDB

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.7%2B-blue" alt="Python 3.7+">
  <img src="https://img.shields.io/badge/License-Custom-green" alt="Custom License">
  <img src="https://img.shields.io/badge/Database-MySQL%208-orange" alt="MySQL 8">
  <img src="https://img.shields.io/badge/Storage-AWS%20S3-yellow" alt="AWS S3">
</div>

<p align="center">
  <b>A powerful yet minimal database management interface for MySQL with integrated S3 backups</b>
</p>

**NEXDB** is a focused web panel for database administrators and developers who need a clean, streamlined interface for managing databases without bloat. It provides essential tools for database administration, browsing, querying, and automated backup management.

## ✨ Features

### 🗄️ Database Management

- **Complete Administrative Control**
  - Create, edit, and delete MySQL databases
  - Manage database users and permissions
  - Monitor connection status and performance metrics

- **Database Explorer** 
  - Browse database tables with a clean, intuitive interface
  - View, search, and filter table data with pagination
  - Edit records with a user-friendly form interface
  - Execute custom SQL queries with syntax highlighting
  - Manage table structure and perform operations like truncate/drop

- **Multi-Database Support**
  - Core support for MySQL 8
  - Optional PostgreSQL support configurable via dashboard
  - Consistent interface for both database types
  - Type-specific features where appropriate

### 🔄 Backup System

- **Automated Backup Management**
  - One-click manual backups
  - Schedule automated backups (daily, weekly, monthly)
  - Configurable retention policies

- **Cloud Integration**
  - AWS S3 integration for secure, off-site storage
  - Direct download options for local storage
  - Backup compression for efficient storage

- **Recovery Tools**
  - Simple one-click database restoration
  - Point-in-time recovery options
  - Backup verification

### 🛡️ System Management

- **Server Monitoring**
  - Track system resource usage
  - Monitor database server performance
  - View active connections and queries

- **Security Features**
  - Role-based authentication
  - Secure password management
  - CSRF protection on all forms
  - IP restriction support

### 🎨 User Experience

- **Modern Interface**
  - Clean, responsive Bootstrap 5 design
  - Mobile-friendly dashboard
  - Intuitive navigation and workflows
  - Dark/light mode support

## 🚀 Getting Started

### Prerequisites

- Ubuntu 24.04 or higher
- Root access to your server
- Fresh VPS installation recommended

### One-Line Installation

```bash
wget -qO- https://raw.githubusercontent.com/nexwinds/nexdb/main/install.sh | sudo bash
```

This will:
1. Check if your system meets the requirements (Ubuntu 24+)
2. Install MySQL 8 and configure it securely
3. Set up NEXDB with an admin account
4. Configure the database connection
5. Display the access credentials when complete

## 🔧 Configuration

All configuration can be managed through the NEXDB dashboard after installation. 

### PostgreSQL Installation

PostgreSQL can be installed directly from the system dashboard:

1. Navigate to "System" → "Dashboard"
2. In the "Services Status" section, find the PostgreSQL row
3. If PostgreSQL is not installed, click the "Install PostgreSQL" button
4. The system will install PostgreSQL, configure it with secure defaults, and display the credentials
5. These credentials will be automatically saved in the NEXDB configuration

The PostgreSQL installation process:
- Installs PostgreSQL server and client packages
- Starts and enables the PostgreSQL service
- Sets a secure random password for the 'postgres' user
- Automatically configures NEXDB to connect to the local PostgreSQL server

### AWS S3 Backup Configuration

Configure S3 backups in the dashboard:

1. Go to "Settings" → "Backup Configuration"
2. Enter your AWS credentials and bucket details
3. Save the configuration

## 🖥️ Usage Guide

### Database Explorer

1. **Browsing Databases and Tables**
   - Navigate to "DB Explorer" from the main menu
   - Select database type (MySQL/PostgreSQL) from the dropdown
   - Choose a database from the sidebar
   - Browse tables in the selected database

2. **Viewing and Editing Table Data**
   - Click on any table name to view its contents
   - Use search box to filter records
   - Sort columns by clicking column headers
   - Edit records with the edit button
   - Add new records with the "Add Record" button

3. **Running SQL Queries**
   - Click "Run SQL Query" button
   - Write your SQL query in the editor
   - Press Execute or Ctrl+Enter to run
   - View results in the table below

### Backup Management

1. **Creating a Manual Backup**
   - Go to "Backups" section
   - Select database to backup
   - Choose destination (local/S3)
   - Click "Create Backup"

2. **Setting Up Scheduled Backups**
   - Configure backup schedule
   - Set retention period
   - Select databases to include
   - Enable/disable compressed backups

## 💡 Best Practices

- **Security**
  - Always access NEXDB via HTTPS in production
  - Use strong passwords for admin access
  - Regularly update your NEXDB installation

- **Backups**
  - Schedule regular automated backups
  - Test restore functionality periodically
  - Use off-site S3 backups for critical databases

- **Performance**
  - Monitor system resource usage
  - Optimize large queries before execution
  - Schedule backups during low-usage periods

## 🔒 Security Considerations

- Single-user authentication system with secure password hashing (PBKDF2-SHA256)
- CSRF tokens protect against cross-site request forgery
- All user inputs are sanitized to prevent SQL injection
- Optional IP restriction for additional security

## 🛣️ Roadmap

- Docker deployment option with docker-compose
- Multi-admin role support with different permission levels
- Advanced monitoring with alerting capabilities
- Support for additional database types (MongoDB, SQLite)
- Additional cloud backup providers (Google Cloud, Azure)
- Customizable dashboard widgets

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under a custom license by Nexwinds Solutions Lda - see the LICENSE.md file for details. The license permits private use and modification but has specific conditions for commercial use, distribution, and attribution.

## 🙏 Acknowledgements

- Flask web framework
- Bootstrap 5 for the UI components
- MySQL and PostgreSQL connector libraries
- AWS SDK for Python (Boto3)
- All open source contributors who've made this project possible