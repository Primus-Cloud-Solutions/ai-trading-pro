// AI Trading Pro - Complete Trading Interface
// Provides buy/sell buttons, recommendations, and automated trading controls

class TradingInterface {
    constructor() {
        this.autoTradingEnabled = false;
        this.recommendations = [];
        this.orders = [];
        this.autoTradingSettings = {};
        this.init();
    }

    init() {
        console.log('🚀 Trading Interface initialized');
        this.loadRecommendations();
        this.loadAutoTradingSettings();
        this.loadOrders();
        this.setupAutoRefresh();
    }

    async loadRecommendations() {
        try {
            const response = await fetch('/api/trading/recommendations');
            const data = await response.json();
            this.recommendations = data.recommendations || [];
            this.renderRecommendations();
        } catch (error) {
            console.error('Error loading recommendations:', error);
        }
    }

    async loadAutoTradingSettings() {
        try {
            const response = await fetch('/api/trading/auto-trading/settings');
            const data = await response.json();
            this.autoTradingSettings = data.settings || {};
            this.autoTradingEnabled = this.autoTradingSettings.is_enabled || false;
            this.renderAutoTradingControls();
        } catch (error) {
            console.error('Error loading auto trading settings:', error);
        }
    }

    async loadOrders() {
        try {
            const response = await fetch('/api/trading/orders');
            const data = await response.json();
            this.orders = data.orders || [];
            this.renderOrderHistory();
        } catch (error) {
            console.error('Error loading orders:', error);
        }
    }

    renderRecommendations() {
        const container = document.getElementById('recommendations-container') || this.createRecommendationsContainer();
        
        if (this.recommendations.length === 0) {
            container.innerHTML = `
                <div class="no-recommendations">
                    <h3>🤖 AI Recommendations</h3>
                    <p>No active recommendations. AI is analyzing market conditions...</p>
                </div>
            `;
            return;
        }

        const recommendationsHTML = this.recommendations.map(rec => `
            <div class="recommendation-card ${rec.action}">
                <div class="rec-header">
                    <div class="rec-symbol">
                        <span class="symbol">${rec.symbol}</span>
                        <span class="asset-type">${rec.asset_type}</span>
                    </div>
                    <div class="rec-action ${rec.action}">
                        ${rec.action.toUpperCase()}
                    </div>
                </div>
                
                <div class="rec-details">
                    <div class="price-info">
                        <span class="current-price">$${rec.current_price?.toFixed(2)}</span>
                        <span class="target-price">Target: $${rec.target_price?.toFixed(2)}</span>
                    </div>
                    
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${(rec.confidence * 100)}%"></div>
                        <span class="confidence-text">${(rec.confidence * 100).toFixed(0)}% confidence</span>
                    </div>
                    
                    <div class="expected-return ${rec.expected_return >= 0 ? 'positive' : 'negative'}">
                        Expected Return: ${rec.expected_return?.toFixed(1)}%
                    </div>
                    
                    <div class="reasoning">
                        <strong>Strategy:</strong> ${rec.strategy}<br>
                        <strong>Reasoning:</strong> ${rec.reasoning}
                    </div>
                </div>
                
                <div class="rec-actions">
                    <button class="btn-execute ${rec.action}" onclick="tradingInterface.executeRecommendation('${rec.symbol}', '${rec.action}', ${rec.current_price})">
                        ${rec.action === 'buy' ? '🛒 Buy Now' : '💰 Sell Now'}
                    </button>
                    <button class="btn-quick-trade" onclick="tradingInterface.quickTrade('${rec.symbol}', '${rec.action}')">
                        ⚡ Quick $100
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="recommendations-header">
                <h3>🤖 AI Trading Recommendations</h3>
                <button class="btn-refresh" onclick="tradingInterface.loadRecommendations()">🔄 Refresh</button>
            </div>
            <div class="recommendations-grid">
                ${recommendationsHTML}
            </div>
        `;
    }

    renderAutoTradingControls() {
        const container = document.getElementById('auto-trading-container') || this.createAutoTradingContainer();
        
        container.innerHTML = `
            <div class="auto-trading-panel">
                <div class="auto-trading-header">
                    <h3>🤖 Automated Trading</h3>
                    <div class="auto-trading-toggle">
                        <label class="toggle-switch">
                            <input type="checkbox" ${this.autoTradingEnabled ? 'checked' : ''} 
                                   onchange="tradingInterface.toggleAutoTrading(this.checked)">
                            <span class="toggle-slider"></span>
                        </label>
                        <span class="toggle-label">${this.autoTradingEnabled ? 'ON' : 'OFF'}</span>
                    </div>
                </div>
                
                <div class="auto-trading-status ${this.autoTradingEnabled ? 'enabled' : 'disabled'}">
                    <div class="status-indicator"></div>
                    <span>Automated Trading is ${this.autoTradingEnabled ? 'ACTIVE' : 'INACTIVE'}</span>
                </div>
                
                <div class="auto-trading-settings">
                    <div class="setting-row">
                        <label>Max Daily Trades:</label>
                        <span>${this.autoTradingSettings.max_daily_trades || 10}</span>
                    </div>
                    <div class="setting-row">
                        <label>Max Position Size:</label>
                        <span>$${this.autoTradingSettings.max_position_size || 1000}</span>
                    </div>
                    <div class="setting-row">
                        <label>Min Confidence:</label>
                        <span>${((this.autoTradingSettings.min_confidence || 0.7) * 100).toFixed(0)}%</span>
                    </div>
                    <div class="setting-row">
                        <label>Stop Loss:</label>
                        <span>${((this.autoTradingSettings.stop_loss_percentage || 0.05) * 100).toFixed(0)}%</span>
                    </div>
                </div>
                
                <div class="auto-trading-actions">
                    <button class="btn-execute-auto" onclick="tradingInterface.executeAutomatedTrades()">
                        ⚡ Execute Auto Trades Now
                    </button>
                    <button class="btn-settings" onclick="tradingInterface.showAutoTradingSettings()">
                        ⚙️ Settings
                    </button>
                </div>
            </div>
        `;
    }

    renderOrderHistory() {
        const container = document.getElementById('orders-container') || this.createOrdersContainer();
        
        if (this.orders.length === 0) {
            container.innerHTML = `
                <div class="no-orders">
                    <h3>📋 Recent Orders</h3>
                    <p>No orders yet. Start trading to see your order history.</p>
                </div>
            `;
            return;
        }

        const ordersHTML = this.orders.slice(0, 10).map(order => `
            <div class="order-row ${order.side}">
                <div class="order-symbol">${order.symbol}</div>
                <div class="order-side ${order.side}">${order.side.toUpperCase()}</div>
                <div class="order-quantity">${order.quantity}</div>
                <div class="order-price">$${order.filled_price?.toFixed(2) || order.price?.toFixed(2)}</div>
                <div class="order-status ${order.status}">${order.status}</div>
                <div class="order-time">${new Date(order.created_at).toLocaleTimeString()}</div>
                ${order.is_automated ? '<div class="order-auto">🤖 AUTO</div>' : ''}
            </div>
        `).join('');

        container.innerHTML = `
            <div class="orders-header">
                <h3>📋 Recent Orders</h3>
                <button class="btn-refresh" onclick="tradingInterface.loadOrders()">🔄 Refresh</button>
            </div>
            <div class="orders-table">
                <div class="orders-header-row">
                    <div>Symbol</div>
                    <div>Side</div>
                    <div>Quantity</div>
                    <div>Price</div>
                    <div>Status</div>
                    <div>Time</div>
                    <div>Type</div>
                </div>
                ${ordersHTML}
            </div>
        `;
    }

    async executeRecommendation(symbol, action, price) {
        try {
            const amount = 100; // Default $100 trade
            const quantity = amount / price;
            
            const response = await fetch('/api/trading/execute-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    side: action,
                    quantity: quantity,
                    strategy: 'ai_recommendation'
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`✅ ${action.toUpperCase()} order executed: ${quantity.toFixed(4)} ${symbol} at $${price.toFixed(2)}`, 'success');
                this.loadOrders();
                this.loadRecommendations();
            } else {
                this.showNotification(`❌ Order failed: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Error executing recommendation:', error);
            this.showNotification('❌ Failed to execute order', 'error');
        }
    }

    async quickTrade(symbol, action) {
        try {
            const endpoint = action === 'buy' ? '/api/trading/quick-buy' : '/api/trading/quick-sell';
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    amount: 100 // $100 quick trade
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`⚡ Quick ${action} executed for ${symbol}`, 'success');
                this.loadOrders();
            } else {
                this.showNotification(`❌ Quick trade failed: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Error executing quick trade:', error);
            this.showNotification('❌ Failed to execute quick trade', 'error');
        }
    }

    async toggleAutoTrading(enabled) {
        try {
            const response = await fetch('/api/trading/auto-trading/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    enabled: enabled
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.autoTradingEnabled = enabled;
                this.showNotification(`🤖 Automated trading ${enabled ? 'enabled' : 'disabled'}`, 'success');
                this.renderAutoTradingControls();
            } else {
                this.showNotification(`❌ Failed to toggle auto trading: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Error toggling auto trading:', error);
            this.showNotification('❌ Failed to toggle auto trading', 'error');
        }
    }

    async executeAutomatedTrades() {
        try {
            const response = await fetch('/api/trading/auto-trading/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`⚡ Executed ${result.executed_trades?.length || 0} automated trades`, 'success');
                this.loadOrders();
            } else {
                this.showNotification(`❌ Auto trading failed: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Error executing automated trades:', error);
            this.showNotification('❌ Failed to execute automated trades', 'error');
        }
    }

    createRecommendationsContainer() {
        const container = document.createElement('div');
        container.id = 'recommendations-container';
        container.className = 'trading-section';
        
        // Find a good place to insert it
        const dashboardContent = document.querySelector('.dashboard-content') || document.body;
        dashboardContent.appendChild(container);
        
        return container;
    }

    createAutoTradingContainer() {
        const container = document.createElement('div');
        container.id = 'auto-trading-container';
        container.className = 'trading-section';
        
        const dashboardContent = document.querySelector('.dashboard-content') || document.body;
        dashboardContent.appendChild(container);
        
        return container;
    }

    createOrdersContainer() {
        const container = document.createElement('div');
        container.id = 'orders-container';
        container.className = 'trading-section';
        
        const dashboardContent = document.querySelector('.dashboard-content') || document.body;
        dashboardContent.appendChild(container);
        
        return container;
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    setupAutoRefresh() {
        // Refresh data every 30 seconds
        setInterval(() => {
            this.loadRecommendations();
            this.loadOrders();
        }, 30000);
    }

    showAutoTradingSettings() {
        // Create settings modal (simplified for demo)
        const modal = document.createElement('div');
        modal.className = 'settings-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>⚙️ Auto Trading Settings</h3>
                <div class="settings-form">
                    <label>Max Daily Trades: <input type="number" value="${this.autoTradingSettings.max_daily_trades || 10}"></label>
                    <label>Max Position Size: <input type="number" value="${this.autoTradingSettings.max_position_size || 1000}"></label>
                    <label>Min Confidence: <input type="range" min="0.5" max="1" step="0.05" value="${this.autoTradingSettings.min_confidence || 0.7}"></label>
                </div>
                <div class="modal-actions">
                    <button onclick="this.parentNode.parentNode.parentNode.removeChild(this.parentNode.parentNode)">Close</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
}

// Initialize trading interface when page loads
let tradingInterface;

document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for the main app to load
    setTimeout(() => {
        tradingInterface = new TradingInterface();
    }, 2000);
});

// Also initialize if called directly
if (typeof window !== 'undefined' && !tradingInterface) {
    tradingInterface = new TradingInterface();
}

