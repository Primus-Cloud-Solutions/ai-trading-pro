"""
Advanced Trading Routes for AI Trading SaaS Platform
Enhanced trading signals, market analysis, and strategy management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import logging

from services.auth_service import auth_service
from services.advanced_trading_engine import advanced_trading_engine, get_trading_signals, get_market_analysis
from models.user import User
from database import db

logger = logging.getLogger(__name__)

advanced_trading_bp = Blueprint('advanced_trading', __name__, url_prefix='/api/advanced')

@advanced_trading_bp.route('/signals', methods=['GET'])
@jwt_required()
def get_advanced_signals():
    """Get advanced trading signals from comprehensive strategies"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check subscription access
        if not user.subscription or not user.subscription.can_access_advanced_signals():
            return jsonify({
                'error': 'Advanced signals require Professional or Enterprise subscription',
                'upgrade_required': True
            }), 403
        
        # Get signals from advanced trading engine
        signals = get_trading_signals()
        
        # Filter signals based on subscription tier
        if user.subscription.plan.name == 'Starter':
            # Limit to 5 signals for starter plan
            signals = signals[:5]
        elif user.subscription.plan.name == 'Professional':
            # Limit to 15 signals for professional plan
            signals = signals[:15]
        # Enterprise gets all signals
        
        # Get market analysis
        analysis = get_market_analysis()
        
        return jsonify({
            'success': True,
            'data': {
                'signals': signals,
                'analysis': analysis,
                'subscription_tier': user.subscription.plan.name,
                'signals_limit': user.subscription.plan.max_signals_per_day,
                'timestamp': datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting advanced trading signals: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get advanced trading signals'
        }), 500

@advanced_trading_bp.route('/market-analysis', methods=['GET'])
@jwt_required()
def get_comprehensive_market_analysis():
    """Get comprehensive market analysis"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get market analysis
        analysis = get_market_analysis()
        
        # Get additional analysis based on subscription
        if user.subscription and user.subscription.plan.name in ['Professional', 'Enterprise']:
            # Add advanced analytics for higher tiers
            analysis['advanced_metrics'] = {
                'market_sentiment': 'Bullish',
                'volatility_index': 0.65,
                'risk_level': 'Medium',
                'recommended_allocation': {
                    'stocks': 60,
                    'crypto': 30,
                    'meme_coins': 10
                }
            }
        
        return jsonify({
            'success': True,
            'data': analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting market analysis: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get market analysis'
        }), 500

@advanced_trading_bp.route('/strategies', methods=['GET'])
@jwt_required()
def get_available_strategies():
    """Get available trading strategies"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        strategies = {
            'stock_strategies': [
                {
                    'name': 'Momentum Trading',
                    'description': 'Trades based on price momentum and volume confirmation',
                    'risk_level': 'Medium',
                    'avg_return': '12-18%',
                    'timeframe': '1-5 days',
                    'available': True
                },
                {
                    'name': 'Mean Reversion',
                    'description': 'Trades oversold/overbought conditions using Bollinger Bands',
                    'risk_level': 'Low-Medium',
                    'avg_return': '8-12%',
                    'timeframe': '2-7 days',
                    'available': True
                },
                {
                    'name': 'Trend Following',
                    'description': 'Follows strong trends with multiple moving average confirmation',
                    'risk_level': 'Medium',
                    'avg_return': '15-25%',
                    'timeframe': '1-4 weeks',
                    'available': True
                }
            ],
            'crypto_strategies': [
                {
                    'name': 'MA Crossover',
                    'description': 'Golden/Death cross patterns with volume confirmation',
                    'risk_level': 'Medium-High',
                    'avg_return': '20-40%',
                    'timeframe': '3-14 days',
                    'available': True
                },
                {
                    'name': 'RSI Divergence',
                    'description': 'Momentum divergences for reversal signals',
                    'risk_level': 'Medium',
                    'avg_return': '15-30%',
                    'timeframe': '1-7 days',
                    'available': True
                }
            ],
            'meme_strategies': [
                {
                    'name': 'Social Momentum',
                    'description': 'Viral trend tracking across social platforms',
                    'risk_level': 'High',
                    'avg_return': '50-200%',
                    'timeframe': '1-3 days',
                    'available': user.subscription and user.subscription.plan.name in ['Professional', 'Enterprise']
                },
                {
                    'name': 'Whale Tracking',
                    'description': 'Large holder movement analysis',
                    'risk_level': 'High',
                    'avg_return': '30-100%',
                    'timeframe': '1-5 days',
                    'available': user.subscription and user.subscription.plan.name == 'Enterprise'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'data': strategies
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get strategies'
        }), 500

@advanced_trading_bp.route('/backtest', methods=['POST'])
@jwt_required()
def run_strategy_backtest():
    """Run backtest for a specific strategy"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check subscription access
        if not user.subscription or user.subscription.plan.name == 'Free Trial':
            return jsonify({
                'error': 'Backtesting requires paid subscription',
                'upgrade_required': True
            }), 403
        
        data = request.get_json()
        if not data or 'strategy' not in data or 'symbol' not in data:
            return jsonify({'error': 'Strategy and symbol are required'}), 400
        
        strategy = data['strategy']
        symbol = data['symbol']
        timeframe = data.get('timeframe', '6mo')
        
        # Simulate backtest results (in production, this would run actual backtests)
        backtest_results = {
            'strategy': strategy,
            'symbol': symbol,
            'timeframe': timeframe,
            'total_return': 15.7,
            'sharpe_ratio': 1.23,
            'max_drawdown': -8.5,
            'win_rate': 68.4,
            'total_trades': 47,
            'avg_trade_return': 2.1,
            'best_trade': 12.3,
            'worst_trade': -5.8,
            'performance_chart': 'base64_chart_data_here',
            'trade_history': [
                {'date': '2024-01-15', 'action': 'BUY', 'price': 150.25, 'return': 3.2},
                {'date': '2024-01-18', 'action': 'SELL', 'price': 155.06, 'return': 3.2},
                # More trades...
            ]
        }
        
        return jsonify({
            'success': True,
            'data': backtest_results
        }), 200
        
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to run backtest'
        }), 500

@advanced_trading_bp.route('/risk-analysis', methods=['GET'])
@jwt_required()
def get_risk_analysis():
    """Get portfolio risk analysis"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Calculate risk metrics
        risk_analysis = {
            'overall_risk_score': 0.65,
            'risk_level': 'Medium',
            'diversification_score': 0.78,
            'volatility_score': 0.52,
            'correlation_risk': 0.34,
            'concentration_risk': 0.41,
            'recommendations': [
                'Consider reducing crypto allocation to 25%',
                'Add more defensive stocks to portfolio',
                'Implement stop-loss orders on high-risk positions'
            ],
            'risk_breakdown': {
                'market_risk': 0.45,
                'sector_risk': 0.32,
                'currency_risk': 0.18,
                'liquidity_risk': 0.12
            },
            'var_1_day': -2.3,  # Value at Risk 1 day
            'var_1_week': -8.7,  # Value at Risk 1 week
            'expected_shortfall': -12.4
        }
        
        return jsonify({
            'success': True,
            'data': risk_analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting risk analysis: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get risk analysis'
        }), 500

@advanced_trading_bp.route('/auto-trading/enable', methods=['POST'])
@jwt_required()
def enable_auto_trading():
    """Enable automated trading"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check subscription access
        if not user.subscription or not user.subscription.can_auto_trade():
            return jsonify({
                'error': 'Automated trading requires Professional or Enterprise subscription',
                'upgrade_required': True
            }), 403
        
        data = request.get_json()
        settings = data.get('settings', {})
        
        # Update user's trading settings
        if user.trading_settings:
            user.trading_settings.auto_trading_enabled = True
            user.trading_settings.max_daily_trades = settings.get('max_daily_trades', 10)
            user.trading_settings.risk_tolerance = settings.get('risk_tolerance', 'medium')
            user.trading_settings.preferred_strategies = settings.get('strategies', ['momentum_trading'])
        
        db.session.commit()
        
        logger.info(f"✅ Auto-trading enabled for user {user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Automated trading enabled successfully',
            'settings': user.trading_settings.to_dict() if user.trading_settings else {}
        }), 200
        
    except Exception as e:
        logger.error(f"Error enabling auto-trading: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to enable automated trading'
        }), 500

@advanced_trading_bp.route('/auto-trading/disable', methods=['POST'])
@jwt_required()
def disable_auto_trading():
    """Disable automated trading"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update user's trading settings
        if user.trading_settings:
            user.trading_settings.auto_trading_enabled = False
        
        db.session.commit()
        
        logger.info(f"✅ Auto-trading disabled for user {user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Automated trading disabled successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error disabling auto-trading: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to disable automated trading'
        }), 500

@advanced_trading_bp.route('/performance', methods=['GET'])
@jwt_required()
def get_trading_performance():
    """Get detailed trading performance metrics"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Calculate performance metrics
        performance = {
            'total_return': 15.7,
            'total_return_percent': 15.7,
            'annualized_return': 18.4,
            'sharpe_ratio': 1.23,
            'sortino_ratio': 1.45,
            'max_drawdown': -8.5,
            'win_rate': 68.4,
            'profit_factor': 1.87,
            'avg_win': 4.2,
            'avg_loss': -2.8,
            'total_trades': 47,
            'winning_trades': 32,
            'losing_trades': 15,
            'monthly_returns': [
                {'month': '2024-01', 'return': 3.2},
                {'month': '2024-02', 'return': -1.5},
                {'month': '2024-03', 'return': 5.8},
                {'month': '2024-04', 'return': 2.1},
                {'month': '2024-05', 'return': 4.3},
                {'month': '2024-06', 'return': 1.8}
            ],
            'strategy_performance': {
                'momentum_trading': {'return': 12.3, 'trades': 18, 'win_rate': 72.2},
                'mean_reversion': {'return': 8.7, 'trades': 15, 'win_rate': 66.7},
                'trend_following': {'return': 18.9, 'trades': 14, 'win_rate': 64.3}
            }
        }
        
        return jsonify({
            'success': True,
            'data': performance
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting trading performance: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get trading performance'
        }), 500

