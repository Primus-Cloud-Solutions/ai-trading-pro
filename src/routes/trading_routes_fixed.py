"""
Trading Routes - Fixed for Testing (No JWT Required)
Provides comprehensive trading functionality with real-time AI signals
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import logging

from services.deployment_trading_engine import advanced_trading_engine

logger = logging.getLogger(__name__)

trading_bp = Blueprint('trading', __name__, url_prefix='/api/trading')

# Trading Operations
@trading_bp.route('/signals', methods=['GET'])
def get_trading_signals():
    """Get AI-generated trading signals"""
    try:
        # Get live signals from advanced trading engine
        signals = advanced_trading_engine.get_trading_signals()
        
        return jsonify({
            'signals': signals,
            'total_signals': len(signals),
            'engine_status': 'active',
            'strategies_active': ['momentum_trading', 'mean_reversion', 'trend_following', 'crypto_ma_crossover', 'meme_social_momentum'],
            'last_update': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_trading_signals endpoint: {e}")
        return jsonify({'error': 'Failed to get trading signals'}), 500

@trading_bp.route('/market-data', methods=['GET'])
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

@trading_bp.route('/ai-status', methods=['GET'])
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

@trading_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({
        'status': 'API is working',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Trading routes are functional'
    }), 200

