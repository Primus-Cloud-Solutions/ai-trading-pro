// Enhanced Homepage Interactions - AI Trading Pro
// Handles real-time data, live KOL opinions, and interactive prediction comments

class EnhancedHomepageManager {
    constructor() {
        this.currentAssetFilter = 'all';
        this.currentPredictionFilter = 'all';
        this.refreshIntervals = {};
        this.websocketConnection = null;
        this.lastUpdateTime = Date.now();
        this.isConnected = true;
        
        // Configuration
        this.config = {
            refreshIntervals: {
                predictions: 10000,    // 10 seconds
                kols: 15000,          // 15 seconds
                activity: 20000,      // 20 seconds
                ticker: 5000,         // 5 seconds
                algorithm: 8000       // 8 seconds
            },
            maxRetries: 3,
            retryDelay: 2000
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeChart();
        this.startLiveDataFeeds();
        this.loadInitialData();
        this.setupConnectionMonitoring();
    }

    setupEventListeners() {
        // Filter tabs for predictions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-tab')) {
                this.handlePredictionFilterChange(e.target);
            }
            
            if (e.target.classList.contains('asset-tab')) {
                this.handleAssetFilterChange(e.target);
            }
            
            if (e.target.classList.contains('add-comment-btn')) {
                const symbol = e.target.getAttribute('data-symbol');
                this.toggleCommentForm(symbol);
            }
            
            if (e.target.classList.contains('submit-comment')) {
                const symbol = e.target.getAttribute('data-symbol');
                this.submitComment(symbol);
            }
            
            if (e.target.classList.contains('cancel-comment')) {
                const symbol = e.target.getAttribute('data-symbol');
                this.toggleCommentForm(symbol);
            }
        });

        // Smooth scrolling for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Auto-hide header on scroll
        this.setupHeaderScroll();
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'r':
                        e.preventDefault();
                        this.refreshAllData();
                        break;
                    case '1':
                        e.preventDefault();
                        this.setAssetFilter('stocks');
                        break;
                    case '2':
                        e.preventDefault();
                        this.setAssetFilter('crypto');
                        break;
                    case '3':
                        e.preventDefault();
                        this.setAssetFilter('meme');
                        break;
                }
            }
        });
    }

    setupHeaderScroll() {
        let lastScrollTop = 0;
        const header = document.querySelector('.header');
        
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                header.style.transform = 'translateY(-100%)';
            } else {
                header.style.transform = 'translateY(0)';
            }
            
            lastScrollTop = scrollTop;
        });
    }

    initializeChart() {
        const canvas = document.getElementById('liveChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        this.chartData = {
            labels: [],
            datasets: [{
                label: 'Portfolio Value',
                data: [],
                borderColor: '#00ff88',
                backgroundColor: 'rgba(0, 255, 136, 0.1)',
                tension: 0.4
            }]
        };
        
        // Simple chart animation
        this.animateChart(ctx);
    }

    animateChart(ctx) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;
        
        // Generate sample data points
        const points = [];
        for (let i = 0; i < 50; i++) {
            const x = (i / 49) * width;
            const y = height/2 + Math.sin(i * 0.2) * 50 + Math.random() * 20 - 10;
            points.push({x, y});
        }
        
        let animationFrame = 0;
        const animate = () => {
            ctx.clearRect(0, 0, width, height);
            
            // Draw grid
            ctx.strokeStyle = 'rgba(0, 255, 136, 0.1)';
            ctx.lineWidth = 1;
            for (let i = 0; i < 10; i++) {
                const y = (i / 9) * height;
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(width, y);
                ctx.stroke();
            }
            
            // Draw chart line
            ctx.strokeStyle = '#00ff88';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            points.forEach((point, index) => {
                const animatedY = point.y + Math.sin(animationFrame * 0.02 + index * 0.1) * 5;
                if (index === 0) {
                    ctx.moveTo(point.x, animatedY);
                } else {
                    ctx.lineTo(point.x, animatedY);
                }
            });
            
            ctx.stroke();
            
            // Draw glow effect
            ctx.shadowColor = '#00ff88';
            ctx.shadowBlur = 10;
            ctx.stroke();
            ctx.shadowBlur = 0;
            
            animationFrame++;
            requestAnimationFrame(animate);
        };
        
        animate();
    }

    startLiveDataFeeds() {
        // Start all live data feeds
        this.startPredictionFeed();
        this.startKOLFeed();
        this.startActivityFeed();
        this.startTickerFeed();
        this.startAlgorithmFeed();
        
        console.log('🔴 All live data feeds started');
    }

    startPredictionFeed() {
        this.refreshIntervals.predictions = setInterval(() => {
            this.loadPredictions();
        }, this.config.refreshIntervals.predictions);
    }

    startKOLFeed() {
        this.refreshIntervals.kols = setInterval(() => {
            this.loadKOLOpinions();
        }, this.config.refreshIntervals.kols);
    }

    startActivityFeed() {
        this.refreshIntervals.activity = setInterval(() => {
            this.loadActivityFeed();
        }, this.config.refreshIntervals.activity);
    }

    startTickerFeed() {
        this.refreshIntervals.ticker = setInterval(() => {
            this.updateTicker();
        }, this.config.refreshIntervals.ticker);
    }

    startAlgorithmFeed() {
        this.refreshIntervals.algorithm = setInterval(() => {
            this.updateAlgorithmStats();
        }, this.config.refreshIntervals.algorithm);
    }

    async loadInitialData() {
        this.showLoadingState();
        
        try {
            await Promise.all([
                this.loadPredictions(),
                this.loadKOLOpinions(),
                this.loadActivityFeed(),
                this.updateTicker(),
                this.updateAlgorithmStats()
            ]);
            
            this.hideLoadingState();
            this.updateConnectionStatus(true);
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showErrorState();
        }
    }

    async loadPredictions() {
        try {
            const response = await fetch(`/api/live/predictions/live?market=${this.currentPredictionFilter}&limit=6`);
            const data = await response.json();
            
            if (data.success) {
                this.renderPredictions(data.data);
                this.updateLastUpdateTime();
            }
        } catch (error) {
            console.error('Error loading predictions:', error);
            this.handleConnectionError();
        }
    }

    renderPredictions(predictions) {
        const grid = document.getElementById('predictionsGrid');
        if (!grid) return;

        grid.innerHTML = '';
        
        predictions.forEach(prediction => {
            const card = this.createPredictionCard(prediction);
            grid.appendChild(card);
        });

        // Add stagger animation
        this.animateCards('.prediction-card');
    }

    createPredictionCard(prediction) {
        const card = document.createElement('div');
        card.className = 'prediction-card';
        card.setAttribute('data-symbol', prediction.symbol);
        
        const predictionType = prediction.action.toLowerCase();
        const typeClass = predictionType === 'buy' ? 'buy' : 'sell';
        const returnColor = prediction.expected_return >= 0 ? '#00ff88' : '#ff6b6b';
        const confidenceColor = prediction.confidence >= 0.7 ? '#00ff88' : (prediction.confidence >= 0.5 ? '#4dabf7' : '#ff6b6b');
        
        card.innerHTML = `
            <div class="prediction-header">
                <div class="stock-symbol">${prediction.symbol}</div>
                <div class="prediction-type ${typeClass}">
                    <i class="fas fa-${predictionType === 'buy' ? 'arrow-up' : 'arrow-down'}"></i>
                    ${prediction.action}
                </div>
            </div>
            <div class="prediction-details">
                <div class="price-info">
                    <span><i class="fas fa-dollar-sign"></i> Current: $${prediction.current_price.toFixed(2)}</span>
                    <span><i class="fas fa-target"></i> Target: $${prediction.target_price.toFixed(2)}</span>
                </div>
                <div class="price-info">
                    <span class="confidence" style="color: ${confidenceColor}">
                        <i class="fas fa-brain"></i> ${Math.round(prediction.confidence * 100)}% confidence
                    </span>
                    <span style="color: ${returnColor}; font-weight: 600;">
                        ${prediction.expected_return >= 0 ? '+' : ''}${prediction.expected_return.toFixed(1)}%
                    </span>
                </div>
                <div class="strategy-info">
                    <i class="fas fa-cogs"></i> Strategy: ${prediction.strategy || 'multi_strategy'}
                </div>
                <div class="strategy-info">
                    <i class="fas fa-shield-alt"></i> Risk: ${prediction.risk_level || 'Medium'}
                </div>
                <p class="reasoning">
                    <i class="fas fa-lightbulb"></i> ${prediction.reasoning}
                </p>
            </div>
            <div class="prediction-actions">
                <button class="action-btn ${typeClass}" onclick="window.enhancedHomepage.handleQuickTrade('${prediction.symbol}', '${prediction.action}')">
                    <i class="fas fa-bolt"></i> Quick ${prediction.action}
                </button>
                <button class="action-btn secondary" onclick="window.enhancedHomepage.viewDetails('${prediction.symbol}')">
                    <i class="fas fa-chart-line"></i> View Chart
                </button>
            </div>
            <div class="comments-section">
                <div class="comments-header">
                    <span class="comments-count">
                        <i class="fas fa-comments"></i> <span id="count-${prediction.symbol}">0</span> comments
                    </span>
                    <button class="add-comment-btn" data-symbol="${prediction.symbol}">
                        <i class="fas fa-plus"></i> Add Comment
                    </button>
                </div>
                <div class="comment-form" id="form-${prediction.symbol}">
                    <div class="comment-form-header">
                        <input type="text" class="author-input" placeholder="Your name (optional)" id="author-${prediction.symbol}">
                        <select class="sentiment-select" id="sentiment-${prediction.symbol}">
                            <option value="neutral">😐 Neutral</option>
                            <option value="bullish">📈 Bullish</option>
                            <option value="bearish">📉 Bearish</option>
                        </select>
                    </div>
                    <textarea class="comment-input" placeholder="Share your thoughts on this ${prediction.action} signal for ${prediction.symbol}..." id="input-${prediction.symbol}"></textarea>
                    <div class="comment-actions">
                        <button class="submit-comment" data-symbol="${prediction.symbol}">
                            <i class="fas fa-paper-plane"></i> Post
                        </button>
                        <button class="cancel-comment" data-symbol="${prediction.symbol}">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                    </div>
                </div>
                <div class="comments-list" id="comments-${prediction.symbol}">
                    <!-- Comments will be loaded here -->
                </div>
            </div>
        `;
        
        // Load existing comments
        this.loadComments(prediction.symbol);
        
        return card;
    }

    async loadKOLOpinions() {
        try {
            const response = await fetch(`/api/live/kols/opinions?asset_class=${this.currentAssetFilter}&limit=12`);
            const data = await response.json();
            
            if (data.success) {
                this.renderKOLOpinions(data.data);
                this.updateKOLStats(data.data);
            }
        } catch (error) {
            console.error('Error loading KOL opinions:', error);
            this.handleConnectionError();
        }
    }

    renderKOLOpinions(opinions) {
        const grid = document.getElementById('kolGrid');
        if (!grid) return;

        grid.innerHTML = '';
        
        opinions.forEach(opinion => {
            const card = this.createKOLCard(opinion);
            grid.appendChild(card);
        });

        // Add stagger animation
        this.animateCards('.kol-opinion');
    }

    createKOLCard(opinion) {
        const card = document.createElement('div');
        card.className = 'kol-opinion';
        
        const sentimentClass = opinion.sentiment.toLowerCase();
        const platformIcon = this.getPlatformIcon(opinion.platform);
        const sentimentIcon = this.getSentimentIcon(opinion.sentiment);
        
        // Add trending indicator
        const trendingBadge = opinion.trending ? '<span class="trending-badge"><i class="fas fa-fire"></i> Trending</span>' : '';
        
        card.innerHTML = `
            <div class="kol-header">
                <div class="kol-avatar">${opinion.name.charAt(0)}</div>
                <div class="kol-info">
                    <h4>${opinion.name} ${opinion.verified ? '<i class="fas fa-check-circle verified"></i>' : ''}</h4>
                    <div class="kol-platform">
                        <i class="${platformIcon}"></i> ${opinion.platform}
                        ${opinion.platform_handle ? `• ${opinion.platform_handle}` : ''}
                    </div>
                </div>
                <div class="kol-actions">
                    <button class="follow-btn" onclick="window.enhancedHomepage.followKOL('${opinion.name}')">
                        <i class="fas fa-user-plus"></i>
                    </button>
                </div>
            </div>
            <div class="kol-content">${opinion.content}</div>
            ${opinion.symbol ? `<div class="kol-symbol"><i class="fas fa-tag"></i> ${opinion.symbol}</div>` : ''}
            ${trendingBadge}
            <div class="kol-meta">
                <span class="kol-time">
                    <i class="fas fa-clock"></i> ${opinion.time_ago}
                </span>
                <span class="kol-sentiment ${sentimentClass}">
                    ${sentimentIcon} ${opinion.sentiment}
                </span>
                <span class="kol-engagement">
                    <i class="fas fa-heart"></i> ${opinion.engagement_score || 0}
                </span>
            </div>
            <div class="kol-actions-bar">
                <button class="kol-action" onclick="window.enhancedHomepage.likeOpinion(${opinion.id})">
                    <i class="fas fa-thumbs-up"></i> ${opinion.likes || 0}
                </button>
                <button class="kol-action" onclick="window.enhancedHomepage.shareOpinion(${opinion.id})">
                    <i class="fas fa-share"></i> ${opinion.retweets || 0}
                </button>
                <button class="kol-action" onclick="window.enhancedHomepage.replyToOpinion(${opinion.id})">
                    <i class="fas fa-reply"></i> ${opinion.replies || 0}
                </button>
            </div>
        `;
        
        return card;
    }

    async loadActivityFeed() {
        try {
            const response = await fetch('/api/live/activity/feed?limit=15');
            const data = await response.json();
            
            if (data.success) {
                this.renderActivityFeed(data.data);
            }
        } catch (error) {
            console.error('Error loading activity feed:', error);
        }
    }

    renderActivityFeed(activities) {
        const stream = document.getElementById('activityStream');
        if (!stream) return;

        stream.innerHTML = '';
        
        activities.forEach(activity => {
            const item = document.createElement('div');
            item.className = 'activity-item';
            
            const iconClass = this.getActivityIcon(activity.type, activity.icon);
            
            item.innerHTML = `
                <div class="activity-icon">
                    <i class="fas fa-${iconClass}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-text">${activity.text}</div>
                    <div class="activity-time">${activity.time}</div>
                </div>
            `;
            
            stream.appendChild(item);
        });
    }

    async updateTicker() {
        try {
            const response = await fetch('/api/live/market/pulse');
            const data = await response.json();
            
            if (data.success) {
                this.renderTicker(data.data);
            }
        } catch (error) {
            console.error('Error updating ticker:', error);
        }
    }

    renderTicker(tickerData) {
        const ticker = document.getElementById('liveTicker');
        if (!ticker) return;

        ticker.innerHTML = '';
        
        tickerData.forEach(item => {
            const tickerItem = document.createElement('span');
            tickerItem.className = 'ticker-item';
            
            const changeClass = item.change > 0 ? 'positive' : 'negative';
            
            tickerItem.innerHTML = `
                <span class="ticker-symbol">${item.symbol}</span>
                <span class="ticker-change ${changeClass}">${item.formatted}</span>
            `;
            
            ticker.appendChild(tickerItem);
        });
    }

    async updateAlgorithmStats() {
        try {
            const response = await fetch('/api/live/algorithm/status');
            const data = await response.json();
            
            if (data.success) {
                this.renderAlgorithmStats(data.data);
            }
        } catch (error) {
            console.error('Error updating algorithm stats:', error);
        }
    }

    renderAlgorithmStats(stats) {
        // Update live signals counter
        const liveSignals = document.getElementById('liveSignals');
        if (liveSignals) {
            this.animateNumber(liveSignals, stats.signals_generated);
        }
        
        // Update accuracy
        const accuracy = document.getElementById('accuracy');
        if (accuracy) {
            accuracy.textContent = `${stats.success_rate}%`;
        }
        
        // Update other stats if elements exist
        const elements = {
            'profitToday': `$${stats.profit_today.toLocaleString()}`,
            'activeTrades': stats.active_trades,
            'avgResponse': `${stats.avg_response_time}s`
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    // Comment system methods
    toggleCommentForm(symbol) {
        const form = document.getElementById(`form-${symbol}`);
        if (form) {
            form.classList.toggle('active');
            
            if (form.classList.contains('active')) {
                const input = document.getElementById(`input-${symbol}`);
                if (input) input.focus();
            }
        }
    }

    async submitComment(symbol) {
        const input = document.getElementById(`input-${symbol}`);
        const authorInput = document.getElementById(`author-${symbol}`);
        const sentimentSelect = document.getElementById(`sentiment-${symbol}`);
        
        if (!input) return;
        
        const text = input.value.trim();
        if (!text) {
            this.showNotification('Please enter a comment', 'error');
            return;
        }
        
        const commentData = {
            symbol: symbol,
            content: text,
            author_name: authorInput?.value || 'Anonymous Trader',
            sentiment: sentimentSelect?.value || 'neutral'
        };
        
        try {
            const response = await fetch('/api/social/comments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(commentData)
            });
            
            if (response.ok) {
                input.value = '';
                if (authorInput) authorInput.value = '';
                this.toggleCommentForm(symbol);
                this.loadComments(symbol);
                this.showNotification('Comment posted successfully!', 'success');
            } else {
                this.showNotification('Failed to post comment', 'error');
            }
        } catch (error) {
            console.error('Error posting comment:', error);
            this.showNotification('Failed to post comment', 'error');
        }
    }

    async loadComments(symbol) {
        try {
            const response = await fetch(`/api/social/comments/${symbol}`);
            const data = await response.json();
            
            if (data.success) {
                this.displayComments(symbol, data.data);
                this.updateCommentCount(symbol, data.data.length);
            }
        } catch (error) {
            console.error('Error loading comments:', error);
        }
    }

    displayComments(symbol, comments) {
        const container = document.getElementById(`comments-${symbol}`);
        if (!container) return;
        
        container.innerHTML = '';
        
        comments.slice(0, 3).forEach(comment => {
            const commentEl = document.createElement('div');
            commentEl.className = 'comment';
            
            const sentimentIcon = this.getSentimentIcon(comment.sentiment || 'neutral');
            
            commentEl.innerHTML = `
                <div class="comment-header">
                    <span class="comment-author">${comment.author_name}</span>
                    <span class="comment-sentiment">${sentimentIcon}</span>
                </div>
                <div class="comment-text">${comment.content}</div>
                <div class="comment-footer">
                    <span class="comment-time">${comment.time_ago || 'Just now'}</span>
                    <button class="comment-like" onclick="window.enhancedHomepage.likeComment(${comment.id})">
                        <i class="fas fa-heart"></i> ${comment.likes || 0}
                    </button>
                </div>
            `;
            container.appendChild(commentEl);
        });
        
        if (comments.length > 3) {
            const showMore = document.createElement('button');
            showMore.className = 'show-more-comments';
            showMore.innerHTML = `<i class="fas fa-chevron-down"></i> Show ${comments.length - 3} more comments`;
            showMore.onclick = () => this.showAllComments(symbol, comments);
            container.appendChild(showMore);
        }
    }

    updateCommentCount(symbol, count) {
        const countEl = document.getElementById(`count-${symbol}`);
        if (countEl) {
            countEl.textContent = count;
        }
    }

    // Filter handling
    handlePredictionFilterChange(tab) {
        document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        this.currentPredictionFilter = tab.getAttribute('data-filter');
        this.loadPredictions();
    }

    handleAssetFilterChange(tab) {
        document.querySelectorAll('.asset-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        this.currentAssetFilter = tab.getAttribute('data-asset');
        this.loadKOLOpinions();
    }

    setAssetFilter(filter) {
        const tab = document.querySelector(`[data-asset="${filter}"]`);
        if (tab) {
            this.handleAssetFilterChange(tab);
        }
    }

    // Trading actions
    async handleQuickTrade(symbol, action) {
        this.showNotification(`Executing ${action} order for ${symbol}...`, 'info');
        
        try {
            const response = await fetch('/api/trading/execute-trade', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    action: action.toLowerCase(),
                    quantity: 100,
                    order_type: 'market'
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`${action} order for ${symbol} executed successfully!`, 'success');
            } else {
                this.showNotification(`Failed to execute ${action} order: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('Error executing trade:', error);
            this.showNotification('Failed to execute trade', 'error');
        }
    }

    viewDetails(symbol) {
        // Redirect to dashboard with symbol focus
        window.location.href = `/dashboard?symbol=${symbol}`;
    }

    // Social actions
    async likeOpinion(opinionId) {
        try {
            const response = await fetch(`/api/social/kols/opinions/${opinionId}/like`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showNotification('Opinion liked!', 'success');
                // Refresh KOL opinions to show updated like count
                setTimeout(() => this.loadKOLOpinions(), 1000);
            }
        } catch (error) {
            console.error('Error liking opinion:', error);
        }
    }

    shareOpinion(opinionId) {
        // Simulate sharing
        navigator.clipboard.writeText(`Check out this trading insight: ${window.location.href}#opinion-${opinionId}`);
        this.showNotification('Opinion link copied to clipboard!', 'success');
    }

    followKOL(kolName) {
        this.showNotification(`Now following ${kolName}!`, 'success');
    }

    async likeComment(commentId) {
        try {
            const response = await fetch(`/api/social/comments/${commentId}/like`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showNotification('Comment liked!', 'success');
            }
        } catch (error) {
            console.error('Error liking comment:', error);
        }
    }

    // Utility methods
    getPlatformIcon(platform) {
        const icons = {
            'twitter': 'fab fa-twitter',
            'telegram': 'fab fa-telegram',
            'discord': 'fab fa-discord',
            'reddit': 'fab fa-reddit',
            'youtube': 'fab fa-youtube'
        };
        return icons[platform.toLowerCase()] || 'fas fa-globe';
    }

    getSentimentIcon(sentiment) {
        const icons = {
            'bullish': '📈',
            'bearish': '📉',
            'neutral': '😐'
        };
        return icons[sentiment.toLowerCase()] || '😐';
    }

    getActivityIcon(type, icon) {
        const icons = {
            'opinion': 'comment',
            'whale_movement': 'fish',
            'volume_spike': 'chart-bar',
            'news_alert': 'newspaper',
            'social_buzz': 'fire'
        };
        return icons[type] || icon || 'info-circle';
    }

    animateCards(selector) {
        const cards = document.querySelectorAll(selector);
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    animateNumber(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const increment = (targetValue - currentValue) / 20;
        let current = currentValue;
        
        const animate = () => {
            current += increment;
            if ((increment > 0 && current >= targetValue) || (increment < 0 && current <= targetValue)) {
                element.textContent = targetValue;
                return;
            }
            element.textContent = Math.round(current);
            requestAnimationFrame(animate);
        };
        
        animate();
    }

    updateKOLStats(opinions) {
        const liveOpinions = document.getElementById('liveOpinions');
        const activeSources = document.getElementById('activeSources');
        
        if (liveOpinions) {
            liveOpinions.textContent = opinions.length;
        }
        
        if (activeSources) {
            const uniqueSources = new Set(opinions.map(op => op.name)).size;
            activeSources.textContent = uniqueSources;
        }
    }

    updateConnectionStatus(connected) {
        this.isConnected = connected;
        const indicator = document.getElementById('connectionStatus');
        if (indicator) {
            const icon = indicator.querySelector('i');
            const text = indicator.querySelector('span');
            
            if (connected) {
                icon.className = 'fas fa-wifi';
                text.textContent = 'Connected';
                indicator.style.color = '#00ff88';
            } else {
                icon.className = 'fas fa-wifi-slash';
                text.textContent = 'Disconnected';
                indicator.style.color = '#ff6b6b';
            }
        }
    }

    updateLastUpdateTime() {
        this.lastUpdateTime = Date.now();
        const indicator = document.getElementById('lastUpdate');
        if (indicator) {
            const text = indicator.querySelector('span');
            text.textContent = 'Just now';
        }
    }

    setupConnectionMonitoring() {
        // Update "last update" time display
        setInterval(() => {
            const indicator = document.getElementById('lastUpdate');
            if (indicator) {
                const text = indicator.querySelector('span');
                const secondsAgo = Math.floor((Date.now() - this.lastUpdateTime) / 1000);
                
                if (secondsAgo < 60) {
                    text.textContent = 'Just now';
                } else if (secondsAgo < 3600) {
                    text.textContent = `${Math.floor(secondsAgo / 60)} min ago`;
                } else {
                    text.textContent = `${Math.floor(secondsAgo / 3600)} hr ago`;
                }
            }
        }, 10000); // Update every 10 seconds
    }

    handleConnectionError() {
        this.updateConnectionStatus(false);
        // Implement retry logic here if needed
    }

    showLoadingState() {
        const grids = ['predictionsGrid', 'kolGrid'];
        grids.forEach(gridId => {
            const grid = document.getElementById(gridId);
            if (grid) {
                grid.classList.add('loading');
            }
        });
    }

    hideLoadingState() {
        const grids = ['predictionsGrid', 'kolGrid'];
        grids.forEach(gridId => {
            const grid = document.getElementById(gridId);
            if (grid) {
                grid.classList.remove('loading');
            }
        });
    }

    showErrorState() {
        this.showNotification('Failed to load data. Retrying...', 'error');
        this.hideLoadingState();
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'exclamation' : 'info'}-circle"></i>
            ${message}
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    refreshPredictions() {
        this.loadPredictions();
        this.showNotification('Predictions refreshed', 'success');
    }

    refreshAllData() {
        this.loadInitialData();
        this.showNotification('All data refreshed', 'success');
    }

    // Cleanup method
    destroy() {
        // Clear all intervals
        Object.values(this.refreshIntervals).forEach(interval => {
            if (interval) clearInterval(interval);
        });
        
        // Close websocket if exists
        if (this.websocketConnection) {
            this.websocketConnection.close();
        }
        
        console.log('🛑 Enhanced homepage manager destroyed');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedHomepage = new EnhancedHomepageManager();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.enhancedHomepage) {
        window.enhancedHomepage.destroy();
    }
});

