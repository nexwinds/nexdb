<?php
// Get the current page to highlight the active nav item
$current_page = basename($_SERVER['PHP_SELF']);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo isset($page_title) ? $page_title . ' - NEXDB' : 'NEXDB - Advanced Database Management Platform'; ?></title>
    <meta name="description" content="<?php echo isset($page_description) ? $page_description : 'NEXDB is an advanced database management platform with powerful tools for database administration, exploration, and performance optimization.'; ?>">
    
    <!-- Favicon -->
    <link rel="icon" href="assets/img/favicon.ico" type="image/x-icon">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    
    <!-- Global CSS -->
    <link rel="stylesheet" href="global.css">
    
    <!-- Page-specific CSS -->
    <?php if (isset($page_css)) echo $page_css; ?>
    
    <!-- Additional head content -->
    <?php if (isset($head_additional)) echo $head_additional; ?>
</head>
<body>
    <!-- Skip Link for Accessibility -->
    <a href="#main-content" class="sr-only">Skip to main content</a>
    
    <!-- Navigation Bar -->
    <nav class="navbar">
        <div class="container navbar-container">
            <a href="index.php" class="navbar-logo">
                <img src="assets/img/logo.png" alt="NEXDB Logo">
                NEXDB
            </a>
            
            <button class="navbar-toggle" id="navbar-toggle" aria-label="Toggle navigation">
                <i class="fas fa-bars"></i>
            </button>
            
            <ul class="navbar-menu" id="navbar-menu">
                <li class="navbar-item">
                    <a href="index.php" class="<?php echo $current_page === 'index.php' ? 'active' : ''; ?>">Home</a>
                </li>
                <li class="navbar-item">
                    <a href="index.php#features" class="<?php echo isset($_GET['section']) && $_GET['section'] === 'features' ? 'active' : ''; ?>">Features</a>
                </li>
                <li class="navbar-item">
                    <a href="index.php#installation" class="<?php echo isset($_GET['section']) && $_GET['section'] === 'installation' ? 'active' : ''; ?>">Installation</a>
                </li>
                <li class="navbar-item">
                    <a href="docs.php" class="<?php echo $current_page === 'docs.php' ? 'active' : ''; ?>">Documentation</a>
                </li>
                <li class="navbar-item">
                    <a href="https://github.com/nexdb/nexdb" target="_blank" rel="noopener noreferrer">GitHub</a>
                </li>
                <li class="navbar-cta">
                    <a href="index.php#download" class="btn btn-primary">Download</a>
                </li>
            </ul>
        </div>
    </nav>

    <!-- Main Content -->
    <main id="main-content"> 