
const pathToIframeMap = {
    'dashboard': 'dashboard-frame',
    'topology': 'topology-frame',
    'honeypot-page': 'honeypot-frame',
    'devices': 'devices-frame',
    'SIEM': 'SIEM-frame',
    'ips': 'ips-frame',
    'sniffer': 'sniffer-frame',
    'settings': 'settings-frame',
    'accounts': 'accounts-frame'
};

// Function to show iframe based on path
function showIframeForPath(path) {
    // Extract path without leading or trailing slashes
    path = path.replace(/^\/+|\/+$/g, '');
    
    // Get target iframe ID
    const iframeId = pathToIframeMap[path];
    
    if (!iframeId) {
        // Default to dashboard if path not found
        showIframe('dashboard-frame');
        setActiveNavLink('dashboard');
        return;
    }
    
    // Hide all iframes
    document.querySelectorAll('iframe').forEach(iframe => {
        iframe.style.display = 'none';
    });
    
    // Show the target iframe
    const iframe = document.getElementById(iframeId);
    if (iframe) {
        iframe.style.display = 'block';
        iframe.contentWindow.location.reload();
        
    }
    
    // Update active nav link
    setActiveNavLink(path);
}

// Function to set active nav link
function setActiveNavLink(path) {
    // Remove active class from all links
    document.querySelectorAll("#nav-menu a").forEach(link => {
        link.classList.remove("active");
    });
    
    // Add active class to matching link
    const activeLink = document.querySelector(`#nav-menu a[data-path="${path}"]`);
    if (activeLink) {
        activeLink.classList.add("active");
    }
}

// Function to show iframe by ID
function showIframe(iframeId) {
    // Hide all iframes
    document.querySelectorAll('iframe').forEach(iframe => {
        iframe.style.display = 'none';
    });
    
    // Show the target iframe
    const iframe = document.getElementById(iframeId);
    if (iframe) {
        iframe.style.display = 'block';
        iframe.contentWindow.location.reload();
    }
}

// Load user settings once
async function loadUserSettings() {
    try {
        const response = await fetch('/user-settings');
        if (response.ok) {
            const data = await response.json();
            document.documentElement.setAttribute('data-theme', data.theme);
            document.documentElement.setAttribute('data-font', data.font_size);
        }
    } catch (error) {
        console.error('Error loading user settings:', error);
        // Don't retry on error
    }
}

// Handle initial page load based on URL
function handleInitialLoad() {
    const path = window.location.pathname;
    showIframeForPath(path);
}

// Wait for DOM content to load
document.addEventListener('DOMContentLoaded', function() {
    // Load user settings
    loadUserSettings();
    
    // Handle initial page load
    handleInitialLoad();
    
    // Set up navigation between iframes
    const navLinks = document.querySelectorAll("#nav-menu a");
    navLinks.forEach(link => {
        link.addEventListener("click", function(e) {
            // Allow normal navigation for logout
            if (link.getAttribute("href") === "/logout") {
                return;
            }
            
            e.preventDefault();
            
            // Get the target path and iframe
            const path = link.getAttribute("data-path");
            const targetFrame = link.getAttribute("data-target");
            
            // Update URL without page reload
            window.history.pushState({path: path}, '', '/' + path);
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove("active"));
            
            // Add active class to clicked link
            link.classList.add("active");
            
            // Show the target iframe
            showIframe(targetFrame);
        });
    });
    
    // Handle browser back/forward navigation
    window.addEventListener('popstate', function(event) {
        const path = window.location.pathname;
        showIframeForPath(path);
    });
});