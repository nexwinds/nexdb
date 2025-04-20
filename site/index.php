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
                <p>Connect to and manage MySQL, PostgreSQL, MongoDB, and more from a single unified interface.</p>
                <a href="docs.php#supported-databases" class="btn btn-sm btn-outline">Learn More</a>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-search"></i>
                </div>
                <h3>Advanced Data Explorer</h3>
                <p>Powerful query builder with syntax highlighting, autocompletion, and visual results to explore your data with ease.</p>
                <a href="docs.php#data-explorer" class="btn btn-sm btn-outline">Learn More</a>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <h3>Performance Monitoring</h3>
                <p>Real-time monitoring of database performance with insights and optimization recommendations.</p>
                <a href="docs.php#performance-monitoring" class="btn btn-sm btn-outline">Learn More</a>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-shield-alt"></i>
                </div>
                <h3>Security Management</h3>
                <p>Manage users, roles, and permissions with fine-grained access control and security auditing.</p>
                <a href="docs.php#security" class="btn btn-sm btn-outline">Learn More</a>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-sync-alt"></i>
                </div>
                <h3>Backup & Recovery</h3>
                <p>Schedule automated backups and effortlessly restore databases when needed with point-in-time recovery.</p>
                <a href="docs.php#backup-recovery" class="btn btn-sm btn-outline">Learn More</a>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-terminal"></i>
                </div>
                <h3>Command Line Interface</h3>
                <p>Powerful CLI tools for automation, scripting, and integration with your development workflow.</p>
                <a href="docs.php#cli" class="btn btn-sm btn-outline">Learn More</a>
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
                        <h3>Install with NPM</h3>
                        <p>Install NEXDB globally using npm:</p>
                        <div class="code-block">
                            <pre>npm install -g nexdb</pre>
                            <button class="copy-button">Copy</button>
                        </div>
                    </div>
                </div>
                
                <div class="installation-step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <h3>Initialize Configuration</h3>
                        <p>Run the setup wizard to create your configuration:</p>
                        <div class="code-block">
                            <pre>nexdb init</pre>
                            <button class="copy-button">Copy</button>
                        </div>
                    </div>
                </div>
                
                <div class="installation-step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <h3>Start NEXDB</h3>
                        <p>Launch the NEXDB server:</p>
                        <div class="code-block">
                            <pre>nexdb start</pre>
                            <button class="copy-button">Copy</button>
                        </div>
                    </div>
                </div>
                
                <div class="installation-step">
                    <div class="step-number">4</div>
                    <div class="step-content">
                        <h3>Access Web Interface</h3>
                        <p>Open your browser and navigate to:</p>
                        <div class="code-block">
                            <pre>http://localhost:8080</pre>
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
            <a href="#" class="btn btn-lg btn-light">Download NEXDB</a>
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
