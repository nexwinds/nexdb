<?php
// Page specific variables
$page_title = "Documentation - NEXDB";
$page_description = "Comprehensive documentation for NEXDB - a lightweight, secure alternative for fast, reliable database management.";
$page_css = '<link rel="stylesheet" href="docs.css">';

// Include header
include 'includes/header.php';
?>

<!-- Documentation Hero -->
<section class="docs-hero">
    <div class="container">
        <h1>NEXDB Documentation</h1>
        <p>Everything you need to install, configure, and use NEXDB effectively. Browse our comprehensive guides, tutorials, and reference materials.</p>
    </div>
</section>

<!-- Documentation Content -->
<div class="container docs-container">
    <!-- Sidebar (Table of Contents) -->
    <aside class="docs-sidebar">
        <div class="docs-sidebar-inner">
            <div class="docs-sidebar-header">
                <h3>Documentation</h3>
            </div>
            <nav class="docs-nav">
                <ul class="docs-nav-list">
                    <li class="docs-nav-item">
                        <h4>Getting Started</h4>
                        <ul class="docs-nav-sublist">
                            <li class="docs-nav-subitem"><a href="#introduction" class="docs-nav-link">Introduction</a></li>
                            <li class="docs-nav-subitem"><a href="#system-requirements" class="docs-nav-link">System Requirements</a></li>
                            <li class="docs-nav-subitem"><a href="#installation" class="docs-nav-link">Installation</a></li>
                            <li class="docs-nav-subitem"><a href="#quick-start" class="docs-nav-link">Quick Start Guide</a></li>
                        </ul>
                    </li>
                    <li class="docs-nav-item">
                        <h4>Configuration</h4>
                        <ul class="docs-nav-sublist">
                            <li class="docs-nav-subitem"><a href="#basic-configuration" class="docs-nav-link">Basic Configuration</a></li>
                            <li class="docs-nav-subitem"><a href="#database-setup" class="docs-nav-link">Database Setup</a></li>
                            <li class="docs-nav-subitem"><a href="#aws-s3-integration" class="docs-nav-link">AWS S3 Integration</a></li>
                            <li class="docs-nav-subitem"><a href="#security-settings" class="docs-nav-link">Security Settings</a></li>
                        </ul>
                    </li>
                    <li class="docs-nav-item">
                        <h4>Usage Guide</h4>
                        <ul class="docs-nav-sublist">
                            <li class="docs-nav-subitem"><a href="#dashboard" class="docs-nav-link">Dashboard</a></li>
                            <li class="docs-nav-subitem"><a href="#database-explorer" class="docs-nav-link">Database Explorer</a></li>
                            <li class="docs-nav-subitem"><a href="#sql-query-console" class="docs-nav-link">SQL Query Console</a></li>
                            <li class="docs-nav-subitem"><a href="#user-management" class="docs-nav-link">User Management</a></li>
                            <li class="docs-nav-subitem"><a href="#backup-recovery" class="docs-nav-link">Backup & Recovery</a></li>
                        </ul>
                    </li>
                    <li class="docs-nav-item">
                        <h4>Advanced Topics</h4>
                        <ul class="docs-nav-sublist">
                            <li class="docs-nav-subitem"><a href="#performance-tuning" class="docs-nav-link">Performance Tuning</a></li>
                            <li class="docs-nav-subitem"><a href="#cli-usage" class="docs-nav-link">CLI Usage</a></li>
                            <li class="docs-nav-subitem"><a href="#api-integration" class="docs-nav-link">API Integration</a></li>
                            <li class="docs-nav-subitem"><a href="#customization" class="docs-nav-link">Customization</a></li>
                        </ul>
                    </li>
                    <li class="docs-nav-item">
                        <h4>Troubleshooting</h4>
                        <ul class="docs-nav-sublist">
                            <li class="docs-nav-subitem"><a href="#common-issues" class="docs-nav-link">Common Issues</a></li>
                            <li class="docs-nav-subitem"><a href="#error-messages" class="docs-nav-link">Error Messages</a></li>
                            <li class="docs-nav-subitem"><a href="#logs" class="docs-nav-link">Logs</a></li>
                        </ul>
                    </li>
                    <li class="docs-nav-item">
                        <h4>API Reference</h4>
                        <ul class="docs-nav-sublist">
                            <li class="docs-nav-subitem"><a href="#api-overview" class="docs-nav-link">API Overview</a></li>
                            <li class="docs-nav-subitem"><a href="#authentication" class="docs-nav-link">Authentication</a></li>
                            <li class="docs-nav-subitem"><a href="#endpoints" class="docs-nav-link">Endpoints</a></li>
                        </ul>
                    </li>
                </ul>
            </nav>
        </div>
    </aside>

    <!-- Main Documentation Content -->
    <main class="docs-content">
        <section id="introduction">
            <h2>Introduction</h2>
            <p>NEXDB is a lightweight and secure alternative to traditional database control panels. Designed for speed, reliability, and modern database management, NEXDB helps you efficiently manage your databases with a clean, intuitive interface and powerful tools.</p>
            
            <p>This documentation provides detailed information on how to install, configure, and use NEXDB, as well as advanced topics for power users and developers.</p>
        </section>

        <section id="system-requirements">
            <h2>System Requirements</h2>
            <p>Before installing NEXDB, ensure your system meets the following requirements:</p>
            
            <h3>Minimum Requirements</h3>
            <ul>
                <li>Ubuntu 24.04 or higher</li>
                <li>Python 3.7+</li>
                <li>2GB RAM (4GB recommended)</li>
                <li>Modern web browser (Chrome, Firefox, Safari, Edge)</li>
                <li>Root access to your server</li>
            </ul>
            
            <h3>Supported Database Systems</h3>
            <ul>
                <li>MySQL 8+ (installed by default)</li>
                <li>PostgreSQL 10+ (optional, can be installed via dashboard)</li>
            </ul>
            
            <h3>Optional Requirements</h3>
            <ul>
                <li>AWS account (for S3 backup functionality)</li>
            </ul>
            
            <div class="alert alert-info">
                <div class="alert-title">
                    <i class="fas fa-info-circle"></i> Note
                </div>
                <p>For production use, we recommend using NEXDB on a fresh VPS or dedicated server for optimal performance and security.</p>
            </div>
        </section>

        <section id="installation">
            <h2>Installation</h2>
            <p>NEXDB can be installed with a simple one-line command on Ubuntu systems.</p>
            
            <h3>One-Line Installation</h3>
            <p>The simplest way to install NEXDB is through our installation script:</p>
            
            <div class="code-block">
                <div class="code-header">
                    <span class="code-title">Terminal</span>
                    <button class="copy-btn">Copy</button>
                </div>
                <div class="code-content">
                    <pre>wget -qO- https://raw.githubusercontent.com/nexwinds/nexdb/main/install.sh | sudo bash</pre>
                </div>
            </div>
            
            <p>This will:</p>
            <ol>
                <li>Check if your system meets the requirements (Ubuntu 24+)</li>
                <li>Install MySQL 8 and configure it securely</li>
                <li>Set up NEXDB with an admin account</li>
                <li>Configure the database connection</li>
                <li>Display the access credentials when complete</li>
            </ol>
            
            <div class="alert alert-warning">
                <div class="alert-title">
                    <i class="fas fa-exclamation-triangle"></i> Warning
                </div>
                <p>Installation requires root privileges. Make sure you have sudo access before proceeding.</p>
            </div>
        </section>

        <!-- Additional sections would continue here -->
        <section id="quick-start">
            <h2>Quick Start Guide</h2>
            <p>After installing NEXDB, follow these steps to get started:</p>
            
            <h3>1. Access the Web Interface</h3>
            <p>Open your browser and navigate to the URL shown at the end of the installation:</p>
            
            <div class="code-block">
                <div class="code-header">
                    <span class="code-title">URL</span>
                    <button class="copy-btn">Copy</button>
                </div>
                <div class="code-content">
                    <pre>http://YOUR_SERVER_IP:5000</pre>
                </div>
            </div>
            
            <p>Log in with the credentials provided during installation:</p>
            <ul>
                <li><strong>Username:</strong> admin</li>
                <li><strong>Password:</strong> [generated during installation]</li>
            </ul>
            
            <h3>2. Explore the Dashboard</h3>
            <p>The dashboard provides an overview of your system resources, database status, and recent backups.</p>
            
            <h3>3. Install PostgreSQL (Optional)</h3>
            <p>If you need PostgreSQL in addition to the default MySQL installation:</p>
            <ol>
                <li>Navigate to "System" → "Dashboard"</li>
                <li>In the "Services Status" section, find the PostgreSQL row</li>
                <li>If PostgreSQL is not installed, click the "Install PostgreSQL" button</li>
                <li>The system will install PostgreSQL, configure it with secure defaults, and display the credentials</li>
                <li>These credentials will be automatically saved in the NEXDB configuration</li>
            </ol>
            
            <div class="alert alert-success">
                <div class="alert-title">
                    <i class="fas fa-check-circle"></i> Tip
                </div>
                <p>The PostgreSQL installation process handles all configurations automatically, including setting a secure random password for the 'postgres' user.</p>
            </div>
        </section>

        <section id="database-setup">
            <h2>Database Setup</h2>
            <p>NEXDB comes pre-configured with MySQL. PostgreSQL can be installed through the dashboard.</p>
            
            <h3>MySQL Configuration</h3>
            <p>MySQL is installed and configured automatically during the NEXDB installation process. The MySQL root password is generated during installation and displayed in the terminal.</p>
            
            <h3>PostgreSQL Installation</h3>
            <p>To install and configure PostgreSQL:</p>
            <ol>
                <li>Navigate to "System" → "Dashboard"</li>
                <li>Find the PostgreSQL service in the services list</li>
                <li>Click the "Install PostgreSQL" button</li>
                <li>Wait for the installation to complete</li>
                <li>The system will display the credentials and save them automatically</li>
            </ol>
            
            <p>The PostgreSQL installation process:</p>
            <ul>
                <li>Installs PostgreSQL server and client packages</li>
                <li>Starts and enables the PostgreSQL service</li>
                <li>Sets a secure random password for the 'postgres' user</li>
                <li>Automatically configures NEXDB to connect to the local PostgreSQL server</li>
            </ul>
            
            <div class="alert alert-info">
                <div class="alert-title">
                    <i class="fas fa-info-circle"></i> Note
                </div>
                <p>PostgreSQL installation requires root privileges and is only supported on Ubuntu systems.</p>
            </div>
        </section>

        <!-- Add more sections as needed -->
    </main>
</div>

<?php
// Set any page-specific scripts
$page_scripts = <<<EOT
<script>
    // Active link handling for documentation navigation
    document.addEventListener('DOMContentLoaded', function() {
        const sections = document.querySelectorAll('.docs-content section');
        const navLinks = document.querySelectorAll('.docs-nav-link');
        
        // Highlight the active section in the navigation
        function setActiveLink() {
            let currentSection = '';
            
            sections.forEach(section => {
                const sectionTop = section.offsetTop - 100;
                const sectionBottom = sectionTop + section.offsetHeight;
                
                if (window.scrollY >= sectionTop && window.scrollY < sectionBottom) {
                    currentSection = '#' + section.getAttribute('id');
                }
            });
            
            navLinks.forEach(link => {
                if (link.getAttribute('href') === currentSection) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }
        
        // Set active link on page load and scroll
        setActiveLink();
        window.addEventListener('scroll', setActiveLink);
        
        // Copy button functionality
        document.querySelectorAll('.copy-btn').forEach(button => {
            button.addEventListener('click', () => {
                const codeBlock = button.closest('.code-block').querySelector('pre');
                const textToCopy = codeBlock.textContent;
                
                navigator.clipboard.writeText(textToCopy).then(() => {
                    button.textContent = 'Copied!';
                    
                    setTimeout(() => {
                        button.textContent = 'Copy';
                    }, 2000);
                });
            });
        });
    });
</script>
EOT;

// Include footer
include 'includes/footer.php';
?>