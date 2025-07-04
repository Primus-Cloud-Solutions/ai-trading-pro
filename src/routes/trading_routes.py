"""
Trading API Routes for AI Trading SaaS Platform
Portfolio management, trading operations, market data, and AI trading
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import logging

from services.auth_service import auth_service
from services.ai_trading_engine import ai_trading_engine
from models.user import User
from models.trading import Portfolio, Position, Trade, Asset, TradingSignal, MarketData
from database import db

logger = logging.getLogger(__name__)

trading_bp = Blueprint('trading', __name__, url_prefix='/api/trading')

# Portfolio Management
@trading_bp.route('/portfolio', methods=['GET'])
@jwt_required()
def get_portfolio():
    """Get user portfolio"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        portfolio = user.portfolio
        
        # Get positions
        positions = Position.query.filter_by(
            portfolio_id=portfolio.id,
            is_open=True
        ).all()
        
        # Get recent trades
        recent_trades = Trade.query.filter_by(
            portfolio_id=portfolio.id
        ).order_by(Trade.executed_at.desc()).limit(10).all()
        
        # Calculate portfolio metrics
        portfolio.calculate_portfolio_value()
        
        return jsonify({
            'portfolio': portfolio.to_dict(),
            'positions': [pos.to_dict() for pos in positions],
            'recent_trades': [trade.to_dict() for trade in recent_trades],
            'performance': {
                'total_return': portfolio.total_return,
                'total_return_percent': portfolio.total_return_percent,
                'daily_pnl': portfolio.daily_pnl,
                'daily_pnl_percent': portfolio.daily_pnl_percent
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_portfolio endpoint: {e}")
        return jsonify({'error': 'Failed to get portfolio'}), 500

@trading_bp.route('/portfolio/fund', methods=['POST'])
@jwt_required()
def fund_portfolio():
    """Add funds to portfolio"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        data = request.get_json()
        if not data or 'amount' not in data:
            return jsonify({'error': 'Amount is required'}), 400
        
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        # Check subscription limits
        if not user.subscription or not user.subscription.can_fund_account():
            return jsonify({'error': 'Subscription does not allow funding'}), 403
        
        # Add funds to portfolio
        portfolio = user.portfolio
        portfolio.add_funds(amount)
        
        # Record funding transaction
        # TODO: Integrate with payment processor
        
        db.session.commit()
        
        logger.info(f"✅ Portfolio funded: ${amount} for user {user.email}")
        
        return jsonify({
            'message': f'Successfully added ${amount:,.2f} to your portfolio',
            'portfolio': portfolio.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in fund_portfolio endpoint: {e}")
        return jsonify({'error': 'Failed to fund portfolio'}), 500

@trading_bp.route('/portfolio/withdraw', methods=['POST'])
@jwt_required()
def withdraw_funds():
    """Withdraw funds from portfolio"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        data = request.get_json()
        if not data or 'amount' not in data:
            return jsonify({'error': 'Amount is required'}), 400
        
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        portfolio = user.portfolio
        
        if amount > portfolio.cash_balance:
            return jsonify({'error': 'Insufficient cash balance'}), 400
        
        # Withdraw funds
        portfolio.withdraw_funds(amount)
        
        # Record withdrawal transaction
        # TODO: Integrate with payment processor
        
        db.session.commit()
        
        logger.info(f"✅ Funds withdrawn: ${amount} for user {user.email}")
        
        return jsonify({
            'message': f'Successfully withdrew ${amount:,.2f} from your portfolio',
            'portfolio': portfolio.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in withdraw_funds endpoint: {e}")
        return jsonify({'error': 'Failed to withdraw funds'}), 500

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
        
        # Get recent signals
        signals = TradingSignal.query.filter(
            TradingSignal.created_at >= datetime.utcnow() - timedelta(days=7),
            TradingSignal.confidence >= user.trading_settings.min_confidence_threshold
        ).order_by(TradingSignal.created_at.desc()).limit(20).all()
        
        return jsonify({
            'signals': [signal.to_dict() for signal in signals],
            'total_signals': len(signals)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_trading_signals endpoint: {e}")
        return jsonify({'error': 'Failed to get trading signals'}), 500

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
        required_fields = ['asset_symbol', 'trade_type', 'amount']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Asset symbol, trade type, and amount are required'}), 400
        
        # Check if manual trading is allowed
        if not user.subscription.can_trade_manually():
            return jsonify({'error': 'Manual trading not allowed on current plan'}), 403
        
        asset_symbol = data['asset_symbol']
        trade_type = data['trade_type'].upper()
        amount = float(data['amount'])
        
        if trade_type not in ['BUY', 'SELL']:
            return jsonify({'error': 'Trade type must be BUY or SELL'}), 400
        
        # Find asset
        asset = Asset.query.filter_by(symbol=asset_symbol, is_active=True).first()
        if not asset:
            return jsonify({'error': 'Asset not found or not tradeable'}), 404
        
        # Execute trade logic here
        # TODO: Implement manual trade execution
        
        return jsonify({
            'message': f'Manual {trade_type} order for {asset_symbol} submitted',
            'trade_id': 'manual_trade_123'  # Placeholder
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in execute_manual_trade endpoint: {e}")
        return jsonify({'error': 'Failed to execute trade'}), 500

@trading_bp.route('/positions', methods=['GET'])
@jwt_required()
def get_positions():
    """Get user positions"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Get positions
        open_positions = Position.query.filter_by(
            portfolio_id=user.portfolio.id,
            is_open=True
        ).all()
        
        closed_positions = Position.query.filter_by(
            portfolio_id=user.portfolio.id,
            is_open=False
        ).order_by(Position.closed_at.desc()).limit(20).all()
        
        return jsonify({
            'open_positions': [pos.to_dict() for pos in open_positions],
            'closed_positions': [pos.to_dict() for pos in closed_positions],
            'total_open': len(open_positions),
            'total_closed': len(closed_positions)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_positions endpoint: {e}")
        return jsonify({'error': 'Failed to get positions'}), 500

@trading_bp.route('/trades', methods=['GET'])
@jwt_required()
def get_trades():
    """Get user trade history"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Get trades
        trades_query = Trade.query.filter_by(
            portfolio_id=user.portfolio.id
        ).order_by(Trade.executed_at.desc())
        
        trades_paginated = trades_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'trades': [trade.to_dict() for trade in trades_paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': trades_paginated.total,
                'pages': trades_paginated.pages,
                'has_next': trades_paginated.has_next,
                'has_prev': trades_paginated.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_trades endpoint: {e}")
        return jsonify({'error': 'Failed to get trades'}), 500

# Market Data
@trading_bp.route('/assets', methods=['GET'])
@jwt_required()
def get_assets():
    """Get available trading assets"""
    try:
        # Get query parameters
        asset_type = request.args.get('type')  # stock, crypto, forex, commodity
        search = request.args.get('search')
        limit = min(request.args.get('limit', 50, type=int), 200)
        
        # Build query
        query = Asset.query.filter_by(is_active=True, is_tradeable=True)
        
        if asset_type:
            query = query.filter_by(asset_type=asset_type)
        
        if search:
            query = query.filter(
                Asset.symbol.ilike(f'%{search}%') |
                Asset.name.ilike(f'%{search}%')
            )
        
        assets = query.limit(limit).all()
        
        return jsonify({
            'assets': [asset.to_dict() for asset in assets],
            'total': len(assets)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_assets endpoint: {e}")
        return jsonify({'error': 'Failed to get assets'}), 500

@trading_bp.route('/market-data/<symbol>', methods=['GET'])
@jwt_required()
def get_market_data(symbol):
    """Get market data for specific asset"""
    try:
        asset = Asset.query.filter_by(symbol=symbol.upper(), is_active=True).first()
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404
        
        # Get time range
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get market data
        market_data = MarketData.query.filter(
            MarketData.asset_id == asset.id,
            MarketData.timestamp >= start_date,
            MarketData.timestamp <= end_date
        ).order_by(MarketData.timestamp.asc()).all()
        
        return jsonify({
            'asset': asset.to_dict(),
            'market_data': [data.to_dict() for data in market_data],
            'total_points': len(market_data)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_market_data endpoint: {e}")
        return jsonify({'error': 'Failed to get market data'}), 500

# AI Trading Engine
@trading_bp.route('/ai-engine/status', methods=['GET'])
@jwt_required()
def get_ai_engine_status():
    """Get AI trading engine status"""
    try:
        status = ai_trading_engine.get_engine_status()
        return jsonify({'engine_status': status}), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_ai_engine_status endpoint: {e}")
        return jsonify({'error': 'Failed to get engine status'}), 500

@trading_bp.route('/ai-engine/start', methods=['POST'])
@jwt_required()
def start_ai_engine():
    """Start AI trading engine (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        ai_trading_engine.start_engine()
        
        return jsonify({'message': 'AI trading engine started successfully'}), 200
        
    except Exception as e:
        logger.error(f"❌ Error in start_ai_engine endpoint: {e}")
        return jsonify({'error': 'Failed to start AI engine'}), 500

@trading_bp.route('/ai-engine/stop', methods=['POST'])
@jwt_required()
def stop_ai_engine():
    """Stop AI trading engine (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        ai_trading_engine.stop_engine()
        
        return jsonify({'message': 'AI trading engine stopped successfully'}), 200
        
    except Exception as e:
        logger.error(f"❌ Error in stop_ai_engine endpoint: {e}")
        return jsonify({'error': 'Failed to stop AI engine'}), 500

# Analytics
@trading_bp.route('/analytics/performance', methods=['GET'])
@jwt_required()
def get_performance_analytics():
    """Get portfolio performance analytics"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        portfolio = user.portfolio
        
        # Get time range
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get trades in time range
        trades = Trade.query.filter(
            Trade.portfolio_id == portfolio.id,
            Trade.executed_at >= start_date,
            Trade.executed_at <= end_date,
            Trade.status == 'executed'
        ).all()
        
        # Calculate analytics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if (t.pnl or 0) > 0])
        losing_trades = len([t for t in trades if (t.pnl or 0) < 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_pnl = sum(t.pnl or 0 for t in trades)
        
        return jsonify({
            'analytics': {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 2),
                'total_pnl': round(total_pnl, 2),
                'average_trade': round(total_pnl / total_trades, 2) if total_trades > 0 else 0,
                'portfolio_value': portfolio.total_value,
                'cash_balance': portfolio.cash_balance,
                'invested_value': portfolio.invested_value
            },
            'period': f'{days} days'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_performance_analytics endpoint: {e}")
        return jsonify({'error': 'Failed to get performance analytics'}), 500

# Error handlers
@trading_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@trading_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@trading_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

@trading_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@trading_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

