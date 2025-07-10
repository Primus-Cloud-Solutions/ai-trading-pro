"""
Simplified AI Trading Engine for SaaS Platform
Basic trading decisions and market analysis without heavy ML dependencies
"""

import logging
import random
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import threading
import time
import schedule

from database import db
from models.trading import Asset, Portfolio, Position, Trade, TradingSignal, MarketData
from models.user import User, TradingSettings

logger = logging.getLogger(__name__)

class AITradingEngine:
    """Simplified AI Trading Engine with basic decision making"""
    
    def __init__(self):
        self.is_running = False
        self.trading_thread = None
        self.market_data_thread = None
        
        # Trading parameters
        self.min_confidence_threshold = 0.75
        self.max_position_size = 0.10  # 10% of portfolio
        self.stop_loss_percent = 0.05  # 5% stop loss
        self.take_profit_percent = 0.15  # 15% take profit
        
        # Market analysis parameters
        self.lookback_days = 30
        self.prediction_horizon = 24  # hours
        
        logger.info("🤖 Simplified AI Trading Engine initialized")
    
    def start_engine(self):
        """Start the AI trading engine"""
        if self.is_running:
            logger.warning("⚠️ AI Trading Engine is already running")
            return
        
        self.is_running = True
        
        # Schedule market data updates
        schedule.every(5).minutes.do(self._update_market_data)
        schedule.every(15).minutes.do(self._generate_trading_signals)
        schedule.every(30).minutes.do(self._execute_automated_trades)
        
        # Start background threads
        self.market_data_thread = threading.Thread(target=self._market_data_worker, daemon=True)
        self.trading_thread = threading.Thread(target=self._trading_worker, daemon=True)
        
        self.market_data_thread.start()
        self.trading_thread.start()
        
        logger.info("🚀 AI Trading Engine started successfully")
    
    def stop_engine(self):
        """Stop the AI trading engine"""
        self.is_running = False
        schedule.clear()
        logger.info("🛑 AI Trading Engine stopped")
    
    def _market_data_worker(self):
        """Background worker for market data updates"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"❌ Market data worker error: {e}")
                time.sleep(60)
    
    def _trading_worker(self):
        """Background worker for trading operations"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"❌ Trading worker error: {e}")
                time.sleep(60)
    
    def _update_market_data(self):
        """Update market data for tracked assets"""
        try:
            # Get sample market data (simplified)
            sample_assets = [
                {'symbol': 'BTC-USD', 'name': 'Bitcoin', 'price': 45000 + random.uniform(-2000, 2000)},
                {'symbol': 'ETH-USD', 'name': 'Ethereum', 'price': 3000 + random.uniform(-200, 200)},
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 180 + random.uniform(-10, 10)},
                {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'price': 250 + random.uniform(-20, 20)},
                {'symbol': 'DOGE-USD', 'name': 'Dogecoin', 'price': 0.08 + random.uniform(-0.01, 0.01)},
                {'symbol': 'ADA-USD', 'name': 'Cardano', 'price': 0.45 + random.uniform(-0.05, 0.05)},
            ]
            
            for asset_data in sample_assets:
                # Create or update asset
                asset = Asset.query.filter_by(symbol=asset_data['symbol']).first()
                if not asset:
                    asset = Asset(
                        symbol=asset_data['symbol'],
                        name=asset_data['name'],
                        asset_type='crypto' if 'USD' in asset_data['symbol'] else 'stock'
                    )
                    db.session.add(asset)
                
                # Add market data
                market_data = MarketData(
                    asset_id=asset.id if asset.id else None,
                    price=asset_data['price'],
                    volume=random.randint(1000000, 10000000),
                    timestamp=datetime.utcnow()
                )
                db.session.add(market_data)
            
            db.session.commit()
            logger.info("📊 Market data updated successfully")
            
        except Exception as e:
            logger.error(f"❌ Error updating market data: {e}")
            db.session.rollback()
    
    def _generate_trading_signals(self):
        """Generate trading signals using simplified analysis"""
        try:
            assets = Asset.query.all()
            
            for asset in assets:
                # Get recent market data
                recent_data = MarketData.query.filter_by(asset_id=asset.id)\
                    .order_by(MarketData.timestamp.desc())\
                    .limit(10).all()
                
                if len(recent_data) < 5:
                    continue
                
                # Simple trend analysis
                prices = [data.price for data in recent_data]
                trend = self._calculate_simple_trend(prices)
                confidence = random.uniform(0.6, 0.95)
                
                # Generate signal
                if trend > 0.02:  # Upward trend
                    signal_type = 'BUY'
                    target_price = prices[0] * 1.1
                elif trend < -0.02:  # Downward trend
                    signal_type = 'SELL'
                    target_price = prices[0] * 0.9
                else:
                    signal_type = 'HOLD'
                    target_price = prices[0]
                
                # Create trading signal
                signal = TradingSignal(
                    asset_id=asset.id,
                    signal_type=signal_type,
                    confidence=confidence,
                    target_price=target_price,
                    current_price=prices[0],
                    timestamp=datetime.utcnow(),
                    reasoning=f"Simple trend analysis: {trend:.3f}"
                )
                db.session.add(signal)
            
            db.session.commit()
            logger.info("🎯 Trading signals generated successfully")
            
        except Exception as e:
            logger.error(f"❌ Error generating trading signals: {e}")
            db.session.rollback()
    
    def _calculate_simple_trend(self, prices: List[float]) -> float:
        """Calculate simple trend from price list"""
        if len(prices) < 2:
            return 0.0
        
        # Simple linear trend calculation
        n = len(prices)
        x_sum = sum(range(n))
        y_sum = sum(prices)
        xy_sum = sum(i * prices[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope / prices[0] if prices[0] != 0 else 0.0
    
    def _execute_automated_trades(self):
        """Execute automated trades based on signals and user settings"""
        try:
            # Get users with automated trading enabled
            users = User.query.join(TradingSettings)\
                .filter(TradingSettings.automated_trading_enabled == True).all()
            
            for user in users:
                self._process_user_trades(user)
            
            logger.info("🤖 Automated trades processed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error executing automated trades: {e}")
    
    def _process_user_trades(self, user: User):
        """Process trades for a specific user"""
        try:
            # Get user's portfolio
            portfolio = Portfolio.query.filter_by(user_id=user.id).first()
            if not portfolio:
                return
            
            # Get recent signals
            signals = TradingSignal.query\
                .filter(TradingSignal.confidence >= self.min_confidence_threshold)\
                .filter(TradingSignal.timestamp >= datetime.utcnow() - timedelta(hours=1))\
                .order_by(TradingSignal.timestamp.desc())\
                .limit(5).all()
            
            for signal in signals:
                if signal.signal_type == 'BUY':
                    self._execute_buy_order(user, portfolio, signal)
                elif signal.signal_type == 'SELL':
                    self._execute_sell_order(user, portfolio, signal)
            
        except Exception as e:
            logger.error(f"❌ Error processing trades for user {user.id}: {e}")
    
    def _execute_buy_order(self, user: User, portfolio: Portfolio, signal: TradingSignal):
        """Execute a buy order"""
        try:
            # Calculate position size
            max_investment = portfolio.cash_balance * self.max_position_size
            shares = int(max_investment / signal.current_price)
            
            if shares > 0 and portfolio.cash_balance >= shares * signal.current_price:
                # Create trade record
                trade = Trade(
                    user_id=user.id,
                    asset_id=signal.asset_id,
                    trade_type='BUY',
                    quantity=shares,
                    price=signal.current_price,
                    total_amount=shares * signal.current_price,
                    timestamp=datetime.utcnow(),
                    status='EXECUTED'
                )
                db.session.add(trade)
                
                # Update portfolio
                portfolio.cash_balance -= shares * signal.current_price
                
                # Create or update position
                position = Position.query.filter_by(
                    portfolio_id=portfolio.id,
                    asset_id=signal.asset_id
                ).first()
                
                if position:
                    # Update existing position
                    total_value = position.quantity * position.average_price + shares * signal.current_price
                    position.quantity += shares
                    position.average_price = total_value / position.quantity
                else:
                    # Create new position
                    position = Position(
                        portfolio_id=portfolio.id,
                        asset_id=signal.asset_id,
                        quantity=shares,
                        average_price=signal.current_price
                    )
                    db.session.add(position)
                
                db.session.commit()
                logger.info(f"✅ Buy order executed: {shares} shares at ${signal.current_price}")
            
        except Exception as e:
            logger.error(f"❌ Error executing buy order: {e}")
            db.session.rollback()
    
    def _execute_sell_order(self, user: User, portfolio: Portfolio, signal: TradingSignal):
        """Execute a sell order"""
        try:
            # Find existing position
            position = Position.query.filter_by(
                portfolio_id=portfolio.id,
                asset_id=signal.asset_id
            ).first()
            
            if position and position.quantity > 0:
                # Sell all shares in position
                shares_to_sell = position.quantity
                sale_amount = shares_to_sell * signal.current_price
                
                # Create trade record
                trade = Trade(
                    user_id=user.id,
                    asset_id=signal.asset_id,
                    trade_type='SELL',
                    quantity=shares_to_sell,
                    price=signal.current_price,
                    total_amount=sale_amount,
                    timestamp=datetime.utcnow(),
                    status='EXECUTED'
                )
                db.session.add(trade)
                
                # Update portfolio
                portfolio.cash_balance += sale_amount
                
                # Remove position
                db.session.delete(position)
                
                db.session.commit()
                logger.info(f"✅ Sell order executed: {shares_to_sell} shares at ${signal.current_price}")
            
        except Exception as e:
            logger.error(f"❌ Error executing sell order: {e}")
            db.session.rollback()
    
    def get_portfolio_performance(self, user_id: int) -> Dict:
        """Get portfolio performance metrics"""
        try:
            portfolio = Portfolio.query.filter_by(user_id=user_id).first()
            if not portfolio:
                return {'error': 'Portfolio not found'}
            
            positions = Position.query.filter_by(portfolio_id=portfolio.id).all()
            
            total_value = portfolio.cash_balance
            total_invested = 0
            
            for position in positions:
                # Get current price
                latest_data = MarketData.query.filter_by(asset_id=position.asset_id)\
                    .order_by(MarketData.timestamp.desc()).first()
                
                if latest_data:
                    current_value = position.quantity * latest_data.price
                    total_value += current_value
                    total_invested += position.quantity * position.average_price
            
            return {
                'total_value': total_value,
                'cash_balance': portfolio.cash_balance,
                'total_invested': total_invested,
                'profit_loss': total_value - total_invested,
                'profit_loss_percent': ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating portfolio performance: {e}")
            return {'error': str(e)}
    
    def get_trading_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent trading signals"""
        try:
            signals = TradingSignal.query\
                .order_by(TradingSignal.timestamp.desc())\
                .limit(limit).all()
            
            result = []
            for signal in signals:
                asset = Asset.query.get(signal.asset_id)
                result.append({
                    'symbol': asset.symbol if asset else 'Unknown',
                    'signal_type': signal.signal_type,
                    'confidence': signal.confidence,
                    'target_price': signal.target_price,
                    'current_price': signal.current_price,
                    'timestamp': signal.timestamp.isoformat(),
                    'reasoning': signal.reasoning
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting trading signals: {e}")
            return []

# Global instance
ai_trading_engine = AITradingEngine()

