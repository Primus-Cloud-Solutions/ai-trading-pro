/**
 * Authentication Check and User Management
 * Handles login state, token management, and protected routes
 */

class AuthManager {
    constructor() {
        this.user = null;
        this.accessToken = null;
        this.refreshToken = null;
        this.init();
    }

    init() {
        // Load user data from localStorage
        this.loadUserData();
        
        // Check if current page requires authentication
        this.checkAuthRequired();
        
        // Set up token refresh interval
        this.setupTokenRefresh();
    }

    loadUserData() {
        try {
            const userData = localStorage.getItem('user');
            const accessToken = localStorage.getItem('access_token');
            const refreshToken = localStorage.getItem('refresh_token');
            
            if (userData) {
                this.user = JSON.parse(userData);
            }
            
            if (accessToken) {
                this.accessToken = accessToken;
            }
            
            if (refreshToken) {
                this.refreshToken = refreshToken;
            }
        } catch (error) {
            console.error('Error loading user data:', error);
            this.clearUserData();
        }
    }

    saveUserData(userData) {
        try {
            this.user = userData.user;
            this.accessToken = userData.access_token;
            this.refreshToken = userData.refresh_token;
            
            localStorage.setItem('user', JSON.stringify(userData.user));
            localStorage.setItem('access_token', userData.access_token);
            localStorage.setItem('refresh_token', userData.refresh_token);
        } catch (error) {
            console.error('Error saving user data:', error);
        }
    }

    clearUserData() {
        this.user = null;
        this.accessToken = null;
        this.refreshToken = null;
        
        localStorage.removeItem('user');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    isAuthenticated() {
        return this.user && this.accessToken;
    }

    checkAuthRequired() {
        const protectedPages = ['/dashboard', '/trading-interface.html'];
        const currentPath = window.location.pathname;
        
        const isProtectedPage = protectedPages.some(page => 
            currentPath.includes(page) || currentPath.endsWith(page)
        );
        
        if (isProtectedPage && !this.isAuthenticated()) {
            // Redirect to login page
            window.location.href = '/login?redirect=' + encodeURIComponent(currentPath);
            return false;
        }
        
        return true;
    }

    async refreshAccessToken() {
        if (!this.refreshToken) {
            this.logout();
            return false;
        }

        try {
            const response = await fetch('/api/auth/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.refreshToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.accessToken = data.access_token;
                localStorage.setItem('access_token', data.access_token);
                return true;
            } else {
                this.logout();
                return false;
            }
        } catch (error) {
            console.error('Error refreshing token:', error);
            this.logout();
            return false;
        }
    }

    setupTokenRefresh() {
        // Refresh token every 23 hours (tokens expire in 24 hours)
        setInterval(() => {
            if (this.isAuthenticated()) {
                this.refreshAccessToken();
            }
        }, 23 * 60 * 60 * 1000);
    }

    async makeAuthenticatedRequest(url, options = {}) {
        if (!this.isAuthenticated()) {
            throw new Error('User not authenticated');
        }

        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.accessToken}`,
            ...options.headers
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            // If token expired, try to refresh
            if (response.status === 401) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Retry the request with new token
                    headers['Authorization'] = `Bearer ${this.accessToken}`;
                    return fetch(url, {
                        ...options,
                        headers
                    });
                } else {
                    throw new Error('Authentication failed');
                }
            }

            return response;
        } catch (error) {
            console.error('Authenticated request failed:', error);
            throw error;
        }
    }

    logout() {
        this.clearUserData();
        window.location.href = '/login';
    }

    updateUserProfile() {
        // Update user profile display if elements exist
        const userNameElement = document.getElementById('userName');
        const userEmailElement = document.getElementById('userEmail');
        const userAvatarElement = document.getElementById('userAvatar');
        
        if (this.user) {
            if (userNameElement) {
                userNameElement.textContent = `${this.user.first_name} ${this.user.last_name}`;
            }
            if (userEmailElement) {
                userEmailElement.textContent = this.user.email;
            }
            if (userAvatarElement) {
                userAvatarElement.textContent = this.user.first_name.charAt(0).toUpperCase();
            }
        }
    }
}

// Create global auth manager instance
const authManager = new AuthManager();

// Update user profile when page loads
document.addEventListener('DOMContentLoaded', function() {
    authManager.updateUserProfile();
    
    // Add logout functionality to logout buttons
    const logoutButtons = document.querySelectorAll('[data-logout]');
    logoutButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            authManager.logout();
        });
    });
});

// Export for use in other scripts
window.authManager = authManager;

