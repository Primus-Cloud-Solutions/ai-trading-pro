import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'

// Import components
import LoginPage from './components/LoginPage'
import RegisterPage from './components/RegisterPage'
import Dashboard from './components/Dashboard'
import Portfolio from './components/Portfolio'
import Trading from './components/Trading'
import Analytics from './components/Analytics'
import Settings from './components/Settings'
import Sidebar from './components/Sidebar'
import Header from './components/Header'

// API configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? window.location.origin 
  : 'http://localhost:5000'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [darkMode, setDarkMode] = useState(true)

  // Check for existing authentication on app load
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      // Verify token and get user data
      fetchUserProfile(token)
    } else {
      setLoading(false)
    }
  }, [])

  // Apply dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  const fetchUserProfile = async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUser(data.user)
      } else {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    } catch (error) {
      console.error('Error fetching user profile:', error)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = (userData) => {
    setUser(userData.user)
    localStorage.setItem('access_token', userData.access_token)
    localStorage.setItem('refresh_token', userData.refresh_token)
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading AI Trading Pro...</p>
        </div>
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen bg-background">
        {!user ? (
          // Authentication Routes
          <Routes>
            <Route 
              path="/login" 
              element={<LoginPage onLogin={handleLogin} apiBaseUrl={API_BASE_URL} />} 
            />
            <Route 
              path="/register" 
              element={<RegisterPage apiBaseUrl={API_BASE_URL} />} 
            />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        ) : (
          // Authenticated App Layout
          <div className="flex h-screen">
            <Sidebar user={user} onLogout={handleLogout} />
            <div className="flex-1 flex flex-col overflow-hidden">
              <Header 
                user={user} 
                darkMode={darkMode} 
                setDarkMode={setDarkMode}
                onLogout={handleLogout}
              />
              <main className="flex-1 overflow-auto bg-background">
                <Routes>
                  <Route 
                    path="/dashboard" 
                    element={<Dashboard user={user} apiBaseUrl={API_BASE_URL} />} 
                  />
                  <Route 
                    path="/portfolio" 
                    element={<Portfolio user={user} apiBaseUrl={API_BASE_URL} />} 
                  />
                  <Route 
                    path="/trading" 
                    element={<Trading user={user} apiBaseUrl={API_BASE_URL} />} 
                  />
                  <Route 
                    path="/analytics" 
                    element={<Analytics user={user} apiBaseUrl={API_BASE_URL} />} 
                  />
                  <Route 
                    path="/settings" 
                    element={<Settings user={user} apiBaseUrl={API_BASE_URL} />} 
                  />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </main>
            </div>
          </div>
        )}
      </div>
    </Router>
  )
}

export default App

