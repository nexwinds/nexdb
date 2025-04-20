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
                <li>Node.js 14.x or later</li>
                <li>NPM 6.x or later</li>
                <li>2GB RAM (4GB recommended)</li>
                <li>Modern web browser (Chrome, Firefox, Safari, Edge)</li>
            </ul>
            
            <h3>Supported Database Systems</h3>
            <ul>
                <li>MySQL 5.7+ / MariaDB 10.3+</li>
                <li>PostgreSQL 10+</li>
                <li>MongoDB 4.2+</li>
                <li>SQLite 3.x</li>
            </ul>
            
            <h3>Optional Requirements</h3>
            <ul>
                <li>AWS account (for S3 backup functionality)</li>
                <li>Redis (for enhanced caching)</li>
            </ul>
            
            <div class="alert alert-info">
                <div class="alert-title">
                    <i class="fas fa-info-circle"></i> Note
                </div>
                <p>For production use, we recommend using NEXDB on a dedicated server or instance for optimal performance and security.</p>
            </div>
        </section>

        <section id="installation">
            <h2>Installation</h2>
            <p>NEXDB can be installed in several ways depending on your requirements and environment. Choose the method that works best for your setup.</p>
            
            <h3>Global NPM Installation</h3>
            <p>The simplest way to install NEXDB is through NPM:</p>
            
            <div class="code-block">
                <div class="code-header">
                    <span class="code-title">Terminal</span>
                    <button class="copy-btn">Copy</button>
                </div>
                <div class="code-content">
                    <pre>npm install -g nexdb</pre>
                </div>
            </div>
            
            <p>After installation, you can start NEXDB with the following command:</p>
            
            <div class="code-block">
                <div class="code-header">
                    <span class="code-title">Terminal</span>
                    <button class="copy-btn">Copy</button>
                </div>
                <div class="code-content">
                    <pre>nexdb start</pre>
                </div>
            </div>
            
            <h3>Docker Installation</h3>
            <p>For containerized environments, you can use the official NEXDB Docker image:</p>
            
            <div class="code-block">
                <div class="code-header">
                    <span class="code-title">Terminal</span>
                    <button class="copy-btn">Copy</button>
                </div>
                <div class="code-content">
                    <pre>docker pull nexdb/nexdb:latest
docker run -p 8080:8080 -v nexdb-data:/data nexdb/nexdb:latest</pre>
                </div>
            </div>
            
            <h3>Manual Installation</h3>
            <p>For manual installation, follow these steps:</p>
            
            <ol>
                <li>Clone the repository:
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-title">Terminal</span>
                            <button class="copy-btn">Copy</button>
                        </div>
                        <div class="code-content">
                            <pre>git clone https://github.com/nexdb/nexdb.git
cd nexdb</pre>
                        </div>
                    </div>
                </li>
                <li>Install dependencies:
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-title">Terminal</span>
                            <button class="copy-btn">Copy</button>
                        </div>
                        <div class="code-content">
                            <pre>npm install</pre>
                        </div>
                    </div>
                </li>
                <li>Build the application:
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-title">Terminal</span>
                            <button class="copy-btn">Copy</button>
                        </div>
                        <div class="code-content">
                            <pre>npm run build</pre>
                        </div>
                    </div>
                </li>
                <li>Start the application:
                    <div class="code-block">
                        <div class="code-header">
                            <span class="code-title">Terminal</span>
                            <button class="copy-btn">Copy</button>
                        </div>
                        <div class="code-content">
                            <pre>npm start</pre>
                        </div>
                    </div>
                </li>
            </ol>
            
            <div class="alert alert-warning">
                <div class="alert-title">
                    <i class="fas fa-exclamation-triangle"></i> Warning
                </div>
                <p>Some installation steps may require root or administrator privileges. Make sure you have the necessary permissions before proceeding.</p>
            </div>
        </section>

        <!-- Additional sections would continue here -->
        <section id="quick-start">
            <h2>Quick Start Guide</h2>
            <p>After installing NEXDB, follow these steps to get started:</p>
            
            <h3>1. Initialize Configuration</h3>
            <p>Run the initialization command to set up your configuration:</p>
            
            <div class="code-block">
                <div class="code-header">
                    <span class="code-title">Terminal</span>
                    <button class="copy-btn">Copy</button>
                </div>
                <div class="code-content">
                    <pre>nexdb init</pre>
                </div>
            </div>
            
            <p>This will guide you through setting up the initial configuration, including database connections and security settings.</p>
            
            <h3>2. Start the Server</h3>
            <p>Start the NEXDB server:</p>
            
            <div class="code-block">
                <div class="code-header">
                    <span class="code-title">Terminal</span>
                    <button class="copy-btn">Copy</button>
                </div>
                <div class="code-content">
                    <pre>nexdb start</pre>
                </div>
            </div>
            
            <h3>3. Access the Web Interface</h3>
            <p>Open your browser and navigate to:</p>
            
            <div class="code-block">
                <div class="code-header">
                    <span class="code-title">URL</span>
                    <button class="copy-btn">Copy</button>
                </div>
                <div class="code-content">
                    <pre>http://localhost:8080</pre>
                </div>
            </div>
            
            <p>Log in with the default credentials:</p>
            <ul>
                <li><strong>Username:</strong> admin</li>
                <li><strong>Password:</strong> nexdb (You'll be prompted to change this on first login)</li>
            </ul>
            
            <h3>4. Add Your First Database Connection</h3>
            <p>After logging in, click on "Connections" in the sidebar and then "Add New Connection" to set up your first database connection.</p>
            
            <div class="alert alert-success">
                <div class="alert-title">
                    <i class="fas fa-check-circle"></i> Tip
                </div>
                <p>Check out the detailed tutorials in the <a href="#database-setup">Database Setup</a> section for more information on configuring different database types.</p>
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