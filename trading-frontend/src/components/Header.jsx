import { useState, useEffect } from 'react'
import { Bell, Moon, Sun, Search, DollarSign, TrendingUp, TrendingDown } from 'lucide-react'

const Header = ({ user, darkMode, setDarkMode, onLogout }) => {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [marketStatus, setMarketStatus] = useState('OPEN')

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    // Determine market status based on current time
    const now = new Date()
    const hour = now.getHours()
    const day = now.getDay()
    
    // Simple market hours check (9:30 AM - 4:00 PM EST, Monday-Friday)
    if (day >= 1 && day <= 5 && hour >= 9 && hour < 16) {
      setMarketStatus('OPEN')
    } else {
      setMarketStatus('CLOSED')
    }
  }, [currentTime])

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: true,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  return (
    <header className="bg-card border-b border-border px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left Section - Market Info */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${marketStatus === 'OPEN' ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm font-medium text-foreground">
              Market {marketStatus}
            </span>
          </div>
          
          <div className="hidden md:flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-1">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span className="text-foreground">S&P 500</span>
              <span className="text-green-500 font-medium">+0.85%</span>
            </div>
            <div className="flex items-center space-x-1">
              <TrendingDown className="h-4 w-4 text-red-500" />
              <span className="text-foreground">NASDAQ</span>
              <span className="text-red-500 font-medium">-0.23%</span>
            </div>
            <div className="flex items-center space-x-1">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span className="text-foreground">BTC</span>
              <span className="text-green-500 font-medium">+2.14%</span>
            </div>
          </div>
        </div>

        {/* Center Section - Search */}
        <div className="hidden lg:flex flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search assets, signals, or trades..."
              className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
        </div>

        {/* Right Section - User Actions */}
        <div className="flex items-center space-x-4">
          {/* Portfolio Value */}
          <div className="hidden md:flex items-center space-x-2 bg-background px-3 py-2 rounded-lg border border-border">
            <DollarSign className="h-4 w-4 text-green-500" />
            <div className="text-right">
              <p className="text-xs text-muted-foreground">Portfolio</p>
              <p className="text-sm font-semibold text-foreground">
                ${user?.portfolio?.total_value?.toLocaleString() || '0.00'}
              </p>
            </div>
          </div>

          {/* Time Display */}
          <div className="hidden md:block text-right">
            <p className="text-xs text-muted-foreground">{formatDate(currentTime)}</p>
            <p className="text-sm font-medium text-foreground">{formatTime(currentTime)}</p>
          </div>

          {/* Notifications */}
          <button className="relative p-2 text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* Dark Mode Toggle */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors"
          >
            {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>

          {/* User Menu */}
          <div className="flex items-center space-x-2">
            <div className="bg-gradient-to-r from-green-500 to-blue-500 rounded-full p-2">
              <span className="text-white font-semibold text-sm">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </span>
            </div>
            <div className="hidden md:block">
              <p className="text-sm font-medium text-foreground">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs text-muted-foreground">
                {user?.subscription?.plan?.name || 'Free Trial'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header

