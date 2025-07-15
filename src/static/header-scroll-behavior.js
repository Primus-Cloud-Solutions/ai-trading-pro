// Header Scroll Behavior
// Adds dynamic header styling based on scroll position

class HeaderManager {
    constructor() {
        this.header = document.querySelector('.header');
        this.lastScrollTop = 0;
        this.scrollThreshold = 50;
        
        this.init();
    }
    
    init() {
        if (!this.header) return;
        
        // Add scroll event listener
        window.addEventListener('scroll', this.handleScroll.bind(this));
        
        // Add resize event listener for responsive behavior
        window.addEventListener('resize', this.handleResize.bind(this));
        
        // Initial setup
        this.handleScroll();
    }
    
    handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Add/remove scrolled class based on scroll position
        if (scrollTop > this.scrollThreshold) {
            this.header.classList.add('scrolled');
        } else {
            this.header.classList.remove('scrolled');
        }
        
        // Optional: Hide header on scroll down, show on scroll up
        // Uncomment the following code if you want this behavior
        /*
        if (scrollTop > this.lastScrollTop && scrollTop > 100) {
            // Scrolling down
            this.header.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            this.header.style.transform = 'translateY(0)';
        }
        */
        
        this.lastScrollTop = scrollTop;
    }
    
    handleResize() {
        // Recalculate any responsive behavior if needed
        this.handleScroll();
    }
}

// Smooth scrolling for navigation links
class SmoothScrollManager {
    constructor() {
        this.init();
    }
    
    init() {
        // Add click handlers to navigation links
        const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
        navLinks.forEach(link => {
            link.addEventListener('click', this.handleNavClick.bind(this));
        });
    }
    
    handleNavClick(event) {
        event.preventDefault();
        
        const targetId = event.target.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
            const headerHeight = document.querySelector('.header').offsetHeight;
            const targetPosition = targetElement.offsetTop - headerHeight - 20;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    }
}

// Mobile menu handler (if needed for responsive design)
class MobileMenuManager {
    constructor() {
        this.menuToggle = document.querySelector('.menu-toggle');
        this.navLinks = document.querySelector('.nav-links');
        this.isMenuOpen = false;
        
        this.init();
    }
    
    init() {
        if (!this.menuToggle) return;
        
        this.menuToggle.addEventListener('click', this.toggleMenu.bind(this));
        
        // Close menu when clicking outside
        document.addEventListener('click', (event) => {
            if (this.isMenuOpen && !event.target.closest('.nav-container')) {
                this.closeMenu();
            }
        });
        
        // Close menu on window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768 && this.isMenuOpen) {
                this.closeMenu();
            }
        });
    }
    
    toggleMenu() {
        if (this.isMenuOpen) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    }
    
    openMenu() {
        this.navLinks.classList.add('mobile-menu-open');
        this.menuToggle.classList.add('active');
        this.isMenuOpen = true;
        document.body.style.overflow = 'hidden';
    }
    
    closeMenu() {
        this.navLinks.classList.remove('mobile-menu-open');
        this.menuToggle.classList.remove('active');
        this.isMenuOpen = false;
        document.body.style.overflow = '';
    }
}

// Connection status manager
class ConnectionStatusManager {
    constructor() {
        this.statusElement = document.getElementById('connection-status');
        this.isConnected = true;
        
        this.init();
    }
    
    init() {
        if (!this.statusElement) return;
        
        // Simulate connection status changes
        this.startConnectionMonitoring();
    }
    
    startConnectionMonitoring() {
        // Check connection every 30 seconds
        setInterval(() => {
            this.checkConnection();
        }, 30000);
        
        // Initial check
        this.checkConnection();
    }
    
    checkConnection() {
        // Simulate connection check (in real app, this would be an actual API call)
        const isOnline = navigator.onLine;
        
        if (isOnline !== this.isConnected) {
            this.isConnected = isOnline;
            this.updateConnectionStatus();
        }
    }
    
    updateConnectionStatus() {
        if (this.statusElement) {
            this.statusElement.textContent = this.isConnected ? 'Connected' : 'Reconnecting...';
            this.statusElement.className = `connection-status ${this.isConnected ? 'connected' : 'disconnected'}`;
        }
    }
}

// Initialize all managers when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize header management
    window.headerManager = new HeaderManager();
    
    // Initialize smooth scrolling
    window.smoothScrollManager = new SmoothScrollManager();
    
    // Initialize mobile menu (if elements exist)
    window.mobileMenuManager = new MobileMenuManager();
    
    // Initialize connection status
    window.connectionStatusManager = new ConnectionStatusManager();
    
    // Add loading animation completion
    document.body.classList.add('loaded');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden
        console.log('Page hidden');
    } else {
        // Page is visible
        console.log('Page visible');
        // Refresh connection status when page becomes visible
        if (window.connectionStatusManager) {
            window.connectionStatusManager.checkConnection();
        }
    }
});

// Add CSS for mobile menu if needed
const mobileMenuStyles = `
    @media (max-width: 768px) {
        .menu-toggle {
            display: flex;
            flex-direction: column;
            cursor: pointer;
            padding: 0.5rem;
            gap: 0.25rem;
        }
        
        .menu-toggle span {
            width: 25px;
            height: 3px;
            background: var(--primary-green);
            transition: all 0.3s ease;
        }
        
        .menu-toggle.active span:nth-child(1) {
            transform: rotate(45deg) translate(6px, 6px);
        }
        
        .menu-toggle.active span:nth-child(2) {
            opacity: 0;
        }
        
        .menu-toggle.active span:nth-child(3) {
            transform: rotate(-45deg) translate(6px, -6px);
        }
        
        .nav-links {
            position: fixed;
            top: 65px;
            left: 0;
            right: 0;
            background: rgba(15, 15, 35, 0.98);
            backdrop-filter: blur(20px);
            flex-direction: column;
            padding: 2rem;
            transform: translateY(-100%);
            opacity: 0;
            transition: all 0.3s ease;
            border-bottom: 1px solid rgba(0, 255, 136, 0.2);
        }
        
        .nav-links.mobile-menu-open {
            transform: translateY(0);
            opacity: 1;
        }
        
        .nav-link {
            padding: 1rem;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .nav-link:last-child {
            border-bottom: none;
        }
    }
    
    .connection-status.disconnected {
        background: rgba(239, 68, 68, 0.9);
        border-color: rgba(239, 68, 68, 0.3);
    }
    
    .connection-status.disconnected::before {
        color: #ef4444;
        animation: none;
    }
    
    body.loaded {
        opacity: 1;
    }
    
    body {
        opacity: 0;
        transition: opacity 0.3s ease;
    }
`;

// Add the mobile menu styles to the document
const styleSheet = document.createElement('style');
styleSheet.textContent = mobileMenuStyles;
document.head.appendChild(styleSheet);

