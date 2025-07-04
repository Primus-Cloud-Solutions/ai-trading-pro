import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Eye, EyeOff, TrendingUp, Bot, Shield, Zap } from 'lucide-react'

const LoginPage = ({ onLogin, apiBaseUrl }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${apiBaseUrl}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email_or_username: formData.email,
          password: formData.password
        })
      })

      const data = await response.json()

      if (response.ok) {
        // Backend returns { user, access_token, refresh_token, expires_in }
        onLogin(data.data)
      } else {
        setError(data.error || 'Login failed')
      }
    } catch (error) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-center px-12 text-white">
        <div className="max-w-md">
          <div className="flex items-center mb-8">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-xl mr-4">
              <Bot className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">AI Trading Pro</h1>
              <p className="text-purple-200">Professional Trading Platform</p>
            </div>
          </div>
          
          <h2 className="text-4xl font-bold mb-6 leading-tight">
            Maximize Your Trading Profits with AI
          </h2>
          
          <p className="text-xl text-purple-100 mb-8">
            Join thousands of traders using our advanced AI algorithms to generate consistent profits in the markets.
          </p>
          
          <div className="space-y-4">
            <div className="flex items-center">
              <TrendingUp className="h-6 w-6 text-green-400 mr-3" />
              <span className="text-lg">Average 78.5% Win Rate</span>
            </div>
            <div className="flex items-center">
              <Shield className="h-6 w-6 text-blue-400 mr-3" />
              <span className="text-lg">Advanced Risk Management</span>
            </div>
            <div className="flex items-center">
              <Zap className="h-6 w-6 text-yellow-400 mr-3" />
              <span className="text-lg">Automated Trading 24/7</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold text-white mb-2">Welcome Back</h3>
              <p className="text-purple-200">Sign in to your trading account</p>
            </div>

            {error && (
              <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3 mb-6">
                <p className="text-red-200 text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-purple-200 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Enter your email"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-purple-200 mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent pr-12"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-purple-300 hover:text-white"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-transparent transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Signing In...
                  </div>
                ) : (
                  'Sign In'
                )}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-purple-200">
                Don't have an account?{' '}
                <Link 
                  to="/register" 
                  className="text-blue-400 hover:text-blue-300 font-semibold transition-colors"
                >
                  Sign up for free
                </Link>
              </p>
            </div>

            <div className="mt-6 pt-6 border-t border-white/20">
              <p className="text-center text-sm text-purple-300">
                Demo Account: admin@aitradingpro.com / admin123
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage

