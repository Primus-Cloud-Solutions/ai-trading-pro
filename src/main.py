"""
AI Trading SaaS Platform - Main Application
Enterprise-grade trading platform with user management, subscriptions, and AI trading
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import models and services
from database import db
from models.user import User, Subscription, SubscriptionPlan, TradingSettings
from models.trading import Portfolio, Asset, Position, Trade, TradingSignal, MarketData

# Import routes
from routes.auth_routes import auth_bp
from routes.trading_routes import trading_bp
from routes.subscription_routes import subscription_bp

# Import services
from services.ai_trading_engine import ai_trading_engine
from services.auth_service import auth_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_trading_saas.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='static', static_url_path='')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///ai_trading_saas.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # CORS Configuration
    app.config['CORS_ORIGINS'] = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize database migration
    migrate = Migrate(app, db)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(trading_bp)
    app.register_blueprint(subscription_bp)
    
    # Create tables and initialize data
    with app.app_context():
        db.create_all()
        initialize_default_data()
    
    # Initialize AI trading engine
    ai_trading_engine.start_engine()
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token is required'}), 401
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'ai_engine_status': ai_trading_engine.get_engine_status()
        })
    
    # Serve React app
    @app.route('/')
    def serve_react_app():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_react_routes(path):
        if path.startswith('api/'):
            return jsonify({'error': 'API endpoint not found'}), 404
        
        # Check if file exists in static folder
        try:
            return send_from_directory(app.static_folder, path)
        except:
            # Fallback to React app for client-side routing
            return send_from_directory(app.static_folder, 'index.html')
    
    logger.info("🚀 AI Trading SaaS Platform initialized successfully")
    
    return app

def initialize_default_data():
    """Initialize default data for the application"""
    try:
        # Create subscription plans
        plans_data = [
            {
                'name': 'Free Trial',
                'description': '7-day free trial with basic features',
                'price': 0.00,
                'billing_cycle': 'monthly',
                'max_portfolio_value': 1000.00,
                'max_trades_per_day': 5,
                'max_open_positions': 3,
                'features': ['Basic AI signals', 'Portfolio tracking', 'Email support']
            },
            {
                'name': 'Starter',
                'description': 'Perfect for beginners',
                'price': 29.99,
                'billing_cycle': 'monthly',
                'max_portfolio_value': 10000.00,
                'max_trades_per_day': 20,
                'max_open_positions': 10,
                'features': ['Advanced AI signals', 'Real-time data', 'Priority support', 'Mobile app']
            },
            {
                'name': 'Professional',
                'description': 'For serious traders',
                'price': 99.99,
                'billing_cycle': 'monthly',
                'max_portfolio_value': 100000.00,
                'max_trades_per_day': 100,
                'max_open_positions': 50,
                'features': ['Premium AI models', 'Advanced analytics', 'API access', 'Phone support']
            },
            {
                'name': 'Enterprise',
                'description': 'Unlimited trading power',
                'price': 299.99,
                'billing_cycle': 'monthly',
                'max_portfolio_value': 1000000.00,
                'max_trades_per_day': 1000,
                'max_open_positions': 200,
                'features': ['All features', 'Custom strategies', 'Dedicated support', 'White-label option']
            }
        ]
        
        for plan_data in plans_data:
            existing_plan = SubscriptionPlan.query.filter_by(name=plan_data['name']).first()
            if not existing_plan:
                plan = SubscriptionPlan(**plan_data)
                db.session.add(plan)
        
        # Create default assets
        assets_data = [
            # Cryptocurrencies
            {'symbol': 'BTC-USD', 'name': 'Bitcoin', 'asset_type': 'crypto', 'is_tradeable': True},
            {'symbol': 'ETH-USD', 'name': 'Ethereum', 'asset_type': 'crypto', 'is_tradeable': True},
            {'symbol': 'ADA-USD', 'name': 'Cardano', 'asset_type': 'crypto', 'is_tradeable': True},
            {'symbol': 'DOT-USD', 'name': 'Polkadot', 'asset_type': 'crypto', 'is_tradeable': True},
            {'symbol': 'LINK-USD', 'name': 'Chainlink', 'asset_type': 'crypto', 'is_tradeable': True},
            {'symbol': 'DOGE-USD', 'name': 'Dogecoin', 'asset_type': 'crypto', 'is_tradeable': True},
            {'symbol': 'XRP-USD', 'name': 'Ripple', 'asset_type': 'crypto', 'is_tradeable': True},
            {'symbol': 'LTC-USD', 'name': 'Litecoin', 'asset_type': 'crypto', 'is_tradeable': True},
            
            # Stocks
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'asset_type': 'stock', 'is_tradeable': True},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'asset_type': 'stock', 'is_tradeable': True},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'asset_type': 'stock', 'is_tradeable': True},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'asset_type': 'stock', 'is_tradeable': True},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'asset_type': 'stock', 'is_tradeable': True},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'asset_type': 'stock', 'is_tradeable': True},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'asset_type': 'stock', 'is_tradeable': True},
            {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'asset_type': 'stock', 'is_tradeable': True},
            {'symbol': 'AMD', 'name': 'Advanced Micro Devices', 'asset_type': 'stock', 'is_tradeable': True},
            {'symbol': 'PYPL', 'name': 'PayPal Holdings Inc.', 'asset_type': 'stock', 'is_tradeable': True},
            
            # ETFs
            {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF', 'asset_type': 'etf', 'is_tradeable': True},
            {'symbol': 'QQQ', 'name': 'Invesco QQQ Trust', 'asset_type': 'etf', 'is_tradeable': True},
            {'symbol': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'asset_type': 'etf', 'is_tradeable': True},
        ]
        
        for asset_data in assets_data:
            existing_asset = Asset.query.filter_by(symbol=asset_data['symbol']).first()
            if not existing_asset:
                asset = Asset(**asset_data)
                db.session.add(asset)
        
        # Create admin user if not exists
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@aitradingpro.com')
        admin_user = User.query.filter_by(email=admin_email).first()
        
        if not admin_user:
            admin_user = User(
                email=admin_email,
                username='admin',
                first_name='Admin',
                last_name='User',
                is_admin=True,
                is_verified=True,
                is_active=True
            )
            admin_user.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin_user)
            db.session.flush()
            
            # Create admin portfolio
            admin_portfolio = Portfolio(
                user_id=admin_user.id,
                cash_balance=100000.00,  # $100k for testing
                total_value=100000.00
            )
            db.session.add(admin_portfolio)
            
            # Create admin trading settings
            admin_settings = TradingSettings(
                user_id=admin_user.id,
                auto_trading_enabled=True,
                max_position_size=0.20,  # 20% for admin
                daily_loss_limit=0.10,   # 10% daily loss limit
                min_confidence_threshold=0.70  # 70% minimum confidence
            )
            db.session.add(admin_settings)
            
            # Create enterprise subscription for admin
            enterprise_plan = SubscriptionPlan.query.filter_by(name='Enterprise').first()
            if enterprise_plan:
                admin_subscription = Subscription(
                    user_id=admin_user.id,
                    plan_id=enterprise_plan.id,
                    status='active',
                    billing_cycle='monthly',
                    expires_at=datetime.utcnow() + timedelta(days=365)  # 1 year
                )
                db.session.add(admin_subscription)
        
        db.session.commit()
        
        logger.info("✅ Default data initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Error initializing default data: {e}")
        db.session.rollback()

if __name__ == '__main__':
    app = create_app()
    
    # Get configuration from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🌐 Starting AI Trading SaaS Platform on {host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

