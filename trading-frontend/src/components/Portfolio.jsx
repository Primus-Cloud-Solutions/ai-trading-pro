import { useState, useEffect } from 'react'
import { DollarSign, Plus, Minus, TrendingUp, TrendingDown } from 'lucide-react'

const Portfolio = ({ user, apiBaseUrl }) => {
  const [portfolioData, setPortfolioData] = useState(null)
  const [fundAmount, setFundAmount] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPortfolioData()
  }, [])

  const fetchPortfolioData = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${apiBaseUrl}/api/trading/portfolio`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setPortfolioData(data)
      }
    } catch (error) {
      console.error('Error fetching portfolio:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFundAccount = async () => {
    if (!fundAmount || parseFloat(fundAmount) <= 0) return

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${apiBaseUrl}/api/trading/portfolio/fund`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ amount: parseFloat(fundAmount) })
      })

      if (response.ok) {
        setFundAmount('')
        fetchPortfolioData()
      }
    } catch (error) {
      console.error('Error funding account:', error)
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-muted rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-foreground">Portfolio</h1>
        <div className="flex items-center space-x-4">
          <input
            type="number"
            value={fundAmount}
            onChange={(e) => setFundAmount(e.target.value)}
            placeholder="Amount to fund"
            className="px-3 py-2 border border-border rounded-lg bg-background text-foreground"
          />
          <button
            onClick={handleFundAccount}
            className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
          >
            <Plus className="h-4 w-4" />
            <span>Fund Account</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Value</p>
              <p className="text-2xl font-bold text-foreground">
                ${portfolioData?.portfolio?.total_value?.toLocaleString() || '0.00'}
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Cash Balance</p>
              <p className="text-2xl font-bold text-foreground">
                ${portfolioData?.portfolio?.cash_balance?.toLocaleString() || '0.00'}
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Return</p>
              <p className="text-2xl font-bold text-foreground">
                {portfolioData?.performance?.total_return_percent?.toFixed(2) || '0.00'}%
              </p>
            </div>
            {(portfolioData?.performance?.total_return_percent || 0) >= 0 ? (
              <TrendingUp className="h-8 w-8 text-green-500" />
            ) : (
              <TrendingDown className="h-8 w-8 text-red-500" />
            )}
          </div>
        </div>
      </div>

      <div className="bg-card rounded-lg p-6 border border-border">
        <h2 className="text-xl font-semibold text-foreground mb-4">Active Positions</h2>
        {portfolioData?.positions?.length > 0 ? (
          <div className="space-y-4">
            {portfolioData.positions.map((position, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-background rounded-lg">
                <div>
                  <p className="font-medium text-foreground">{position.asset_symbol}</p>
                  <p className="text-sm text-muted-foreground">{position.quantity} shares</p>
                </div>
                <div className="text-right">
                  <p className="font-medium text-foreground">${position.current_value?.toFixed(2)}</p>
                  <p className={`text-sm ${position.unrealized_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {position.unrealized_pnl >= 0 ? '+' : ''}${position.unrealized_pnl?.toFixed(2)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground text-center py-8">No active positions</p>
        )}
      </div>
    </div>
  )
}

export default Portfolio

