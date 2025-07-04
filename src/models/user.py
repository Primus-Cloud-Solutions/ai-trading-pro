"""
User Management Models for AI Trading SaaS Platform
Complete user authentication, subscription, and account management
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
from database import db

class User(db.Model):
    """User model with complete authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    country = db.Column(db.String(50))
    timezone = db.Column(db.String(50), default='UTC')
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Email verification
    verification_token = db.Column(db.String(100))
    verification_expires = db.Column(db.DateTime)
    
    # Password reset
    reset_token = db.Column(db.String(100))
    reset_expires = db.Column(db.DateTime)
    
    # Payment integration
    stripe_customer_id = db.Column(db.String(100))
    
    # Relationships
    subscription = db.relationship('Subscription', backref='user', uselist=False, cascade='all, delete-orphan')
    portfolio = db.relationship('Portfolio', backref='user', uselist=False, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', cascade='all, delete-orphan')
    trading_settings = db.relationship('TradingSettings', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        """Generate email verification token"""
        self.verification_token = self._generate_token()
        self.verification_expires = datetime.utcnow() + timedelta(hours=24)
        return self.verification_token
    
    def generate_reset_token(self):
        """Generate password reset token"""
        self.reset_token = self._generate_token()
        self.reset_expires = datetime.utcnow() + timedelta(hours=2)
        return self.reset_token
    
    def _generate_token(self):
        """Generate secure random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def verify_email(self, token):
        """Verify email with token"""
        if (self.verification_token == token and 
            self.verification_expires and 
            datetime.utcnow() < self.verification_expires):
            self.is_verified = True
            self.verification_token = None
            self.verification_expires = None
            return True
        return False
    
    def reset_password(self, token, new_password):
        """Reset password with token"""
        if (self.reset_token == token and 
            self.reset_expires and 
            datetime.utcnow() < self.reset_expires):
            self.set_password(new_password)
            self.reset_token = None
            self.reset_expires = None
            return True
        return False
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
    
    def get_full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    def has_active_subscription(self):
        """Check if user has active subscription"""
        return (self.subscription and 
                self.subscription.is_active and 
                self.subscription.expires_at > datetime.utcnow())
    
    def can_trade(self):
        """Check if user can trade"""
        return (self.is_active and 
                self.is_verified and 
                self.has_active_subscription() and
                self.portfolio and 
                self.portfolio.cash_balance > 0)
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'phone': self.phone,
            'country': self.country,
            'timezone': self.timezone,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'has_active_subscription': self.has_active_subscription(),
            'can_trade': self.can_trade()
        }
        
        if include_sensitive:
            data.update({
                'verification_token': self.verification_token,
                'reset_token': self.reset_token
            })
        
        return data

class SubscriptionPlan(db.Model):
    """Subscription plans for the trading platform"""
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    billing_cycle = db.Column(db.String(10), default='monthly')  # monthly, yearly
    
    # Trading limits
    max_portfolio_value = db.Column(db.Float, default=100000)  # Maximum portfolio value
    max_trades_per_day = db.Column(db.Integer, default=10)
    max_open_positions = db.Column(db.Integer, default=5)
    
    # Features
    features = db.Column(db.JSON)  # List of features
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='plan', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'billing_cycle': self.billing_cycle,
            'max_portfolio_value': self.max_portfolio_value,
            'max_trades_per_day': self.max_trades_per_day,
            'max_open_positions': self.max_open_positions,
            'features': self.features or [],
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Subscription(db.Model):
    """User subscriptions"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    
    # Subscription details
    status = db.Column(db.String(20), default='active')  # active, cancelled, expired, suspended
    billing_cycle = db.Column(db.String(10), default='monthly')  # monthly, yearly
    
    # Dates
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    cancelled_at = db.Column(db.DateTime)
    
    # Payment
    stripe_subscription_id = db.Column(db.String(100))
    stripe_customer_id = db.Column(db.String(100))
    last_payment_date = db.Column(db.DateTime)
    next_payment_date = db.Column(db.DateTime)
    
    # Usage tracking
    trades_this_month = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_active(self):
        """Check if subscription is active"""
        return (self.status == 'active' and 
                self.expires_at > datetime.utcnow())
    
    @property
    def days_remaining(self):
        """Get days remaining in subscription"""
        if self.expires_at > datetime.utcnow():
            return (self.expires_at - datetime.utcnow()).days
        return 0
    
    def can_trade_today(self):
        """Check if user can trade today based on plan limits"""
        if not self.is_active:
            return False
        
        # Reset monthly counter if needed
        now = datetime.utcnow()
        if (now - self.last_reset_date).days >= 30:
            self.trades_this_month = 0
            self.last_reset_date = now
        
        return self.trades_this_month < self.plan.max_trades_per_day
    
    def get_trades_today(self):
        """Get number of trades today"""
        from models.trading import Trade
        today = datetime.utcnow().date()
        return Trade.query.filter(
            Trade.portfolio_id == self.user.portfolio.id,
            Trade.executed_at >= today
        ).count() if self.user.portfolio else 0
    
    def can_fund_account(self):
        """Check if user can fund their account"""
        return self.is_active
    
    def increment_trade_count(self):
        """Increment trade count"""
        self.trades_this_month += 1
    
    def extend_subscription(self, months=1):
        """Extend subscription"""
        if self.expires_at > datetime.utcnow():
            self.expires_at += timedelta(days=30 * months)
        else:
            self.expires_at = datetime.utcnow() + timedelta(days=30 * months)
    
    def cancel_subscription(self):
        """Cancel subscription"""
        self.status = 'cancelled'
        self.cancelled_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan': self.plan.to_dict() if self.plan else None,
            'status': self.status,
            'billing_cycle': self.billing_cycle,
            'is_active': self.is_active,
            'started_at': self.started_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'days_remaining': self.days_remaining,
            'trades_this_month': self.trades_this_month,
            'max_trades_per_day': self.plan.max_trades_per_day if self.plan else 0,
            'can_trade_today': self.can_trade_today(),
            'last_payment_date': self.last_payment_date.isoformat() if self.last_payment_date else None,
            'next_payment_date': self.next_payment_date.isoformat() if self.next_payment_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Transaction(db.Model):
    """Financial transactions (deposits, withdrawals, fees)"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Transaction details
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal, fee, profit, loss
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, cancelled
    
    # Payment details
    payment_method = db.Column(db.String(50))  # stripe, bank_transfer, crypto
    payment_reference = db.Column(db.String(100))
    stripe_payment_intent_id = db.Column(db.String(100))
    
    # Metadata
    description = db.Column(db.String(255))
    transaction_metadata = db.Column(db.JSON)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def complete_transaction(self):
        """Mark transaction as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
    
    def fail_transaction(self, reason=None):
        """Mark transaction as failed"""
        self.status = 'failed'
        if reason:
            self.description = f"{self.description} - Failed: {reason}"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'description': self.description,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class TradingSettings(db.Model):
    """User trading preferences and risk settings"""
    __tablename__ = 'trading_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Risk management
    max_position_size = db.Column(db.Float, default=0.10)  # 10% of portfolio
    daily_loss_limit = db.Column(db.Float, default=0.05)   # 5% daily loss limit
    min_confidence_threshold = db.Column(db.Float, default=0.75)  # 75% minimum confidence
    
    # Trading preferences
    auto_trading_enabled = db.Column(db.Boolean, default=True)
    stop_loss_enabled = db.Column(db.Boolean, default=True)
    take_profit_ratio = db.Column(db.Float, default=2.0)  # 2:1 profit to loss ratio
    max_open_positions = db.Column(db.Integer, default=10)
    
    # Asset preferences
    trade_stocks = db.Column(db.Boolean, default=True)
    trade_crypto = db.Column(db.Boolean, default=True)
    trade_forex = db.Column(db.Boolean, default=False)
    trade_commodities = db.Column(db.Boolean, default=False)
    
    # Notification preferences
    email_notifications = db.Column(db.Boolean, default=True)
    trade_notifications = db.Column(db.Boolean, default=True)
    profit_notifications = db.Column(db.Boolean, default=True)
    loss_notifications = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'max_position_size': self.max_position_size,
            'daily_loss_limit': self.daily_loss_limit,
            'min_confidence_threshold': self.min_confidence_threshold,
            'auto_trading_enabled': self.auto_trading_enabled,
            'stop_loss_enabled': self.stop_loss_enabled,
            'take_profit_ratio': self.take_profit_ratio,
            'max_open_positions': self.max_open_positions,
            'trade_stocks': self.trade_stocks,
            'trade_crypto': self.trade_crypto,
            'trade_forex': self.trade_forex,
            'trade_commodities': self.trade_commodities,
            'email_notifications': self.email_notifications,
            'trade_notifications': self.trade_notifications,
            'profit_notifications': self.profit_notifications,
            'loss_notifications': self.loss_notifications,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

