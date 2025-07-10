"""
Order Management System
Handles trade execution, order tracking, and automated trading
"""

from datetime import datetime, timedelta
from enum import Enum
from database import db
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIALLY_FILLED = "partially_filled"

class Order(db.Model):
    """Order model for trade execution"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    
    # Order details
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # buy/sell
    order_type = Column(String(20), nullable=False)  # market/limit/stop_loss
    quantity = Column(Float, nullable=False)
    price = Column(Float)  # For limit orders
    stop_price = Column(Float)  # For stop orders
    
    # Execution details
    filled_quantity = Column(Float, default=0.0)
    filled_price = Column(Float)
    status = Column(String(20), default='pending')
    
    # AI-related
    ai_signal_id = Column(String(50))  # Reference to AI signal
    confidence = Column(Float)
    strategy = Column(String(50))
    is_automated = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    filled_at = Column(DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'portfolio_id': self.portfolio_id,
            'symbol': self.symbol,
            'side': self.side,
            'order_type': self.order_type,
            'quantity': self.quantity,
            'price': self.price,
            'stop_price': self.stop_price,
            'filled_quantity': self.filled_quantity,
            'filled_price': self.filled_price,
            'status': self.status,
            'ai_signal_id': self.ai_signal_id,
            'confidence': self.confidence,
            'strategy': self.strategy,
            'is_automated': self.is_automated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'filled_at': self.filled_at.isoformat() if self.filled_at else None
        }

class AutoTradingSettings(db.Model):
    """Automated trading settings for users"""
    __tablename__ = 'auto_trading_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Automation settings
    is_enabled = Column(Boolean, default=False)
    max_daily_trades = Column(Integer, default=10)
    max_position_size = Column(Float, default=1000.0)  # USD
    min_confidence = Column(Float, default=0.7)  # 70%
    
    # Risk management
    stop_loss_percentage = Column(Float, default=0.05)  # 5%
    take_profit_percentage = Column(Float, default=0.10)  # 10%
    max_daily_loss = Column(Float, default=500.0)  # USD
    
    # Strategy preferences
    enabled_strategies = Column(Text)  # JSON string of enabled strategies
    enabled_assets = Column(Text)  # JSON string of enabled asset types
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'is_enabled': self.is_enabled,
            'max_daily_trades': self.max_daily_trades,
            'max_position_size': self.max_position_size,
            'min_confidence': self.min_confidence,
            'stop_loss_percentage': self.stop_loss_percentage,
            'take_profit_percentage': self.take_profit_percentage,
            'max_daily_loss': self.max_daily_loss,
            'enabled_strategies': self.enabled_strategies,
            'enabled_assets': self.enabled_assets
        }

class TradeRecommendation(db.Model):
    """AI-generated trade recommendations"""
    __tablename__ = 'trade_recommendations'
    
    id = Column(Integer, primary_key=True)
    
    # Asset details
    symbol = Column(String(20), nullable=False)
    asset_type = Column(String(20), nullable=False)  # stock/crypto/meme_coin
    
    # Recommendation details
    action = Column(String(10), nullable=False)  # buy/sell/hold
    confidence = Column(Float, nullable=False)
    target_price = Column(Float)
    stop_loss = Column(Float)
    expected_return = Column(Float)
    risk_score = Column(Float)
    
    # AI analysis
    strategy = Column(String(50), nullable=False)
    reasoning = Column(Text)
    technical_indicators = Column(Text)  # JSON string
    
    # Status
    is_active = Column(Boolean, default=True)
    is_executed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'asset_type': self.asset_type,
            'action': self.action,
            'confidence': self.confidence,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'expected_return': self.expected_return,
            'risk_score': self.risk_score,
            'strategy': self.strategy,
            'reasoning': self.reasoning,
            'technical_indicators': self.technical_indicators,
            'is_active': self.is_active,
            'is_executed': self.is_executed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

