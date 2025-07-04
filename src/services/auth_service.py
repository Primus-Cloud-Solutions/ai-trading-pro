"""
Authentication Service for AI Trading SaaS Platform
Complete user authentication, registration, and session management
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
import secrets
import string

from database import db
from models.user import User, Subscription, SubscriptionPlan, TradingSettings
from models.trading import Portfolio

logger = logging.getLogger(__name__)

class AuthService:
    """Complete authentication service"""
    
    @staticmethod
    def register_user(email: str, username: str, password: str, 
                     first_name: str, last_name: str, **kwargs) -> Tuple[bool, str, Optional[User]]:
        """Register a new user"""
        try:
            # Validate input
            if not email or not username or not password:
                return False, "Email, username, and password are required", None
            
            if len(password) < 8:
                return False, "Password must be at least 8 characters long", None
            
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                return False, "Email already registered", None
            
            if User.query.filter_by(username=username).first():
                return False, "Username already taken", None
            
            # Create new user
            user = User(
                email=email.lower().strip(),
                username=username.strip(),
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                phone=kwargs.get('phone'),
                country=kwargs.get('country'),
                timezone=kwargs.get('timezone', 'UTC')
            )
            user.set_password(password)
            
            # Generate verification token
            verification_token = user.generate_verification_token()
            
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Create default portfolio
            portfolio = Portfolio(
                user_id=user.id,
                cash_balance=0.0,  # User will need to fund their account
                total_value=0.0
            )
            db.session.add(portfolio)
            
            # Create default trading settings
            trading_settings = TradingSettings(
                user_id=user.id,
                auto_trading_enabled=True,
                max_position_size=0.10,  # 10% max position size
                daily_loss_limit=0.05,   # 5% daily loss limit
                min_confidence_threshold=0.75  # 75% minimum confidence
            )
            db.session.add(trading_settings)
            
            db.session.commit()
            
            logger.info(f"✅ User registered successfully: {email}")
            
            # TODO: Send verification email
            # self._send_verification_email(user, verification_token)
            
            return True, "User registered successfully. Please check your email to verify your account.", user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Error registering user {email}: {e}")
            return False, f"Registration failed: {str(e)}", None
    
    @staticmethod
    def login_user(email_or_username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Authenticate user and return tokens"""
        try:
            # Find user by email or username
            user = User.query.filter(
                (User.email == email_or_username.lower()) | 
                (User.username == email_or_username)
            ).first()
            
            if not user:
                return False, "Invalid credentials", None
            
            if not user.check_password(password):
                return False, "Invalid credentials", None
            
            if not user.is_active:
                return False, "Account is deactivated", None
            
            # Update last login
            user.update_last_login()
            db.session.commit()
            
            # Create JWT tokens
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(hours=24)
            )
            refresh_token = create_refresh_token(
                identity=user.id,
                expires_delta=timedelta(days=30)
            )
            
            # Prepare user data
            user_data = {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': 24 * 3600  # 24 hours in seconds
            }
            
            logger.info(f"✅ User logged in successfully: {user.email}")
            
            return True, "Login successful", user_data
            
        except Exception as e:
            logger.error(f"❌ Error logging in user {email_or_username}: {e}")
            return False, f"Login failed: {str(e)}", None
    
    @staticmethod
    def refresh_token(current_user_id: int) -> Tuple[bool, str, Optional[str]]:
        """Refresh access token"""
        try:
            user = User.query.get(current_user_id)
            if not user or not user.is_active:
                return False, "Invalid user", None
            
            # Create new access token
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(hours=24)
            )
            
            return True, "Token refreshed successfully", access_token
            
        except Exception as e:
            logger.error(f"❌ Error refreshing token for user {current_user_id}: {e}")
            return False, f"Token refresh failed: {str(e)}", None
    
    @staticmethod
    def verify_email(token: str) -> Tuple[bool, str]:
        """Verify user email with token"""
        try:
            user = User.query.filter_by(verification_token=token).first()
            
            if not user:
                return False, "Invalid verification token"
            
            if user.verify_email(token):
                # Create free trial subscription
                free_plan = SubscriptionPlan.query.filter_by(name='Free Trial').first()
                if free_plan:
                    subscription = Subscription(
                        user_id=user.id,
                        plan_id=free_plan.id,
                        status='active',
                        billing_cycle='monthly',
                        expires_at=datetime.utcnow() + timedelta(days=7)  # 7-day free trial
                    )
                    db.session.add(subscription)
                
                db.session.commit()
                
                logger.info(f"✅ Email verified for user: {user.email}")
                return True, "Email verified successfully"
            else:
                return False, "Invalid or expired verification token"
                
        except Exception as e:
            logger.error(f"❌ Error verifying email with token {token}: {e}")
            return False, f"Email verification failed: {str(e)}"
    
    @staticmethod
    def request_password_reset(email: str) -> Tuple[bool, str]:
        """Request password reset"""
        try:
            user = User.query.filter_by(email=email.lower()).first()
            
            if not user:
                # Don't reveal if email exists
                return True, "If the email exists, a reset link has been sent"
            
            # Generate reset token
            reset_token = user.generate_reset_token()
            db.session.commit()
            
            # TODO: Send reset email
            # self._send_password_reset_email(user, reset_token)
            
            logger.info(f"✅ Password reset requested for: {email}")
            return True, "Password reset link has been sent to your email"
            
        except Exception as e:
            logger.error(f"❌ Error requesting password reset for {email}: {e}")
            return False, f"Password reset request failed: {str(e)}"
    
    @staticmethod
    def reset_password(token: str, new_password: str) -> Tuple[bool, str]:
        """Reset password with token"""
        try:
            if len(new_password) < 8:
                return False, "Password must be at least 8 characters long"
            
            user = User.query.filter_by(reset_token=token).first()
            
            if not user:
                return False, "Invalid reset token"
            
            if user.reset_password(token, new_password):
                db.session.commit()
                logger.info(f"✅ Password reset successfully for: {user.email}")
                return True, "Password reset successfully"
            else:
                return False, "Invalid or expired reset token"
                
        except Exception as e:
            logger.error(f"❌ Error resetting password with token {token}: {e}")
            return False, f"Password reset failed: {str(e)}"
    
    @staticmethod
    def update_user_profile(user_id: int, **kwargs) -> Tuple[bool, str, Optional[User]]:
        """Update user profile"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found", None
            
            # Update allowed fields
            allowed_fields = ['first_name', 'last_name', 'phone', 'country', 'timezone']
            
            for field in allowed_fields:
                if field in kwargs:
                    setattr(user, field, kwargs[field])
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"✅ Profile updated for user: {user.email}")
            return True, "Profile updated successfully", user
            
        except Exception as e:
            logger.error(f"❌ Error updating profile for user {user_id}: {e}")
            return False, f"Profile update failed: {str(e)}", None
    
    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            if not user.check_password(current_password):
                return False, "Current password is incorrect"
            
            if len(new_password) < 8:
                return False, "New password must be at least 8 characters long"
            
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"✅ Password changed for user: {user.email}")
            return True, "Password changed successfully"
            
        except Exception as e:
            logger.error(f"❌ Error changing password for user {user_id}: {e}")
            return False, f"Password change failed: {str(e)}"
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return User.query.get(user_id)
        except Exception as e:
            logger.error(f"❌ Error getting user {user_id}: {e}")
            return None
    
    @staticmethod
    def deactivate_user(user_id: int) -> Tuple[bool, str]:
        """Deactivate user account"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            
            # Cancel subscription
            if user.subscription:
                user.subscription.cancel_subscription()
            
            db.session.commit()
            
            logger.info(f"✅ User deactivated: {user.email}")
            return True, "Account deactivated successfully"
            
        except Exception as e:
            logger.error(f"❌ Error deactivating user {user_id}: {e}")
            return False, f"Account deactivation failed: {str(e)}"
    
    @staticmethod
    def update_trading_settings(user_id: int, **kwargs) -> Tuple[bool, str, Optional[TradingSettings]]:
        """Update user trading settings"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found", None
            
            settings = user.trading_settings
            if not settings:
                # Create default settings
                settings = TradingSettings(user_id=user_id)
                db.session.add(settings)
            
            # Update allowed fields
            allowed_fields = [
                'max_position_size', 'daily_loss_limit', 'min_confidence_threshold',
                'auto_trading_enabled', 'stop_loss_enabled', 'take_profit_ratio',
                'max_open_positions', 'trade_stocks', 'trade_crypto', 'trade_forex',
                'trade_commodities', 'email_notifications', 'trade_notifications',
                'profit_notifications', 'loss_notifications'
            ]
            
            for field in allowed_fields:
                if field in kwargs:
                    setattr(settings, field, kwargs[field])
            
            settings.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"✅ Trading settings updated for user: {user.email}")
            return True, "Trading settings updated successfully", settings
            
        except Exception as e:
            logger.error(f"❌ Error updating trading settings for user {user_id}: {e}")
            return False, f"Trading settings update failed: {str(e)}", None
    
    @staticmethod
    def _generate_secure_token(length: int = 32) -> str:
        """Generate secure random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def _send_verification_email(user: User, token: str):
        """Send email verification (placeholder)"""
        # TODO: Implement email sending
        verification_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={token}"
        logger.info(f"📧 Verification email would be sent to {user.email}: {verification_url}")
    
    @staticmethod
    def _send_password_reset_email(user: User, token: str):
        """Send password reset email (placeholder)"""
        # TODO: Implement email sending
        reset_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}"
        logger.info(f"📧 Password reset email would be sent to {user.email}: {reset_url}")

# Global instance
auth_service = AuthService()

