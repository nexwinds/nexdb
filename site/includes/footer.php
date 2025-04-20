    </main>
    
    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-section">
                    <h3>NEXDB</h3>
                    <p>Advanced database management platform with powerful tools for database administration, exploration, and performance optimization.</p>
                    <div class="social-icons">
                        <a href="https://github.com/nexdb/nexdb" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                            <i class="fab fa-github"></i>
                        </a>
                        <a href="https://twitter.com/nexdb" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
                            <i class="fab fa-twitter"></i>
                        </a>
                        <a href="https://discord.gg/nexdb" target="_blank" rel="noopener noreferrer" aria-label="Discord">
                            <i class="fab fa-discord"></i>
                        </a>
                    </div>
                </div>
                
                <div class="footer-section">
                    <h3>Resources</h3>
                    <ul>
                        <li><a href="docs.php">Documentation</a></li>
                        <li><a href="docs.php#api-reference">API Reference</a></li>
                        <li><a href="index.php#features">Features</a></li>
                        <li><a href="index.php#installation">Installation</a></li>
                    </ul>
                </div>
                
                <div class="footer-section">
                    <h3>Support</h3>
                    <ul>
                        <li><a href="docs.php#troubleshooting">Troubleshooting</a></li>
                        <li><a href="https://github.com/nexdb/nexdb/issues" target="_blank" rel="noopener noreferrer">Report an Issue</a></li>
                        <li><a href="https://github.com/nexdb/nexdb/discussions" target="_blank" rel="noopener noreferrer">Community Forum</a></li>
                        <li><a href="mailto:support@nexdb.io">Contact Us</a></li>
                    </ul>
                </div>
                
                <div class="footer-section">
                    <h3>Legal</h3>
                    <ul>
                        <li><a href="privacy.php">Privacy Policy</a></li>
                        <li><a href="terms.php">Terms of Service</a></li>
                        <li><a href="license.php">License</a></li>
                    </ul>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>&copy; <?php echo date("Y"); ?> NEXDB. All rights reserved.</p>
                <p>Made with <i class="fas fa-heart"></i> by the NEXDB Team</p>
            </div>
        </div>
    </footer>
    
    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Main JavaScript -->
    <script>
        // Mobile menu toggle
        document.addEventListener('DOMContentLoaded', function() {
            const navbarToggle = document.getElementById('navbar-toggle');
            const navbarMenu = document.getElementById('navbar-menu');
            
            if (navbarToggle && navbarMenu) {
                navbarToggle.addEventListener('click', function() {
                    navbarMenu.classList.toggle('active');
                    navbarToggle.classList.toggle('active');
                });
            }
            
            // Add smooth scrolling for anchor links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    const href = this.getAttribute('href');
                    
                    // Only apply smooth scroll for actual anchor links, not "#" placeholders
                    if (href !== "#") {
                        e.preventDefault();
                        
                        const targetId = href.substring(href.indexOf('#') + 1);
                        const targetElement = document.getElementById(targetId);
                        
                        if (targetElement) {
                            window.scrollTo({
                                top: targetElement.offsetTop - 80, // Adjust for the fixed header
                                behavior: 'smooth'
                            });
                        }
                    }
                });
            });
        });
    </script>
    
    <!-- Page-specific JavaScript -->
    <?php if (isset($page_scripts)) echo $page_scripts; ?>
</body>
</html> 