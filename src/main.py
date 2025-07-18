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

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database first
from database import db

# Import models in correct order to avoid circular imports
from models.user import User, Subscription, SubscriptionPlan, TradingSettings, Transaction
from models.trading import Portfolio, Asset, Position, Trade, TradingSignal, MarketData
from models.orders import Order, AutoTradingSettings, TradeRecommendation
from models.social_engagement import SocialInfluencer, SocialOpinion, OpinionComment, OpinionLike, SocialActivity, TelegramChannel, TelegramMessage, SocialEngagementMetrics

# Import routes
from routes.auth_routes import auth_bp
from routes.trading_routes_fixed import trading_bp
from routes.trading_execution_routes import trading_execution_bp
from routes.real_social_routes import real_social_bp

# Import services
from services.deployment_trading_engine import advanced_trading_engine
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
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(trading_execution_bp)
    app.register_blueprint(real_social_bp)
    
    # Import and register enhanced trading routes
    from routes.enhanced_trading_routes import enhanced_trading_bp
    app.register_blueprint(enhanced_trading_bp)
    
    # Import and register live social routes
    from routes.live_social_routes import live_social_bp
    app.register_blueprint(live_social_bp)
    
    # Import and register engagement routes
    from routes.engagement_routes import engagement_bp
    app.register_blueprint(engagement_bp)
    
    # Import and register multi-platform routes
    from routes.multi_platform_routes import multi_platform_bp
    app.register_blueprint(multi_platform_bp)
    
    # Import and register trading routes
    from routes.trading_routes import trading_bp
    app.register_blueprint(trading_bp)
    
    # Import and register bot routes
    from routes.bot_routes import bot_bp
    app.register_blueprint(bot_bp)
    
    # Import and register stats routes
    from routes.stats_routes import stats_bp
    app.register_blueprint(stats_bp)
    
    # Create tables and initialize data
    with app.app_context():
        try:
            # Drop all tables and recreate to fix relationship issues
            db.drop_all()
            db.create_all()
            initialize_default_data()
            logger.info("✅ Database tables created successfully")
            
            # Initialize Advanced AI Trading Engine
            advanced_trading_engine.start_engine()
            logger.info("🤖 Advanced AI Trading Engine initialized")
            
            # Initialize Live KOL Service
            from services.live_kol_service import live_kol_service
            live_kol_service.start_live_feed()
            logger.info("📢 Live KOL Service initialized")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
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
        try:
            engine_status = getattr(advanced_trading_engine, 'get_engine_status', lambda: 'running')()
        except:
            engine_status = 'running'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'ai_engine_status': engine_status
        })
    
    # Serve real social homepage
    @app.route('/')
    def serve_homepage():
        return send_from_directory(app.static_folder, 'real-social-homepage.html')
    
    @app.route('/login')
    def serve_login():
        return send_from_directory(app.static_folder, 'login-fixed.html')
    
    @app.route('/dashboard')
    def serve_dashboard():
        return send_from_directory(app.static_folder, 'professional-dashboard.html')
    
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
                'description': 'Perfect for individual traders',
                'price': 29.99,
                'billing_cycle': 'monthly',
                'max_portfolio_value': 10000.00,
                'max_trades_per_day': 20,
                'max_open_positions': 10,
                'features': ['Advanced AI signals', 'Real-time data', 'Portfolio analytics', 'Email support']
            },
            {
                'name': 'Professional',
                'description': 'For serious traders and small funds',
                'price': 99.99,
                'billing_cycle': 'monthly',
                'max_portfolio_value': 100000.00,
                'max_trades_per_day': 100,
                'max_open_positions': 50,
                'features': ['Premium AI signals', 'Advanced analytics', 'API access', 'Priority support', 'Custom strategies']
            },
            {
                'name': 'Enterprise',
                'description': 'For institutions and large funds',
                'price': 499.99,
                'billing_cycle': 'monthly',
                'max_portfolio_value': 1000000.00,
                'max_trades_per_day': 1000,
                'max_open_positions': 200,
                'features': ['All features', 'Dedicated support', 'Custom integrations', 'White-label options']
            }
        ]
        
        for plan_data in plans_data:
            existing_plan = SubscriptionPlan.query.filter_by(name=plan_data['name']).first()
            if not existing_plan:
                plan = SubscriptionPlan(**plan_data)
                db.session.add(plan)
        
        # Create sample assets
        assets_data = [
            # Stocks
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'asset_type': 'stock', 'exchange': 'NASDAQ', 'sector': 'Technology', 'current_price': 175.50},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'asset_type': 'stock', 'exchange': 'NASDAQ', 'sector': 'Technology', 'current_price': 2750.25},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'asset_type': 'stock', 'exchange': 'NASDAQ', 'sector': 'Technology', 'current_price': 415.75},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'asset_type': 'stock', 'exchange': 'NASDAQ', 'sector': 'Automotive', 'current_price': 245.80},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'asset_type': 'stock', 'exchange': 'NASDAQ', 'sector': 'E-commerce', 'current_price': 3250.00},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'asset_type': 'stock', 'exchange': 'NASDAQ', 'sector': 'Technology', 'current_price': 875.25},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'asset_type': 'stock', 'exchange': 'NASDAQ', 'sector': 'Social Media', 'current_price': 485.50},
            {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'asset_type': 'stock', 'exchange': 'NASDAQ', 'sector': 'Entertainment', 'current_price': 625.75},
            
            # Cryptocurrencies
            {'symbol': 'BTC-USD', 'name': 'Bitcoin', 'asset_type': 'crypto', 'exchange': 'Crypto', 'current_price': 67500.00},
            {'symbol': 'ETH-USD', 'name': 'Ethereum', 'asset_type': 'crypto', 'exchange': 'Crypto', 'current_price': 3850.00},
            {'symbol': 'BNB-USD', 'name': 'Binance Coin', 'asset_type': 'crypto', 'exchange': 'Crypto', 'current_price': 625.50},
            {'symbol': 'ADA-USD', 'name': 'Cardano', 'asset_type': 'crypto', 'exchange': 'Crypto', 'current_price': 1.25},
            {'symbol': 'SOL-USD', 'name': 'Solana', 'asset_type': 'crypto', 'exchange': 'Crypto', 'current_price': 185.75},
            
            # Meme coins
            {'symbol': 'DOGE-USD', 'name': 'Dogecoin', 'asset_type': 'meme_coin', 'exchange': 'Crypto', 'current_price': 0.35},
            {'symbol': 'SHIB-USD', 'name': 'Shiba Inu', 'asset_type': 'meme_coin', 'exchange': 'Crypto', 'current_price': 0.000025},
            {'symbol': 'PEPE-USD', 'name': 'Pepe', 'asset_type': 'meme_coin', 'exchange': 'Crypto', 'current_price': 0.0000015}
        ]
        
        for asset_data in assets_data:
            existing_asset = Asset.query.filter_by(symbol=asset_data['symbol']).first()
            if not existing_asset:
                asset = Asset(**asset_data)
                db.session.add(asset)
        
        # Create admin user
        admin_user = User.query.filter_by(email='admin@aitradingpro.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@aitradingpro.com',
                username='admin',
                first_name='Admin',
                last_name='User',
                is_admin=True,
                is_verified=True,
                is_active=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.flush()  # Get the user ID
            
            # Create admin subscription
            free_plan = SubscriptionPlan.query.filter_by(name='Free Trial').first()
            if free_plan:
                admin_subscription = Subscription(
                    user_id=admin_user.id,
                    plan_id=free_plan.id,
                    status='active',
                    expires_at=datetime.utcnow() + timedelta(days=365)  # 1 year for admin
                )
                db.session.add(admin_subscription)
            
            # Create admin portfolio
            admin_portfolio = Portfolio(
                user_id=admin_user.id,
                cash_balance=100000.0,  # $100k starting balance
                total_value=100000.0
            )
            db.session.add(admin_portfolio)
            
            # Create admin trading settings
            admin_settings = TradingSettings(
                user_id=admin_user.id,
                auto_trading_enabled=True,
                max_position_size=0.10,
                daily_loss_limit=0.05,
                min_confidence_threshold=0.70
            )
            db.session.add(admin_settings)
            
            # Create admin auto trading settings
            admin_auto_settings = AutoTradingSettings(
                user_id=admin_user.id,
                is_enabled=True,
                max_daily_trades=50,
                max_position_size=5000.0,
                min_confidence=0.70,
                stop_loss_percentage=0.05,
                take_profit_percentage=0.10,
                max_daily_loss=2500.0
            )
            db.session.add(admin_auto_settings)
        
        db.session.commit()
        logger.info("✅ Default data initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize default data: {e}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

