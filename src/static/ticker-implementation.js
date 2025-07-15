// Live Market Ticker Implementation
// Creates a scrolling ticker with real-time market data

class LiveTicker {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.tickerData = [];
        this.isRunning = false;
        
        if (this.container) {
            this.init();
        }
    }
    
    init() {
        this.generateTickerData();
        this.createTicker();
        this.startUpdates();
    }
    
    generateTickerData() {
        const symbols = [
            { symbol: 'BTC/USD', price: 42500, change: 2.3 },
            { symbol: 'ETH/USD', price: 2650, change: -1.2 },
            { symbol: 'AAPL', price: 185.50, change: 0.8 },
            { symbol: 'TSLA', price: 242.75, change: 3.2 },
            { symbol: 'NVDA', price: 875.25, change: -0.5 },
            { symbol: 'GOOGL', price: 142.80, change: 1.1 },
            { symbol: 'META', price: 325.60, change: 2.7 },
            { symbol: 'AMZN', price: 155.30, change: -0.3 },
            { symbol: 'MSFT', price: 378.90, change: 1.5 },
            { symbol: 'DOGE/USD', price: 0.085, change: 5.2 },
            { symbol: 'SOL/USD', price: 98.45, change: 4.1 },
            { symbol: 'ADA/USD', price: 0.52, change: -2.1 }
        ];
        
        this.tickerData = symbols.map(item => ({
            ...item,
            price: this.addRandomVariation(item.price, 0.02),
            change: this.addRandomVariation(item.change, 0.5)
        }));
    }
    
    addRandomVariation(value, variance) {
        const variation = (Math.random() - 0.5) * variance * 2;
        return value + (value * variation);
    }
    
    createTicker() {
        const tickerItems = this.tickerData.map(item => {
            const isPositive = item.change >= 0;
            const changeClass = isPositive ? 'positive' : 'negative';
            const changeSymbol = isPositive ? '+' : '';
            
            let priceDisplay;
            if (item.price < 1) {
                priceDisplay = '$' + item.price.toFixed(4);
            } else if (item.price < 100) {
                priceDisplay = '$' + item.price.toFixed(2);
            } else {
                priceDisplay = '$' + item.price.toFixed(2);
            }
            
            return `
                <div class="ticker-item">
                    <span class="ticker-symbol">${item.symbol}</span>
                    <span class="ticker-price">${priceDisplay}</span>
                    <span class="ticker-change ${changeClass}">
                        ${changeSymbol}${item.change.toFixed(2)}%
                    </span>
                </div>
            `;
        }).join('');
        
        this.container.innerHTML = `
            <div class="ticker-scroll">
                ${tickerItems}
                ${tickerItems} <!-- Duplicate for seamless loop -->
            </div>
        `;
        
        // Add CSS if not already added
        this.addTickerStyles();
    }
    
    addTickerStyles() {
        if (document.getElementById('ticker-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'ticker-styles';
        style.textContent = `
            .ticker-scroll {
                display: flex;
                animation: ticker-scroll 60s linear infinite;
                gap: 3rem;
            }
            
            .ticker-item {
                display: flex;
                align-items: center;
                gap: 1rem;
                white-space: nowrap;
                padding: 0.5rem 1rem;
                background: rgba(26, 26, 46, 0.6);
                border-radius: 8px;
                border: 1px solid rgba(42, 42, 62, 0.8);
            }
            
            .ticker-symbol {
                font-weight: 600;
                color: #ffffff;
                font-size: 0.9rem;
            }
            
            .ticker-price {
                color: #e0e0e0;
                font-weight: 500;
                font-size: 0.9rem;
            }
            
            .ticker-change {
                font-weight: 600;
                font-size: 0.85rem;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
            }
            
            .ticker-change.positive {
                color: #22c55e;
                background: rgba(34, 197, 94, 0.1);
            }
            
            .ticker-change.negative {
                color: #ef4444;
                background: rgba(239, 68, 68, 0.1);
            }
            
            @keyframes ticker-scroll {
                0% { transform: translateX(0); }
                100% { transform: translateX(-50%); }
            }
            
            .ticker-scroll:hover {
                animation-play-state: paused;
            }
        `;
        
        document.head.appendChild(style);
    }
    
    updateData() {
        this.tickerData = this.tickerData.map(item => ({
            ...item,
            price: this.addRandomVariation(item.price, 0.01),
            change: this.addRandomVariation(item.change, 0.3)
        }));
        
        this.createTicker();
    }
    
    startUpdates() {
        // Update ticker data every 10 seconds
        setInterval(() => {
            this.updateData();
        }, 10000);
        
        this.isRunning = true;
    }
    
    stop() {
        this.isRunning = false;
    }
}

// Market Status Indicator
class MarketStatus {
    constructor() {
        this.status = {
            isOpen: this.isMarketOpen(),
            nextOpen: this.getNextMarketOpen(),
            timezone: 'EST'
        };
        
        this.updateStatus();
        this.startStatusUpdates();
    }
    
    isMarketOpen() {
        const now = new Date();
        const day = now.getDay(); // 0 = Sunday, 6 = Saturday
        const hour = now.getHours();
        
        // Market is closed on weekends
        if (day === 0 || day === 6) return false;
        
        // Market hours: 9:30 AM - 4:00 PM EST (simplified)
        return hour >= 9 && hour < 16;
    }
    
    getNextMarketOpen() {
        const now = new Date();
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(9, 30, 0, 0);
        
        return tomorrow;
    }
    
    updateStatus() {
        this.status.isOpen = this.isMarketOpen();
        
        const statusElement = document.getElementById('market-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <span class="status-indicator ${this.status.isOpen ? 'open' : 'closed'}"></span>
                <span class="status-text">
                    Market ${this.status.isOpen ? 'Open' : 'Closed'}
                </span>
            `;
        }
    }
    
    startStatusUpdates() {
        // Update every minute
        setInterval(() => {
            this.updateStatus();
        }, 60000);
    }
}

// Price Alerts System
class PriceAlerts {
    constructor() {
        this.alerts = [];
        this.watchlist = ['BTC/USD', 'ETH/USD', 'AAPL', 'TSLA'];
        this.priceHistory = new Map();
        
        this.startPriceMonitoring();
    }
    
    addAlert(symbol, targetPrice, type = 'above') {
        this.alerts.push({
            id: Date.now(),
            symbol,
            targetPrice,
            type, // 'above' or 'below'
            created: new Date(),
            triggered: false
        });
    }
    
    checkAlerts(symbol, currentPrice) {
        this.alerts.forEach(alert => {
            if (alert.symbol === symbol && !alert.triggered) {
                const shouldTrigger = 
                    (alert.type === 'above' && currentPrice >= alert.targetPrice) ||
                    (alert.type === 'below' && currentPrice <= alert.targetPrice);
                
                if (shouldTrigger) {
                    this.triggerAlert(alert, currentPrice);
                }
            }
        });
    }
    
    triggerAlert(alert, currentPrice) {
        alert.triggered = true;
        
        // Show notification
        this.showNotification(
            `Price Alert: ${alert.symbol}`,
            `Price ${alert.type} $${alert.targetPrice} - Current: $${currentPrice.toFixed(2)}`
        );
    }
    
    showNotification(title, message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'price-alert-notification';
        notification.innerHTML = `
            <div class="alert-title">${title}</div>
            <div class="alert-message">${message}</div>
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    startPriceMonitoring() {
        // Monitor prices every 5 seconds
        setInterval(() => {
            this.watchlist.forEach(symbol => {
                // Simulate price data (in real app, this would come from API)
                const basePrice = this.getBasePrice(symbol);
                const currentPrice = basePrice + (Math.random() - 0.5) * basePrice * 0.02;
                
                this.priceHistory.set(symbol, currentPrice);
                this.checkAlerts(symbol, currentPrice);
            });
        }, 5000);
    }
    
    getBasePrice(symbol) {
        const basePrices = {
            'BTC/USD': 42500,
            'ETH/USD': 2650,
            'AAPL': 185.50,
            'TSLA': 242.75
        };
        
        return basePrices[symbol] || 100;
    }
}

// Initialize components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize ticker
    window.liveTicker = new LiveTicker('liveTicker');
    
    // Initialize market status
    window.marketStatus = new MarketStatus();
    
    // Initialize price alerts
    window.priceAlerts = new PriceAlerts();
    
    // Add notification styles
    const notificationStyles = document.createElement('style');
    notificationStyles.textContent = `
        .price-alert-notification {
            position: fixed;
            top: 100px;
            right: 20px;
            background: rgba(13, 128, 67, 0.95);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            animation: slideInRight 0.3s ease;
            max-width: 300px;
        }
        
        .alert-title {
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .alert-message {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }
        
        .status-indicator.open {
            background: #22c55e;
            animation: pulse 2s infinite;
        }
        
        .status-indicator.closed {
            background: #ef4444;
        }
        
        .status-text {
            font-size: 0.9rem;
            font-weight: 500;
        }
    `;
    
    document.head.appendChild(notificationStyles);
});

