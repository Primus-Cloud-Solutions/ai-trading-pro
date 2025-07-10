"""
Trading Execution Routes
Handles trade execution, recommendations, and automated trading
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from services.trade_execution_service import trade_execution_service
from services.auth_service import auth_service

logger = logging.getLogger(__name__)

trading_execution_bp = Blueprint('trading_execution', __name__, url_prefix='/api/trading')

@trading_execution_bp.route('/execute-order', methods=['POST'])
def execute_order():
    """Execute a buy/sell order"""
    try:
        data = request.get_json()
        
        # For demo purposes, use a default user ID (in production, get from JWT)
        user_id = data.get('user_id', 1)  # Default to admin user
        
        required_fields = ['symbol', 'side', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        result = trade_execution_service.execute_market_order(
            user_id=user_id,
            symbol=data['symbol'],
            side=data['side'],
            quantity=float(data['quantity']),
            ai_signal_id=data.get('ai_signal_id'),
            confidence=data.get('confidence'),
            strategy=data.get('strategy'),
            is_automated=data.get('is_automated', False)
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in execute_order endpoint: {e}")
        return jsonify({'error': 'Failed to execute order'}), 500

@trading_execution_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get AI-generated trade recommendations"""
    try:
        # For demo purposes, use a default user ID
        user_id = request.args.get('user_id', 1, type=int)
        
        recommendations = trade_execution_service.get_trade_recommendations(user_id)
        
        return jsonify({
            'recommendations': recommendations,
            'total_recommendations': len(recommendations),
            'last_update': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_recommendations endpoint: {e}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

@trading_execution_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get user's order history"""
    try:
        # For demo purposes, use a default user ID
        user_id = request.args.get('user_id', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        orders = trade_execution_service.get_user_orders(user_id, limit)
        
        return jsonify({
            'orders': orders,
            'total_orders': len(orders)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_orders endpoint: {e}")
        return jsonify({'error': 'Failed to get orders'}), 500

@trading_execution_bp.route('/auto-trading/settings', methods=['GET'])
def get_auto_trading_settings():
    """Get automated trading settings"""
    try:
        # For demo purposes, use a default user ID
        user_id = request.args.get('user_id', 1, type=int)
        
        settings = trade_execution_service.get_auto_trading_settings(user_id)
        
        return jsonify({
            'settings': settings,
            'status': 'success'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_auto_trading_settings endpoint: {e}")
        return jsonify({'error': 'Failed to get auto trading settings'}), 500

@trading_execution_bp.route('/auto-trading/settings', methods=['POST'])
def update_auto_trading_settings():
    """Update automated trading settings"""
    try:
        data = request.get_json()
        
        # For demo purposes, use a default user ID
        user_id = data.get('user_id', 1)
        
        result = trade_execution_service.update_auto_trading_settings(user_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in update_auto_trading_settings endpoint: {e}")
        return jsonify({'error': 'Failed to update auto trading settings'}), 500

@trading_execution_bp.route('/auto-trading/execute', methods=['POST'])
def execute_automated_trades():
    """Execute automated trades based on AI signals"""
    try:
        data = request.get_json()
        
        # For demo purposes, use a default user ID
        user_id = data.get('user_id', 1)
        
        result = trade_execution_service.execute_automated_trades(user_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"❌ Error in execute_automated_trades endpoint: {e}")
        return jsonify({'error': 'Failed to execute automated trades'}), 500

@trading_execution_bp.route('/auto-trading/toggle', methods=['POST'])
def toggle_auto_trading():
    """Toggle automated trading on/off"""
    try:
        data = request.get_json()
        
        # For demo purposes, use a default user ID
        user_id = data.get('user_id', 1)
        enabled = data.get('enabled', False)
        
        result = trade_execution_service.update_auto_trading_settings(
            user_id, 
            {'is_enabled': enabled}
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f"Automated trading {'enabled' if enabled else 'disabled'}",
                'is_enabled': enabled
            }), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in toggle_auto_trading endpoint: {e}")
        return jsonify({'error': 'Failed to toggle auto trading'}), 500

@trading_execution_bp.route('/quick-buy', methods=['POST'])
def quick_buy():
    """Quick buy based on AI recommendation"""
    try:
        data = request.get_json()
        
        # For demo purposes, use a default user ID
        user_id = data.get('user_id', 1)
        symbol = data.get('symbol')
        amount = data.get('amount', 100.0)  # Default $100
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        # Get current price to calculate quantity
        from services.deployment_trading_engine import advanced_trading_engine
        market_data = advanced_trading_engine.get_market_data()
        
        current_price = None
        for asset in market_data:
            if asset['symbol'] == symbol:
                current_price = asset['current_price']
                break
        
        if not current_price:
            return jsonify({'error': 'Market data not available'}), 400
        
        quantity = amount / current_price
        
        result = trade_execution_service.execute_market_order(
            user_id=user_id,
            symbol=symbol,
            side='buy',
            quantity=quantity,
            strategy='quick_buy'
        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"❌ Error in quick_buy endpoint: {e}")
        return jsonify({'error': 'Failed to execute quick buy'}), 500

@trading_execution_bp.route('/quick-sell', methods=['POST'])
def quick_sell():
    """Quick sell position"""
    try:
        data = request.get_json()
        
        # For demo purposes, use a default user ID
        user_id = data.get('user_id', 1)
        symbol = data.get('symbol')
        percentage = data.get('percentage', 100)  # Default sell all
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        # Get current position
        from models.trading import Position
        from models.user import User
        
        user = User.query.get(user_id)
        if not user or not user.portfolio:
            return jsonify({'error': 'User or portfolio not found'}), 404
        
        position = Position.query.filter_by(
            portfolio_id=user.portfolio.id,
            symbol=symbol,
            is_active=True
        ).first()
        
        if not position:
            return jsonify({'error': 'No position found'}), 404
        
        quantity = position.quantity * (percentage / 100)
        
        result = trade_execution_service.execute_market_order(
            user_id=user_id,
            symbol=symbol,
            side='sell',
            quantity=quantity,
            strategy='quick_sell'
        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"❌ Error in quick_sell endpoint: {e}")
        return jsonify({'error': 'Failed to execute quick sell'}), 500

