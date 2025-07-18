"""
Trade Execution Service
Handles order execution, portfolio updates, and automated trading
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from database import db
from models.user import User
from models.trading import Portfolio, Position
from models.orders import Order, AutoTradingSettings, TradeRecommendation, OrderStatus, OrderSide
from services.deployment_trading_engine import advanced_trading_engine

logger = logging.getLogger(__name__)

class TradeExecutionService:
    """Service for executing trades and managing orders"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def execute_market_order(self, user_id: int, symbol: str, side: str, quantity: float, 
                           ai_signal_id: Optional[str] = None, confidence: Optional[float] = None, 
                           strategy: Optional[str] = None, is_automated: bool = False) -> Dict:
        """Execute a market order"""
        try:
            # Get user and portfolio
            user = User.query.get(user_id)
            if not user or not user.portfolio:
                return {'success': False, 'error': 'User or portfolio not found'}
            
            portfolio = user.portfolio
            
            # Get current market price
            market_data = advanced_trading_engine.get_market_data()
            current_price = None
            for asset in market_data:
                if asset['symbol'] == symbol:
                    current_price = asset['current_price']
                    break
            
            if not current_price:
                return {'success': False, 'error': 'Market data not available'}
            
            # Calculate order value
            order_value = quantity * current_price
            
            # Check if user has sufficient funds for buy orders
            if side.lower() == 'buy':
                if portfolio.balance < order_value:
                    return {'success': False, 'error': 'Insufficient funds'}
            
            # Create order
            order = Order(
                user_id=user_id,
                portfolio_id=portfolio.id,
                symbol=symbol,
                side=side.lower(),
                order_type='market',
                quantity=quantity,
                price=current_price,
                filled_quantity=quantity,
                filled_price=current_price,
                status='filled',
                ai_signal_id=ai_signal_id,
                confidence=confidence,
                strategy=strategy,
                is_automated=is_automated,
                filled_at=datetime.utcnow()
            )
            
            db.session.add(order)
            
            # Update portfolio and positions
            if side.lower() == 'buy':
                # Deduct from balance
                portfolio.balance -= order_value
                
                # Add or update position
                position = Position.query.filter_by(
                    portfolio_id=portfolio.id, 
                    symbol=symbol, 
                    is_active=True
                ).first()
                
                if position:
                    # Update existing position
                    total_value = (position.quantity * position.average_price) + order_value
                    total_quantity = position.quantity + quantity
                    position.average_price = total_value / total_quantity
                    position.quantity = total_quantity
                    position.current_price = current_price
                    position.updated_at = datetime.utcnow()
                else:
                    # Create new position
                    position = Position(
                        portfolio_id=portfolio.id,
                        symbol=symbol,
                        quantity=quantity,
                        average_price=current_price,
                        current_price=current_price,
                        is_active=True
                    )
                    db.session.add(position)
            
            elif side.lower() == 'sell':
                # Add to balance
                portfolio.balance += order_value
                
                # Update position
                position = Position.query.filter_by(
                    portfolio_id=portfolio.id, 
                    symbol=symbol, 
                    is_active=True
                ).first()
                
                if position:
                    if position.quantity >= quantity:
                        position.quantity -= quantity
                        position.current_price = current_price
                        position.updated_at = datetime.utcnow()
                        
                        # Close position if quantity is zero
                        if position.quantity <= 0:
                            position.is_active = False
                    else:
                        return {'success': False, 'error': 'Insufficient position size'}
                else:
                    return {'success': False, 'error': 'No position found to sell'}
            
            # Update portfolio total value
            self._update_portfolio_value(portfolio)
            
            db.session.commit()
            
            self.logger.info(f"✅ Order executed: {side.upper()} {quantity} {symbol} at ${current_price}")
            
            return {
                'success': True,
                'order': order.to_dict(),
                'message': f'Successfully {side.lower()} {quantity} shares of {symbol} at ${current_price:.2f}'
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Error executing order: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_trade_recommendations(self, user_id: int) -> List[Dict]:
        """Get AI-generated trade recommendations for user"""
        try:
            # Get fresh AI signals
            signals = advanced_trading_engine.get_trading_signals()
            
            recommendations = []
            for signal in signals:
                if signal['signal'] in ['buy', 'sell']:  # Skip hold signals
                    # Calculate expected return
                    current_price = signal['entry_price']
                    target_price = signal['target_price']
                    expected_return = ((target_price - current_price) / current_price) * 100
                    
                    recommendation = {
                        'id': f"rec_{signal['symbol']}_{int(datetime.utcnow().timestamp())}",
                        'symbol': signal['symbol'],
                        'asset_type': signal['asset_type'],
                        'action': signal['signal'],
                        'confidence': signal['confidence'],
                        'current_price': current_price,
                        'target_price': target_price,
                        'stop_loss': signal['stop_loss'],
                        'expected_return': expected_return,
                        'risk_score': signal['risk_score'],
                        'strategy': signal['strategy'],
                        'reasoning': signal['reasoning'],
                        'timestamp': signal['timestamp'],
                        'is_active': True
                    }
                    recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Error getting recommendations: {e}")
            return []
    
    def get_user_orders(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's order history"""
        try:
            orders = Order.query.filter_by(user_id=user_id)\
                              .order_by(Order.created_at.desc())\
                              .limit(limit).all()
            
            return [order.to_dict() for order in orders]
            
        except Exception as e:
            self.logger.error(f"❌ Error getting orders: {e}")
            return []
    
    def get_auto_trading_settings(self, user_id: int) -> Dict:
        """Get user's automated trading settings"""
        try:
            settings = AutoTradingSettings.query.filter_by(user_id=user_id).first()
            
            if not settings:
                # Create default settings
                settings = AutoTradingSettings(
                    user_id=user_id,
                    is_enabled=False,
                    max_daily_trades=10,
                    max_position_size=1000.0,
                    min_confidence=0.7,
                    stop_loss_percentage=0.05,
                    take_profit_percentage=0.10,
                    max_daily_loss=500.0,
                    enabled_strategies=json.dumps(['momentum_trading', 'mean_reversion']),
                    enabled_assets=json.dumps(['stock', 'crypto'])
                )
                db.session.add(settings)
                db.session.commit()
            
            return settings.to_dict()
            
        except Exception as e:
            self.logger.error(f"❌ Error getting auto trading settings: {e}")
            return {}
    
    def update_auto_trading_settings(self, user_id: int, settings_data: Dict) -> Dict:
        """Update user's automated trading settings"""
        try:
            settings = AutoTradingSettings.query.filter_by(user_id=user_id).first()
            
            if not settings:
                settings = AutoTradingSettings(user_id=user_id)
                db.session.add(settings)
            
            # Update settings
            for key, value in settings_data.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
            
            settings.updated_at = datetime.utcnow()
            db.session.commit()
            
            self.logger.info(f"✅ Auto trading settings updated for user {user_id}")
            
            return {'success': True, 'settings': settings.to_dict()}
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Error updating auto trading settings: {e}")
            return {'success': False, 'error': str(e)}
    
    def execute_automated_trades(self, user_id: int) -> Dict:
        """Execute automated trades based on AI signals and user settings"""
        try:
            # Get user settings
            settings = self.get_auto_trading_settings(user_id)
            
            if not settings.get('is_enabled'):
                return {'success': False, 'message': 'Automated trading is disabled'}
            
            # Get AI recommendations
            recommendations = self.get_trade_recommendations(user_id)
            
            executed_trades = []
            
            for rec in recommendations:
                # Check if recommendation meets criteria
                if rec['confidence'] >= settings['min_confidence']:
                    # Calculate position size (simplified)
                    position_size = min(settings['max_position_size'], 100.0)  # $100 per trade for demo
                    quantity = position_size / rec['current_price']
                    
                    # Execute trade
                    result = self.execute_market_order(
                        user_id=user_id,
                        symbol=rec['symbol'],
                        side=rec['action'],
                        quantity=quantity,
                        ai_signal_id=rec['id'],
                        confidence=rec['confidence'],
                        strategy=rec['strategy'],
                        is_automated=True
                    )
                    
                    if result['success']:
                        executed_trades.append(result['order'])
            
            return {
                'success': True,
                'executed_trades': executed_trades,
                'message': f'Executed {len(executed_trades)} automated trades'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error executing automated trades: {e}")
            return {'success': False, 'error': str(e)}
    
    def _update_portfolio_value(self, portfolio):
        """Update portfolio total value based on current positions"""
        try:
            total_value = portfolio.balance
            
            positions = Position.query.filter_by(portfolio_id=portfolio.id, is_active=True).all()
            for position in positions:
                total_value += position.quantity * position.current_price
            
            portfolio.total_value = total_value
            
        except Exception as e:
            self.logger.error(f"❌ Error updating portfolio value: {e}")

# Global instance
trade_execution_service = TradeExecutionService()

