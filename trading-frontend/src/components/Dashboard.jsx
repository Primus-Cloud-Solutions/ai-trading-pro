import { useState, useEffect } from 'react'
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Target, 
  Bot,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

const Dashboard = ({ user, apiBaseUrl }) => {
  const [portfolioData, setPortfolioData] = useState(null)
  const [recentTrades, setRecentTrades] = useState([])
  const [tradingSignals, setTradingSignals] = useState([])
  const [marketOpportunities, setMarketOpportunities] = useState([])
  const [aiEngineStatus, setAiEngineStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  useEffect(() => {
    fetchDashboardData()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }

      // Fetch portfolio data
      const portfolioResponse = await fetch(`${apiBaseUrl}/api/trading/portfolio`, { headers })
      if (portfolioResponse.ok) {
        const portfolioData = await portfolioResponse.json()
        setPortfolioData(portfolioData)
        setRecentTrades(portfolioData.recent_trades || [])
      }

      // Fetch trading signals
      const signalsResponse = await fetch(`${apiBaseUrl}/api/trading/signals`, { headers })
      if (signalsResponse.ok) {
        const signalsData = await signalsResponse.json()
        setTradingSignals(signalsData.signals || [])
      }

      // Fetch AI engine status
      const engineResponse = await fetch(`${apiBaseUrl}/api/trading/ai-engine/status`, { headers })
      if (engineResponse.ok) {
        const engineData = await engineResponse.json()
        setAiEngineStatus(engineData.engine_status)
      }

      // Generate mock market opportunities for demo
      setMarketOpportunities([
        { symbol: 'DOGE-USD', name: 'Dogecoin', price: 0.08, change: 15.2, confidence: 85, signal: 'BUY' },
        { symbol: 'ADA-USD', name: 'Cardano', price: 0.45, change: 8.7, confidence: 78, signal: 'BUY' },
        { symbol: 'AAPL', name: 'Apple Inc.', price: 175.20, change: 2.1, confidence: 72, signal: 'HOLD' },
        { symbol: 'TSLA', name: 'Tesla Inc.', price: 245.80, change: -1.5, confidence: 68, signal: 'SELL' }
      ])

      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0)
  }

  const formatPercentage = (value) => {
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value?.toFixed(2)}%`
  }

  const getSignalColor = (signal) => {
    switch (signal?.toUpperCase()) {
      case 'BUY': return 'text-green-500'
      case 'SELL': return 'text-red-500'
      case 'HOLD': return 'text-yellow-500'
      default: return 'text-muted-foreground'
    }
  }

  const getSignalIcon = (signal) => {
    switch (signal?.toUpperCase()) {
      case 'BUY': return <ArrowUpRight className="h-4 w-4" />
      case 'SELL': return <ArrowDownRight className="h-4 w-4" />
      case 'HOLD': return <Clock className="h-4 w-4" />
      default: return <Activity className="h-4 w-4" />
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading dashboard...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.first_name}! Here's your trading overview.
          </p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Portfolio Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Portfolio</p>
              <p className="text-2xl font-bold text-foreground">
                {formatCurrency(portfolioData?.portfolio?.total_value)}
              </p>
            </div>
            <div className="bg-blue-500/20 p-3 rounded-lg">
              <DollarSign className="h-6 w-6 text-blue-500" />
            </div>
          </div>
          <div className="mt-4 flex items-center">
            <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-sm text-green-500 font-medium">
              {formatPercentage(portfolioData?.performance?.total_return_percent)}
            </span>
            <span className="text-sm text-muted-foreground ml-2">vs yesterday</span>
          </div>
        </div>

        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Cash Balance</p>
              <p className="text-2xl font-bold text-foreground">
                {formatCurrency(portfolioData?.portfolio?.cash_balance)}
              </p>
            </div>
            <div className="bg-green-500/20 p-3 rounded-lg">
              <DollarSign className="h-6 w-6 text-green-500" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-muted-foreground">Available for trading</span>
          </div>
        </div>

        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Active Positions</p>
              <p className="text-2xl font-bold text-foreground">
                {portfolioData?.positions?.length || 0}
              </p>
            </div>
            <div className="bg-purple-500/20 p-3 rounded-lg">
              <Target className="h-6 w-6 text-purple-500" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-muted-foreground">Open trades</span>
          </div>
        </div>

        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">AI Win Rate</p>
              <p className="text-2xl font-bold text-foreground">78.5%</p>
            </div>
            <div className="bg-orange-500/20 p-3 rounded-lg">
              <Bot className="h-6 w-6 text-orange-500" />
            </div>
          </div>
          <div className="mt-4 flex items-center">
            <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-sm text-green-500 font-medium">+2.1%</span>
            <span className="text-sm text-muted-foreground ml-2">this week</span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Trading Activity */}
        <div className="lg:col-span-2 bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-foreground">Recent Trading Activity</h2>
            <div className="flex items-center text-sm text-muted-foreground">
              <Clock className="h-4 w-4 mr-1" />
              Last updated: {lastUpdate.toLocaleTimeString()}
            </div>
          </div>

          {recentTrades.length > 0 ? (
            <div className="space-y-4">
              {recentTrades.slice(0, 5).map((trade, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-background rounded-lg border border-border">
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-lg ${trade.trade_type === 'BUY' ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                      {trade.trade_type === 'BUY' ? (
                        <ArrowUpRight className="h-4 w-4 text-green-500" />
                      ) : (
                        <ArrowDownRight className="h-4 w-4 text-red-500" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-foreground">{trade.asset_symbol}</p>
                      <p className="text-sm text-muted-foreground">
                        {trade.trade_type} • {trade.quantity} shares
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-foreground">{formatCurrency(trade.price)}</p>
                    <p className={`text-sm ${trade.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {trade.pnl >= 0 ? '+' : ''}{formatCurrency(trade.pnl)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No recent trades</p>
              <p className="text-sm text-muted-foreground">AI is analyzing market conditions</p>
            </div>
          )}
        </div>

        {/* AI Trading Signals */}
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-foreground">AI Signals</h2>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2"></div>
              <span className="text-sm text-green-500">Live</span>
            </div>
          </div>

          <div className="space-y-4">
            {marketOpportunities.map((opportunity, index) => (
              <div key={index} className="p-4 bg-background rounded-lg border border-border">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className={getSignalColor(opportunity.signal)}>
                      {getSignalIcon(opportunity.signal)}
                    </span>
                    <span className="font-medium text-foreground">{opportunity.symbol}</span>
                  </div>
                  <span className={`text-sm font-medium ${getSignalColor(opportunity.signal)}`}>
                    {opportunity.signal}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mb-2">{opportunity.name}</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">
                    {formatCurrency(opportunity.price)}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className={`text-sm ${opportunity.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {formatPercentage(opportunity.change)}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {opportunity.confidence}% confidence
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
            <div className="flex items-center space-x-2 mb-2">
              <Bot className="h-4 w-4 text-blue-500" />
              <span className="text-sm font-medium text-blue-500">AI Engine Status</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Analyzing {marketOpportunities.length} opportunities across crypto and stock markets
            </p>
          </div>
        </div>
      </div>

      {/* Market Opportunities */}
      <div className="bg-card rounded-lg p-6 border border-border">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-foreground">Market Opportunities</h2>
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-4 w-4 text-orange-500" />
            <span className="text-sm text-orange-500">High Potential Detected</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {marketOpportunities.map((opportunity, index) => (
            <div key={index} className="p-4 bg-background rounded-lg border border-border hover:border-primary/50 transition-colors cursor-pointer">
              <div className="flex items-center justify-between mb-3">
                <span className="font-medium text-foreground">{opportunity.symbol}</span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  opportunity.signal === 'BUY' ? 'bg-green-500/20 text-green-500' :
                  opportunity.signal === 'SELL' ? 'bg-red-500/20 text-red-500' :
                  'bg-yellow-500/20 text-yellow-500'
                }`}>
                  {opportunity.signal}
                </span>
              </div>
              <p className="text-sm text-muted-foreground mb-2">{opportunity.name}</p>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Price</span>
                  <span className="text-sm font-medium text-foreground">
                    {formatCurrency(opportunity.price)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Change</span>
                  <span className={`text-sm font-medium ${opportunity.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {formatPercentage(opportunity.change)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Confidence</span>
                  <span className="text-sm font-medium text-foreground">{opportunity.confidence}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

