// Dynamic Platform Links Handler
// Enhanced functionality for dynamic social media links

class DynamicPlatformLinks {
    constructor() {
        this.linkCache = new Map();
        this.linkValidation = new Map();
        this.init();
    }

    init() {
        console.log('🔗 Dynamic Platform Links initialized');
        this.setupLinkHandlers();
        this.setupLinkValidation();
        this.setupLinkPreview();
    }

    setupLinkHandlers() {
        // Handle platform link clicks with analytics
        document.addEventListener('click', (event) => {
            const platformLink = event.target.closest('.platform-link');
            if (platformLink) {
                this.handlePlatformLinkClick(platformLink, event);
            }
        });
    }

    handlePlatformLinkClick(link, event) {
        const url = link.href;
        const platform = this.detectPlatform(url);
        const opinionId = link.closest('.opinion-card')?.dataset.opinionId;

        console.log(`🔗 Opening ${platform} link:`, url);

        // Track click analytics
        this.trackLinkClick(opinionId, platform, url);

        // Add visual feedback
        this.addClickFeedback(link);

        // Let the browser handle the actual navigation
        // The link will open in a new tab due to target="_blank"
    }

    detectPlatform(url) {
        if (url.includes('twitter.com') || url.includes('x.com')) return 'twitter';
        if (url.includes('instagram.com')) return 'instagram';
        if (url.includes('discord.com')) return 'discord';
        if (url.includes('t.me')) return 'telegram';
        return 'unknown';
    }

    addClickFeedback(link) {
        // Add temporary visual feedback
        link.classList.add('clicked');
        link.style.transform = 'scale(0.95)';
        
        setTimeout(() => {
            link.classList.remove('clicked');
            link.style.transform = '';
        }, 200);
    }

    trackLinkClick(opinionId, platform, url) {
        // Track link clicks for analytics
        const clickData = {
            opinionId,
            platform,
            url,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent
        };

        // Send to analytics endpoint (if available)
        fetch('/api/analytics/link-click', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(clickData)
        }).catch(error => {
            console.log('Analytics tracking failed:', error);
        });

        // Store in local analytics
        this.storeLocalAnalytics(clickData);
    }

    storeLocalAnalytics(clickData) {
        const analytics = JSON.parse(localStorage.getItem('platformLinkAnalytics') || '[]');
        analytics.push(clickData);
        
        // Keep only last 100 clicks
        if (analytics.length > 100) {
            analytics.splice(0, analytics.length - 100);
        }
        
        localStorage.setItem('platformLinkAnalytics', JSON.stringify(analytics));
    }

    setupLinkValidation() {
        // Validate platform links periodically
        setInterval(() => {
            this.validateVisibleLinks();
        }, 30000); // Every 30 seconds
    }

    validateVisibleLinks() {
        const visibleLinks = document.querySelectorAll('.platform-link:not(.validated)');
        
        visibleLinks.forEach(link => {
            this.validateLink(link);
        });
    }

    validateLink(link) {
        const url = link.href;
        const platform = this.detectPlatform(url);
        
        // Mark as validated to avoid re-checking
        link.classList.add('validated');
        
        // Add platform-specific styling
        link.classList.add(platform);
        
        // Update tooltip with platform info
        const platformName = this.getPlatformDisplayName(platform);
        link.title = `View original ${platformName} post`;
    }

    getPlatformDisplayName(platform) {
        const names = {
            'twitter': 'Twitter',
            'instagram': 'Instagram',
            'discord': 'Discord',
            'telegram': 'Telegram'
        };
        return names[platform] || 'Social Media';
    }

    setupLinkPreview() {
        // Add hover preview functionality
        document.addEventListener('mouseenter', (event) => {
            const platformLink = event.target.closest('.platform-link');
            if (platformLink) {
                this.showLinkPreview(platformLink);
            }
        }, true);

        document.addEventListener('mouseleave', (event) => {
            const platformLink = event.target.closest('.platform-link');
            if (platformLink) {
                this.hideLinkPreview();
            }
        }, true);
    }

    showLinkPreview(link) {
        const url = link.href;
        const platform = this.detectPlatform(url);
        const platformName = this.getPlatformDisplayName(platform);
        
        // Create preview tooltip
        const preview = document.createElement('div');
        preview.className = 'platform-link-preview';
        preview.innerHTML = `
            <div class="preview-header">
                <i class="platform-icon ${platform}"></i>
                <span>${platformName}</span>
            </div>
            <div class="preview-url">${this.shortenUrl(url)}</div>
            <div class="preview-action">Click to open in new tab</div>
        `;
        
        // Position and show preview
        document.body.appendChild(preview);
        this.positionPreview(preview, link);
        
        // Store reference for cleanup
        this.currentPreview = preview;
    }

    hideLinkPreview() {
        if (this.currentPreview) {
            this.currentPreview.remove();
            this.currentPreview = null;
        }
    }

    positionPreview(preview, link) {
        const linkRect = link.getBoundingClientRect();
        const previewRect = preview.getBoundingClientRect();
        
        let top = linkRect.bottom + 8;
        let left = linkRect.left + (linkRect.width / 2) - (previewRect.width / 2);
        
        // Adjust if preview goes off screen
        if (left < 8) left = 8;
        if (left + previewRect.width > window.innerWidth - 8) {
            left = window.innerWidth - previewRect.width - 8;
        }
        
        if (top + previewRect.height > window.innerHeight - 8) {
            top = linkRect.top - previewRect.height - 8;
        }
        
        preview.style.top = `${top}px`;
        preview.style.left = `${left}px`;
    }

    shortenUrl(url) {
        if (url.length <= 50) return url;
        return url.substring(0, 25) + '...' + url.substring(url.length - 20);
    }

    // Public method to refresh links when new opinions are loaded
    refreshLinks() {
        console.log('🔄 Refreshing platform links');
        
        // Clear validation cache
        this.linkValidation.clear();
        
        // Re-validate all links
        const allLinks = document.querySelectorAll('.platform-link');
        allLinks.forEach(link => {
            link.classList.remove('validated');
            this.validateLink(link);
        });
    }

    // Get analytics data
    getAnalytics() {
        return JSON.parse(localStorage.getItem('platformLinkAnalytics') || '[]');
    }

    // Clear analytics data
    clearAnalytics() {
        localStorage.removeItem('platformLinkAnalytics');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dynamicPlatformLinks = new DynamicPlatformLinks();
});

// Refresh links when new opinions are loaded
document.addEventListener('opinionsUpdated', () => {
    if (window.dynamicPlatformLinks) {
        window.dynamicPlatformLinks.refreshLinks();
    }
});

// Export for use in other scripts
window.DynamicPlatformLinks = DynamicPlatformLinks;

