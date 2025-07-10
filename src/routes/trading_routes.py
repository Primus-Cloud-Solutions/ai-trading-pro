"""
Trading Routes - Enhanced with Advanced AI Trading Engine
Provides comprehensive trading functionality with real-time AI signals
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import logging

from services.auth_service import auth_service
from services.deployment_trading_engine import advanced_trading_engine
from models.user import User
from models.trading import Portfolio, Position, Trade, Asset, TradingSignal, MarketData
from database import db

logger = logging.getLogger(__name__)

trading_bp = Blueprint('trading', __name__, url_prefix='/api/trading')

# Portfolio Management
@trading_bp.route('/portfolio', methods=['GET'])
@jwt_required()
def get_portfolio():
    """Get user's portfolio information"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        portfolio = user.portfolio
        positions = Position.query.filter_by(portfolio_id=portfolio.id, is_active=True).all()
        recent_trades = Trade.query.filter_by(portfolio_id=portfolio.id).order_by(Trade.executed_at.desc()).limit(10).all()
        
        # Get portfolio analysis from advanced engine
        portfolio_analysis = advanced_trading_engine.get_portfolio_analysis()
        
        return jsonify({
            'portfolio': portfolio.to_dict(),
            'positions': [pos.to_dict() for pos in positions],
            'recent_trades': [trade.to_dict() for trade in recent_trades],
            'performance': portfolio_analysis,
            'ai_analysis': {
                'total_balance': portfolio_analysis.get('total_balance', portfolio.balance),
                'daily_pnl': portfolio_analysis.get('daily_pnl', 0),
                'win_rate': portfolio_analysis.get('win_rate', 75.0),
                'active_strategies': portfolio_analysis.get('active_strategies', 8)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_portfolio endpoint: {e}")
        return jsonify({'error': 'Failed to get portfolio'}), 500

# Trading Operations
@trading_bp.route('/signals', methods=['GET'])
@jwt_required()
def get_trading_signals():
    """Get AI-generated trading signals"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get live signals from advanced trading engine
        signals = advanced_trading_engine.get_trading_signals()
        
        # Filter by user's confidence threshold
        min_confidence = user.trading_settings.min_confidence_threshold if user.trading_settings else 0.5
        filtered_signals = [s for s in signals if s.get('confidence', 0) >= min_confidence]
        
        return jsonify({
            'signals': filtered_signals,
            'total_signals': len(filtered_signals),
            'engine_status': 'active',
            'strategies_active': ['momentum_trading', 'mean_reversion', 'trend_following', 'crypto_ma_crossover', 'meme_social_momentum'],
            'last_update': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_trading_signals endpoint: {e}")
        return jsonify({'error': 'Failed to get trading signals'}), 500

@trading_bp.route('/market-data', methods=['GET'])
@jwt_required()
def get_live_market_data():
    """Get live market data from advanced trading engine"""
    try:
        # Get live market data from advanced engine
        market_data = advanced_trading_engine.get_market_data()
        
        return jsonify({
            'market_data': market_data,
            'total_assets': len(market_data),
            'last_update': datetime.utcnow().isoformat(),
            'data_source': 'advanced_ai_engine'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_live_market_data endpoint: {e}")
        return jsonify({'error': 'Failed to get market data'}), 500

@trading_bp.route('/execute-trade', methods=['POST'])
@jwt_required()
def execute_manual_trade():
    """Execute a manual trade"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        data = request.get_json()
        required_fields = ['symbol', 'action', 'quantity']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        symbol = data['symbol'].upper()
        action = data['action'].upper()
        quantity = float(data['quantity'])
        
        if action not in ['BUY', 'SELL']:
            return jsonify({'error': 'Invalid action'}), 400
        
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
        
        # Check subscription limits
        if not user.subscription or not user.subscription.can_execute_trades():
            return jsonify({'error': 'Subscription does not allow manual trading'}), 403
        
        # Execute trade through advanced engine (simulation)
        trade_result = advanced_trading_engine.execute_trade(symbol, action, quantity)
        
        if trade_result.get('success'):
            # Record trade in database
            portfolio = user.portfolio
            
            # Create trade record
            trade = Trade(
                portfolio_id=portfolio.id,
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=trade_result['execution_price'],
                total_value=trade_result['total_value'],
                executed_at=datetime.utcnow(),
                trade_type='manual',
                status='completed'
            )
            
            db.session.add(trade)
            
            # Update portfolio balance
            if action == 'BUY':
                portfolio.balance -= trade_result['total_value']
            else:
                portfolio.balance += trade_result['total_value']
            
            db.session.commit()
            
            logger.info(f"✅ Manual trade executed: {action} {quantity} {symbol} at ${trade_result['execution_price']}")
            
            return jsonify({
                'message': 'Trade executed successfully',
                'trade': trade_result,
                'new_balance': portfolio.balance
            }), 200
        else:
            return jsonify({'error': trade_result.get('message', 'Trade execution failed')}), 400
        
    except Exception as e:
        logger.error(f"❌ Error in execute_manual_trade endpoint: {e}")
        return jsonify({'error': 'Failed to execute trade'}), 500

@trading_bp.route('/ai-status', methods=['GET'])
@jwt_required()
def get_ai_status():
    """Get AI trading engine status"""
    try:
        # Get model status from advanced engine
        status = advanced_trading_engine.get_model_status()
        
        return jsonify({
            'ai_engine': status,
            'features': {
                'momentum_trading': True,
                'mean_reversion': True,
                'trend_following': True,
                'crypto_strategies': True,
                'meme_coin_analysis': True,
                'social_sentiment': True,
                'whale_tracking': True,
                'technical_indicators': True
            },
            'performance': {
                'uptime': f"{status.get('uptime_seconds', 0)} seconds",
                'signals_generated': status.get('signals_generated', 0),
                'confidence_level': f"{status.get('confidence_level', 85)}%",
                'learning_rate': status.get('learning_rate', 0.001)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_ai_status endpoint: {e}")
        return jsonify({'error': 'Failed to get AI status'}), 500

@trading_bp.route('/assets', methods=['GET'])
@jwt_required()
def get_available_assets():
    """Get available trading assets"""
    try:
        # Get market data which includes all available assets
        market_data = advanced_trading_engine.get_market_data()
        
        # Format as assets
        assets = []
        for data in market_data:
            asset_type = 'stock'
            if '-USD' in data['symbol']:
                if data['symbol'] in ['DOGE-USD', 'SHIB-USD', 'PEPE-USD']:
                    asset_type = 'meme_coin'
                else:
                    asset_type = 'crypto'
            
            assets.append({
                'symbol': data['symbol'],
                'name': data['symbol'].replace('-USD', ''),
                'asset_type': asset_type,
                'current_price': data['current_price'],
                'change_percent': data['change_percent'],
                'volume': data['volume'],
                'market_cap': data.get('market_cap', 0),
                'is_active': True
            })
        
        return jsonify({
            'assets': assets,
            'total_assets': len(assets),
            'asset_types': {
                'stocks': len([a for a in assets if a['asset_type'] == 'stock']),
                'crypto': len([a for a in assets if a['asset_type'] == 'crypto']),
                'meme_coins': len([a for a in assets if a['asset_type'] == 'meme_coin'])
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_available_assets endpoint: {e}")
        return jsonify({'error': 'Failed to get assets'}), 500

