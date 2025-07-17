"""
AI Trading Bot Routes
Bot management and automation endpoints
"""

from flask import Blueprint, request, jsonify, session
from services.ai_trading_bot import ai_trading_bot, BotConfig
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot_bp = Blueprint('bot', __name__, url_prefix='/api/bot')

@bot_bp.route('/status', methods=['GET'])
def get_bot_status():
    """
    Get AI trading bot status
    """
    try:
        status = ai_trading_bot.get_bot_status()
        return jsonify({
            'success': True,
            'bot_status': status
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting bot status: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting bot status: {str(e)}'
        }), 500

@bot_bp.route('/start', methods=['POST'])
def start_bot():
    """
    Start the AI trading bot
    """
    try:
        user_id = session.get('user_id', 'demo_user')
        data = request.get_json() or {}
        
        # Create bot configuration
        config = BotConfig(
            enabled=True,
            max_position_size=float(data.get('max_position_size', 1000.0)),
            risk_per_trade=float(data.get('risk_per_trade', 0.02)),
            stop_loss_pct=float(data.get('stop_loss_pct', 0.05)),
            take_profit_pct=float(data.get('take_profit_pct', 0.10)),
            min_confidence=float(data.get('min_confidence', 0.7)),
            symbols=data.get('symbols', ['BTC', 'ETH', 'AAPL', 'TSLA', 'NVDA'])
        )
        
        success = ai_trading_bot.start_bot(user_id, config)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'AI Trading Bot started successfully',
                'bot_status': ai_trading_bot.get_bot_status()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to start AI Trading Bot'
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Error starting bot: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error starting bot: {str(e)}'
        }), 500

@bot_bp.route('/stop', methods=['POST'])
def stop_bot():
    """
    Stop the AI trading bot
    """
    try:
        ai_trading_bot.stop_bot()
        
        return jsonify({
            'success': True,
            'message': 'AI Trading Bot stopped successfully',
            'bot_status': ai_trading_bot.get_bot_status()
        })
        
    except Exception as e:
        logger.error(f"❌ Error stopping bot: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error stopping bot: {str(e)}'
        }), 500

@bot_bp.route('/config', methods=['GET', 'POST'])
def bot_config():
    """
    Get or update bot configuration
    """
    try:
        if request.method == 'GET':
            status = ai_trading_bot.get_bot_status()
            return jsonify({
                'success': True,
                'config': status['config']
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            success = ai_trading_bot.update_config(data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Bot configuration updated successfully',
                    'config': ai_trading_bot.get_bot_status()['config']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to update bot configuration'
                }), 400
                
    except Exception as e:
        logger.error(f"❌ Error with bot config: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error with bot config: {str(e)}'
        }), 500

@bot_bp.route('/signals', methods=['GET'])
def get_signals():
    """
    Get recent AI trading signals
    """
    try:
        limit = int(request.args.get('limit', 20))
        status = ai_trading_bot.get_bot_status()
        
        signals = status['recent_signals'][-limit:] if status['recent_signals'] else []
        
        return jsonify({
            'success': True,
            'signals': signals,
            'count': len(signals)
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting signals: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting signals: {str(e)}'
        }), 500

@bot_bp.route('/performance', methods=['GET'])
def get_performance():
    """
    Get bot performance metrics
    """
    try:
        status = ai_trading_bot.get_bot_status()
        
        return jsonify({
            'success': True,
            'performance': status['performance'],
            'active_positions': status['active_positions']
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting performance: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting performance: {str(e)}'
        }), 500

@bot_bp.route('/positions', methods=['GET'])
def get_active_positions():
    """
    Get active bot positions
    """
    try:
        positions = []
        for symbol, position in ai_trading_bot.active_positions.items():
            positions.append({
                'symbol': symbol,
                'side': position['side'],
                'quantity': position['quantity'],
                'entry_price': position['entry_price'],
                'stop_loss': position['stop_loss'],
                'take_profit': position['take_profit'],
                'timestamp': position['timestamp'].isoformat(),
                'reasoning': position['signal'].reasoning
            })
        
        return jsonify({
            'success': True,
            'positions': positions,
            'count': len(positions)
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting positions: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting positions: {str(e)}'
        }), 500

