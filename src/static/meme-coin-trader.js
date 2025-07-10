// Meme Coin Trading Interface
// Advanced features for meme coin analysis and trading

class MemeCoinTrader {
    constructor() {
        this.memeCoins = [];
        this.socialSentiment = {};
        this.whaleActivity = {};
        this.trendingCoins = [];
        this.init();
    }

    init() {
        this.loadMemeCoinData();
        this.setupSocialSentimentTracking();
        this.setupWhaleActivityMonitoring();
        this.startRealTimeUpdates();
    }

    async loadMemeCoinData() {
        try {
            const response = await fetch('/api/trading/meme-coins');
            const data = await response.json();
            
            if (data.success) {
                this.memeCoins = data.meme_coins;
                this.renderMemeCoinDashboard();
                this.updateMarketOverview(data.market_overview);
            }
        } catch (error) {
            console.error('Error loading meme coin data:', error);
        }
    }

    renderMemeCoinDashboard() {
        const container = document.getElementById('meme-coin-container');
        if (!container) return;

        container.innerHTML = `
            <div class="meme-coin-dashboard">
                <div class="meme-header">
                    <h2><i class="fas fa-rocket"></i> Meme Coin Trading Hub</h2>
                    <div class="meme-controls">
                        <button class="btn btn-primary" onclick="memeCoinTrader.refreshData()">
                            <i class="fas fa-sync"></i> Refresh
                        </button>
                        <button class="btn btn-secondary" onclick="memeCoinTrader.showTrendingCoins()">
                            <i class="fas fa-fire"></i> Trending
                        </button>
                        <button class="btn btn-secondary" onclick="memeCoinTrader.showSocialSentiment()">
                            <i class="fas fa-comments"></i> Social Buzz
                        </button>
                    </div>
                </div>

                <div class="meme-grid">
                    ${this.memeCoins.map(coin => this.renderMemeCoinCard(coin)).join('')}
                </div>

                <div class="meme-analytics">
                    <div class="social-sentiment-panel">
                        <h3><i class="fas fa-chart-line"></i> Social Sentiment Analysis</h3>
                        <div id="sentiment-chart"></div>
                    </div>
                    
                    <div class="whale-activity-panel">
                        <h3><i class="fas fa-whale"></i> Whale Activity Monitor</h3>
                        <div id="whale-activity-feed"></div>
                    </div>
                </div>
            </div>
        `;

        this.renderSentimentChart();
        this.renderWhaleActivity();
    }

    renderMemeCoinCard(coin) {
        const changeClass = coin.change_24h > 0 ? 'positive' : 'negative';
        const sentimentIcon = this.getSentimentIcon(coin.social_sentiment);
        const whaleIcon = this.getWhaleActivityIcon(coin.whale_activity);

        return `
            <div class="meme-coin-card ${coin.recommendation.toLowerCase()}">
                <div class="coin-header">
                    <div class="coin-info">
                        <h3>${coin.symbol}</h3>
                        <span class="coin-name">${coin.name}</span>
                    </div>
                    <div class="coin-price">
                        <span class="price">$${coin.current_price.toFixed(8)}</span>
                        <span class="change ${changeClass}">
                            ${coin.change_24h > 0 ? '+' : ''}${coin.change_24h.toFixed(2)}%
                        </span>
                    </div>
                </div>

                <div class="coin-metrics">
                    <div class="metric">
                        <span class="label">Market Cap</span>
                        <span class="value">$${this.formatNumber(coin.market_cap)}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Volume 24h</span>
                        <span class="value">$${this.formatNumber(coin.volume_24h)}</span>
                    </div>
                </div>

                <div class="social-indicators">
                    <div class="indicator">
                        <i class="fas fa-comments"></i>
                        <span>Sentiment: ${sentimentIcon} ${coin.social_sentiment}</span>
                    </div>
                    <div class="indicator">
                        <i class="fab fa-reddit"></i>
                        <span>Reddit: ${coin.reddit_mentions}</span>
                    </div>
                    <div class="indicator">
                        <i class="fab fa-twitter"></i>
                        <span>Twitter: ${coin.twitter_mentions}</span>
                    </div>
                    <div class="indicator">
                        <i class="fas fa-whale"></i>
                        <span>Whales: ${whaleIcon} ${coin.whale_activity}</span>
                    </div>
                </div>

                <div class="recommendation-badge ${coin.recommendation.toLowerCase()}">
                    <i class="fas fa-${coin.recommendation === 'BUY' ? 'arrow-up' : coin.recommendation === 'SELL' ? 'arrow-down' : 'minus'}"></i>
                    ${coin.recommendation}
                </div>

                <div class="coin-actions">
                    <button class="btn btn-${coin.recommendation === 'BUY' ? 'primary' : 'danger'}" 
                            onclick="memeCoinTrader.executeTrade('${coin.symbol}', '${coin.recommendation}')">
                        <i class="fas fa-${coin.recommendation === 'BUY' ? 'shopping-cart' : 'money-bill-wave'}"></i>
                        ${coin.recommendation} Now
                    </button>
                    <button class="btn btn-secondary" 
                            onclick="memeCoinTrader.showCoinDetails('${coin.symbol}')">
                        <i class="fas fa-chart-bar"></i>
                        Details
                    </button>
                </div>
            </div>
        `;
    }

    getSentimentIcon(sentiment) {
        const icons = {
            'very_bullish': '🚀',
            'bullish': '📈',
            'neutral': '➡️',
            'bearish': '📉',
            'very_bearish': '💥'
        };
        return icons[sentiment] || '➡️';
    }

    getWhaleActivityIcon(activity) {
        const icons = {
            'high': '🔥',
            'moderate': '⚡',
            'low': '💤'
        };
        return icons[activity] || '💤';
    }

    formatNumber(num) {
        if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
        return num.toString();
    }

    renderSentimentChart() {
        const chartContainer = document.getElementById('sentiment-chart');
        if (!chartContainer) return;

        // Create a simple sentiment visualization
        const sentimentData = this.memeCoins.map(coin => ({
            name: coin.symbol,
            sentiment: coin.social_sentiment,
            reddit: coin.reddit_mentions,
            twitter: coin.twitter_mentions
        }));

        chartContainer.innerHTML = `
            <div class="sentiment-bars">
                ${sentimentData.map(data => `
                    <div class="sentiment-bar">
                        <div class="bar-label">${data.name}</div>
                        <div class="bar-container">
                            <div class="bar ${data.sentiment}" style="width: ${this.getSentimentWidth(data.sentiment)}%"></div>
                        </div>
                        <div class="bar-value">${data.sentiment}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    getSentimentWidth(sentiment) {
        const widths = {
            'very_bullish': 90,
            'bullish': 70,
            'neutral': 50,
            'bearish': 30,
            'very_bearish': 10
        };
        return widths[sentiment] || 50;
    }

    renderWhaleActivity() {
        const whaleContainer = document.getElementById('whale-activity-feed');
        if (!whaleContainer) return;

        // Generate some sample whale activity
        const whaleActivities = [
            { time: '2 min ago', action: 'Large DOGE purchase', amount: '$2.5M', impact: 'bullish' },
            { time: '15 min ago', action: 'SHIB whale movement', amount: '$1.8M', impact: 'bearish' },
            { time: '32 min ago', action: 'PEPE accumulation', amount: '$950K', impact: 'bullish' },
            { time: '1 hour ago', action: 'Multi-coin distribution', amount: '$3.2M', impact: 'neutral' }
        ];

        whaleContainer.innerHTML = `
            <div class="whale-feed">
                ${whaleActivities.map(activity => `
                    <div class="whale-activity-item ${activity.impact}">
                        <div class="activity-time">${activity.time}</div>
                        <div class="activity-description">${activity.action}</div>
                        <div class="activity-amount">${activity.amount}</div>
                        <div class="activity-impact">
                            <i class="fas fa-${activity.impact === 'bullish' ? 'arrow-up' : activity.impact === 'bearish' ? 'arrow-down' : 'minus'}"></i>
                            ${activity.impact}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    async executeTrade(symbol, action) {
        const amount = prompt(`Enter amount to ${action} ${symbol}:`);
        if (!amount || isNaN(amount) || amount <= 0) return;

        try {
            const response = await fetch('/api/trading/execute-trade', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symbol: symbol,
                    action: action,
                    amount: parseFloat(amount),
                    market_type: 'meme_coin'
                })
            });

            const data = await response.json();
            if (data.success) {
                alert(`Meme coin trade executed! ${action} $${amount} of ${symbol}`);
                this.loadMemeCoinData(); // Refresh data
            } else {
                alert('Trade failed: ' + data.error);
            }
        } catch (error) {
            alert('Error executing trade: ' + error.message);
        }
    }

    showCoinDetails(symbol) {
        const coin = this.memeCoins.find(c => c.symbol === symbol);
        if (!coin) return;

        // Create a detailed modal or panel
        const modal = document.createElement('div');
        modal.className = 'coin-details-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${coin.name} (${coin.symbol}) Details</h2>
                    <button class="close-btn" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="detail-grid">
                        <div class="detail-item">
                            <label>Current Price:</label>
                            <span>$${coin.current_price.toFixed(8)}</span>
                        </div>
                        <div class="detail-item">
                            <label>24h Change:</label>
                            <span class="${coin.change_24h > 0 ? 'positive' : 'negative'}">
                                ${coin.change_24h > 0 ? '+' : ''}${coin.change_24h.toFixed(2)}%
                            </span>
                        </div>
                        <div class="detail-item">
                            <label>Market Cap:</label>
                            <span>$${this.formatNumber(coin.market_cap)}</span>
                        </div>
                        <div class="detail-item">
                            <label>24h Volume:</label>
                            <span>$${this.formatNumber(coin.volume_24h)}</span>
                        </div>
                        <div class="detail-item">
                            <label>Social Sentiment:</label>
                            <span>${this.getSentimentIcon(coin.social_sentiment)} ${coin.social_sentiment}</span>
                        </div>
                        <div class="detail-item">
                            <label>Whale Activity:</label>
                            <span>${this.getWhaleActivityIcon(coin.whale_activity)} ${coin.whale_activity}</span>
                        </div>
                    </div>
                    <div class="social-metrics">
                        <h3>Social Media Metrics</h3>
                        <div class="metric-row">
                            <i class="fab fa-reddit"></i>
                            <span>Reddit Mentions: ${coin.reddit_mentions}</span>
                        </div>
                        <div class="metric-row">
                            <i class="fab fa-twitter"></i>
                            <span>Twitter Mentions: ${coin.twitter_mentions}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    refreshData() {
        this.loadMemeCoinData();
    }

    showTrendingCoins() {
        // Filter and show trending coins
        const trending = this.memeCoins
            .filter(coin => coin.change_24h > 5 || coin.social_sentiment === 'very_bullish')
            .sort((a, b) => b.change_24h - a.change_24h);

        alert(`Trending Meme Coins:\n${trending.map(c => `${c.symbol}: +${c.change_24h.toFixed(2)}%`).join('\n')}`);
    }

    showSocialSentiment() {
        const sentimentSummary = this.memeCoins.map(coin => 
            `${coin.symbol}: ${coin.social_sentiment} (${coin.reddit_mentions + coin.twitter_mentions} mentions)`
        ).join('\n');

        alert(`Social Sentiment Summary:\n${sentimentSummary}`);
    }

    setupSocialSentimentTracking() {
        // Simulate real-time social sentiment updates
        setInterval(() => {
            this.memeCoins.forEach(coin => {
                // Randomly update social metrics
                coin.reddit_mentions += Math.floor(Math.random() * 10) - 5;
                coin.twitter_mentions += Math.floor(Math.random() * 50) - 25;
                
                // Keep values positive
                coin.reddit_mentions = Math.max(0, coin.reddit_mentions);
                coin.twitter_mentions = Math.max(0, coin.twitter_mentions);
            });
        }, 30000); // Update every 30 seconds
    }

    setupWhaleActivityMonitoring() {
        // Simulate whale activity alerts
        setInterval(() => {
            if (Math.random() < 0.3) { // 30% chance of whale activity
                const coin = this.memeCoins[Math.floor(Math.random() * this.memeCoins.length)];
                const activities = ['Large purchase', 'Massive sell-off', 'Accumulation pattern', 'Distribution detected'];
                const activity = activities[Math.floor(Math.random() * activities.length)];
                
                this.showWhaleAlert(coin.symbol, activity);
            }
        }, 60000); // Check every minute
    }

    showWhaleAlert(symbol, activity) {
        const alert = document.createElement('div');
        alert.className = 'whale-alert';
        alert.innerHTML = `
            <div class="alert-content">
                <i class="fas fa-whale"></i>
                <strong>Whale Alert!</strong>
                <span>${activity} detected for ${symbol}</span>
                <button onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        document.body.appendChild(alert);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 10000);
    }

    startRealTimeUpdates() {
        // Update prices every 10 seconds
        setInterval(() => {
            this.memeCoins.forEach(coin => {
                // Simulate price movement
                const change = (Math.random() - 0.5) * 0.1; // ±5% max change
                coin.current_price *= (1 + change);
                coin.change_24h += change * 100;
            });
            
            // Re-render if the meme coin dashboard is visible
            if (document.getElementById('meme-coin-container')) {
                this.renderMemeCoinDashboard();
            }
        }, 10000);
    }
}

// Initialize meme coin trader
const memeCoinTrader = new MemeCoinTrader();

