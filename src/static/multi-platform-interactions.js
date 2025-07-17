// Multi-Platform Social Interactions
// Handles Telegram, Discord, Reddit integration with working links

class MultiPlatformSocialManager {
    constructor() {
        this.currentAssetFilter = 'all';
        this.refreshInterval = 15000; // 15 seconds
        this.connectionStatus = false;
        this.init();
    }

    async init() {
        console.log('🚀 Initializing Multi-Platform Social Manager...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadInitialData();
        
        // Start auto-refresh
        this.startAutoRefresh();
        
        console.log('✅ Multi-Platform Social Manager initialized');
    }

    setupEventListeners() {
        // Asset filter buttons
        document.querySelectorAll('.asset-filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.currentAssetFilter = e.target.dataset.filter;
                this.updateFilterButtons();
                this.loadMultiPlatformOpinions();
            });
        });

        // Refresh button
        const refreshBtn = document.querySelector('.refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadInitialData();
            });
        }
    }

    async loadInitialData() {
        try {
            console.log('📡 Loading multi-platform data...');
            
            await Promise.all([
                this.loadMultiPlatformOpinions(),
                this.loadMultiPlatformStats()
            ]);
            
            this.updateConnectionStatus(true);
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.updateConnectionStatus(false);
        }
    }

    async loadMultiPlatformOpinions() {
        try {
            const response = await fetch('/api/multi-platform/opinions/all?limit=8');
            const data = await response.json();
            
            if (data.success && data.opinions) {
                this.renderMultiPlatformOpinions(data.opinions);
                console.log(`✅ Loaded ${data.opinions.length} multi-platform opinions`);
            } else {
                console.error('❌ Failed to load multi-platform opinions:', data.error);
                this.renderErrorState();
            }
        } catch (error) {
            console.error('❌ Error loading multi-platform opinions:', error);
            this.renderErrorState();
        }
    }

    async loadMultiPlatformStats() {
        try {
            const response = await fetch('/api/multi-platform/stats');
            const data = await response.json();
            
            if (data.success && data.stats) {
                this.updateStatsDisplay(data.stats);
                console.log('✅ Loaded multi-platform stats');
            }
        } catch (error) {
            console.error('❌ Error loading multi-platform stats:', error);
        }
    }

    renderMultiPlatformOpinions(opinions) {
        const container = document.querySelector('.kol-opinions-container');
        if (!container) return;

        let html = '';
        
        opinions.forEach(opinion => {
            html += this.createOpinionCard(opinion);
        });

        container.innerHTML = html;
        this.attachEngagementListeners();
        
        // Trigger event for dynamic platform links
        document.dispatchEvent(new CustomEvent('opinionsUpdated', {
            detail: { opinions: opinions }
        }));
    }

    createOpinionCard(opinion) {
        const platformIcon = this.getPlatformIcon(opinion.platform);
        const platformColor = this.getPlatformColor(opinion.platform);
        const timeAgo = this.getTimeAgo(opinion.timestamp);
        
        return `
            <div class="opinion-card" data-opinion-id="${opinion.id}">
                <div class="opinion-header">
                    <div class="author-info">
                        <div class="author-avatar">
                            <i class="${platformIcon}" style="color: ${platformColor}"></i>
                        </div>
                        <div class="author-details">
                            <div class="author-name">
                                ${opinion.author}
                                ${opinion.verified ? '<i class="fas fa-check-circle verified-badge"></i>' : ''}
                            </div>
                            <div class="opinion-meta">
                                <span class="platform-badge" style="background-color: ${platformColor}">
                                    ${opinion.platform.toUpperCase()}
                                </span>
                                <span class="time-ago">${timeAgo}</span>
                            </div>
                        </div>
                    </div>
                    <div class="platform-link">
                        <a href="${opinion.url}" target="_blank" rel="noopener noreferrer" 
                           class="platform-link-btn" style="border-color: ${platformColor}; color: ${platformColor}">
                            <i class="fas fa-external-link-alt"></i>
                            View Original
                        </a>
                    </div>
                </div>
                
                <div class="opinion-content">
                    <p>${opinion.content}</p>
                </div>
                
                <div class="opinion-engagement">
                    <div class="engagement-stats">
                        <span class="stat">
                            <i class="fas fa-eye"></i>
                            ${this.formatNumber(opinion.engagement.views)}
                        </span>
                        <span class="stat">
                            <i class="fas fa-heart"></i>
                            ${this.formatNumber(opinion.engagement.likes)}
                        </span>
                        <span class="stat">
                            <i class="fas fa-share"></i>
                            ${this.formatNumber(opinion.engagement.shares)}
                        </span>
                        <span class="stat">
                            <i class="fas fa-comment"></i>
                            ${this.formatNumber(opinion.engagement.comments)}
                        </span>
                    </div>
                    
                    <div class="engagement-actions">
                        <button class="engagement-btn like-btn" data-action="like" data-opinion-id="${opinion.id}">
                            <i class="fas fa-heart"></i>
                            Like
                        </button>
                        <button class="engagement-btn comment-btn" data-action="comment" data-opinion-id="${opinion.id}">
                            <i class="fas fa-comment"></i>
                            Comment
                        </button>
                        <button class="engagement-btn share-btn" data-action="share" data-opinion-id="${opinion.id}">
                            <i class="fas fa-share"></i>
                            Share
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    getPlatformIcon(platform) {
        const icons = {
            'telegram': 'fab fa-telegram-plane',
            'discord': 'fab fa-discord',
            'reddit': 'fab fa-reddit-alien',
            'twitter': 'fab fa-twitter'
        };
        return icons[platform] || 'fas fa-globe';
    }

    getPlatformColor(platform) {
        const colors = {
            'telegram': '#0088cc',
            'discord': '#5865f2',
            'reddit': '#ff4500',
            'twitter': '#1da1f2'
        };
        return colors[platform] || '#00d4aa';
    }

    attachEngagementListeners() {
        document.querySelectorAll('.engagement-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.closest('.engagement-btn').dataset.action;
                const opinionId = e.target.closest('.engagement-btn').dataset.opinionId;
                this.handleEngagement(action, opinionId, e.target.closest('.engagement-btn'));
            });
        });

        // Platform link click tracking
        document.querySelectorAll('.platform-link-btn').forEach(link => {
            link.addEventListener('click', (e) => {
                const url = e.target.closest('a').href;
                console.log(`🔗 Platform link clicked: ${url}`);
                
                // Track click analytics
                this.trackPlatformLinkClick(url);
            });
        });
    }

    async handleEngagement(action, opinionId, button) {
        try {
            const response = await fetch('/api/engagement/interact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    opinion_id: opinionId,
                    action: action,
                    platform: 'multi-platform'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.updateEngagementUI(button, action, data.new_count);
                console.log(`✅ ${action} successful for opinion ${opinionId}`);
            }
        } catch (error) {
            console.error(`❌ Error with ${action}:`, error);
        }
    }

    updateEngagementUI(button, action, newCount) {
        button.classList.add('engaged');
        
        // Update count in stats
        const opinionCard = button.closest('.opinion-card');
        const statElement = opinionCard.querySelector(`.stat i.fa-${action === 'like' ? 'heart' : action}`);
        if (statElement && newCount) {
            statElement.parentElement.textContent = this.formatNumber(newCount);
        }
        
        // Visual feedback
        button.style.transform = 'scale(1.1)';
        setTimeout(() => {
            button.style.transform = 'scale(1)';
        }, 200);
    }

    trackPlatformLinkClick(url) {
        // Send analytics data
        fetch('/api/multi-platform/analytics/click', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent
            })
        }).catch(error => {
            console.error('Analytics tracking failed:', error);
        });
    }

    updateStatsDisplay(stats) {
        // Update live stats
        const liveOpinionsEl = document.querySelector('.stat-value[data-stat="live-opinions"]');
        const activeSourcesEl = document.querySelector('.stat-value[data-stat="active-sources"]');
        const avgEngagementEl = document.querySelector('.stat-value[data-stat="avg-engagement"]');

        if (liveOpinionsEl) liveOpinionsEl.textContent = stats.live_opinions;
        if (activeSourcesEl) activeSourcesEl.textContent = stats.active_sources;
        if (avgEngagementEl) avgEngagementEl.textContent = stats.avg_engagement;
    }

    updateConnectionStatus(connected) {
        this.connectionStatus = connected;
        const statusEl = document.querySelector('.connection-status');
        if (statusEl) {
            statusEl.textContent = connected ? 'Connected' : 'Disconnected';
            statusEl.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
        }
    }

    updateFilterButtons() {
        document.querySelectorAll('.asset-filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === this.currentAssetFilter);
        });
    }

    startAutoRefresh() {
        setInterval(() => {
            if (this.connectionStatus) {
                this.loadMultiPlatformOpinions();
            }
        }, this.refreshInterval);
    }

    renderErrorState() {
        const container = document.querySelector('.kol-opinions-container');
        if (!container) return;

        container.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Unable to load social data</h3>
                <p>Please check your connection and try again.</p>
                <button class="retry-btn" onclick="multiPlatformManager.loadInitialData()">
                    <i class="fas fa-redo"></i>
                    Retry
                </button>
            </div>
        `;
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    getTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);

        if (diffInSeconds < 60) {
            return 'Just now';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes}m ago`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours}h ago`;
        } else {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days}d ago`;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.multiPlatformManager = new MultiPlatformSocialManager();
});

