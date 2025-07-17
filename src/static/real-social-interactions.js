// Real Social Interactions - AI Trading Pro
// Handles real influencer data, live social feeds, and genuine user engagement

class RealSocialManager {
    constructor() {
        this.currentAssetFilter = 'all';
        this.refreshIntervals = {};
        this.lastUpdateTime = Date.now();
        this.isConnected = true;
        this.engagementCache = new Map();
        
        // Configuration
        this.config = {
            refreshIntervals: {
                opinions: 8000,       // 8 seconds for real opinions
                activity: 12000,      // 12 seconds for activity feed
                telegram: 15000,      // 15 seconds for telegram updates
                stats: 30000          // 30 seconds for stats
            },
            maxRetries: 3,
            retryDelay: 2000
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startLiveDataFeeds();
        this.loadInitialData();
        this.setupConnectionMonitoring();
    }

    setupEventListeners() {
        // Asset filter tabs
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('asset-tab')) {
                this.handleAssetFilterChange(e.target);
            }
            
            // Comment functionality
            if (e.target.classList.contains('comment-btn')) {
                const opinionId = e.target.getAttribute('data-opinion-id');
                this.toggleCommentSection(opinionId);
            }
            
            // Like functionality
            if (e.target.classList.contains('like-btn')) {
                const opinionId = e.target.getAttribute('data-opinion-id');
                this.handleLikeToggle(opinionId);
            }
            
            // Share functionality
            if (e.target.classList.contains('share-btn')) {
                const opinionId = e.target.getAttribute('data-opinion-id');
                this.handleShare(opinionId);
            }
            
            // Submit comment
            if (e.target.classList.contains('submit-comment-btn')) {
                const opinionId = e.target.getAttribute('data-opinion-id');
                this.submitComment(opinionId);
            }
        });
    }

    async loadInitialData() {
        try {
            // Load all real social data
            await Promise.all([
                this.loadRealOpinions(),
                this.loadActivityFeed(),
                this.loadSocialStats(),
                this.loadTelegramUpdates()
            ]);
            
            this.updateConnectionStatus(true);
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.updateConnectionStatus(false);
          async loadRealOpinions() {
        try {
            // Use multi-platform API instead of real-social API
            const response = await fetch('/api/multi-platform/opinions/all?limit=8');
            const data = await response.json();
            
            if (data.success && data.opinions) {
                this.renderRealOpinions(data.opinions);
                console.log(`✅ Loaded ${data.opinions.length} multi-platform opinions`);
            } else {
                console.error('❌ Failed to load multi-platform opinions:', data.error);
                this.renderErrorState();
            }
        } catch (error) {
            console.error('❌ Error loading multi-platform opinions:', error);
            this.renderErrorState();
        }
    }Object.entries(opinionsData).forEach(([category, opinions]) => {
            if (this.currentAssetFilter === 'all' || this.currentAssetFilter === category) {
                opinions.forEach(opinion => {
                    html += this.createOpinionCard(opinion, category);
                });
            }
        });

        container.innerHTML = html;
        this.attachEngagementListeners();
        
        // Trigger event for dynamic platform links
        document.dispatchEvent(new CustomEvent('opinionsUpdated', {
            detail: { opinionsData }
        }));
    }

    createOpinionCard(opinion, category) {
        const categoryIcon = this.getCategoryIcon(category);
        const platformIcon = this.getPlatformIcon(opinion.platform);
        
        return `
            <div class="opinion-card" data-opinion-id="${opinion.id}" data-category="${category}">
                <div class="opinion-header">
                    <div class="influencer-info">
                        <div class="influencer-avatar">
                            <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(opinion.author)}&background=0D8043&color=fff&size=40" 
                                 alt="${opinion.author}" class="avatar-img">
                            ${opinion.verified ? '<div class="verified-badge">✓</div>' : ''}
                        </div>
                        <div class="influencer-details">
                            <div class="influencer-name">${opinion.author}</div>
                            <div class="influencer-handle">
                                ${platformIcon} ${opinion.handle} • ${opinion.followers}
                            </div>
                        </div>
                    </div>
                    <div class="opinion-meta">
                        <span class="category-badge ${category}">
                            ${categoryIcon} ${category.toUpperCase()}
                        </span>
                        <span class="time-ago">${opinion.time_ago}</span>
                        <a href="${opinion.url}" target="_blank" class="platform-link" title="View original post">
                            <i class="icon-external-link"></i>
                        </a>
                    </div>
                </div>
                
                <div class="opinion-content">
                    <p>${opinion.content}</p>
                    <div class="opinion-tags">
                        <span class="symbol-tag">${opinion.symbol}</span>
                        <span class="sentiment-tag ${opinion.sentiment.split(' ')[1]}">${opinion.sentiment}</span>
                    </div>
                </div>
                
                <div class="engagement-section">
                    <div class="engagement-stats">
                        <span class="stat-item">
                            <i class="icon-eye"></i> ${this.formatNumber(opinion.engagement.views)}
                        </span>
                        <span class="stat-item">
                            <i class="icon-heart"></i> ${this.formatNumber(opinion.engagement.likes)}
                        </span>
                        <span class="stat-item">
                            <i class="icon-share"></i> ${this.formatNumber(opinion.engagement.shares)}
                        </span>
                        <span class="stat-item">
                            <i class="icon-message-circle"></i> ${this.formatNumber(opinion.engagement.comments)}
                        </span>
                    </div>
                    
                    <div class="engagement-actions">
                        <button class="engagement-btn like-btn" data-opinion-id="${opinion.id}">
                            <i class="icon-heart"></i> Like
                        </button>
                        <button class="engagement-btn share-btn" data-opinion-id="${opinion.id}">
                            <i class="icon-share"></i> Share
                        </button>
                        <button class="engagement-btn comment-btn" data-opinion-id="${opinion.id}">
                            <i class="icon-message-circle"></i> Comment
                        </button>
                        <button class="engagement-btn bookmark-btn" data-opinion-id="${opinion.id}">
                            <i class="icon-bookmark"></i> Save
                        </button>
                    </div>
                </div>
                
                <div class="comment-section" id="comments-${opinion.id}" style="display: none;">
                    <div class="comment-form">
                        <input type="text" placeholder="Your name" class="comment-author" id="author-${opinion.id}">
                        <textarea placeholder="Share your thoughts..." class="comment-input" id="comment-${opinion.id}"></textarea>
                        <div class="comment-sentiment">
                            <label>Sentiment:</label>
                            <select class="sentiment-select" id="sentiment-${opinion.id}">
                                <option value="📈 bullish">📈 Bullish</option>
                                <option value="📉 bearish">📉 Bearish</option>
                                <option value="😐 neutral">😐 Neutral</option>
                            </select>
                        </div>
                        <button class="submit-comment-btn" data-opinion-id="${opinion.id}">Post Comment</button>
                    </div>
                    <div class="comments-list" id="comments-list-${opinion.id}"></div>
                </div>
            </div>
        `;
    }

    getCategoryIcon(category) {
        const icons = {
            'stocks': '📈',
            'crypto': '₿',
            'meme': '🚀',
            'forex': '💱'
        };
        return icons[category] || '📊';
    }

    getPlatformIcon(platform) {
        const icons = {
            'twitter': '🐦',
            'telegram': '✈️',
            'discord': '💬',
            'instagram': '📷'
        };
        return icons[platform] || '🌐';
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    handleAssetFilterChange(tab) {
        // Remove active class from all tabs
        document.querySelectorAll('.asset-tab').forEach(t => t.classList.remove('active'));
        
        // Add active class to clicked tab
        tab.classList.add('active');
        
        // Update current filter
        this.currentAssetFilter = tab.getAttribute('data-filter');
        
        // Reload opinions with new filter
        this.loadRealOpinions();
    }

    toggleCommentSection(opinionId) {
        const commentSection = document.getElementById(`comments-${opinionId}`);
        if (commentSection) {
            const isVisible = commentSection.style.display !== 'none';
            commentSection.style.display = isVisible ? 'none' : 'block';
            
            if (!isVisible) {
                // Load existing comments
                this.loadComments(opinionId);
            }
        }
    }

    async handleLikeToggle(opinionId) {
        try {
            const likeBtn = document.querySelector(`[data-opinion-id="${opinionId}"].like-btn`);
            const isLiked = likeBtn.classList.contains('liked');
            
            // Optimistic UI update
            likeBtn.classList.toggle('liked');
            
            const response = await fetch(`/api/social/engagement/like/${opinionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: isLiked ? 'unlike' : 'like'
                })
            });
            
            const data = await response.json();
            if (data.success) {
                // Update like count in UI
                this.updateEngagementCount(opinionId, 'likes', data.new_count);
            } else {
                // Revert optimistic update on failure
                likeBtn.classList.toggle('liked');
            }
        } catch (error) {
            console.error('Error toggling like:', error);
        }
    }

    async handleShare(opinionId) {
        try {
            const shareUrl = `${window.location.origin}/opinion/${opinionId}`;
            
            if (navigator.share) {
                await navigator.share({
                    title: 'Trading Insight',
                    text: 'Check out this trading insight from AI Trading Pro',
                    url: shareUrl
                });
            } else {
                // Fallback to clipboard
                await navigator.clipboard.writeText(shareUrl);
                this.showNotification('Link copied to clipboard!');
            }
            
            // Track share
            await fetch(`/api/social/engagement/share/${opinionId}`, {
                method: 'POST'
            });
            
        } catch (error) {
            console.error('Error sharing:', error);
        }
    }

    async submitComment(opinionId) {
        try {
            const author = document.getElementById(`author-${opinionId}`).value.trim();
            const content = document.getElementById(`comment-${opinionId}`).value.trim();
            const sentiment = document.getElementById(`sentiment-${opinionId}`).value;
            
            if (!author || !content) {
                this.showNotification('Please fill in all fields', 'error');
                return;
            }
            
            const response = await fetch(`/api/social/comments/${opinionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    author_name: author,
                    content: content,
                    sentiment: sentiment
                })
            });
            
            const data = await response.json();
            if (data.success) {
                // Clear form
                document.getElementById(`author-${opinionId}`).value = '';
                document.getElementById(`comment-${opinionId}`).value = '';
                
                // Reload comments
                this.loadComments(opinionId);
                
                // Update comment count
                this.updateEngagementCount(opinionId, 'comments', data.new_count);
                
                this.showNotification('Comment posted successfully!');
            } else {
                this.showNotification('Failed to post comment', 'error');
            }
        } catch (error) {
            console.error('Error submitting comment:', error);
            this.showNotification('Failed to post comment', 'error');
        }
    }

    async loadComments(opinionId) {
        try {
            const response = await fetch(`/api/social/comments/${opinionId}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderComments(opinionId, data.comments);
            }
        } catch (error) {
            console.error('Error loading comments:', error);
        }
    }

    renderComments(opinionId, comments) {
        const container = document.getElementById(`comments-list-${opinionId}`);
        if (!container) return;
        
        let html = '';
        comments.forEach(comment => {
            html += `
                <div class="comment-item">
                    <div class="comment-header">
                        <span class="comment-author">${comment.author_name}</span>
                        <span class="comment-sentiment ${comment.sentiment.split(' ')[1]}">${comment.sentiment}</span>
                        <span class="comment-time">${this.formatTimeAgo(comment.created_at)}</span>
                    </div>
                    <div class="comment-content">${comment.content}</div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }

    updateEngagementCount(opinionId, type, newCount) {
        const card = document.querySelector(`[data-opinion-id="${opinionId}"]`);
        if (card) {
            const statItem = card.querySelector(`.stat-item .icon-${type === 'likes' ? 'heart' : type === 'shares' ? 'share' : 'message-circle'}`);
            if (statItem && statItem.parentNode) {
                statItem.parentNode.innerHTML = `<i class="icon-${type === 'likes' ? 'heart' : type === 'shares' ? 'share' : 'message-circle'}"></i> ${this.formatNumber(newCount)}`;
            }
        }
    }

    async loadActivityFeed() {
        try {
            const response = await fetch('/api/real-social/activity/feed?limit=10');
            const data = await response.json();
            
            if (data.success) {
                this.renderActivityFeed(data.data);
            }
        } catch (error) {
            console.error('Error loading activity feed:', error);
        }
    }

    renderActivityFeed(activities) {
        const container = document.getElementById('activity-feed');
        if (!container) return;
        
        let html = '';
        activities.forEach(activity => {
            html += `
                <div class="activity-item">
                    <div class="activity-icon">${this.getActivityIcon(activity.type)}</div>
                    <div class="activity-content">
                        <div class="activity-text">
                            ${activity.type === 'opinion' ? 
                                `${activity.author} ${activity.action}` : 
                                activity.content
                            }
                        </div>
                        <div class="activity-time">${activity.time_ago}</div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }

    getActivityIcon(type) {
        const icons = {
            'opinion': '💬',
            'news': '📰',
            'trade': '💰',
            'alert': '🚨'
        };
        return icons[type] || '📊';
    }

    async loadSocialStats() {
        try {
            const response = await fetch('/api/real-social/stats');
            const data = await response.json();
            
            if (data.success) {
                this.updateSocialStats(data.data);
            }
        } catch (error) {
            console.error('Error loading social stats:', error);
        }
    }

    updateSocialStats(stats) {
        // Update live counters
        this.updateCounter('live-opinions-count', stats.live_opinions);
        this.updateCounter('active-sources-count', stats.total_influencers);
        this.updateCounter('avg-engagement-count', stats.avg_engagement);
        
        // Update category counts
        Object.entries(stats.categories).forEach(([category, count]) => {
            this.updateCounter(`${category}-count`, count);
        });
    }

    updateCounter(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = this.formatNumber(value);
        }
    }

    startLiveDataFeeds() {
        // Start all refresh intervals
        Object.entries(this.config.refreshIntervals).forEach(([key, interval]) => {
            this.refreshIntervals[key] = setInterval(() => {
                switch(key) {
                    case 'opinions':
                        this.loadRealOpinions();
                        break;
                    case 'activity':
                        this.loadActivityFeed();
                        break;
                    case 'stats':
                        this.loadSocialStats();
                        break;
                    case 'telegram':
                        this.loadTelegramUpdates();
                        break;
                }
            }, interval);
        });
    }

    async loadTelegramUpdates() {
        try {
            const response = await fetch('/api/real-social/telegram/updates?limit=5');
            const data = await response.json();
            
            if (data.success) {
                this.renderTelegramUpdates(data.data);
            }
        } catch (error) {
            console.error('Error loading telegram updates:', error);
        }
    }

    renderTelegramUpdates(updates) {
        const container = document.getElementById('telegram-updates');
        if (!container) return;
        
        let html = '';
        updates.forEach(update => {
            html += `
                <div class="telegram-update">
                    <div class="update-header">
                        <span class="channel-name">✈️ ${update.channel}</span>
                        <span class="update-time">${update.time_ago}</span>
                    </div>
                    <div class="update-content">${update.content}</div>
                    <div class="update-stats">
                        <span>👁️ ${this.formatNumber(update.engagement.views)}</span>
                        <span>❤️ ${this.formatNumber(update.engagement.reactions)}</span>
                        <span>↗️ ${this.formatNumber(update.engagement.forwards)}</span>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }

    setupConnectionMonitoring() {
        // Monitor connection status
        setInterval(() => {
            this.checkConnectionStatus();
        }, 30000); // Check every 30 seconds
    }

    async checkConnectionStatus() {
        try {
            const response = await fetch('/api/real-social/stats');
            this.updateConnectionStatus(response.ok);
        } catch (error) {
            this.updateConnectionStatus(false);
        }
    }

    updateConnectionStatus(isConnected) {
        this.isConnected = isConnected;
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = isConnected ? 'Connected' : 'Reconnecting...';
            statusElement.className = `connection-status ${isConnected ? 'connected' : 'disconnected'}`;
        }
    }

    updateLastUpdateTime() {
        this.lastUpdateTime = Date.now();
        const timeElement = document.getElementById('last-update-time');
        if (timeElement) {
            timeElement.textContent = new Date().toLocaleTimeString();
        }
    }

    formatTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInMinutes = Math.floor((now - time) / (1000 * 60));
        
        if (diffInMinutes < 1) return 'Just now';
        if (diffInMinutes < 60) return `${diffInMinutes} min ago`;
        if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} hr ago`;
        return `${Math.floor(diffInMinutes / 1440)} day ago`;
    }

    showNotification(message, type = 'success') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    attachEngagementListeners() {
        // Ensure all engagement buttons have proper event listeners
        document.querySelectorAll('.engagement-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
    }

    destroy() {
        // Clean up intervals
        Object.values(this.refreshIntervals).forEach(interval => {
            clearInterval(interval);
        });
        
        // Close websocket if exists
        if (this.websocketConnection) {
            this.websocketConnection.close();
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.realSocialManager = new RealSocialManager();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (window.realSocialManager) {
        window.realSocialManager.destroy();
    }
});

