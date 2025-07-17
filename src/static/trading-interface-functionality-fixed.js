// Trading Interface Functionality - FIXED VERSION
// Properly connects to working backend APIs

class TradingInterfaceManager {
    constructor() {
        this.isConnected = false;
        this.selectedBroker = 'demo';
        this.accountBalance = 100000;
        this.portfolio = {};
        this.tradeHistory = [];
        this.init();
    }

    async init() {
        console.log('🚀 Initializing Trading Interface...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Auto-connect to demo account
        await this.autoConnectDemo();
        
        // Load initial data
        await this.loadAccountData();
        
        // Start real-time updates
        this.startRealTimeUpdates();
        
        console.log('✅ Trading Interface initialized');
    }

    setupEventListeners() {
        // Buy button
        const buyBtn = document.getElementById('buy-btn');
        if (buyBtn) {
            buyBtn.addEventListener('click', () => {
                this.executeTrade('buy');
            });
        }

        // Sell button
        const sellBtn = document.getElementById('sell-btn');
        if (sellBtn) {
            sellBtn.addEventListener('click', () => {
                this.executeTrade('sell');
            });
        }

        // Disconnect button
        const disconnectBtn = document.getElementById('disconnect-btn');
        if (disconnectBtn) {
            disconnectBtn.addEventListener('click', () => {
                this.disconnectAccount();
            });
        }
    }

    async autoConnectDemo() {
        try {
            console.log('🔌 Auto-connecting to demo account...');
            
            const response = await fetch('/api/trading/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    broker: 'demo'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.isConnected = true;
                this.selectedBroker = 'demo';
                this.accountBalance = data.account?.balance || 100000;
                this.updateConnectionUI();
                console.log('✅ Demo account connected successfully');
            } else {
                console.error('❌ Failed to connect demo account:', data.message);
            }
            
        } catch (error) {
            console.error('❌ Error connecting demo account:', error);
        }
    }

    async loadAccountData() {
        try {
            const response = await fetch('/api/trading/account-info');
            const data = await response.json();
            
            if (data.success && data.account) {
                this.accountBalance = data.account.balance || 100000;
                this.updatePortfolioUI();
            }
            
        } catch (error) {
            console.error('❌ Error loading account data:', error);
        }
    }

    async executeTrade(side) {
        try {
            const symbolInput = document.getElementById('symbol-input');
            const quantityInput = document.getElementById('quantity-input');
            const orderTypeSelect = document.getElementById('order-type-select');
            
            if (!symbolInput || !quantityInput) {
                this.showNotification('Please enter valid symbol and quantity', 'error');
                return;
            }

            const symbol = symbolInput.value.trim().toUpperCase();
            const quantity = parseFloat(quantityInput.value);
            const orderType = orderTypeSelect ? orderTypeSelect.value : 'market';

            // Validation
            if (!symbol) {
                this.showNotification('Please enter a symbol', 'error');
                return;
            }

            if (!quantity || quantity <= 0) {
                this.showNotification('Please enter valid quantity', 'error');
                return;
            }

            // Show loading state
            this.setTradingButtonsLoading(true);

            console.log(`📈 Executing ${side.toUpperCase()} order: ${quantity} ${symbol}`);

            const response = await fetch('/api/trading/execute-trade', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    side: side,
                    quantity: quantity,
                    order_type: orderType
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(`${side.toUpperCase()} order executed successfully!`, 'success');
                
                // Update account balance
                this.accountBalance -= (data.executed_price * data.executed_quantity + (data.fees || 0));
                
                // Add to trade history
                this.addTradeToHistory({
                    symbol: symbol,
                    side: side.toUpperCase(),
                    quantity: data.executed_quantity,
                    price: data.executed_price,
                    timestamp: new Date().toLocaleString(),
                    fees: data.fees || 0
                });

                // Update portfolio
                this.updatePortfolioPosition(symbol, side, data.executed_quantity, data.executed_price);
                
                // Refresh UI
                this.updatePortfolioUI();
                this.updateTradeHistoryUI();
                
                // Clear form
                symbolInput.value = '';
                quantityInput.value = '';
                
            } else {
                this.showNotification(`Trade failed: ${data.message}`, 'error');
            }

        } catch (error) {
            console.error('❌ Error executing trade:', error);
            this.showNotification('Error executing trade. Please try again.', 'error');
        } finally {
            this.setTradingButtonsLoading(false);
        }
    }

    updatePortfolioPosition(symbol, side, quantity, price) {
        if (!this.portfolio[symbol]) {
            this.portfolio[symbol] = {
                quantity: 0,
                avgPrice: 0,
                currentPrice: price
            };
        }

        const position = this.portfolio[symbol];
        
        if (side === 'buy') {
            const totalValue = (position.quantity * position.avgPrice) + (quantity * price);
            const totalQuantity = position.quantity + quantity;
            position.avgPrice = totalValue / totalQuantity;
            position.quantity = totalQuantity;
        } else if (side === 'sell') {
            position.quantity = Math.max(0, position.quantity - quantity);
            if (position.quantity === 0) {
                delete this.portfolio[symbol];
            }
        }
    }

    addTradeToHistory(trade) {
        this.tradeHistory.unshift(trade);
        // Keep only last 50 trades
        if (this.tradeHistory.length > 50) {
            this.tradeHistory = this.tradeHistory.slice(0, 50);
        }
    }

    updateConnectionUI() {
        const connectionStatus = document.querySelector('.connection-status');
        const accountBalanceEl = document.querySelector('.account-balance');
        
        if (connectionStatus) {
            connectionStatus.textContent = this.isConnected ? 'Connected to DEMO' : 'Disconnected';
            connectionStatus.className = `connection-status ${this.isConnected ? 'connected' : 'disconnected'}`;
        }
        
        if (accountBalanceEl) {
            accountBalanceEl.textContent = `$${this.accountBalance.toLocaleString()}`;
        }
    }

    updatePortfolioUI() {
        // Update cash balance
        const cashBalanceEl = document.querySelector('.cash-balance');
        if (cashBalanceEl) {
            cashBalanceEl.textContent = `$${this.accountBalance.toLocaleString()}`;
        }

        // Calculate total portfolio value
        let totalValue = this.accountBalance;
        for (const [symbol, position] of Object.entries(this.portfolio)) {
            totalValue += position.quantity * position.currentPrice;
        }

        // Update total value
        const totalValueEl = document.querySelector('.total-value');
        if (totalValueEl) {
            totalValueEl.textContent = `$${totalValue.toLocaleString()}`;
        }

        // Update positions
        const positionsContainer = document.querySelector('.positions-container');
        if (positionsContainer) {
            positionsContainer.innerHTML = '';
            
            for (const [symbol, position] of Object.entries(this.portfolio)) {
                const positionEl = document.createElement('div');
                positionEl.className = 'position-item';
                positionEl.innerHTML = `
                    <div class="position-symbol">${symbol}</div>
                    <div class="position-quantity">${position.quantity} shares</div>
                    <div class="position-value">$${(position.quantity * position.currentPrice).toLocaleString()}</div>
                `;
                positionsContainer.appendChild(positionEl);
            }
        }
    }

    updateTradeHistoryUI() {
        const tradeHistoryContainer = document.querySelector('.trade-history-container');
        if (tradeHistoryContainer && this.tradeHistory.length > 0) {
            tradeHistoryContainer.innerHTML = '';
            
            this.tradeHistory.slice(0, 10).forEach(trade => {
                const tradeEl = document.createElement('div');
                tradeEl.className = 'trade-item';
                tradeEl.innerHTML = `
                    <div class="trade-action">${trade.side} ${trade.symbol}</div>
                    <div class="trade-details">${trade.quantity} @ $${trade.price.toLocaleString()}</div>
                    <div class="trade-timestamp">${trade.timestamp}</div>
                `;
                tradeHistoryContainer.appendChild(tradeEl);
            });
        }
    }

    setTradingButtonsLoading(loading) {
        const buyBtn = document.getElementById('buy-btn');
        const sellBtn = document.getElementById('sell-btn');
        
        if (buyBtn) {
            buyBtn.disabled = loading;
            buyBtn.textContent = loading ? 'Processing...' : '↗ BUY';
        }
        
        if (sellBtn) {
            sellBtn.disabled = loading;
            sellBtn.textContent = loading ? 'Processing...' : '↘ SELL';
        }
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(n => n.remove());

        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            z-index: 10000;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    async disconnectAccount() {
        this.isConnected = false;
        this.selectedBroker = null;
        this.accountBalance = 0;
        this.portfolio = {};
        this.tradeHistory = [];
        
        this.updateConnectionUI();
        this.updatePortfolioUI();
        this.updateTradeHistoryUI();
        
        this.showNotification('Account disconnected', 'info');
    }

    startRealTimeUpdates() {
        // Update market prices every 5 seconds
        setInterval(() => {
            this.updateMarketPrices();
        }, 5000);
    }

    updateMarketPrices() {
        // Simulate price updates for portfolio positions
        for (const symbol in this.portfolio) {
            const position = this.portfolio[symbol];
            // Random price movement ±2%
            const change = (Math.random() - 0.5) * 0.04;
            position.currentPrice *= (1 + change);
        }
        
        // Update UI if there are positions
        if (Object.keys(this.portfolio).length > 0) {
            this.updatePortfolioUI();
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.tradingManager = new TradingInterfaceManager();
});

// Export for global access
window.TradingInterfaceManager = TradingInterfaceManager;

