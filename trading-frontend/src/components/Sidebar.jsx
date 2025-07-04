import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Briefcase, 
  TrendingUp, 
  BarChart3, 
  Settings, 
  LogOut,
  Bot,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'

const Sidebar = ({ user, onLogout }) => {
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Portfolio', href: '/portfolio', icon: Briefcase },
    { name: 'Trading', href: '/trading', icon: TrendingUp },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const isActive = (href) => location.pathname === href

  return (
    <div className={`bg-card border-r border-border transition-all duration-300 ${collapsed ? 'w-16' : 'w-64'} flex flex-col`}>
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <div className="flex items-center">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-2 rounded-lg mr-3">
                <Bot className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-foreground">AI Trading Pro</h1>
                <p className="text-xs text-muted-foreground">Professional Platform</p>
              </div>
            </div>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1 rounded-lg hover:bg-accent transition-colors"
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronLeft className="h-4 w-4 text-muted-foreground" />
            )}
          </button>
        </div>
      </div>

      {/* User Info */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center">
          <div className="bg-gradient-to-r from-green-500 to-blue-500 rounded-full p-2 mr-3">
            <span className="text-white font-semibold text-sm">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </span>
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs text-muted-foreground truncate">
                {user?.subscription?.plan?.name || 'Free Trial'}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon
            return (
              <li key={item.name}>
                <Link
                  to={item.href}
                  className={`flex items-center px-3 py-2 rounded-lg transition-colors ${
                    isActive(item.href)
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                  }`}
                >
                  <Icon className="h-5 w-5 mr-3" />
                  {!collapsed && <span className="font-medium">{item.name}</span>}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* AI Engine Status */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center">
          <div className="flex items-center mr-3">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse ml-1"></div>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse ml-1"></div>
          </div>
          {!collapsed && (
            <div>
              <p className="text-xs font-medium text-foreground">AI Engine</p>
              <p className="text-xs text-green-500">Active & Learning</p>
            </div>
          )}
        </div>
      </div>

      {/* Logout */}
      <div className="p-4 border-t border-border">
        <button
          onClick={onLogout}
          className="flex items-center w-full px-3 py-2 text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors"
        >
          <LogOut className="h-5 w-5 mr-3" />
          {!collapsed && <span className="font-medium">Logout</span>}
        </button>
      </div>
    </div>
  )
}

export default Sidebar

