// Trading Chart Implementation
// Creates a live trading chart with real-time data visualization

class TradingChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.chart = null;
        this.data = [];
        this.labels = [];
        this.isInitialized = false;
        
        this.init();
    }
    
    init() {
        if (!this.canvas) {
            console.error('Chart canvas not found');
            return;
        }
        
        // Generate initial data
        this.generateInitialData();
        
        // Create the chart
        this.createChart();
        
        // Start live updates
        this.startLiveUpdates();
        
        this.isInitialized = true;
    }
    
    generateInitialData() {
        const now = new Date();
        const basePrice = 42500; // Starting BTC price
        
        // Generate 50 data points for the last 50 minutes
        for (let i = 49; i >= 0; i--) {
            const time = new Date(now.getTime() - (i * 60000)); // 1 minute intervals
            const price = basePrice + (Math.random() - 0.5) * 2000 + Math.sin(i * 0.1) * 500;
            
            this.labels.push(time.toLocaleTimeString('en-US', { 
                hour12: false, 
                hour: '2-digit', 
                minute: '2-digit' 
            }));
            this.data.push(price);
        }
    }
    
    createChart() {
        const gradient = this.ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(13, 128, 67, 0.3)');
        gradient.addColorStop(1, 'rgba(13, 128, 67, 0.05)');
        
        this.chart = new Chart(this.ctx, {
            type: 'line',
            data: {
                labels: this.labels,
                datasets: [{
                    label: 'BTC/USD',
                    data: this.data,
                    borderColor: '#0D8043',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#0D8043',
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(26, 26, 46, 0.95)',
                        titleColor: '#ffffff',
                        bodyColor: '#e0e0e0',
                        borderColor: '#0D8043',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: function(context) {
                                return 'BTC/USD';
                            },
                            label: function(context) {
                                return '$' + context.parsed.y.toLocaleString('en-US', {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                });
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#888888',
                            font: {
                                size: 11
                            },
                            maxTicksLimit: 8
                        }
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#888888',
                            font: {
                                size: 11
                            },
                            callback: function(value) {
                                return '$' + value.toLocaleString('en-US', {
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                });
                            }
                        }
                    }
                },
                elements: {
                    point: {
                        hoverRadius: 8
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }
    
    addDataPoint() {
        const now = new Date();
        const timeLabel = now.toLocaleTimeString('en-US', { 
            hour12: false, 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        // Generate realistic price movement
        const lastPrice = this.data[this.data.length - 1];
        const volatility = 50; // Price volatility
        const trend = Math.sin(Date.now() / 100000) * 20; // Subtle trend
        const randomChange = (Math.random() - 0.5) * volatility;
        const newPrice = lastPrice + trend + randomChange;
        
        // Add new data point
        this.labels.push(timeLabel);
        this.data.push(newPrice);
        
        // Keep only last 50 points
        if (this.data.length > 50) {
            this.labels.shift();
            this.data.shift();
        }
        
        // Update chart
        this.chart.update('none');
    }
    
    startLiveUpdates() {
        // Update every 3 seconds
        setInterval(() => {
            this.addDataPoint();
        }, 3000);
        
        // Add some random spikes occasionally
        setInterval(() => {
            if (Math.random() < 0.3) { // 30% chance
                const spike = (Math.random() - 0.5) * 200;
                const lastIndex = this.data.length - 1;
                this.data[lastIndex] += spike;
                this.chart.update('none');
            }
        }, 8000);
    }
    
    updateTheme(isDark = true) {
        if (!this.chart) return;
        
        const textColor = isDark ? '#888888' : '#333333';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        
        this.chart.options.scales.x.ticks.color = textColor;
        this.chart.options.scales.y.ticks.color = textColor;
        this.chart.options.scales.x.grid.color = gridColor;
        this.chart.options.scales.y.grid.color = gridColor;
        
        this.chart.update();
    }
    
    destroy() {
        if (this.chart) {
            this.chart.destroy();
        }
    }
}

// Additional chart utilities
class MarketIndicators {
    constructor() {
        this.indicators = {
            price: 42500,
            change: 0,
            changePercent: 0,
            volume: '1.2B',
            marketCap: '832.5B'
        };
        
        this.updateIndicators();
        this.startIndicatorUpdates();
    }
    
    updateIndicators() {
        // Simulate price changes
        const change = (Math.random() - 0.5) * 100;
        this.indicators.price += change;
        this.indicators.change = change;
        this.indicators.changePercent = (change / this.indicators.price) * 100;
        
        // Update UI elements if they exist
        this.updateUI();
    }
    
    updateUI() {
        const priceElement = document.getElementById('current-price');
        const changeElement = document.getElementById('price-change');
        const percentElement = document.getElementById('price-percent');
        
        if (priceElement) {
            priceElement.textContent = '$' + this.indicators.price.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
        
        if (changeElement) {
            const isPositive = this.indicators.change >= 0;
            changeElement.textContent = (isPositive ? '+' : '') + this.indicators.change.toFixed(2);
            changeElement.className = isPositive ? 'positive' : 'negative';
        }
        
        if (percentElement) {
            const isPositive = this.indicators.changePercent >= 0;
            percentElement.textContent = (isPositive ? '+' : '') + this.indicators.changePercent.toFixed(2) + '%';
            percentElement.className = isPositive ? 'positive' : 'negative';
        }
    }
    
    startIndicatorUpdates() {
        setInterval(() => {
            this.updateIndicators();
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for Chart.js to load
    setTimeout(() => {
        if (typeof Chart !== 'undefined') {
            window.tradingChart = new TradingChart('liveChart');
            window.marketIndicators = new MarketIndicators();
        } else {
            console.error('Chart.js not loaded');
        }
    }, 500);
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (window.tradingChart) {
        window.tradingChart.destroy();
    }
});

