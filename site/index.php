<?php
// Page specific variables
$page_title = "NEXDB - Database Management Panel";
$page_description = "NEXDB is a lightweight, secure alternative for fast, reliable database management.";
$page_css = '<link rel="stylesheet" href="home.css">';

// Include header
include 'includes/header.php';
?>

<!-- Hero Section -->
<section class="hero">
    <div class="container">
        <div class="row align-items-center">
            <div class="col-lg-6">
                <div class="hero-content">
                    <h1>Powerful Database Management Made Simple</h1>
                    <p>NEXDB provides a lightweight and secure alternative to traditional database control panels. Easily manage your databases with a clean, intuitive interface and powerful tools designed for speed and reliability.</p>
                    <div class="hero-buttons">
                        <a href="#download" class="btn btn-primary btn-lg">Download NEXDB</a>
                        <a href="docs.php" class="btn btn-outline btn-lg">View Documentation</a>
                    </div>
                </div>
            </div>
            <div class="col-lg-6 d-none d-lg-block">
                <img src="assets/img/hero-illustration.svg" alt="NEXDB Dashboard" class="img-fluid">
            </div>
        </div>
    </div>
</section>

<!-- Features Section -->
<section id="features" class="features section">
    <div class="container">
        <div class="section-heading">
            <h2>Powerful Features</h2>
            <p>NEXDB comes packed with all the tools you need to manage your databases effectively</p>
        </div>
        
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-database"></i>
                </div>
                <h3>Multi-Database Support</h3>
                <p>Connect to and manage MySQL 8 by default, with the ability to install and configure PostgreSQL directly from the dashboard.</p>
                <a href="docs.php#database-setup" class="btn btn-sm btn-outline">Learn More</a>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-search"></i>
                </div>
                <h3>Advanced Data Explorer</h3>
                <p>Powerful query builder with syntax highlighting and visual results to explore your database tables with ease.</p>
                <a href="docs.php#database-explorer" class="btn btn-sm btn-outline">Learn More</a>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <h3>System Monitoring</h3>
                <p>Real-time monitoring of database and system performance with resource usage visualization.</p>
                <a href="docs.php#system-dashboard" class="btn btn-sm btn-outline">Learn More</a>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-shield-alt"></i>
                </div>
                <h3>Security Management</h3>
                <p>Manage database users and permissions with fine-grained access control and secure authentication.</p>
                <a href="docs.php#security" class="btn btn-sm btn-outline">Learn More</a>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-sync-alt"></i>
                </div>
                <h3>Backup & Recovery</h3>
                <p>Schedule automated backups with optional AWS S3 integration for secure off-site storage and easy restoration.</p>
                <a href="docs.php#backup-recovery" class="btn btn-sm btn-outline">Learn More</a>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-cogs"></i>
                </div>
                <h3>Easy Installation</h3>
                <p>Simple one-line installation script for Ubuntu 24+ with automatic MySQL configuration and secure defaults.</p>
                <a href="docs.php#installation" class="btn btn-sm btn-outline">Learn More</a>
            </div>
        </div>
    </div>
</section>

<!-- Installation Section -->
<section id="installation" class="installation section">
    <div class="container">
        <div class="section-heading">
            <h2>Quick Installation</h2>
            <p>Get started with NEXDB in minutes with our easy installation process</p>
        </div>
        
        <div class="installation-content">
            <div class="installation-steps">
                <div class="installation-step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <h3>Install with One Command</h3>
                        <p>Install NEXDB using our installation script:</p>
                        <div class="code-block">
                            <pre>wget -qO- https://raw.githubusercontent.com/nexwinds/nexdb/main/install.sh | sudo bash</pre>
                            <button class="copy-button">Copy</button>
                        </div>
                    </div>
                </div>
                
                <div class="installation-step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <h3>Save Your Credentials</h3>
                        <p>The installation will display your admin and MySQL credentials:</p>
                        <div class="code-block">
                            <pre>Username: admin
Password: [generated password]
MySQL Root Password: [generated password]</pre>
                            <button class="copy-button">Copy</button>
                        </div>
                    </div>
                </div>
                
                <div class="installation-step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <h3>Access NEXDB</h3>
                        <p>Open your browser and navigate to your server's IP address:</p>
                        <div class="code-block">
                            <pre>http://YOUR_SERVER_IP:5000</pre>
                            <button class="copy-button">Copy</button>
                        </div>
                    </div>
                </div>
                
                <div class="installation-step">
                    <div class="step-number">4</div>
                    <div class="step-content">
                        <h3>Install PostgreSQL (Optional)</h3>
                        <p>If needed, install PostgreSQL directly from the System Dashboard:</p>
                        <div class="code-block">
                            <pre>System → Dashboard → Install PostgreSQL</pre>
                            <button class="copy-button">Copy</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="mt-4 text-center">
                <a href="docs.php#installation" class="btn btn-primary">View Full Installation Guide</a>
            </div>
        </div>
    </div>
</section>

<!-- CTA Section -->
<section id="download" class="cta">
    <div class="container">
        <h2>Ready to Transform Your Database Management?</h2>
        <p>Join thousands of developers and database administrators who've simplified their database workflows with NEXDB.</p>
        <div class="cta-buttons">
            <a href="https://github.com/nexwinds/nexdb" class="btn btn-lg btn-light">Get NEXDB</a>
            <a href="docs.php" class="btn btn-lg btn-outline-light">Browse Documentation</a>
        </div>
    </div>
</section>

<?php
// Set any page-specific scripts
$page_scripts = <<<EOT
<script>
    // Copy button functionality
    document.querySelectorAll('.copy-button').forEach(button => {
        button.addEventListener('click', () => {
            const codeBlock = button.previousElementSibling;
            const textToCopy = codeBlock.textContent;
            
            navigator.clipboard.writeText(textToCopy).then(() => {
                button.textContent = 'Copied!';
                
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            });
        });
    });
</script>
EOT;

// Include footer
include 'includes/footer.php';
?>
