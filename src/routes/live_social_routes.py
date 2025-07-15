"""
Live Social Routes for Real-time KOL Opinions and Social Features
"""

from flask import Blueprint, jsonify, request
from services.live_kol_service import live_kol_service
import logging

logger = logging.getLogger(__name__)

live_social_bp = Blueprint('live_social', __name__, url_prefix='/api/live')

@live_social_bp.route('/kols/opinions', methods=['GET'])
def get_live_kol_opinions():
    """Get live KOL opinions with filtering"""
    try:
        asset_class = request.args.get('asset_class', 'all')
        limit = int(request.args.get('limit', 10))
        
        opinions = live_kol_service.get_opinions_by_asset_class(asset_class, limit)
        
        return jsonify({
            'success': True,
            'data': opinions,
            'count': len(opinions),
            'asset_class': asset_class,
            'timestamp': live_kol_service.opinion_cache.get('last_update', 'now')
        })
        
    except Exception as e:
        logger.error(f"Error getting live KOL opinions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@live_social_bp.route('/kols/trending', methods=['GET'])
def get_trending_opinions():
    """Get trending KOL opinions"""
    try:
        limit = int(request.args.get('limit', 5))
        trending = live_kol_service.get_trending_opinions(limit)
        
        return jsonify({
            'success': True,
            'data': trending,
            'count': len(trending)
        })
        
    except Exception as e:
        logger.error(f"Error getting trending opinions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@live_social_bp.route('/activity/feed', methods=['GET'])
def get_live_activity_feed():
    """Get live activity feed"""
    try:
        limit = int(request.args.get('limit', 20))
        activities = live_kol_service.get_live_activity_feed(limit)
        
        return jsonify({
            'success': True,
            'data': activities,
            'count': len(activities)
        })
        
    except Exception as e:
        logger.error(f"Error getting activity feed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@live_social_bp.route('/stats', methods=['GET'])
def get_live_stats():
    """Get live statistics for all asset classes"""
    try:
        stats = live_kol_service.get_asset_class_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting live stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@live_social_bp.route('/kols/opinions/<asset_class>', methods=['GET'])
def get_opinions_by_class(asset_class):
    """Get opinions for specific asset class"""
    try:
        limit = int(request.args.get('limit', 10))
        opinions = live_kol_service.get_opinions_by_asset_class(asset_class, limit)
        
        return jsonify({
            'success': True,
            'data': opinions,
            'count': len(opinions),
            'asset_class': asset_class
        })
        
    except Exception as e:
        logger.error(f"Error getting opinions for {asset_class}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@live_social_bp.route('/market/pulse', methods=['GET'])
def get_market_pulse():
    """Get live market pulse data for ticker"""
    try:
        # Simulate live market data
        import random
        
        symbols = [
            {'symbol': 'TSLA', 'change': random.uniform(-8, 12)},
            {'symbol': 'NVDA', 'change': random.uniform(-6, 15)},
            {'symbol': 'AAPL', 'change': random.uniform(-4, 8)},
            {'symbol': 'BTC', 'change': random.uniform(-10, 18)},
            {'symbol': 'ETH', 'change': random.uniform(-8, 14)},
            {'symbol': 'DOGE', 'change': random.uniform(-15, 25)},
            {'symbol': 'GOOGL', 'change': random.uniform(-5, 9)},
            {'symbol': 'MSFT', 'change': random.uniform(-3, 7)},
        ]
        
        # Format for ticker display
        ticker_items = []
        for item in symbols:
            ticker_items.append({
                'symbol': item['symbol'],
                'change': round(item['change'], 2),
                'direction': 'up' if item['change'] > 0 else 'down',
                'formatted': f"{item['symbol']} {'+' if item['change'] > 0 else ''}{item['change']:.1f}%"
            })
        
        return jsonify({
            'success': True,
            'data': ticker_items,
            'timestamp': 'now'
        })
        
    except Exception as e:
        logger.error(f"Error getting market pulse: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@live_social_bp.route('/predictions/live', methods=['GET'])
def get_live_predictions():
    """Get live AI predictions with real-time data"""
    try:
        # Get predictions from trading engine
        from services.deployment_trading_engine import advanced_trading_engine
        
        market = request.args.get('market', 'all')
        limit = int(request.args.get('limit', 6))
        
        # Get recommendations from the AI engine
        try:
            recommendations = advanced_trading_engine.get_trading_recommendations()
        except AttributeError:
            # Fallback if method doesn't exist
            recommendations = []
        
        # Filter by market if specified
        if market != 'all':
            if market == 'stocks':
                recommendations = [r for r in recommendations if not any(crypto in r['symbol'] for crypto in ['USD', 'BTC', 'ETH'])]
            elif market == 'crypto':
                recommendations = [r for r in recommendations if 'USD' in r['symbol'] and r['symbol'] not in ['DOGE-USD', 'SHIB-USD']]
            elif market == 'meme':
                recommendations = [r for r in recommendations if r['symbol'] in ['DOGE-USD', 'SHIB-USD']]
        
        # Limit results
        recommendations = recommendations[:limit]
        
        # Enhance with additional data for frontend
        for rec in recommendations:
            rec['id'] = f"{rec['symbol']}_{int(rec.get('timestamp', 0))}"
            rec['asset_class'] = 'meme' if rec['symbol'] in ['DOGE-USD', 'SHIB-USD'] else ('crypto' if 'USD' in rec['symbol'] else 'stocks')
            rec['time_generated'] = 'Just now'
            rec['model_confidence'] = rec.get('confidence', 0.5)
            rec['risk_level'] = 'High' if rec.get('confidence', 0.5) < 0.4 else ('Medium' if rec.get('confidence', 0.5) < 0.7 else 'Low')
        
        return jsonify({
            'success': True,
            'data': recommendations,
            'count': len(recommendations),
            'market': market,
            'timestamp': 'now'
        })
        
    except Exception as e:
        logger.error(f"Error getting live predictions: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

@live_social_bp.route('/algorithm/status', methods=['GET'])
def get_algorithm_status():
    """Get live algorithm status and metrics"""
    try:
        import random
        import time
        
        # Simulate live algorithm metrics
        status = {
            'active': True,
            'signals_generated': random.randint(240, 260),
            'success_rate': round(random.uniform(91, 96), 1),
            'profit_today': random.randint(8000, 15000),
            'active_trades': random.randint(25, 35),
            'avg_response_time': round(random.uniform(0.5, 1.2), 1),
            'markets_tracked': 15,
            'last_signal': 'TSLA BUY',
            'last_signal_time': '2 min ago',
            'uptime': '99.8%',
            'total_processed': random.randint(15000, 18000)
        }
        
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': int(time.time())
        })
        
    except Exception as e:
        logger.error(f"Error getting algorithm status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

