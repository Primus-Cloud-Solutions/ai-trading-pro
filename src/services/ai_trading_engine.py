"""
Advanced AI Trading Engine for SaaS Platform
Intelligent trading decisions, market analysis, and automated execution
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import threading
import time
import schedule

from database import db
from models.trading import Asset, Portfolio, Position, Trade, TradingSignal, MarketData
from models.user import User, TradingSettings

logger = logging.getLogger(__name__)

class AITradingEngine:
    """Advanced AI Trading Engine with intelligent decision making"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.is_running = False
        self.trading_thread = None
        self.market_data_thread = None
        
        # Trading parameters
        self.min_confidence_threshold = 0.75
        self.max_position_size = 0.10  # 10% of portfolio
        self.stop_loss_percent = 0.05  # 5% stop loss
        self.take_profit_percent = 0.15  # 15% take profit
        
        # Market analysis parameters
        self.lookback_days = 30
        self.prediction_horizon = 24  # hours
        
        logger.info("🤖 AI Trading Engine initialized")
    
    def start_engine(self):
        """Start the AI trading engine"""
        if self.is_running:
            logger.warning("Trading engine is already running")
            return
        
        self.is_running = True
        
        # Schedule trading sessions
        schedule.every().day.at("09:30").do(self._daily_trading_session)
        schedule.every().hour.do(self._hourly_market_analysis)
        schedule.every(15).minutes.do(self._update_market_data)
        
        # Start background threads
        self.trading_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.trading_thread.start()
        
        logger.info("🚀 AI Trading Engine started successfully")
    
    def stop_engine(self):
        """Stop the AI trading engine"""
        self.is_running = False
        schedule.clear()
        logger.info("⏹️ AI Trading Engine stopped")
    
    def _run_scheduler(self):
        """Run the scheduler in background thread"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _daily_trading_session(self):
        """Execute daily trading session for all users"""
        logger.info("📈 Starting daily trading session...")
        
        try:
            # Get all users with active subscriptions and auto-trading enabled
            users = User.query.join(User.subscription).filter(
                User.is_active == True,
                User.is_verified == True
            ).all()
            
            for user in users:
                if user.can_trade() and user.trading_settings.auto_trading_enabled:
                    self._execute_user_trading_session(user)
            
            logger.info("✅ Daily trading session completed")
            
        except Exception as e:
            logger.error(f"❌ Error in daily trading session: {e}")
    
    def _execute_user_trading_session(self, user: User):
        """Execute trading session for a specific user"""
        try:
            logger.info(f"🎯 Executing trading session for user {user.username}")
            
            portfolio = user.portfolio
            settings = user.trading_settings
            
            if not portfolio or not settings:
                logger.warning(f"Missing portfolio or settings for user {user.username}")
                return
            
            # Check daily loss limit
            if self._check_daily_loss_limit(portfolio, settings):
                logger.warning(f"Daily loss limit reached for user {user.username}")
                return
            
            # Get market opportunities
            opportunities = self._find_trading_opportunities(settings)
            
            # Execute trades based on opportunities
            for opportunity in opportunities[:5]:  # Limit to top 5 opportunities
                if self._should_execute_trade(opportunity, portfolio, settings):
                    self._execute_trade(opportunity, portfolio, user)
            
            # Manage existing positions
            self._manage_existing_positions(portfolio, settings)
            
            # Update portfolio metrics
            portfolio.calculate_portfolio_value()
            portfolio.update_trade_statistics()
            
            db.session.commit()
            
            logger.info(f"✅ Trading session completed for user {user.username}")
            
        except Exception as e:
            logger.error(f"❌ Error in trading session for user {user.username}: {e}")
            db.session.rollback()
    
    def _find_trading_opportunities(self, settings: TradingSettings) -> List[Dict]:
        """Find the best trading opportunities using AI analysis"""
        opportunities = []
        
        try:
            # Get tradeable assets based on user preferences
            asset_types = []
            if settings.trade_stocks:
                asset_types.append('stock')
            if settings.trade_crypto:
                asset_types.append('crypto')
            if settings.trade_forex:
                asset_types.append('forex')
            if settings.trade_commodities:
                asset_types.append('commodity')
            
            assets = Asset.query.filter(
                Asset.is_tradeable == True,
                Asset.is_active == True,
                Asset.asset_type.in_(asset_types)
            ).all()
            
            for asset in assets:
                # Analyze each asset
                analysis = self._analyze_asset(asset)
                
                if analysis and analysis['confidence'] >= settings.min_confidence_threshold:
                    opportunities.append({
                        'asset': asset,
                        'signal_type': analysis['signal_type'],
                        'confidence': analysis['confidence'],
                        'target_price': analysis['target_price'],
                        'stop_loss': analysis['stop_loss'],
                        'take_profit': analysis['take_profit'],
                        'reasoning': analysis['reasoning'],
                        'score': analysis['score']
                    })
            
            # Sort by score (best opportunities first)
            opportunities.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"🔍 Found {len(opportunities)} trading opportunities")
            
        except Exception as e:
            logger.error(f"❌ Error finding trading opportunities: {e}")
        
        return opportunities
    
    def _analyze_asset(self, asset: Asset) -> Optional[Dict]:
        """Perform comprehensive AI analysis on an asset"""
        try:
            # Get historical data
            historical_data = self._get_historical_data(asset)
            
            if len(historical_data) < 30:  # Need at least 30 data points
                return None
            
            # Calculate technical indicators
            indicators = self._calculate_technical_indicators(historical_data)
            
            # Prepare features for ML model
            features = self._prepare_features(historical_data, indicators)
            
            if len(features) == 0:
                return None
            
            # Get or train model for this asset
            model = self._get_or_train_model(asset, features, historical_data['close'])
            
            if not model:
                return None
            
            # Make prediction
            latest_features = features.iloc[-1:].values
            predicted_price = model.predict(latest_features)[0]
            current_price = asset.current_price or historical_data['close'].iloc[-1]
            
            # Calculate price change prediction
            price_change_percent = ((predicted_price - current_price) / current_price) * 100
            
            # Determine signal type and confidence
            signal_analysis = self._determine_signal(
                current_price, predicted_price, price_change_percent, indicators.iloc[-1]
            )
            
            # Calculate target prices
            if signal_analysis['signal_type'] == 'BUY':
                target_price = current_price * (1 + self.take_profit_percent)
                stop_loss = current_price * (1 - self.stop_loss_percent)
            elif signal_analysis['signal_type'] == 'SELL':
                target_price = current_price * (1 - self.take_profit_percent)
                stop_loss = current_price * (1 + self.stop_loss_percent)
            else:
                return None
            
            return {
                'signal_type': signal_analysis['signal_type'],
                'confidence': signal_analysis['confidence'],
                'target_price': target_price,
                'stop_loss': stop_loss,
                'take_profit': target_price,
                'reasoning': signal_analysis['reasoning'],
                'score': signal_analysis['confidence'] * abs(price_change_percent),
                'predicted_price': predicted_price,
                'price_change_percent': price_change_percent
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing asset {asset.symbol}: {e}")
            return None
    
    def _get_historical_data(self, asset: Asset) -> pd.DataFrame:
        """Get historical market data for an asset"""
        try:
            # Try to get from database first
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=self.lookback_days)
            
            market_data = MarketData.query.filter(
                MarketData.asset_id == asset.id,
                MarketData.timestamp >= start_date,
                MarketData.timestamp <= end_date
            ).order_by(MarketData.timestamp.asc()).all()
            
            if len(market_data) >= 20:  # If we have enough data in DB
                df = pd.DataFrame([{
                    'timestamp': md.timestamp,
                    'open': md.open_price,
                    'high': md.high_price,
                    'low': md.low_price,
                    'close': md.close_price,
                    'volume': md.volume
                } for md in market_data])
                df.set_index('timestamp', inplace=True)
                return df
            
            # Otherwise, fetch from Yahoo Finance
            ticker = yf.Ticker(asset.symbol)
            df = ticker.history(period=f"{self.lookback_days}d", interval="1d")
            
            if df.empty:
                logger.warning(f"No data available for {asset.symbol}")
                return pd.DataFrame()
            
            # Store in database for future use
            self._store_market_data(asset, df)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error getting historical data for {asset.symbol}: {e}")
            return pd.DataFrame()
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        indicators = pd.DataFrame(index=df.index)
        
        try:
            # Moving averages
            indicators['sma_20'] = df['Close'].rolling(window=20).mean()
            indicators['sma_50'] = df['Close'].rolling(window=50).mean()
            indicators['ema_12'] = df['Close'].ewm(span=12).mean()
            indicators['ema_26'] = df['Close'].ewm(span=26).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            indicators['macd'] = indicators['ema_12'] - indicators['ema_26']
            indicators['macd_signal'] = indicators['macd'].ewm(span=9).mean()
            indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
            
            # Bollinger Bands
            indicators['bb_middle'] = df['Close'].rolling(window=20).mean()
            bb_std = df['Close'].rolling(window=20).std()
            indicators['bb_upper'] = indicators['bb_middle'] + (bb_std * 2)
            indicators['bb_lower'] = indicators['bb_middle'] - (bb_std * 2)
            indicators['bb_position'] = (df['Close'] - indicators['bb_lower']) / (indicators['bb_upper'] - indicators['bb_lower'])
            
            # Volume indicators
            indicators['volume_sma'] = df['Volume'].rolling(window=20).mean()
            indicators['volume_ratio'] = df['Volume'] / indicators['volume_sma']
            
            # Price momentum
            indicators['momentum_5'] = df['Close'] / df['Close'].shift(5) - 1
            indicators['momentum_10'] = df['Close'] / df['Close'].shift(10) - 1
            
            # Volatility
            indicators['volatility'] = df['Close'].rolling(window=20).std() / df['Close'].rolling(window=20).mean()
            
        except Exception as e:
            logger.error(f"❌ Error calculating technical indicators: {e}")
        
        return indicators
    
    def _prepare_features(self, price_data: pd.DataFrame, indicators: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for machine learning model"""
        try:
            features = pd.DataFrame(index=price_data.index)
            
            # Price features
            features['price'] = price_data['Close']
            features['price_change'] = price_data['Close'].pct_change()
            features['high_low_ratio'] = price_data['High'] / price_data['Low']
            features['open_close_ratio'] = price_data['Open'] / price_data['Close']
            
            # Volume features
            features['volume'] = price_data['Volume']
            features['volume_change'] = price_data['Volume'].pct_change()
            
            # Technical indicator features
            for col in indicators.columns:
                if not indicators[col].isna().all():
                    features[col] = indicators[col]
            
            # Lag features
            for lag in [1, 2, 3, 5]:
                features[f'price_lag_{lag}'] = price_data['Close'].shift(lag)
                features[f'volume_lag_{lag}'] = price_data['Volume'].shift(lag)
            
            # Rolling statistics
            for window in [5, 10, 20]:
                features[f'price_mean_{window}'] = price_data['Close'].rolling(window).mean()
                features[f'price_std_{window}'] = price_data['Close'].rolling(window).std()
                features[f'volume_mean_{window}'] = price_data['Volume'].rolling(window).mean()
            
            # Drop rows with NaN values
            features = features.dropna()
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error preparing features: {e}")
            return pd.DataFrame()
    
    def _get_or_train_model(self, asset: Asset, features: pd.DataFrame, target: pd.Series) -> Optional[object]:
        """Get existing model or train new one for asset"""
        try:
            model_key = f"{asset.symbol}_{self.prediction_horizon}h"
            
            # Check if model exists and is recent
            if model_key in self.models:
                return self.models[model_key]
            
            # Prepare training data
            aligned_target = target.loc[features.index]
            
            if len(features) < 20 or len(aligned_target) < 20:
                logger.warning(f"Insufficient data for training model for {asset.symbol}")
                return None
            
            # Create future target (price after prediction_horizon)
            future_target = aligned_target.shift(-1)  # Simplified: next day price
            
            # Remove NaN values
            valid_indices = ~(features.isna().any(axis=1) | future_target.isna())
            X = features[valid_indices]
            y = future_target[valid_indices]
            
            if len(X) < 10:
                logger.warning(f"Insufficient valid data for training model for {asset.symbol}")
                return None
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train ensemble model
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            
            rf_model.fit(X_train_scaled, y_train)
            gb_model.fit(X_train_scaled, y_train)
            
            # Create ensemble predictions
            rf_pred = rf_model.predict(X_test_scaled)
            gb_pred = gb_model.predict(X_test_scaled)
            ensemble_pred = (rf_pred + gb_pred) / 2
            
            # Evaluate model
            mse = mean_squared_error(y_test, ensemble_pred)
            r2 = r2_score(y_test, ensemble_pred)
            
            logger.info(f"📊 Model trained for {asset.symbol}: MSE={mse:.4f}, R²={r2:.4f}")
            
            # Store models and scaler
            self.models[model_key] = {
                'rf_model': rf_model,
                'gb_model': gb_model,
                'scaler': scaler,
                'mse': mse,
                'r2': r2,
                'trained_at': datetime.utcnow()
            }
            self.scalers[model_key] = scaler
            
            return self.models[model_key]
            
        except Exception as e:
            logger.error(f"❌ Error training model for {asset.symbol}: {e}")
            return None
    
    def _determine_signal(self, current_price: float, predicted_price: float, 
                         price_change_percent: float, indicators: pd.Series) -> Dict:
        """Determine trading signal based on AI analysis and technical indicators"""
        try:
            signals = []
            reasoning = []
            
            # Price prediction signal
            if price_change_percent > 5:
                signals.append(('BUY', 0.8))
                reasoning.append(f"AI predicts {price_change_percent:.1f}% price increase")
            elif price_change_percent < -5:
                signals.append(('SELL', 0.8))
                reasoning.append(f"AI predicts {price_change_percent:.1f}% price decrease")
            
            # RSI signal
            if 'rsi' in indicators and not pd.isna(indicators['rsi']):
                if indicators['rsi'] < 30:
                    signals.append(('BUY', 0.7))
                    reasoning.append(f"RSI oversold at {indicators['rsi']:.1f}")
                elif indicators['rsi'] > 70:
                    signals.append(('SELL', 0.7))
                    reasoning.append(f"RSI overbought at {indicators['rsi']:.1f}")
            
            # MACD signal
            if 'macd' in indicators and 'macd_signal' in indicators:
                if (not pd.isna(indicators['macd']) and not pd.isna(indicators['macd_signal'])):
                    if indicators['macd'] > indicators['macd_signal']:
                        signals.append(('BUY', 0.6))
                        reasoning.append("MACD bullish crossover")
                    else:
                        signals.append(('SELL', 0.6))
                        reasoning.append("MACD bearish crossover")
            
            # Bollinger Bands signal
            if 'bb_position' in indicators and not pd.isna(indicators['bb_position']):
                if indicators['bb_position'] < 0.2:
                    signals.append(('BUY', 0.6))
                    reasoning.append("Price near lower Bollinger Band")
                elif indicators['bb_position'] > 0.8:
                    signals.append(('SELL', 0.6))
                    reasoning.append("Price near upper Bollinger Band")
            
            # Volume confirmation
            if 'volume_ratio' in indicators and not pd.isna(indicators['volume_ratio']):
                if indicators['volume_ratio'] > 1.5:
                    # High volume confirms the signal
                    if signals:
                        signals[-1] = (signals[-1][0], signals[-1][1] * 1.2)
                        reasoning.append("High volume confirmation")
            
            # Aggregate signals
            if not signals:
                return {
                    'signal_type': 'HOLD',
                    'confidence': 0.0,
                    'reasoning': "No clear trading signal"
                }
            
            # Calculate weighted signal
            buy_weight = sum(conf for sig, conf in signals if sig == 'BUY')
            sell_weight = sum(conf for sig, conf in signals if sig == 'SELL')
            
            if buy_weight > sell_weight and buy_weight > 0.5:
                signal_type = 'BUY'
                confidence = min(buy_weight / len(signals), 1.0)
            elif sell_weight > buy_weight and sell_weight > 0.5:
                signal_type = 'SELL'
                confidence = min(sell_weight / len(signals), 1.0)
            else:
                signal_type = 'HOLD'
                confidence = 0.0
            
            return {
                'signal_type': signal_type,
                'confidence': confidence,
                'reasoning': "; ".join(reasoning)
            }
            
        except Exception as e:
            logger.error(f"❌ Error determining signal: {e}")
            return {
                'signal_type': 'HOLD',
                'confidence': 0.0,
                'reasoning': f"Error in analysis: {e}"
            }
    
    def _should_execute_trade(self, opportunity: Dict, portfolio: Portfolio, 
                            settings: TradingSettings) -> bool:
        """Determine if a trade should be executed"""
        try:
            # Check confidence threshold
            if opportunity['confidence'] < settings.min_confidence_threshold:
                return False
            
            # Check if we already have a position in this asset
            existing_position = Position.query.filter_by(
                portfolio_id=portfolio.id,
                asset_id=opportunity['asset'].id,
                is_open=True
            ).first()
            
            if existing_position:
                return False  # Don't double up on positions
            
            # Check maximum open positions
            open_positions_count = Position.query.filter_by(
                portfolio_id=portfolio.id,
                is_open=True
            ).count()
            
            if open_positions_count >= settings.max_open_positions:
                return False
            
            # Check available cash
            position_value = portfolio.total_value * settings.max_position_size
            if position_value > portfolio.cash_balance:
                return False
            
            # Check daily trading limit
            if not portfolio.user.subscription.can_trade_today():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking if should execute trade: {e}")
            return False
    
    def _execute_trade(self, opportunity: Dict, portfolio: Portfolio, user: User):
        """Execute a trade based on opportunity"""
        try:
            asset = opportunity['asset']
            signal_type = opportunity['signal_type']
            confidence = opportunity['confidence']
            
            # Calculate position size
            position_value = portfolio.total_value * user.trading_settings.max_position_size
            current_price = asset.current_price or opportunity.get('predicted_price', 100)
            quantity = position_value / current_price
            
            # Create trading signal record
            signal = TradingSignal(
                asset_id=asset.id,
                signal_type=signal_type,
                confidence=confidence,
                target_price=opportunity['target_price'],
                stop_loss_price=opportunity['stop_loss'],
                take_profit_price=opportunity['take_profit'],
                strategy='AI_ENSEMBLE',
                timeframe='1d',
                reasoning=opportunity['reasoning'],
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            db.session.add(signal)
            db.session.flush()
            
            # Create trade record
            trade = Trade(
                portfolio_id=portfolio.id,
                asset_id=asset.id,
                trade_type=signal_type,
                quantity=quantity,
                price=current_price,
                total_value=position_value,
                commission=position_value * 0.001,  # 0.1% commission
                signal_id=signal.id,
                strategy='AI_ENSEMBLE',
                confidence=confidence
            )
            
            # Execute trade
            trade.execute_trade()
            db.session.add(trade)
            
            if signal_type == 'BUY':
                # Create position
                position = Position(
                    portfolio_id=portfolio.id,
                    asset_id=asset.id,
                    quantity=quantity,
                    entry_price=current_price,
                    current_price=current_price,
                    market_value=position_value,
                    stop_loss_price=opportunity['stop_loss'],
                    take_profit_price=opportunity['take_profit']
                )
                db.session.add(position)
                
                # Update portfolio
                portfolio.cash_balance -= position_value + trade.commission
                portfolio.invested_value += position_value
                
            # Update subscription trade count
            user.subscription.increment_trade_count()
            
            # Mark signal as executed
            signal.execute_signal()
            
            logger.info(f"✅ Executed {signal_type} trade for {asset.symbol}: "
                       f"{quantity:.4f} @ ${current_price:.4f} (confidence: {confidence:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Error executing trade: {e}")
            db.session.rollback()
    
    def _manage_existing_positions(self, portfolio: Portfolio, settings: TradingSettings):
        """Manage existing open positions"""
        try:
            open_positions = Position.query.filter_by(
                portfolio_id=portfolio.id,
                is_open=True
            ).all()
            
            for position in open_positions:
                # Update market value
                position.update_market_value()
                
                # Check stop loss
                if settings.stop_loss_enabled and position.should_stop_loss():
                    self._close_position(position, 'STOP_LOSS')
                    continue
                
                # Check take profit
                elif position.should_take_profit():
                    self._close_position(position, 'TAKE_PROFIT')
                    continue
                
                # Check if we should hold or close based on AI analysis
                analysis = self._analyze_asset(position.asset)
                if analysis and analysis['signal_type'] == 'SELL' and analysis['confidence'] > 0.8:
                    self._close_position(position, 'AI_SIGNAL')
            
        except Exception as e:
            logger.error(f"❌ Error managing existing positions: {e}")
    
    def _close_position(self, position: Position, reason: str):
        """Close a position"""
        try:
            current_price = position.asset.current_price or position.current_price
            
            # Create closing trade
            trade = Trade(
                portfolio_id=position.portfolio_id,
                asset_id=position.asset_id,
                position_id=position.id,
                trade_type='SELL',
                quantity=position.quantity,
                price=current_price,
                total_value=position.quantity * current_price,
                commission=position.quantity * current_price * 0.001,
                strategy=f'CLOSE_{reason}'
            )
            
            # Calculate P&L
            trade.pnl = position.unrealized_pnl - trade.commission
            trade.pnl_percent = position.unrealized_pnl_percent
            
            # Execute trade
            trade.execute_trade()
            db.session.add(trade)
            
            # Close position
            position.close_position(current_price)
            
            # Update portfolio
            portfolio = position.portfolio
            portfolio.cash_balance += trade.total_value - trade.commission
            portfolio.invested_value -= position.market_value
            
            logger.info(f"🔄 Closed position {position.asset.symbol}: "
                       f"P&L ${trade.pnl:.2f} ({trade.pnl_percent:.2f}%) - {reason}")
            
        except Exception as e:
            logger.error(f"❌ Error closing position: {e}")
    
    def _check_daily_loss_limit(self, portfolio: Portfolio, settings: TradingSettings) -> bool:
        """Check if daily loss limit has been reached"""
        try:
            today = datetime.utcnow().date()
            
            # Get today's trades
            today_trades = Trade.query.filter(
                Trade.portfolio_id == portfolio.id,
                Trade.executed_at >= datetime.combine(today, datetime.min.time()),
                Trade.status == 'executed'
            ).all()
            
            # Calculate today's P&L
            today_pnl = sum(trade.pnl or 0 for trade in today_trades)
            
            # Check if loss limit exceeded
            loss_limit = portfolio.total_value * settings.daily_loss_limit
            
            return today_pnl < -loss_limit
            
        except Exception as e:
            logger.error(f"❌ Error checking daily loss limit: {e}")
            return False
    
    def _hourly_market_analysis(self):
        """Perform hourly market analysis"""
        try:
            logger.info("📊 Performing hourly market analysis...")
            
            # Update asset prices
            assets = Asset.query.filter_by(is_active=True).all()
            
            for asset in assets[:20]:  # Limit to prevent rate limiting
                try:
                    ticker = yf.Ticker(asset.symbol)
                    info = ticker.info
                    
                    if 'regularMarketPrice' in info:
                        asset.update_price(
                            info['regularMarketPrice'],
                            info.get('regularMarketVolume')
                        )
                except Exception as e:
                    logger.warning(f"Failed to update price for {asset.symbol}: {e}")
            
            db.session.commit()
            logger.info("✅ Hourly market analysis completed")
            
        except Exception as e:
            logger.error(f"❌ Error in hourly market analysis: {e}")
    
    def _update_market_data(self):
        """Update market data every 15 minutes"""
        try:
            # Update prices for actively traded assets
            active_assets = Asset.query.join(Position).filter(
                Position.is_open == True,
                Asset.is_active == True
            ).distinct().all()
            
            for asset in active_assets:
                try:
                    ticker = yf.Ticker(asset.symbol)
                    current_data = ticker.history(period="1d", interval="1m").tail(1)
                    
                    if not current_data.empty:
                        latest = current_data.iloc[-1]
                        asset.update_price(latest['Close'], latest['Volume'])
                        
                        # Update all open positions for this asset
                        positions = Position.query.filter_by(
                            asset_id=asset.id,
                            is_open=True
                        ).all()
                        
                        for position in positions:
                            position.update_market_value()
                            
                except Exception as e:
                    logger.warning(f"Failed to update market data for {asset.symbol}: {e}")
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"❌ Error updating market data: {e}")
    
    def _store_market_data(self, asset: Asset, df: pd.DataFrame):
        """Store market data in database"""
        try:
            for timestamp, row in df.iterrows():
                market_data = MarketData(
                    asset_id=asset.id,
                    timestamp=timestamp,
                    open_price=row['Open'],
                    high_price=row['High'],
                    low_price=row['Low'],
                    close_price=row['Close'],
                    volume=row['Volume']
                )
                db.session.add(market_data)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"❌ Error storing market data for {asset.symbol}: {e}")
    
    def get_engine_status(self) -> Dict:
        """Get current engine status"""
        return {
            'is_running': self.is_running,
            'models_loaded': len(self.models),
            'last_analysis': datetime.utcnow().isoformat(),
            'active_assets': Asset.query.filter_by(is_active=True).count(),
            'total_positions': Position.query.filter_by(is_open=True).count(),
            'total_users': User.query.filter_by(is_active=True).count()
        }

# Global instance
ai_trading_engine = AITradingEngine()

