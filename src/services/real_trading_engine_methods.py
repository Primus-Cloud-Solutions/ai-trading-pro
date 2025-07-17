"""
Real Trading Engine Methods - Additional functionality
Enhanced methods for portfolio management and analytics
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)

class TradingEngineAnalytics:
    """Analytics and reporting methods for the trading engine"""
    
    def __init__(self, trading_engine):
        self.engine = trading_engine
    
    def get_portfolio_performance(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Calculate portfolio performance metrics"""
        try:
            if user_id not in self.engine.accounts:
                return {'error': 'Account not found'}
            
            account = self.engine.accounts[user_id]
            trades = self.engine.get_trade_history(user_id, limit=1000)
            
            # Filter trades by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_trades = [
                trade for trade in trades 
                if datetime.fromisoformat(trade['timestamp']) >= cutoff_date
            ]
            
            if not recent_trades:
                return {
                    'total_trades': 0,
                    'win_rate': 0,
                    'total_pnl': 0,
                    'avg_trade_size': 0,
                    'best_trade': None,
                    'worst_trade': None
                }
            
            # Calculate metrics
            total_trades = len(recent_trades)
            buy_trades = [t for t in recent_trades if t['side'] == 'buy']
            sell_trades = [t for t in recent_trades if t['side'] == 'sell']
            
            # Calculate P&L (simplified)
            total_pnl = 0
            trade_pnls = []
            
            for sell_trade in sell_trades:
                symbol = sell_trade['symbol']
                sell_value = sell_trade['executed_price'] * sell_trade['executed_quantity']
                
                # Find corresponding buy trades
                matching_buys = [
                    t for t in buy_trades 
                    if t['symbol'] == symbol and 
                    datetime.fromisoformat(t['timestamp']) <= datetime.fromisoformat(sell_trade['timestamp'])
                ]
                
                if matching_buys:
                    # Use most recent buy price
                    buy_trade = max(matching_buys, key=lambda x: x['timestamp'])
                    buy_value = buy_trade['executed_price'] * sell_trade['executed_quantity']
                    pnl = sell_value - buy_value - sell_trade['fees'] - buy_trade['fees']
                    total_pnl += pnl
                    trade_pnls.append(pnl)
            
            # Calculate win rate
            winning_trades = len([pnl for pnl in trade_pnls if pnl > 0])
            win_rate = (winning_trades / len(trade_pnls)) * 100 if trade_pnls else 0
            
            # Calculate average trade size
            trade_values = [t['executed_price'] * t['executed_quantity'] for t in recent_trades]
            avg_trade_size = statistics.mean(trade_values) if trade_values else 0
            
            # Find best and worst trades
            best_trade = max(trade_pnls) if trade_pnls else 0
            worst_trade = min(trade_pnls) if trade_pnls else 0
            
            return {
                'total_trades': total_trades,
                'win_rate': round(win_rate, 2),
                'total_pnl': round(total_pnl, 2),
                'avg_trade_size': round(avg_trade_size, 2),
                'best_trade': round(best_trade, 2),
                'worst_trade': round(worst_trade, 2),
                'profitable_trades': winning_trades,
                'losing_trades': len(trade_pnls) - winning_trades
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating portfolio performance: {e}")
            return {'error': str(e)}
    
    def get_position_summary(self, user_id: str) -> Dict[str, Any]:
        """Get detailed position summary"""
        try:
            if user_id not in self.engine.positions:
                return {'positions': [], 'total_value': 0}
            
            positions = self.engine.positions[user_id]
            position_details = []
            total_value = 0
            
            for symbol, quantity in positions.items():
                if quantity > 0:
                    current_price = self.engine.get_market_price(symbol)
                    market_value = quantity * current_price
                    total_value += market_value
                    
                    # Calculate average cost basis from trade history
                    trades = self.engine.get_trade_history(user_id)
                    buy_trades = [t for t in trades if t['symbol'] == symbol and t['side'] == 'buy']
                    
                    if buy_trades:
                        total_cost = sum(t['executed_price'] * t['executed_quantity'] for t in buy_trades)
                        total_quantity = sum(t['executed_quantity'] for t in buy_trades)
                        avg_cost = total_cost / total_quantity if total_quantity > 0 else current_price
                        
                        unrealized_pnl = (current_price - avg_cost) * quantity
                        pnl_percentage = ((current_price - avg_cost) / avg_cost) * 100 if avg_cost > 0 else 0
                    else:
                        avg_cost = current_price
                        unrealized_pnl = 0
                        pnl_percentage = 0
                    
                    position_details.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'current_price': round(current_price, 4),
                        'market_value': round(market_value, 2),
                        'avg_cost': round(avg_cost, 4),
                        'unrealized_pnl': round(unrealized_pnl, 2),
                        'pnl_percentage': round(pnl_percentage, 2)
                    })
            
            return {
                'positions': position_details,
                'total_value': round(total_value, 2),
                'position_count': len(position_details)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting position summary: {e}")
            return {'error': str(e)}
    
    def get_trading_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive trading statistics"""
        try:
            account_info = self.engine.get_account_info(user_id)
            if 'error' in account_info:
                return account_info
            
            performance = self.get_portfolio_performance(user_id)
            positions = self.get_position_summary(user_id)
            
            # Calculate additional metrics
            total_portfolio_value = account_info['portfolio_value']
            cash_percentage = (account_info['balance'] / total_portfolio_value) * 100 if total_portfolio_value > 0 else 100
            invested_percentage = 100 - cash_percentage
            
            return {
                'account': {
                    'balance': account_info['balance'],
                    'portfolio_value': total_portfolio_value,
                    'buying_power': account_info['buying_power'],
                    'cash_percentage': round(cash_percentage, 2),
                    'invested_percentage': round(invested_percentage, 2)
                },
                'performance': performance,
                'positions': positions,
                'broker': account_info['broker'],
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting trading statistics: {e}")
            return {'error': str(e)}

class TradingEngineRiskManagement:
    """Risk management methods for the trading engine"""
    
    def __init__(self, trading_engine):
        self.engine = trading_engine
    
    def check_position_limits(self, user_id: str, symbol: str, quantity: float, side: str) -> Dict[str, Any]:
        """Check if trade violates position limits"""
        try:
            account_info = self.engine.get_account_info(user_id)
            if 'error' in account_info:
                return {'allowed': False, 'reason': account_info['error']}
            
            current_positions = account_info.get('positions', {})
            current_quantity = current_positions.get(symbol, 0)
            
            # Calculate new position after trade
            if side == 'buy':
                new_quantity = current_quantity + quantity
            else:
                new_quantity = current_quantity - quantity
            
            # Check maximum position size (10% of portfolio)
            portfolio_value = account_info['portfolio_value']
            current_price = self.engine.get_market_price(symbol)
            position_value = abs(new_quantity) * current_price
            position_percentage = (position_value / portfolio_value) * 100 if portfolio_value > 0 else 0
            
            max_position_percentage = 25.0  # 25% max per position
            
            if position_percentage > max_position_percentage:
                return {
                    'allowed': False,
                    'reason': f'Position would exceed maximum limit of {max_position_percentage}% per symbol',
                    'current_percentage': round(position_percentage, 2)
                }
            
            # Check for short selling (not allowed in demo)
            if new_quantity < 0:
                return {
                    'allowed': False,
                    'reason': 'Short selling not allowed in demo account'
                }
            
            return {
                'allowed': True,
                'new_quantity': new_quantity,
                'position_percentage': round(position_percentage, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking position limits: {e}")
            return {'allowed': False, 'reason': str(e)}
    
    def calculate_risk_metrics(self, user_id: str) -> Dict[str, Any]:
        """Calculate portfolio risk metrics"""
        try:
            positions = self.engine.positions.get(user_id, {})
            account_info = self.engine.get_account_info(user_id)
            
            if 'error' in account_info:
                return account_info
            
            portfolio_value = account_info['portfolio_value']
            
            # Calculate concentration risk
            position_values = []
            for symbol, quantity in positions.items():
                if quantity > 0:
                    price = self.engine.get_market_price(symbol)
                    value = quantity * price
                    position_values.append(value)
            
            if not position_values:
                return {
                    'concentration_risk': 'Low',
                    'largest_position_percentage': 0,
                    'number_of_positions': 0,
                    'diversification_score': 100
                }
            
            # Calculate largest position percentage
            largest_position = max(position_values)
            largest_position_percentage = (largest_position / portfolio_value) * 100 if portfolio_value > 0 else 0
            
            # Determine concentration risk level
            if largest_position_percentage > 30:
                concentration_risk = 'High'
            elif largest_position_percentage > 15:
                concentration_risk = 'Medium'
            else:
                concentration_risk = 'Low'
            
            # Calculate diversification score (simple version)
            num_positions = len(position_values)
            if num_positions >= 10:
                diversification_score = 100
            elif num_positions >= 5:
                diversification_score = 80
            elif num_positions >= 3:
                diversification_score = 60
            else:
                diversification_score = 40
            
            return {
                'concentration_risk': concentration_risk,
                'largest_position_percentage': round(largest_position_percentage, 2),
                'number_of_positions': num_positions,
                'diversification_score': diversification_score,
                'total_invested': round(sum(position_values), 2),
                'cash_percentage': round((account_info['balance'] / portfolio_value) * 100, 2) if portfolio_value > 0 else 100
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating risk metrics: {e}")
            return {'error': str(e)}

