import { useState, useEffect } from 'react'
import { TrendingUp, Bot, Target, Activity } from 'lucide-react'

const Trading = ({ user, apiBaseUrl }) => {
  const [signals, setSignals] = useState([])
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTradingData()
  }, [])

  const fetchTradingData = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }

      const [signalsResponse, assetsResponse] = await Promise.all([
        fetch(`${apiBaseUrl}/api/trading/signals`, { headers }),
        fetch(`${apiBaseUrl}/api/trading/assets`, { headers })
      ])

      if (signalsResponse.ok) {
        const signalsData = await signalsResponse.json()
        setSignals(signalsData.signals || [])
      }

      if (assetsResponse.ok) {
        const assetsData = await assetsResponse.json()
        setAssets(assetsData.assets || [])
      }
    } catch (error) {
      console.error('Error fetching trading data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/4"></div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[1, 2].map(i => (
              <div key={i} className="h-64 bg-muted rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-foreground">AI Trading</h1>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-green-500">AI Engine Active</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center space-x-2 mb-4">
            <Bot className="h-5 w-5 text-blue-500" />
            <h2 className="text-xl font-semibold text-foreground">AI Trading Signals</h2>
          </div>
          
          {signals.length > 0 ? (
            <div className="space-y-4">
              {signals.slice(0, 5).map((signal, index) => (
                <div key={index} className="p-4 bg-background rounded-lg border border-border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-foreground">{signal.asset_symbol}</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      signal.signal_type === 'BUY' ? 'bg-green-500/20 text-green-500' :
                      signal.signal_type === 'SELL' ? 'bg-red-500/20 text-red-500' :
                      'bg-yellow-500/20 text-yellow-500'
                    }`}>
                      {signal.signal_type}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      Confidence: {signal.confidence}%
                    </span>
                    <span className="text-sm font-medium text-foreground">
                      ${signal.target_price?.toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No active signals</p>
              <p className="text-sm text-muted-foreground">AI is analyzing market conditions</p>
            </div>
          )}
        </div>

        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center space-x-2 mb-4">
            <Target className="h-5 w-5 text-purple-500" />
            <h2 className="text-xl font-semibold text-foreground">Available Assets</h2>
          </div>
          
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {assets.slice(0, 10).map((asset, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-background rounded-lg border border-border">
                <div>
                  <span className="font-medium text-foreground">{asset.symbol}</span>
                  <p className="text-sm text-muted-foreground">{asset.name}</p>
                </div>
                <div className="text-right">
                  <span className="text-sm font-medium text-foreground">{asset.asset_type}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-card rounded-lg p-6 border border-border">
        <h2 className="text-xl font-semibold text-foreground mb-4">Automated Trading Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="bg-green-500/20 p-4 rounded-lg mb-2">
              <TrendingUp className="h-8 w-8 text-green-500 mx-auto" />
            </div>
            <p className="font-medium text-foreground">Auto Trading</p>
            <p className="text-sm text-green-500">ENABLED</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-500/20 p-4 rounded-lg mb-2">
              <Bot className="h-8 w-8 text-blue-500 mx-auto" />
            </div>
            <p className="font-medium text-foreground">AI Models</p>
            <p className="text-sm text-blue-500">5 ACTIVE</p>
          </div>
          <div className="text-center">
            <div className="bg-purple-500/20 p-4 rounded-lg mb-2">
              <Activity className="h-8 w-8 text-purple-500 mx-auto" />
            </div>
            <p className="font-medium text-foreground">Win Rate</p>
            <p className="text-sm text-purple-500">78.5%</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Trading

