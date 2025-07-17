"""
Trading Routes - FIXED VERSION
Real broker integration endpoints with proper error handling
"""

from flask import Blueprint, request, jsonify, session
from services.real_trading_engine_fixed import real_trading_engine, TradeOrder
from services.real_trading_engine_methods import TradingEngineAnalytics, TradingEngineRiskManagement
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

trading_bp = Blueprint('trading', __name__, url_prefix='/api/trading')

# Initialize analytics and risk management
analytics = TradingEngineAnalytics(real_trading_engine)
risk_manager = TradingEngineRiskManagement(real_trading_engine)

@trading_bp.route('/connect', methods=['POST'])
def connect():
    """
    Connect a trading account (simplified endpoint)
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id', 'demo_user')
        
        broker = data.get('broker', 'demo')
        credentials = data.get('credentials', {})
        
        # For demo account, always succeed
        if broker == 'demo':
            success = real_trading_engine.add_account(user_id, 'demo', {})
            if success:
                account_info = real_trading_engine.get_account_info(user_id)
                return jsonify({
                    'success': True,
                    'message': 'Demo account connected successfully',
                    'account': account_info
                })
        
        # For other brokers, use provided credentials
        success = real_trading_engine.add_account(user_id, broker, credentials)
        
        if success:
            account_info = real_trading_engine.get_account_info(user_id)
            return jsonify({
                'success': True,
                'message': f'{broker.title()} account connected successfully',
                'account': account_info
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to connect {broker.title()} account'
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Error connecting account: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error connecting account: {str(e)}'
        }), 500

@trading_bp.route('/connect-account', methods=['POST'])
def connect_account():
    """
    Connect a trading account
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id', 'demo_user')
        
        broker = data.get('broker', '').lower()
        credentials = {
            'api_key': data.get('api_key', ''),
            'api_secret': data.get('api_secret', ''),
            'account_id': data.get('account_id', user_id)
        }
        
        # Validate required fields
        if not broker:
            return jsonify({
                'success': False,
                'message': 'Broker is required'
            }), 400
        
        # Add account to trading engine
        success = real_trading_engine.add_account(user_id, broker, credentials)
        
        if success:
            account_info = real_trading_engine.get_account_info(user_id)
            return jsonify({
                'success': True,
                'message': f'{broker.title()} account connected successfully',
                'account': account_info
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to connect {broker.title()} account'
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Error connecting account: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error connecting account: {str(e)}'
        }), 500

@trading_bp.route('/account-info', methods=['GET'])
def get_account_info():
    """
    Get trading account information
    """
    try:
        user_id = session.get('user_id', 'demo_user')
        account_info = real_trading_engine.get_account_info(user_id)
        
        return jsonify({
            'success': True,
            'account': account_info
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting account info: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting account info: {str(e)}'
        }), 500

@trading_bp.route('/execute-trade', methods=['POST'])
def execute_trade():
    """
    Execute a trade order
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id', 'demo_user')
        
        # Validate required fields
        required_fields = ['symbol', 'side', 'quantity', 'order_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create trade order
        order = TradeOrder(
            symbol=data['symbol'],
            side=data['side'].lower(),
            quantity=float(data['quantity']),
            order_type=data['order_type'].lower(),
            price=float(data.get('price', 0)) if data.get('price') else None,
            stop_loss=float(data.get('stop_loss', 0)) if data.get('stop_loss') else None,
            take_profit=float(data.get('take_profit', 0)) if data.get('take_profit') else None
        )
        
        # Execute trade
        result = real_trading_engine.execute_trade(user_id, order)
        
        if result.success:
            return jsonify({
                'success': True,
                'message': result.message,
                'order_id': result.order_id,
                'executed_price': result.executed_price,
                'executed_quantity': result.executed_quantity,
                'fees': result.fees
            })
        else:
            return jsonify({
                'success': False,
                'message': result.message
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Error executing trade: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error executing trade: {str(e)}'
        }), 500

@trading_bp.route('/trade-history', methods=['GET'])
def get_trade_history():
    """
    Get trade history
    """
    try:
        user_id = session.get('user_id', 'demo_user')
        limit = int(request.args.get('limit', 50))
        
        trades = real_trading_engine.get_trade_history(user_id, limit)
        
        return jsonify({
            'success': True,
            'trades': trades,
            'count': len(trades)
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting trade history: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting trade history: {str(e)}'
        }), 500

@trading_bp.route('/supported-brokers', methods=['GET'])
def get_supported_brokers():
    """
    Get list of supported brokers
    """
    try:
        brokers = [
            {
                'id': 'demo',
                'name': 'Demo Account',
                'description': 'Paper trading for testing',
                'features': ['Stocks', 'Crypto', 'No real money'],
                'setup_required': False
            },
            {
                'id': 'coinbase',
                'name': 'Coinbase Advanced Trade',
                'description': 'Leading cryptocurrency exchange',
                'features': ['Crypto trading', 'Advanced API', 'High liquidity'],
                'setup_required': True
            },
            {
                'id': 'binance',
                'name': 'Binance',
                'description': 'Global cryptocurrency exchange',
                'features': ['Spot trading', 'Futures', 'Options', '300+ assets'],
                'setup_required': True
            },
            {
                'id': 'alpaca',
                'name': 'Alpaca',
                'description': 'Commission-free stock trading',
                'features': ['US stocks', 'ETFs', 'Paper trading', 'API-first'],
                'setup_required': True
            }
        ]
        
        return jsonify({
            'success': True,
            'brokers': brokers
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting supported brokers: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting supported brokers: {str(e)}'
        }), 500

@trading_bp.route('/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol):
    """
    Get real-time market data for a symbol
    """
    try:
        # Demo market data
        market_data = {
            'BTC': {'price': 42000.0, 'change': 2.5, 'volume': 1234567},
            'ETH': {'price': 2600.0, 'change': -1.2, 'volume': 987654},
            'AAPL': {'price': 185.0, 'change': 0.8, 'volume': 45678901},
            'TSLA': {'price': 247.0, 'change': -3.1, 'volume': 23456789},
            'NVDA': {'price': 890.0, 'change': 4.2, 'volume': 12345678}
        }
        
        symbol = symbol.upper().replace('/USD', '').replace('USD', '')
        
        if symbol in market_data:
            data = market_data[symbol]
            return jsonify({
                'success': True,
                'symbol': symbol,
                'price': data['price'],
                'change_percent': data['change'],
                'volume': data['volume'],
                'timestamp': int(time.time())
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Market data not available for {symbol}'
            }), 404
            
    except Exception as e:
        logger.error(f"❌ Error getting market data: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting market data: {str(e)}'
        }), 500

@trading_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """
    Get user's portfolio
    """
    try:
        user_id = session.get('user_id', 'demo_user')
        account_info = real_trading_engine.get_account_info(user_id)
        
        if 'error' in account_info:
            return jsonify({
                'success': False,
                'message': account_info['error']
            }), 400
        
        # Calculate portfolio value
        positions = account_info.get('positions', {})
        market_prices = {
            'BTC': 42000.0,
            'ETH': 2600.0,
            'AAPL': 185.0,
            'TSLA': 247.0,
            'NVDA': 890.0
        }
        
        portfolio_value = account_info.get('balance', 0)
        position_details = []
        
        for symbol, quantity in positions.items():
            if symbol in market_prices:
                current_price = market_prices[symbol]
                market_value = quantity * current_price
                portfolio_value += market_value
                
                position_details.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'current_price': current_price,
                    'market_value': market_value
                })
        
        return jsonify({
            'success': True,
            'portfolio': {
                'total_value': portfolio_value,
                'cash_balance': account_info.get('balance', 0),
                'buying_power': account_info.get('buying_power', 0),
                'positions': position_details,
                'broker': account_info.get('broker', 'demo')
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting portfolio: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting portfolio: {str(e)}'
        }), 500


@trading_bp.route('/trade', methods=['POST'])
def place_trade():
    """
    Place a trade order (simplified endpoint)
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id', 'demo_user')
        
        # Validate required fields
        symbol = data.get('symbol', '').upper()
        side = data.get('side', '').lower()
        quantity = float(data.get('quantity', 0))
        order_type = data.get('order_type', 'market').lower()
        
        if not symbol or not side or quantity <= 0:
            return jsonify({
                'success': False,
                'message': 'Invalid trade parameters'
            }), 400
        
        # Create trade order
        order = TradeOrder(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=float(data.get('price', 0)) if data.get('price') else None
        )
        
        # Execute trade
        result = real_trading_engine.execute_trade(user_id, order)
        
        if result.success:
            return jsonify({
                'success': True,
                'message': result.message,
                'order_id': result.order_id,
                'executed_price': result.executed_price,
                'executed_quantity': result.executed_quantity,
                'fees': result.fees,
                'timestamp': time.time()
            })
        else:
            return jsonify({
                'success': False,
                'message': result.message
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Error placing trade: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error placing trade: {str(e)}'
        }), 500

@trading_bp.route('/status', methods=['GET'])
def get_status():
    """
    Get trading system status
    """
    try:
        user_id = session.get('user_id', 'demo_user')
        account_info = real_trading_engine.get_account_info(user_id)
        
        return jsonify({
            'success': True,
            'connected': account_info is not None,
            'broker': account_info.get('broker', 'none') if account_info else 'none',
            'balance': account_info.get('balance', 0) if account_info else 0,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting status: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting status: {str(e)}'
        }), 500



@trading_bp.route('/analytics/performance', methods=['GET'])
def get_performance_analytics():
    """Get portfolio performance analytics"""
    try:
        user_id = session.get('user_id', 'demo_user')
        days = int(request.args.get('days', 30))
        
        performance = analytics.get_portfolio_performance(user_id, days)
        
        return jsonify({
            'success': True,
            'performance': performance
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting performance analytics: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting performance analytics: {str(e)}'
        }), 500

@trading_bp.route('/analytics/positions', methods=['GET'])
def get_position_analytics():
    """Get detailed position analytics"""
    try:
        user_id = session.get('user_id', 'demo_user')
        
        positions = analytics.get_position_summary(user_id)
        
        return jsonify({
            'success': True,
            'positions': positions
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting position analytics: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting position analytics: {str(e)}'
        }), 500

@trading_bp.route('/analytics/statistics', methods=['GET'])
def get_trading_statistics():
    """Get comprehensive trading statistics"""
    try:
        user_id = session.get('user_id', 'demo_user')
        
        statistics = analytics.get_trading_statistics(user_id)
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting trading statistics: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting trading statistics: {str(e)}'
        }), 500

@trading_bp.route('/risk/check', methods=['POST'])
def check_trade_risk():
    """Check risk for a proposed trade"""
    try:
        data = request.get_json()
        user_id = session.get('user_id', 'demo_user')
        
        symbol = data.get('symbol', '').upper()
        quantity = float(data.get('quantity', 0))
        side = data.get('side', '').lower()
        
        risk_check = risk_manager.check_position_limits(user_id, symbol, quantity, side)
        
        return jsonify({
            'success': True,
            'risk_check': risk_check
        })
        
    except Exception as e:
        logger.error(f"❌ Error checking trade risk: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error checking trade risk: {str(e)}'
        }), 500

@trading_bp.route('/risk/metrics', methods=['GET'])
def get_risk_metrics():
    """Get portfolio risk metrics"""
    try:
        user_id = session.get('user_id', 'demo_user')
        
        risk_metrics = risk_manager.calculate_risk_metrics(user_id)
        
        return jsonify({
            'success': True,
            'risk_metrics': risk_metrics
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting risk metrics: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting risk metrics: {str(e)}'
        }), 500

@trading_bp.route('/market/prices', methods=['GET'])
def get_market_prices():
    """Get current market prices for all supported symbols"""
    try:
        symbols = real_trading_engine.get_supported_symbols()
        prices = {}
        
        for symbol in symbols:
            prices[symbol] = real_trading_engine.get_market_price(symbol)
        
        return jsonify({
            'success': True,
            'prices': prices,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting market prices: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting market prices: {str(e)}'
        }), 500

@trading_bp.route('/orders/history', methods=['GET'])
def get_order_history():
    """Get detailed order history with analytics"""
    try:
        user_id = session.get('user_id', 'demo_user')
        limit = int(request.args.get('limit', 50))
        
        trades = real_trading_engine.get_trade_history(user_id, limit)
        
        # Add additional analytics to each trade
        for trade in trades:
            symbol = trade['symbol']
            current_price = real_trading_engine.get_market_price(symbol)
            
            if trade['side'] == 'buy':
                # Calculate unrealized P&L for buy orders
                trade['current_price'] = current_price
                trade['unrealized_pnl'] = (current_price - trade['executed_price']) * trade['executed_quantity']
                trade['unrealized_pnl_percentage'] = ((current_price - trade['executed_price']) / trade['executed_price']) * 100
        
        return jsonify({
            'success': True,
            'trades': trades,
            'total_trades': len(trades)
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting order history: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting order history: {str(e)}'
        }), 500

