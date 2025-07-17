// Trading Interface Functionality
// Makes all trading features work properly

class TradingInterfaceManager {
    constructor() {
        this.isConnected = false;
        this.selectedBroker = null;
        this.accountBalance = 0;
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
        
        console.log('✅ Trading Interface initialized');
    }

    setupEventListeners() {
        // Broker selection
        const brokerSelect = document.getElementById('broker-select');
        if (brokerSelect) {
            brokerSelect.addEventListener('change', (e) => {
                this.selectedBroker = e.target.value;
                this.updateConnectionUI();
            });
        }

        // Connect button
        const connectBtn = document.getElementById('connect-btn');
        if (connectBtn) {
            connectBtn.addEventListener('click', () => {
                this.connectAccount();
            });
        }

        // Disconnect button
        const disconnectBtn = document.getElementById('disconnect-btn');
        if (disconnectBtn) {
            disconnectBtn.addEventListener('click', () => {
                this.disconnectAccount();
            });
        }

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

        // Symbol input autocomplete
        const symbolInput = document.getElementById('symbol-input');
        if (symbolInput) {
            symbolInput.addEventListener('input', (e) => {
                this.handleSymbolInput(e.target.value);
            });
        }
    }

    async autoConnectDemo() {
        try {
            console.log('🔌 Auto-connecting to demo account...');
            
            const response = await fetch('/api/trading/connect-account', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    broker: 'demo',
                    api_key: 'demo_key',
                    api_secret: 'demo_secret'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.isConnected = true;
                this.selectedBroker = 'demo';
                this.accountBalance = data.account_info.balance;
                this.updateConnectionUI();
                this.updateAccountBalance();
                console.log('✅ Demo account connected successfully');
            } else {
                console.error('❌ Failed to connect demo account:', data.error);
            }
        } catch (error) {
            console.error('❌ Error connecting demo account:', error);
        }
    }

    async connectAccount() {
        try {
            const broker = document.getElementById('broker-select').value;
            const apiKey = document.getElementById('api-key').value;
            const apiSecret = document.getElementById('api-secret').value;

            if (!broker) {
                this.showNotification('Please select a broker', 'error');
                return;
            }

            console.log(`🔌 Connecting to ${broker}...`);

            const response = await fetch('/api/trading/connect-account', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    broker: broker,
                    api_key: apiKey || 'demo_key',
                    api_secret: apiSecret || 'demo_secret'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.isConnected = true;
                this.selectedBroker = broker;
                this.accountBalance = data.account_info.balance;
                this.updateConnectionUI();
                this.updateAccountBalance();
                this.showNotification(`Connected to ${broker.toUpperCase()} successfully!`, 'success');
                console.log(`✅ Connected to ${broker} successfully`);
            } else {
                this.showNotification(`Failed to connect: ${data.error}`, 'error');
                console.error('❌ Failed to connect:', data.error);
            }
        } catch (error) {
            this.showNotification('Connection error occurred', 'error');
            console.error('❌ Connection error:', error);
        }
    }

    async disconnectAccount() {
        try {
            console.log('🔌 Disconnecting account...');

            const response = await fetch('/api/trading/disconnect-account', {
                method: 'POST'
            });

            const data = await response.json();
            
            if (data.success) {
                this.isConnected = false;
                this.selectedBroker = null;
                this.accountBalance = 0;
                this.portfolio = {};
                this.updateConnectionUI();
                this.updateAccountBalance();
                this.updatePortfolio();
                this.showNotification('Account disconnected', 'info');
                console.log('✅ Account disconnected');
            }
        } catch (error) {
            console.error('❌ Disconnect error:', error);
        }
    }

    async executeTrade(side) {
        try {
            if (!this.isConnected) {
                this.showNotification('Please connect to a broker first', 'error');
                return;
            }

            const symbol = document.getElementById('symbol-input').value.toUpperCase();
            const quantity = parseFloat(document.getElementById('quantity-input').value);
            const orderType = document.getElementById('order-type').value;
            const price = document.getElementById('price-input').value;

            if (!symbol || !quantity) {
                this.showNotification('Please enter symbol and quantity', 'error');
                return;
            }

            console.log(`📈 Executing ${side.toUpperCase()} order: ${quantity} ${symbol}`);

            const orderData = {
                symbol: symbol,
                side: side,
                quantity: quantity,
                order_type: orderType,
                price: orderType === 'limit' ? parseFloat(price) : null
            };

            const response = await fetch('/api/trading/execute-trade', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(orderData)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`${side.toUpperCase()} order executed successfully!`, 'success');
                
                // Update account data
                await this.loadAccountData();
                
                // Clear form
                this.clearOrderForm();
                
                console.log(`✅ ${side.toUpperCase()} order executed:`, data.order);
            } else {
                this.showNotification(`Order failed: ${data.error}`, 'error');
                console.error('❌ Order failed:', data.error);
            }
        } catch (error) {
            this.showNotification('Trade execution error', 'error');
            console.error('❌ Trade execution error:', error);
        }
    }

    async loadAccountData() {
        if (!this.isConnected) return;

        try {
            // Load account info
            const accountResponse = await fetch('/api/trading/account-info');
            const accountData = await accountResponse.json();
            
            if (accountData.success) {
                this.accountBalance = accountData.account_info.balance;
                this.updateAccountBalance();
            }

            // Load portfolio
            const portfolioResponse = await fetch('/api/trading/portfolio');
            const portfolioData = await portfolioResponse.json();
            
            if (portfolioData.success) {
                this.portfolio = portfolioData.portfolio;
                this.updatePortfolio();
            }

            // Load trade history
            const historyResponse = await fetch('/api/trading/trade-history');
            const historyData = await historyResponse.json();
            
            if (historyData.success) {
                this.tradeHistory = historyData.trades;
                this.updateTradeHistory();
            }

        } catch (error) {
            console.error('❌ Error loading account data:', error);
        }
    }

    updateConnectionUI() {
        const statusElement = document.querySelector('.connection-status');
        const connectBtn = document.getElementById('connect-btn');
        const disconnectBtn = document.getElementById('disconnect-btn');
        const brokerSelect = document.getElementById('broker-select');

        if (this.isConnected) {
            if (statusElement) {
                statusElement.innerHTML = `
                    <i class="fas fa-circle" style="color: #00ff88;"></i>
                    Connected to ${this.selectedBroker ? this.selectedBroker.toUpperCase() : 'DEMO'}
                `;
            }
            if (connectBtn) connectBtn.style.display = 'none';
            if (disconnectBtn) disconnectBtn.style.display = 'block';
            if (brokerSelect) brokerSelect.disabled = true;
        } else {
            if (statusElement) {
                statusElement.innerHTML = `
                    <i class="fas fa-circle" style="color: #ff4444;"></i>
                    Not Connected
                `;
            }
            if (connectBtn) connectBtn.style.display = 'block';
            if (disconnectBtn) disconnectBtn.style.display = 'none';
            if (brokerSelect) brokerSelect.disabled = false;
        }
    }

    updateAccountBalance() {
        const balanceElement = document.querySelector('.account-balance');
        if (balanceElement) {
            balanceElement.textContent = `$${this.accountBalance.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })}`;
        }
    }

    updatePortfolio() {
        const portfolioContainer = document.querySelector('.portfolio-container');
        if (!portfolioContainer) return;

        if (Object.keys(this.portfolio).length === 0) {
            portfolioContainer.innerHTML = '<p>No positions</p>';
            return;
        }

        let html = '';
        for (const [symbol, position] of Object.entries(this.portfolio)) {
            const value = position.quantity * position.current_price;
            const pnl = value - (position.quantity * position.avg_price);
            const pnlPercent = (pnl / (position.quantity * position.avg_price)) * 100;

            html += `
                <div class="portfolio-item">
                    <div class="position-symbol">${symbol}</div>
                    <div class="position-quantity">${position.quantity} shares</div>
                    <div class="position-value">$${value.toFixed(2)}</div>
                    <div class="position-pnl ${pnl >= 0 ? 'positive' : 'negative'}">
                        ${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)} (${pnlPercent.toFixed(2)}%)
                    </div>
                </div>
            `;
        }

        portfolioContainer.innerHTML = html;
    }

    updateTradeHistory() {
        const historyContainer = document.querySelector('.trade-history-container');
        if (!historyContainer) return;

        if (this.tradeHistory.length === 0) {
            historyContainer.innerHTML = '<p>No trades yet</p>';
            return;
        }

        let html = '';
        this.tradeHistory.slice(-10).reverse().forEach(trade => {
            const date = new Date(trade.timestamp).toLocaleString();
            html += `
                <div class="trade-item">
                    <div class="trade-side ${trade.side}">${trade.side.toUpperCase()}</div>
                    <div class="trade-symbol">${trade.symbol}</div>
                    <div class="trade-quantity">${trade.quantity}</div>
                    <div class="trade-price">$${trade.price}</div>
                    <div class="trade-total">$${(trade.quantity * trade.price).toFixed(2)}</div>
                    <div class="trade-date">${date}</div>
                </div>
            `;
        });

        historyContainer.innerHTML = html;
    }

    clearOrderForm() {
        const symbolInput = document.getElementById('symbol-input');
        const quantityInput = document.getElementById('quantity-input');
        const priceInput = document.getElementById('price-input');

        if (symbolInput) symbolInput.value = '';
        if (quantityInput) quantityInput.value = '';
        if (priceInput) priceInput.value = '';
    }

    handleSymbolInput(value) {
        // Add autocomplete functionality for symbols
        const suggestions = ['BTC', 'ETH', 'AAPL', 'TSLA', 'NVDA', 'GOOGL', 'META', 'AMZN', 'MSFT'];
        const filtered = suggestions.filter(symbol => 
            symbol.toLowerCase().includes(value.toLowerCase())
        );
        
        // You can implement a dropdown here
        console.log('Symbol suggestions:', filtered);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;

        // Set background color based on type
        const colors = {
            success: '#00ff88',
            error: '#ff4444',
            info: '#4488ff',
            warning: '#ffaa00'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        // Add to page
        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Trading Interface Manager...');
    window.tradingManager = new TradingInterfaceManager();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .portfolio-item {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 10px;
        padding: 10px;
        border-bottom: 1px solid #333;
    }
    
    .trade-item {
        display: grid;
        grid-template-columns: 60px 80px 80px 80px 100px 120px;
        gap: 10px;
        padding: 8px;
        border-bottom: 1px solid #333;
        font-size: 14px;
    }
    
    .trade-side.buy { color: #00ff88; }
    .trade-side.sell { color: #ff4444; }
    
    .position-pnl.positive { color: #00ff88; }
    .position-pnl.negative { color: #ff4444; }
`;
document.head.appendChild(style);

