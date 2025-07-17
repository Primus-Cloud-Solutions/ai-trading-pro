// Real-Time Updates System
// Handles live portfolio tracking, balance updates, and market data

class RealTimeUpdatesManager {
    constructor() {
        this.updateInterval = 3000; // 3 seconds
        this.isActive = false;
        this.intervals = [];
        this.lastUpdateTime = 0;
        this.connectionStatus = 'disconnected';
        this.init();
    }

    init() {
        console.log('🔄 Initializing Real-Time Updates Manager...');
        this.startUpdates();
        this.setupConnectionMonitoring();
        console.log('✅ Real-Time Updates Manager initialized');
    }

    startUpdates() {
        if (this.isActive) return;
        
        this.isActive = true;
        console.log('🚀 Starting real-time updates...');
        
        // Portfolio updates
        const portfolioInterval = setInterval(() => {
            this.updatePortfolio();
        }, this.updateInterval);
        
        // Market data updates
        const marketInterval = setInterval(() => {
            this.updateMarketData();
        }, this.updateInterval + 1000); // Offset by 1 second
        
        // Trading statistics updates
        const statsInterval = setInterval(() => {
            this.updateTradingStatistics();
        }, this.updateInterval * 2); // Every 6 seconds
        
        // Connection status updates
        const connectionInterval = setInterval(() => {
            this.updateConnectionStatus();
        }, 5000); // Every 5 seconds
        
        this.intervals.push(portfolioInterval, marketInterval, statsInterval, connectionInterval);
        
        // Update connection indicator
        this.updateConnectionIndicator('connected');
    }

    stopUpdates() {
        this.isActive = false;
        console.log('🛑 Stopping real-time updates...');
        
        this.intervals.forEach(interval => clearInterval(interval));
        this.intervals = [];
        
        this.updateConnectionIndicator('disconnected');
    }

    async updatePortfolio() {
        try {
            const response = await fetch('/api/trading/portfolio');
            const data = await response.json();
            
            if (data.success && data.portfolio) {
                this.updatePortfolioUI(data.portfolio);
                this.lastUpdateTime = Date.now();
            }
            
        } catch (error) {
            console.error('❌ Error updating portfolio:', error);
            this.handleUpdateError('portfolio');
        }
    }

    async updateMarketData() {
        try {
            const response = await fetch('/api/trading/market/prices');
            const data = await response.json();
            
            if (data.success && data.prices) {
                this.updateMarketPricesUI(data.prices);
                this.updatePriceChangeIndicators(data.prices);
            }
            
        } catch (error) {
            console.error('❌ Error updating market data:', error);
            this.handleUpdateError('market');
        }
    }

    async updateTradingStatistics() {
        try {
            const response = await fetch('/api/trading/analytics/statistics');
            const data = await response.json();
            
            if (data.success && data.statistics) {
                this.updateStatisticsUI(data.statistics);
            }
            
        } catch (error) {
            console.error('❌ Error updating statistics:', error);
            this.handleUpdateError('statistics');
        }
    }

    async updateConnectionStatus() {
        try {
            const response = await fetch('/api/trading/status');
            const data = await response.json();
            
            if (data.success) {
                this.connectionStatus = data.connected ? 'connected' : 'disconnected';
                this.updateConnectionIndicator(this.connectionStatus);
            }
            
        } catch (error) {
            console.error('❌ Error checking connection status:', error);
            this.connectionStatus = 'error';
            this.updateConnectionIndicator('error');
        }
    }

    updatePortfolioUI(portfolio) {
        // Update cash balance
        const cashElements = document.querySelectorAll('.cash-balance, .account-balance');
        cashElements.forEach(el => {
            if (el) {
                el.textContent = `$${portfolio.cash_balance.toLocaleString()}`;
                this.addUpdateAnimation(el);
            }
        });

        // Update total portfolio value
        const totalValueElements = document.querySelectorAll('.total-value, .portfolio-value');
        totalValueElements.forEach(el => {
            if (el) {
                el.textContent = `$${portfolio.total_value.toLocaleString()}`;
                this.addUpdateAnimation(el);
            }
        });

        // Update positions
        this.updatePositionsDisplay(portfolio.positions);
        
        // Update buying power
        const buyingPowerElements = document.querySelectorAll('.buying-power');
        buyingPowerElements.forEach(el => {
            if (el) {
                el.textContent = `$${portfolio.buying_power.toLocaleString()}`;
            }
        });
    }

    updatePositionsDisplay(positions) {
        const positionsContainer = document.querySelector('.positions-container');
        if (!positionsContainer || !positions) return;

        // Clear existing positions
        positionsContainer.innerHTML = '';

        if (positions.length === 0) {
            positionsContainer.innerHTML = '<div class="no-positions">No positions</div>';
            return;
        }

        positions.forEach(position => {
            const positionEl = document.createElement('div');
            positionEl.className = 'position-item';
            positionEl.innerHTML = `
                <div class="position-header">
                    <span class="position-symbol">${position.symbol}</span>
                    <span class="position-value">$${position.market_value.toLocaleString()}</span>
                </div>
                <div class="position-details">
                    <span class="position-quantity">${position.quantity} shares</span>
                    <span class="position-price">@$${position.current_price.toLocaleString()}</span>
                </div>
            `;
            
            // Add to container with animation
            positionEl.style.opacity = '0';
            positionsContainer.appendChild(positionEl);
            
            // Animate in
            setTimeout(() => {
                positionEl.style.transition = 'opacity 0.3s ease';
                positionEl.style.opacity = '1';
            }, 50);
        });
    }

    updateMarketPricesUI(prices) {
        // Update any displayed market prices
        Object.entries(prices).forEach(([symbol, price]) => {
            const priceElements = document.querySelectorAll(`[data-symbol="${symbol}"] .price`);
            priceElements.forEach(el => {
                if (el) {
                    el.textContent = `$${price.toLocaleString()}`;
                    this.addUpdateAnimation(el);
                }
            });
        });
    }

    updatePriceChangeIndicators(prices) {
        // Store previous prices for comparison
        if (!this.previousPrices) {
            this.previousPrices = { ...prices };
            return;
        }

        Object.entries(prices).forEach(([symbol, currentPrice]) => {
            const previousPrice = this.previousPrices[symbol];
            if (previousPrice && previousPrice !== currentPrice) {
                const change = currentPrice - previousPrice;
                const changePercent = (change / previousPrice) * 100;
                
                // Update change indicators
                const changeElements = document.querySelectorAll(`[data-symbol="${symbol}"] .price-change`);
                changeElements.forEach(el => {
                    if (el) {
                        el.textContent = `${change >= 0 ? '+' : ''}${changePercent.toFixed(2)}%`;
                        el.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;
                        this.addUpdateAnimation(el);
                    }
                });
            }
        });

        this.previousPrices = { ...prices };
    }

    updateStatisticsUI(statistics) {
        const { account, performance, positions } = statistics;

        // Update account statistics
        if (account) {
            const investedPercentEl = document.querySelector('.invested-percentage');
            if (investedPercentEl) {
                investedPercentEl.textContent = `${account.invested_percentage}%`;
                this.addUpdateAnimation(investedPercentEl);
            }

            const cashPercentEl = document.querySelector('.cash-percentage');
            if (cashPercentEl) {
                cashPercentEl.textContent = `${account.cash_percentage}%`;
                this.addUpdateAnimation(cashPercentEl);
            }
        }

        // Update performance metrics
        if (performance) {
            const winRateEl = document.querySelector('.win-rate');
            if (winRateEl) {
                winRateEl.textContent = `${performance.win_rate}%`;
                this.addUpdateAnimation(winRateEl);
            }

            const totalPnlEl = document.querySelector('.total-pnl');
            if (totalPnlEl) {
                totalPnlEl.textContent = `$${performance.total_pnl.toLocaleString()}`;
                totalPnlEl.className = `total-pnl ${performance.total_pnl >= 0 ? 'positive' : 'negative'}`;
                this.addUpdateAnimation(totalPnlEl);
            }

            const totalTradesEl = document.querySelector('.total-trades');
            if (totalTradesEl) {
                totalTradesEl.textContent = performance.total_trades;
                this.addUpdateAnimation(totalTradesEl);
            }
        }

        // Update position count
        if (positions) {
            const positionCountEl = document.querySelector('.position-count');
            if (positionCountEl) {
                positionCountEl.textContent = positions.position_count;
                this.addUpdateAnimation(positionCountEl);
            }
        }
    }

    updateConnectionIndicator(status) {
        const indicators = document.querySelectorAll('.connection-indicator, .connection-status');
        
        indicators.forEach(indicator => {
            if (indicator) {
                indicator.className = `connection-indicator ${status}`;
                
                switch (status) {
                    case 'connected':
                        indicator.textContent = '🟢 Connected';
                        indicator.style.color = '#10b981';
                        break;
                    case 'disconnected':
                        indicator.textContent = '🔴 Disconnected';
                        indicator.style.color = '#ef4444';
                        break;
                    case 'error':
                        indicator.textContent = '⚠️ Connection Error';
                        indicator.style.color = '#f59e0b';
                        break;
                }
            }
        });

        // Update last update time
        const lastUpdateEl = document.querySelector('.last-update-time');
        if (lastUpdateEl) {
            lastUpdateEl.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }
    }

    addUpdateAnimation(element) {
        if (!element) return;
        
        // Add pulse animation
        element.style.transition = 'all 0.3s ease';
        element.style.transform = 'scale(1.05)';
        element.style.boxShadow = '0 0 10px rgba(16, 185, 129, 0.3)';
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
            element.style.boxShadow = 'none';
        }, 300);
    }

    handleUpdateError(type) {
        console.warn(`⚠️ Update error for ${type}, retrying...`);
        
        // Show error indicator briefly
        const errorIndicator = document.querySelector('.update-error-indicator');
        if (errorIndicator) {
            errorIndicator.style.display = 'block';
            errorIndicator.textContent = `Update error: ${type}`;
            
            setTimeout(() => {
                errorIndicator.style.display = 'none';
            }, 3000);
        }
    }

    setupConnectionMonitoring() {
        // Monitor page visibility to pause/resume updates
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('📱 Page hidden, pausing updates...');
                this.stopUpdates();
            } else {
                console.log('📱 Page visible, resuming updates...');
                this.startUpdates();
            }
        });

        // Monitor online/offline status
        window.addEventListener('online', () => {
            console.log('🌐 Connection restored, resuming updates...');
            if (!this.isActive) {
                this.startUpdates();
            }
        });

        window.addEventListener('offline', () => {
            console.log('📡 Connection lost, pausing updates...');
            this.stopUpdates();
        });
    }

    // Public methods for manual control
    pause() {
        this.stopUpdates();
    }

    resume() {
        this.startUpdates();
    }

    forceUpdate() {
        console.log('🔄 Forcing immediate update...');
        this.updatePortfolio();
        this.updateMarketData();
        this.updateTradingStatistics();
        this.updateConnectionStatus();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.realTimeUpdates = new RealTimeUpdatesManager();
});

// Export for global access
window.RealTimeUpdatesManager = RealTimeUpdatesManager;

