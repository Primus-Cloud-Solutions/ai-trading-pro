// Homepage Interactions for AI Trading Pro
// Handles dynamic content loading, comments, and KOL opinions

class HomepageManager {
    constructor() {
        this.currentFilter = 'all';
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startAutoRefresh();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Filter buttons for predictions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-btn')) {
                this.handleFilterChange(e.target);
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

    async loadInitialData() {
        await Promise.all([
            this.loadPredictions(),
            this.loadKOLOpinions(),
            this.loadTrendingSymbols()
        ]);
    }

    async loadPredictions() {
        try {
            const response = await fetch('/api/trading/recommendations?market=all');
            const predictions = await response.json();
            
            this.renderPredictions(predictions.slice(0, 6));
        } catch (error) {
            console.error('Error loading predictions:', error);
            this.renderMockPredictions();
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

        // Add animation
        this.animateCards('.prediction-card');
    }

    createPredictionCard(prediction) {
        const card = document.createElement('div');
        card.className = 'prediction-card';
        
        const predictionType = prediction.action.toLowerCase();
        const typeClass = predictionType === 'buy' ? 'buy' : 'sell';
        const returnColor = prediction.expected_return >= 0 ? '#00ff88' : '#ff6b6b';
        
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
                    <span class="confidence">
                        <i class="fas fa-brain"></i> ${Math.round(prediction.confidence * 100)}% confidence
                    </span>
                    <span style="color: ${returnColor}; font-weight: 600;">
                        ${prediction.expected_return >= 0 ? '+' : ''}${prediction.expected_return.toFixed(1)}%
                    </span>
                </div>
                <div class="strategy-info">
                    <i class="fas fa-cogs"></i> Strategy: ${prediction.strategy || 'multi_strategy'}
                </div>
                <p class="reasoning">
                    <i class="fas fa-lightbulb"></i> ${prediction.reasoning}
                </p>
            </div>
            <div class="prediction-actions">
                <button class="action-btn ${typeClass}" onclick="this.handleQuickTrade('${prediction.symbol}', '${prediction.action}')">
                    <i class="fas fa-bolt"></i> Quick ${prediction.action}
                </button>
                <button class="action-btn secondary" onclick="this.viewDetails('${prediction.symbol}')">
                    <i class="fas fa-chart-line"></i> View Chart
                </button>
            </div>
            <div class="comments-section">
                <div class="comments-header">
                    <span class="comments-count">
                        <i class="fas fa-comments"></i> <span id="count-${prediction.symbol}">0</span> comments
                    </span>
                    <button class="add-comment-btn" onclick="window.homepageManager.toggleCommentForm('${prediction.symbol}')">
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
                    <textarea class="comment-input" placeholder="Share your thoughts on this prediction..." id="input-${prediction.symbol}"></textarea>
                    <div class="comment-actions">
                        <button class="submit-comment" onclick="window.homepageManager.submitComment('${prediction.symbol}')">
                            <i class="fas fa-paper-plane"></i> Post
                        </button>
                        <button class="cancel-comment" onclick="window.homepageManager.toggleCommentForm('${prediction.symbol}')">
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
            const response = await fetch('/api/social/kols/opinions');
            const opinions = await response.json();
            
            this.renderKOLOpinions(opinions);
        } catch (error) {
            console.error('Error loading KOL opinions:', error);
            this.renderMockKOLOpinions();
        }
    }

    renderKOLOpinions(opinions) {
        const grid = document.getElementById('kolsGrid');
        if (!grid) return;

        grid.innerHTML = '';
        
        opinions.forEach(opinion => {
            const card = this.createKOLCard(opinion);
            grid.appendChild(card);
        });

        // Add animation
        this.animateCards('.kol-opinion');
    }

    createKOLCard(opinion) {
        const card = document.createElement('div');
        card.className = 'kol-opinion';
        
        const sentimentClass = opinion.sentiment.toLowerCase();
        const platformIcon = this.getPlatformIcon(opinion.platform);
        
        card.innerHTML = `
            <div class="kol-header">
                <div class="kol-avatar">${opinion.name.charAt(0)}</div>
                <div class="kol-info">
                    <h4>${opinion.name}</h4>
                    <div class="kol-platform">
                        <i class="${platformIcon}"></i> ${opinion.platform}
                        ${opinion.platform_handle ? `• ${opinion.platform_handle}` : ''}
                    </div>
                </div>
                <div class="kol-actions">
                    <button class="follow-btn" onclick="this.followKOL('${opinion.name}')">
                        <i class="fas fa-user-plus"></i>
                    </button>
                </div>
            </div>
            <div class="kol-content">${opinion.content}</div>
            ${opinion.symbol ? `<div class="kol-symbol"><i class="fas fa-tag"></i> ${opinion.symbol}</div>` : ''}
            <div class="kol-meta">
                <span class="kol-time">
                    <i class="fas fa-clock"></i> ${opinion.time}
                </span>
                <span class="kol-sentiment ${sentimentClass}">
                    ${this.getSentimentIcon(opinion.sentiment)} ${opinion.sentiment}
                </span>
                <span class="kol-engagement">
                    <i class="fas fa-heart"></i> ${opinion.engagement_score || 0}
                </span>
            </div>
            <div class="kol-actions-bar">
                <button class="kol-action" onclick="this.likeOpinion(${opinion.id})">
                    <i class="fas fa-thumbs-up"></i> Like
                </button>
                <button class="kol-action" onclick="this.shareOpinion(${opinion.id})">
                    <i class="fas fa-share"></i> Share
                </button>
                <button class="kol-action" onclick="this.replyToOpinion(${opinion.id})">
                    <i class="fas fa-reply"></i> Reply
                </button>
            </div>
        `;
        
        return card;
    }

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

    async loadTrendingSymbols() {
        // Add trending symbols ticker
        const ticker = document.createElement('div');
        ticker.className = 'trending-ticker';
        ticker.innerHTML = `
            <div class="ticker-content">
                <span class="ticker-label">🔥 Trending:</span>
                <span class="ticker-item">TSLA +5.2%</span>
                <span class="ticker-item">NVDA +3.8%</span>
                <span class="ticker-item">AAPL +2.1%</span>
                <span class="ticker-item">DOGE +12.5%</span>
                <span class="ticker-item">BTC +4.3%</span>
            </div>
        `;
        
        const hero = document.querySelector('.hero');
        if (hero) {
            hero.appendChild(ticker);
        }
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
        if (!text) return;
        
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
            const comments = await response.json();
            
            this.displayComments(symbol, comments);
            this.updateCommentCount(symbol, comments.length);
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
                    <span class="comment-time">${comment.time_ago}</span>
                    <button class="comment-like" onclick="this.likeComment(${comment.id})">
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

    // Utility methods
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
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    startAutoRefresh() {
        // Refresh data every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadPredictions();
            this.loadKOLOpinions();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Initialize homepage manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.homepageManager = new HomepageManager();
});

// Add some additional CSS for new features
const additionalStyles = `
    .trending-ticker {
        background: rgba(0, 255, 136, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 2rem;
        overflow: hidden;
    }

    .ticker-content {
        display: flex;
        align-items: center;
        gap: 2rem;
        animation: ticker 20s linear infinite;
    }

    .ticker-label {
        color: #00ff88;
        font-weight: 600;
        white-space: nowrap;
    }

    .ticker-item {
        color: #ffffff;
        white-space: nowrap;
        font-weight: 500;
    }

    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }

    .prediction-actions {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(0, 255, 136, 0.1);
    }

    .action-btn {
        flex: 1;
        padding: 0.75rem;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    .action-btn.buy {
        background: linear-gradient(135deg, #00ff88, #00cc6a);
        color: #0f0f23;
    }

    .action-btn.sell {
        background: linear-gradient(135deg, #ff6b6b, #ff5252);
        color: #ffffff;
    }

    .action-btn.secondary {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }

    .strategy-info {
        color: #b0b0b0;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }

    .reasoning {
        color: #e0e0e0;
        font-size: 0.9rem;
        line-height: 1.4;
        margin-top: 0.5rem;
    }

    .comment-form-header {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .author-input, .sentiment-select {
        background: rgba(15, 15, 35, 0.8);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 6px;
        padding: 0.5rem;
        color: #ffffff;
        font-size: 0.9rem;
    }

    .author-input {
        flex: 2;
    }

    .sentiment-select {
        flex: 1;
    }

    .comment-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.25rem;
    }

    .comment-sentiment {
        font-size: 0.8rem;
    }

    .comment-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 0.5rem;
    }

    .comment-like {
        background: none;
        border: none;
        color: #888;
        cursor: pointer;
        font-size: 0.8rem;
        transition: color 0.3s ease;
    }

    .comment-like:hover {
        color: #ff6b6b;
    }

    .kol-actions {
        margin-left: auto;
    }

    .follow-btn {
        background: rgba(0, 255, 136, 0.2);
        border: none;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        color: #00ff88;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .follow-btn:hover {
        background: rgba(0, 255, 136, 0.3);
        transform: scale(1.1);
    }

    .kol-symbol {
        background: rgba(0, 255, 136, 0.1);
        color: #00ff88;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 0.5rem 0;
        display: inline-block;
    }

    .kol-actions-bar {
        display: flex;
        gap: 1rem;
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .kol-action {
        background: none;
        border: none;
        color: #888;
        cursor: pointer;
        font-size: 0.8rem;
        transition: color 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }

    .kol-action:hover {
        color: #00ff88;
    }

    .notification {
        position: fixed;
        top: 100px;
        right: 20px;
        background: rgba(26, 26, 46, 0.95);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 8px;
        padding: 1rem;
        color: #ffffff;
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .notification.show {
        transform: translateX(0);
    }

    .notification.success {
        border-color: rgba(0, 255, 136, 0.5);
    }

    .notification.error {
        border-color: rgba(255, 107, 107, 0.5);
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

