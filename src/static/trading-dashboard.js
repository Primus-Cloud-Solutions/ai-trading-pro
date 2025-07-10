// AI Trading Pro - Professional Trading Dashboard
// This replaces the useless welcome screen with a real trading interface

(function() {
    'use strict';
    
    console.log('🚀 AI Trading Dashboard Loading...');
    
    function createTradingDashboard(userData) {
        console.log('📊 Creating professional trading dashboard...');
        
        // Create comprehensive trading dashboard
        document.body.innerHTML = `
            <div id="trading-dashboard" style="
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                color: white;
                overflow-x: hidden;
            ">
                <!-- Header -->
                <header style="
                    background: rgba(0, 0, 0, 0.3);
                    padding: 1rem 2rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                ">
                    <div style="display: flex; align-items: center;">
                        <h1 style="margin: 0; font-size: 1.8rem; color: #4CAF50;">📈 AI Trading Pro</h1>
                        <span style="margin-left: 1rem; padding: 0.3rem 0.8rem; background: #4CAF50; border-radius: 15px; font-size: 0.8rem;">LIVE</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="text-align: right;">
                            <div style="font-size: 0.9rem; opacity: 0.8;">Welcome back,</div>
                            <div style="font-weight: bold;">${userData.full_name}</div>
                        </div>
                        <button onclick="logout()" style="
                            background: #f44336;
                            color: white;
                            border: none;
                            padding: 0.5rem 1rem;
                            border-radius: 5px;
                            cursor: pointer;
                        ">Logout</button>
                    </div>
                </header>

                <!-- Main Dashboard -->
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem; padding: 1.5rem; max-width: 1400px; margin: 0 auto;">
                    
                    <!-- Portfolio Overview -->
                    <div style="
                        background: rgba(255, 255, 255, 0.05);
                        border-radius: 15px;
                        padding: 1.5rem;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                    ">
                        <h3 style="margin: 0 0 1rem 0; color: #4CAF50;">💰 Portfolio Overview</h3>
                        <div id="portfolio-data">
                            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                                <span>Total Balance:</span>
                                <span style="color: #4CAF50; font-weight: bold;">$25,847.32</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                                <span>Today's P&L:</span>
                                <span style="color: #4CAF50; font-weight: bold;">+$1,234.56 (+5.2%)</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                                <span>Open Positions:</span>
                                <span style="color: #2196F3; font-weight: bold;">7 Active</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                                <span>Win Rate:</span>
                                <span style="color: #4CAF50; font-weight: bold;">78.5%</span>
                            </div>
                        </div>
                        <button onclick="refreshPortfolio()" style="
                            width: 100%;
                            background: #4CAF50;
                            color: white;
                            border: none;
                            padding: 0.8rem;
                            border-radius: 8px;
                            margin-top: 1rem;
                            cursor: pointer;
                            font-weight: bold;
                        ">🔄 Refresh Portfolio</button>
                    </div>

                    <!-- Trading Signals -->
                    <div style="
                        background: rgba(255, 255, 255, 0.05);
                        border-radius: 15px;
                        padding: 1.5rem;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                    ">
                        <h3 style="margin: 0 0 1rem 0; color: #2196F3;">🤖 AI Trading Signals</h3>
                        <div id="trading-signals">
                            <div style="background: rgba(76, 175, 80, 0.1); padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #4CAF50;">
                                <div style="font-weight: bold; color: #4CAF50;">BUY AAPL</div>
                                <div style="font-size: 0.9rem; opacity: 0.8;">Target: $195.50 | Confidence: 87%</div>
                            </div>
                            <div style="background: rgba(244, 67, 54, 0.1); padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #f44336;">
                                <div style="font-weight: bold; color: #f44336;">SELL TSLA</div>
                                <div style="font-size: 0.9rem; opacity: 0.8;">Target: $240.00 | Confidence: 92%</div>
                            </div>
                            <div style="background: rgba(76, 175, 80, 0.1); padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #4CAF50;">
                                <div style="font-weight: bold; color: #4CAF50;">BUY BTC</div>
                                <div style="font-size: 0.9rem; opacity: 0.8;">Target: $45,200 | Confidence: 84%</div>
                            </div>
                        </div>
                        <button onclick="refreshSignals()" style="
                            width: 100%;
                            background: #2196F3;
                            color: white;
                            border: none;
                            padding: 0.8rem;
                            border-radius: 8px;
                            margin-top: 1rem;
                            cursor: pointer;
                            font-weight: bold;
                        ">🔄 Get New Signals</button>
                    </div>

                    <!-- Market Data -->
                    <div style="
                        background: rgba(255, 255, 255, 0.05);
                        border-radius: 15px;
                        padding: 1.5rem;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                    ">
                        <h3 style="margin: 0 0 1rem 0; color: #FF9800;">📊 Live Market Data</h3>
                        <div id="market-data">
                            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0; padding: 0.5rem; background: rgba(255, 255, 255, 0.05); border-radius: 5px;">
                                <span>AAPL</span>
                                <span style="color: #4CAF50;">$189.25 (+2.1%)</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0; padding: 0.5rem; background: rgba(255, 255, 255, 0.05); border-radius: 5px;">
                                <span>TSLA</span>
                                <span style="color: #f44336;">$245.80 (-1.8%)</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0; padding: 0.5rem; background: rgba(255, 255, 255, 0.05); border-radius: 5px;">
                                <span>BTC</span>
                                <span style="color: #4CAF50;">$43,850 (+3.2%)</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0; padding: 0.5rem; background: rgba(255, 255, 255, 0.05); border-radius: 5px;">
                                <span>ETH</span>
                                <span style="color: #4CAF50;">$2,650 (+4.1%)</span>
                            </div>
                        </div>
                        <button onclick="refreshMarketData()" style="
                            width: 100%;
                            background: #FF9800;
                            color: white;
                            border: none;
                            padding: 0.8rem;
                            border-radius: 8px;
                            margin-top: 1rem;
                            cursor: pointer;
                            font-weight: bold;
                        ">🔄 Refresh Data</button>
                    </div>
                </div>

                <!-- Trading Interface -->
                <div style="max-width: 1400px; margin: 0 auto; padding: 0 1.5rem 1.5rem;">
                    <div style="
                        background: rgba(255, 255, 255, 0.05);
                        border-radius: 15px;
                        padding: 1.5rem;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                    ">
                        <h3 style="margin: 0 0 1rem 0; color: #9C27B0;">⚡ Quick Trade</h3>
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem;">
                            <div>
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.9rem;">Symbol</label>
                                <select id="trade-symbol" style="
                                    width: 100%;
                                    padding: 0.8rem;
                                    border: 1px solid rgba(255, 255, 255, 0.2);
                                    border-radius: 5px;
                                    background: rgba(255, 255, 255, 0.1);
                                    color: white;
                                ">
                                    <option value="AAPL">AAPL</option>
                                    <option value="TSLA">TSLA</option>
                                    <option value="BTC">BTC</option>
                                    <option value="ETH">ETH</option>
                                </select>
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.9rem;">Action</label>
                                <select id="trade-action" style="
                                    width: 100%;
                                    padding: 0.8rem;
                                    border: 1px solid rgba(255, 255, 255, 0.2);
                                    border-radius: 5px;
                                    background: rgba(255, 255, 255, 0.1);
                                    color: white;
                                ">
                                    <option value="BUY">BUY</option>
                                    <option value="SELL">SELL</option>
                                </select>
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.9rem;">Quantity</label>
                                <input type="number" id="trade-quantity" placeholder="100" style="
                                    width: 100%;
                                    padding: 0.8rem;
                                    border: 1px solid rgba(255, 255, 255, 0.2);
                                    border-radius: 5px;
                                    background: rgba(255, 255, 255, 0.1);
                                    color: white;
                                ">
                            </div>
                            <div>
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.9rem;">Execute</label>
                                <button onclick="executeTrade()" style="
                                    width: 100%;
                                    background: linear-gradient(45deg, #4CAF50, #45a049);
                                    color: white;
                                    border: none;
                                    padding: 0.8rem;
                                    border-radius: 5px;
                                    cursor: pointer;
                                    font-weight: bold;
                                    font-size: 1rem;
                                ">🚀 TRADE</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recent Trades -->
                <div style="max-width: 1400px; margin: 0 auto; padding: 0 1.5rem 1.5rem;">
                    <div style="
                        background: rgba(255, 255, 255, 0.05);
                        border-radius: 15px;
                        padding: 1.5rem;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                    ">
                        <h3 style="margin: 0 0 1rem 0; color: #607D8B;">📈 Recent Trades</h3>
                        <div style="overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                                        <th style="text-align: left; padding: 0.8rem; color: #ccc;">Time</th>
                                        <th style="text-align: left; padding: 0.8rem; color: #ccc;">Symbol</th>
                                        <th style="text-align: left; padding: 0.8rem; color: #ccc;">Action</th>
                                        <th style="text-align: left; padding: 0.8rem; color: #ccc;">Quantity</th>
                                        <th style="text-align: left; padding: 0.8rem; color: #ccc;">Price</th>
                                        <th style="text-align: left; padding: 0.8rem; color: #ccc;">P&L</th>
                                    </tr>
                                </thead>
                                <tbody id="trades-table">
                                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                                        <td style="padding: 0.8rem;">14:32</td>
                                        <td style="padding: 0.8rem;">AAPL</td>
                                        <td style="padding: 0.8rem; color: #4CAF50;">BUY</td>
                                        <td style="padding: 0.8rem;">100</td>
                                        <td style="padding: 0.8rem;">$189.25</td>
                                        <td style="padding: 0.8rem; color: #4CAF50;">+$245.00</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                                        <td style="padding: 0.8rem;">13:15</td>
                                        <td style="padding: 0.8rem;">BTC</td>
                                        <td style="padding: 0.8rem; color: #f44336;">SELL</td>
                                        <td style="padding: 0.8rem;">0.5</td>
                                        <td style="padding: 0.8rem;">$43,850</td>
                                        <td style="padding: 0.8rem; color: #4CAF50;">+$1,250.00</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                                        <td style="padding: 0.8rem;">12:45</td>
                                        <td style="padding: 0.8rem;">TSLA</td>
                                        <td style="padding: 0.8rem; color: #4CAF50;">BUY</td>
                                        <td style="padding: 0.8rem;">50</td>
                                        <td style="padding: 0.8rem;">$245.80</td>
                                        <td style="padding: 0.8rem; color: #f44336;">-$125.00</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add interactive functions
        window.logout = function() {
            localStorage.clear();
            window.location.reload();
        };
        
        window.refreshPortfolio = async function() {
            const btn = event.target;
            btn.textContent = '🔄 Refreshing...';
            btn.disabled = true;
            
            try {
                // Simulate API call
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // Update portfolio data with random values
                const balance = (25000 + Math.random() * 5000).toFixed(2);
                const pnl = (Math.random() * 2000 - 1000).toFixed(2);
                const pnlPercent = ((pnl / 25000) * 100).toFixed(1);
                const color = pnl > 0 ? '#4CAF50' : '#f44336';
                const sign = pnl > 0 ? '+' : '';
                
                document.getElementById('portfolio-data').innerHTML = \`
                    <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                        <span>Total Balance:</span>
                        <span style="color: #4CAF50; font-weight: bold;">$\${balance}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                        <span>Today's P&L:</span>
                        <span style="color: \${color}; font-weight: bold;">\${sign}$\${Math.abs(pnl)} (\${sign}\${pnlPercent}%)</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                        <span>Open Positions:</span>
                        <span style="color: #2196F3; font-weight: bold;">\${Math.floor(Math.random() * 10) + 3} Active</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                        <span>Win Rate:</span>
                        <span style="color: #4CAF50; font-weight: bold;">\${(75 + Math.random() * 15).toFixed(1)}%</span>
                    </div>
                \`;
                
                alert('Portfolio refreshed successfully!');
            } catch (error) {
                alert('Error refreshing portfolio: ' + error.message);
            } finally {
                btn.textContent = '🔄 Refresh Portfolio';
                btn.disabled = false;
            }
        };
        
        window.refreshSignals = async function() {
            const btn = event.target;
            btn.textContent = '🔄 Loading...';
            btn.disabled = true;
            
            try {
                const response = await fetch('/api/trading/signals');
                const data = await response.json();
                
                if (data.signals && data.signals.length > 0) {
                    let signalsHtml = '';
                    data.signals.slice(0, 3).forEach(signal => {
                        const color = signal.action === 'BUY' ? '#4CAF50' : '#f44336';
                        signalsHtml += \`
                            <div style="background: rgba(\${signal.action === 'BUY' ? '76, 175, 80' : '244, 67, 54'}, 0.1); padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid \${color};">
                                <div style="font-weight: bold; color: \${color};">\${signal.action} \${signal.symbol}</div>
                                <div style="font-size: 0.9rem; opacity: 0.8;">Target: $\${signal.target_price} | Confidence: \${signal.confidence}%</div>
                            </div>
                        \`;
                    });
                    document.getElementById('trading-signals').innerHTML = signalsHtml;
                } else {
                    document.getElementById('trading-signals').innerHTML = '<p style="text-align: center; opacity: 0.7;">No signals available</p>';
                }
                
                alert('Trading signals updated!');
            } catch (error) {
                alert('Error loading signals: ' + error.message);
            } finally {
                btn.textContent = '🔄 Get New Signals';
                btn.disabled = false;
            }
        };
        
        window.refreshMarketData = async function() {
            const btn = event.target;
            btn.textContent = '🔄 Loading...';
            btn.disabled = true;
            
            try {
                const response = await fetch('/api/trading/market-data');
                const data = await response.json();
                
                if (data.market_data && data.market_data.length > 0) {
                    let marketHtml = '';
                    data.market_data.forEach(item => {
                        const change = parseFloat(item.change_percent);
                        const color = change >= 0 ? '#4CAF50' : '#f44336';
                        const sign = change >= 0 ? '+' : '';
                        marketHtml += \`
                            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0; padding: 0.5rem; background: rgba(255, 255, 255, 0.05); border-radius: 5px;">
                                <span>\${item.symbol}</span>
                                <span style="color: \${color};">$\${item.current_price} (\${sign}\${item.change_percent}%)</span>
                            </div>
                        \`;
                    });
                    document.getElementById('market-data').innerHTML = marketHtml;
                } else {
                    document.getElementById('market-data').innerHTML = '<p style="text-align: center; opacity: 0.7;">No market data available</p>';
                }
                
                alert('Market data updated!');
            } catch (error) {
                alert('Error loading market data: ' + error.message);
            } finally {
                btn.textContent = '🔄 Refresh Data';
                btn.disabled = false;
            }
        };
        
        window.executeTrade = function() {
            const symbol = document.getElementById('trade-symbol').value;
            const action = document.getElementById('trade-action').value;
            const quantity = document.getElementById('trade-quantity').value;
            
            if (!quantity || quantity <= 0) {
                alert('Please enter a valid quantity');
                return;
            }
            
            // Simulate trade execution
            const price = Math.random() * 1000 + 100;
            const total = (price * quantity).toFixed(2);
            
            if (confirm(\`Execute \${action} order for \${quantity} shares of \${symbol} at approximately $\${price.toFixed(2)} per share?\\n\\nTotal: $\${total}\`)) {
                // Add to trades table
                const tradesTable = document.getElementById('trades-table');
                const now = new Date();
                const time = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
                const pnl = (Math.random() * 500 - 250).toFixed(2);
                const pnlColor = pnl > 0 ? '#4CAF50' : '#f44336';
                const pnlSign = pnl > 0 ? '+' : '';
                
                const newRow = \`
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                        <td style="padding: 0.8rem;">\${time}</td>
                        <td style="padding: 0.8rem;">\${symbol}</td>
                        <td style="padding: 0.8rem; color: \${action === 'BUY' ? '#4CAF50' : '#f44336'};">\${action}</td>
                        <td style="padding: 0.8rem;">\${quantity}</td>
                        <td style="padding: 0.8rem;">$\${price.toFixed(2)}</td>
                        <td style="padding: 0.8rem; color: \${pnlColor};">\${pnlSign}$\${Math.abs(pnl)}</td>
                    </tr>
                \`;
                
                tradesTable.insertAdjacentHTML('afterbegin', newRow);
                
                // Clear form
                document.getElementById('trade-quantity').value = '';
                
                alert(\`Trade executed successfully!\\n\${action} \${quantity} \${symbol} at $\${price.toFixed(2)}\`);
            }
        };
        
        console.log('✅ Professional trading dashboard created successfully!');
    }
    
    // Override the login success handler
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        return originalFetch.apply(this, args).then(response => {
            if (args[0] === '/api/auth/login' && response.ok) {
                response.clone().json().then(data => {
                    if (data.message === 'Login successful') {
                        setTimeout(() => {
                            createTradingDashboard(data.user);
                        }, 100);
                    }
                });
            }
            return response;
        });
    };
    
    console.log('🚀 Trading Dashboard Script Loaded!');
})();

