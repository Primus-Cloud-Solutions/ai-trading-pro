// AI Trading Pro - Login Authentication Fix
// Simplified login fix that properly handles authentication

(function() {
    'use strict';
    
    console.log('🔐 Login Authentication Fix Loading...');
    
    // Wait for page to load and find login elements
    function initializeLoginFix() {
        // Wait for login form to be available
        const checkForLoginForm = setInterval(() => {
            const emailInput = document.querySelector('input[placeholder*="email"], input[type="email"]');
            const passwordInput = document.querySelector('input[placeholder*="password"], input[type="password"]');
            const signInButton = Array.from(document.querySelectorAll('button')).find(btn => 
                btn.textContent.includes('Sign In') || btn.textContent.includes('Login')
            );
            
            if (emailInput && passwordInput && signInButton) {
                clearInterval(checkForLoginForm);
                setupLoginHandler(emailInput, passwordInput, signInButton);
            }
        }, 500);
        
        // Clear interval after 30 seconds to prevent infinite checking
        setTimeout(() => clearInterval(checkForLoginForm), 30000);
    }
    
    function setupLoginHandler(emailInput, passwordInput, signInButton) {
        console.log('✅ Login form found, setting up authentication handler...');
        
        // Remove any existing event listeners
        const newSignInButton = signInButton.cloneNode(true);
        signInButton.parentNode.replaceChild(newSignInButton, signInButton);
        
        newSignInButton.addEventListener('click', async function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const email = emailInput.value.trim();
            const password = passwordInput.value.trim();
            
            if (!email || !password) {
                alert('Please enter both email and password');
                return;
            }
            
            console.log('🔐 Attempting login for:', email);
            
            // Update button state
            const originalText = newSignInButton.textContent;
            newSignInButton.textContent = 'Signing In...';
            newSignInButton.disabled = true;
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email_or_username: email,
                        password: password
                    })
                });
                
                const data = await response.json();
                console.log('📡 Login response:', response.status, data);
                
                if (response.ok && data.message === 'Login successful') {
                    console.log('✅ Login successful!');
                    
                    // Store authentication data
                    if (data.data && data.data.access_token) {
                        localStorage.setItem('access_token', data.data.access_token);
                        localStorage.setItem('user', JSON.stringify(data.data.user));
                    }
                    
                    // Show success message
                    alert('Login successful! Redirecting to dashboard...');
                    
                    // Redirect to dashboard or reload page
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                    
                } else {
                    console.log('❌ Login failed:', data.error || data.message);
                    alert(data.error || data.message || 'Login failed. Please check your credentials.');
                }
            } catch (error) {
                console.error('❌ Login error:', error);
                alert('Network error. Please try again.');
            } finally {
                // Reset button state
                newSignInButton.textContent = originalText;
                newSignInButton.disabled = false;
            }
        });
        
        // Also handle Enter key press
        [emailInput, passwordInput].forEach(input => {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    newSignInButton.click();
                }
            });
        });
        
        console.log('✅ Login authentication handler setup complete!');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeLoginFix);
    } else {
        initializeLoginFix();
    }
    
    console.log('🚀 Login Authentication Fix Loaded!');
})();

