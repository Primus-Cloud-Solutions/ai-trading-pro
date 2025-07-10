"""
Trading Models for AI Trading SaaS Platform
Complete portfolio management, trading execution, and market data models
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from database import db
import json

class Asset(db.Model):
    """Financial assets (stocks, crypto, etc.)"""
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, unique=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column(db.String(20), nullable=False)  # stock, crypto, forex, commodity
    exchange = db.Column(db.String(50))
    sector = db.Column(db.String(50))
    
    # Current market data
    current_price = db.Column(db.Float)
    previous_close = db.Column(db.Float)
    day_change = db.Column(db.Float)
    day_change_percent = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    market_cap = db.Column(db.BigInteger)
    
    # Trading status
    is_tradeable = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadata
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_price_update = db.Column(db.DateTime)
    
    # Relationships
    positions = db.relationship('Position', backref='asset', cascade='all, delete-orphan')
    trades = db.relationship('Trade', backref='asset', cascade='all, delete-orphan')
    signals = db.relationship('TradingSignal', backref='asset', cascade='all, delete-orphan')
    market_data = db.relationship('MarketData', backref='asset', cascade='all, delete-orphan')
    
    def update_price(self, price, volume=None):
        """Update current price and calculate changes"""
        if self.current_price:
            self.previous_close = self.current_price
            self.day_change = price - self.current_price
            self.day_change_percent = (self.day_change / self.current_price) * 100
        
        self.current_price = price
        if volume:
            self.volume = volume
        self.last_price_update = datetime.utcnow()
    
    def get_price_trend(self, days=7):
        """Get price trend over specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_data = MarketData.query.filter(
            MarketData.asset_id == self.id,
            MarketData.timestamp >= cutoff_date
        ).order_by(MarketData.timestamp.asc()).all()
        
        if len(recent_data) < 2:
            return 'neutral'
        
        start_price = recent_data[0].close_price
        end_price = recent_data[-1].close_price
        change_percent = ((end_price - start_price) / start_price) * 100
        
        if change_percent > 5:
            return 'bullish'
        elif change_percent < -5:
            return 'bearish'
        else:
            return 'neutral'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'asset_type': self.asset_type,
            'exchange': self.exchange,
            'sector': self.sector,
            'current_price': self.current_price,
            'previous_close': self.previous_close,
            'day_change': self.day_change,
            'day_change_percent': self.day_change_percent,
            'volume': self.volume,
            'market_cap': self.market_cap,
            'is_tradeable': self.is_tradeable,
            'is_active': self.is_active,
            'description': self.description,
            'website': self.website,
            'price_trend': self.get_price_trend(),
            'last_price_update': self.last_price_update.isoformat() if self.last_price_update else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Portfolio(db.Model):
    """User portfolios"""
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Portfolio values
    cash_balance = db.Column(db.Float, default=0.0)
    invested_value = db.Column(db.Float, default=0.0)
    total_value = db.Column(db.Float, default=0.0)
    
    # Performance metrics
    total_pnl = db.Column(db.Float, default=0.0)
    daily_pnl = db.Column(db.Float, default=0.0)
    unrealized_pnl = db.Column(db.Float, default=0.0)
    realized_pnl = db.Column(db.Float, default=0.0)
    
    # Trading statistics
    total_trades = db.Column(db.Integer, default=0)
    winning_trades = db.Column(db.Integer, default=0)
    losing_trades = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    
    # Risk metrics
    max_drawdown = db.Column(db.Float, default=0.0)
    sharpe_ratio = db.Column(db.Float, default=0.0)
    profit_factor = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_calculation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    positions = db.relationship('Position', backref='portfolio', cascade='all, delete-orphan')
    trades = db.relationship('Trade', backref='portfolio', cascade='all, delete-orphan')
    
    @property
    def balance(self):
        """Compatibility property for cash_balance"""
        return self.cash_balance
    
    @balance.setter
    def balance(self, value):
        """Compatibility setter for cash_balance"""
        self.cash_balance = value
    
    def add_funds(self, amount):
        """Add funds to portfolio"""
        self.cash_balance += amount
        self.total_value += amount
        self.updated_at = datetime.utcnow()
    
    def withdraw_funds(self, amount):
        """Withdraw funds from portfolio"""
        if self.cash_balance >= amount:
            self.cash_balance -= amount
            self.total_value -= amount
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def calculate_portfolio_value(self):
        """Calculate current portfolio value"""
        # Get all open positions
        open_positions = Position.query.filter_by(
            portfolio_id=self.id, 
            is_open=True
        ).all()
        
        # Calculate invested value
        self.invested_value = sum(pos.market_value or 0 for pos in open_positions)
        
        # Calculate unrealized P&L
        self.unrealized_pnl = sum(pos.unrealized_pnl or 0 for pos in open_positions)
        
        # Calculate total value
        self.total_value = self.cash_balance + self.invested_value
        
        # Update timestamp
        self.last_calculation = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_trade_statistics(self):
        """Update trading statistics"""
        all_trades = Trade.query.filter_by(
            portfolio_id=self.id,
            status='executed'
        ).all()
        
        self.total_trades = len(all_trades)
        
        if self.total_trades > 0:
            # Calculate win/loss statistics
            profitable_trades = [t for t in all_trades if t.pnl and t.pnl > 0]
            losing_trades = [t for t in all_trades if t.pnl and t.pnl < 0]
            
            self.winning_trades = len(profitable_trades)
            self.losing_trades = len(losing_trades)
            self.win_rate = (self.winning_trades / self.total_trades) * 100
            
            # Calculate realized P&L
            self.realized_pnl = sum(t.pnl or 0 for t in all_trades)
            
            # Calculate profit factor
            total_profits = sum(t.pnl for t in profitable_trades)
            total_losses = abs(sum(t.pnl for t in losing_trades))
            
            if total_losses > 0:
                self.profit_factor = total_profits / total_losses
            else:
                self.profit_factor = float('inf') if total_profits > 0 else 0
        
        # Calculate total P&L
        self.total_pnl = self.realized_pnl + self.unrealized_pnl
    
    def get_performance_summary(self):
        """Get performance summary"""
        self.calculate_portfolio_value()
        self.update_trade_statistics()
        
        # Calculate ROI
        initial_value = 100000  # Assuming $100k starting capital
        roi = ((self.total_value - initial_value) / initial_value) * 100 if initial_value > 0 else 0
        
        return {
            'total_value': self.total_value,
            'cash_balance': self.cash_balance,
            'invested_value': self.invested_value,
            'total_pnl': self.total_pnl,
            'daily_pnl': self.daily_pnl,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'roi': roi,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio
        }
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'cash_balance': self.cash_balance,
            'invested_value': self.invested_value,
            'total_value': self.total_value,
            'total_pnl': self.total_pnl,
            'daily_pnl': self.daily_pnl,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'profit_factor': self.profit_factor,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_calculation': self.last_calculation.isoformat()
        }

class Position(db.Model):
    """Trading positions"""
    __tablename__ = 'positions'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    
    # Position details
    quantity = db.Column(db.Float, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float)
    market_value = db.Column(db.Float)
    
    # P&L calculations
    unrealized_pnl = db.Column(db.Float, default=0.0)
    unrealized_pnl_percent = db.Column(db.Float, default=0.0)
    
    # Position management
    stop_loss_price = db.Column(db.Float)
    take_profit_price = db.Column(db.Float)
    is_open = db.Column(db.Boolean, default=True)
    
    # Timestamps
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def update_market_value(self):
        """Update market value and P&L"""
        if self.asset and self.asset.current_price:
            self.current_price = self.asset.current_price
            self.market_value = self.quantity * self.current_price
            
            # Calculate unrealized P&L
            cost_basis = self.quantity * self.entry_price
            self.unrealized_pnl = self.market_value - cost_basis
            self.unrealized_pnl_percent = (self.unrealized_pnl / cost_basis) * 100
            
            self.updated_at = datetime.utcnow()
    
    def should_stop_loss(self):
        """Check if position should be stopped out"""
        if self.stop_loss_price and self.current_price:
            return self.current_price <= self.stop_loss_price
        return False
    
    def should_take_profit(self):
        """Check if position should take profit"""
        if self.take_profit_price and self.current_price:
            return self.current_price >= self.take_profit_price
        return False
    
    def close_position(self, exit_price=None):
        """Close the position"""
        if exit_price:
            self.current_price = exit_price
        self.is_open = False
        self.closed_at = datetime.utcnow()
        self.update_market_value()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'asset': self.asset.to_dict() if self.asset else None,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'market_value': self.market_value,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_percent': self.unrealized_pnl_percent,
            'stop_loss_price': self.stop_loss_price,
            'take_profit_price': self.take_profit_price,
            'is_open': self.is_open,
            'opened_at': self.opened_at.isoformat(),
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'updated_at': self.updated_at.isoformat()
        }

class Trade(db.Model):
    """Individual trades"""
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'))
    
    # Trade details
    trade_type = db.Column(db.String(10), nullable=False)  # BUY, SELL
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    
    # Fees and costs
    commission = db.Column(db.Float, default=0.0)
    fees = db.Column(db.Float, default=0.0)
    
    # Trade execution
    status = db.Column(db.String(20), default='pending')  # pending, executed, cancelled, failed
    order_type = db.Column(db.String(20), default='market')  # market, limit, stop
    
    # P&L (for closing trades)
    pnl = db.Column(db.Float)
    pnl_percent = db.Column(db.Float)
    
    # AI/Strategy information
    signal_id = db.Column(db.Integer, db.ForeignKey('trading_signals.id'))
    strategy = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime)
    
    def execute_trade(self):
        """Mark trade as executed"""
        self.status = 'executed'
        self.executed_at = datetime.utcnow()
    
    def calculate_pnl(self, exit_price):
        """Calculate P&L for closing trade"""
        if self.trade_type == 'SELL':
            # This is a closing trade
            cost_basis = self.quantity * self.price
            exit_value = self.quantity * exit_price
            self.pnl = exit_value - cost_basis - self.commission - self.fees
            self.pnl_percent = (self.pnl / cost_basis) * 100 if cost_basis > 0 else 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'asset': self.asset.to_dict() if self.asset else None,
            'position_id': self.position_id,
            'trade_type': self.trade_type,
            'quantity': self.quantity,
            'price': self.price,
            'total_value': self.total_value,
            'commission': self.commission,
            'fees': self.fees,
            'status': self.status,
            'order_type': self.order_type,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent,
            'strategy': self.strategy,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }

class TradingSignal(db.Model):
    """AI-generated trading signals"""
    __tablename__ = 'trading_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    
    # Signal details
    signal_type = db.Column(db.String(10), nullable=False)  # BUY, SELL, HOLD
    confidence = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    target_price = db.Column(db.Float)
    stop_loss_price = db.Column(db.Float)
    take_profit_price = db.Column(db.Float)
    
    # Signal metadata
    strategy = db.Column(db.String(50))
    timeframe = db.Column(db.String(20))  # 1m, 5m, 15m, 1h, 4h, 1d
    reasoning = db.Column(db.Text)
    
    # Technical indicators
    rsi = db.Column(db.Float)
    macd = db.Column(db.Float)
    bollinger_position = db.Column(db.Float)
    volume_ratio = db.Column(db.Float)
    
    # Signal status
    is_active = db.Column(db.Boolean, default=True)
    executed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    executed_at = db.Column(db.DateTime)
    
    # Relationships
    trades = db.relationship('Trade', backref='signal')
    
    def is_expired(self):
        """Check if signal is expired"""
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    def execute_signal(self):
        """Mark signal as executed"""
        self.executed = True
        self.executed_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'asset': self.asset.to_dict() if self.asset else None,
            'signal_type': self.signal_type,
            'confidence': self.confidence,
            'target_price': self.target_price,
            'stop_loss_price': self.stop_loss_price,
            'take_profit_price': self.take_profit_price,
            'strategy': self.strategy,
            'timeframe': self.timeframe,
            'reasoning': self.reasoning,
            'rsi': self.rsi,
            'macd': self.macd,
            'bollinger_position': self.bollinger_position,
            'volume_ratio': self.volume_ratio,
            'is_active': self.is_active,
            'executed': self.executed,
            'is_expired': self.is_expired(),
            'timestamp': self.timestamp.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }

class MarketData(db.Model):
    """Historical market data"""
    __tablename__ = 'market_data'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    
    # OHLCV data
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    open_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.BigInteger, default=0)
    
    # Technical indicators
    sma_20 = db.Column(db.Float)
    sma_50 = db.Column(db.Float)
    ema_12 = db.Column(db.Float)
    ema_26 = db.Column(db.Float)
    rsi = db.Column(db.Float)
    macd = db.Column(db.Float)
    macd_signal = db.Column(db.Float)
    bollinger_upper = db.Column(db.Float)
    bollinger_lower = db.Column(db.Float)
    
    # Metadata
    timeframe = db.Column(db.String(10), default='1d')  # 1m, 5m, 15m, 1h, 4h, 1d
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'timestamp': self.timestamp.isoformat(),
            'open_price': self.open_price,
            'high_price': self.high_price,
            'low_price': self.low_price,
            'close_price': self.close_price,
            'volume': self.volume,
            'sma_20': self.sma_20,
            'sma_50': self.sma_50,
            'ema_12': self.ema_12,
            'ema_26': self.ema_26,
            'rsi': self.rsi,
            'macd': self.macd,
            'macd_signal': self.macd_signal,
            'bollinger_upper': self.bollinger_upper,
            'bollinger_lower': self.bollinger_lower,
            'timeframe': self.timeframe,
            'created_at': self.created_at.isoformat()
        }

