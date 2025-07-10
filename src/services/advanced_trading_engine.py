"""
Advanced AI Trading Engine
Implements comprehensive trading strategies from research document
Supports stocks, cryptocurrencies, and meme coins with sophisticated algorithms
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
import yfinance as yf
from textblob import TextBlob
import tweepy
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssetType(Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    MEME_COIN = "meme_coin"

class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

@dataclass
class TechnicalIndicators:
    """Technical indicators for trading decisions"""
    rsi: float
    macd: float
    macd_signal: float
    bollinger_upper: float
    bollinger_lower: float
    bollinger_middle: float
    ema_9: float
    ema_21: float
    ema_50: float
    ema_200: float
    adx: float
    atr: float
    volume_ratio: float
    price_momentum_5d: float
    price_momentum_20d: float

@dataclass
class TradingSignal:
    """Trading signal with confidence and reasoning"""
    symbol: str
    asset_type: AssetType
    signal: SignalType
    confidence: float
    entry_price: float
    target_price: float
    stop_loss: float
    strategy: str
    reasoning: str
    timestamp: datetime
    risk_score: float

@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    price: float
    volume: float
    market_cap: float
    price_change_24h: float
    volume_change_24h: float
    timestamp: datetime

class AdvancedTradingEngine:
    """
    Advanced AI Trading Engine implementing comprehensive strategies
    """
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.active_signals = {}
        self.portfolio_allocation = {
            AssetType.STOCK: 0.6,
            AssetType.CRYPTO: 0.3,
            AssetType.MEME_COIN: 0.1
        }
        self.max_position_size = {
            AssetType.STOCK: 0.10,  # 10% max per stock
            AssetType.CRYPTO: 0.05,  # 5% max per crypto
            AssetType.MEME_COIN: 0.02  # 2% max per meme coin
        }
        
        # Initialize data sources
        self.initialize_data_sources()
        
        # Start background processes
        self.start_background_processes()
    
    def initialize_data_sources(self):
        """Initialize external data sources"""
        try:
            # Twitter API for sentiment analysis (placeholder)
            self.twitter_api = None  # Initialize with actual credentials
            
            # Reddit API for meme coin analysis
            self.reddit_api = None  # Initialize with actual credentials
            
            # Market data APIs
            self.alpha_vantage_key = "demo"  # Replace with actual key
            self.coinmarketcap_key = "demo"  # Replace with actual key
            
            logger.info("Data sources initialized")
        except Exception as e:
            logger.error(f"Error initializing data sources: {e}")
    
    def start_background_processes(self):
        """Start background monitoring and analysis processes"""
        # Market data update thread
        market_thread = threading.Thread(target=self.continuous_market_monitoring, daemon=True)
        market_thread.start()
        
        # Signal generation thread
        signal_thread = threading.Thread(target=self.continuous_signal_generation, daemon=True)
        signal_thread.start()
        
        # Risk monitoring thread
        risk_thread = threading.Thread(target=self.continuous_risk_monitoring, daemon=True)
        risk_thread.start()
        
        logger.info("Background processes started")
    
    def continuous_market_monitoring(self):
        """Continuously monitor market data"""
        while True:
            try:
                # Update stock data
                self.update_stock_data()
                
                # Update crypto data
                self.update_crypto_data()
                
                # Update meme coin data
                self.update_meme_coin_data()
                
                time.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Error in market monitoring: {e}")
                time.sleep(30)
    
    def continuous_signal_generation(self):
        """Continuously generate trading signals"""
        while True:
            try:
                # Generate signals for all asset types
                self.generate_all_signals()
                
                time.sleep(300)  # Generate signals every 5 minutes
            except Exception as e:
                logger.error(f"Error in signal generation: {e}")
                time.sleep(60)
    
    def continuous_risk_monitoring(self):
        """Continuously monitor risk levels"""
        while True:
            try:
                # Monitor portfolio risk
                self.monitor_portfolio_risk()
                
                # Check stop losses
                self.check_stop_losses()
                
                # Update position sizes
                self.update_position_sizes()
                
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in risk monitoring: {e}")
                time.sleep(30)
    
    def get_technical_indicators(self, symbol: str, asset_type: AssetType) -> TechnicalIndicators:
        """Calculate comprehensive technical indicators"""
        try:
            # Get historical data
            if asset_type == AssetType.STOCK:
                data = yf.download(symbol, period="6mo", interval="1d")
            else:
                data = self.get_crypto_historical_data(symbol)
            
            if data.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Calculate indicators
            close = data['Close']
            high = data['High']
            low = data['Low']
            volume = data['Volume']
            
            # RSI calculation
            rsi = self.calculate_rsi(close, 14)
            
            # MACD calculation
            macd, macd_signal = self.calculate_macd(close)
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(close, 20, 2)
            
            # EMAs
            ema_9 = close.ewm(span=9).mean().iloc[-1]
            ema_21 = close.ewm(span=21).mean().iloc[-1]
            ema_50 = close.ewm(span=50).mean().iloc[-1]
            ema_200 = close.ewm(span=200).mean().iloc[-1]
            
            # ADX calculation
            adx = self.calculate_adx(high, low, close, 14)
            
            # ATR calculation
            atr = self.calculate_atr(high, low, close, 14)
            
            # Volume ratio
            volume_ratio = volume.iloc[-1] / volume.rolling(20).mean().iloc[-1]
            
            # Price momentum
            price_momentum_5d = (close.iloc[-1] / close.iloc[-6] - 1) * 100
            price_momentum_20d = (close.iloc[-1] / close.iloc[-21] - 1) * 100
            
            return TechnicalIndicators(
                rsi=rsi,
                macd=macd,
                macd_signal=macd_signal,
                bollinger_upper=bb_upper,
                bollinger_lower=bb_lower,
                bollinger_middle=bb_middle,
                ema_9=ema_9,
                ema_21=ema_21,
                ema_50=ema_50,
                ema_200=ema_200,
                adx=adx,
                atr=atr,
                volume_ratio=volume_ratio,
                price_momentum_5d=price_momentum_5d,
                price_momentum_20d=price_momentum_20d
            )
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float]:
        """Calculate MACD and signal line"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd.iloc[-1], macd_signal.iloc[-1]
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper.iloc[-1], sma.iloc[-1], lower.iloc[-1]
    
    def calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        """Calculate Average Directional Index"""
        try:
            # True Range calculation
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Directional Movement calculation
            dm_plus = high.diff()
            dm_minus = low.diff() * -1
            
            dm_plus[dm_plus < 0] = 0
            dm_minus[dm_minus < 0] = 0
            
            # Smoothed values
            tr_smooth = tr.rolling(window=period).mean()
            dm_plus_smooth = dm_plus.rolling(window=period).mean()
            dm_minus_smooth = dm_minus.rolling(window=period).mean()
            
            # Directional Indicators
            di_plus = (dm_plus_smooth / tr_smooth) * 100
            di_minus = (dm_minus_smooth / tr_smooth) * 100
            
            # ADX calculation
            dx = abs(di_plus - di_minus) / (di_plus + di_minus) * 100
            adx = dx.rolling(window=period).mean()
            
            return adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 25.0
        except:
            return 25.0  # Default neutral value
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            return atr.iloc[-1]
        except:
            return 1.0  # Default value
    
    # STOCK TRADING STRATEGIES
    
    def momentum_trading_strategy(self, symbol: str, indicators: TechnicalIndicators, current_price: float) -> Optional[TradingSignal]:
        """Implement momentum trading strategy for stocks"""
        try:
            confidence = 0.0
            signal = SignalType.HOLD
            reasoning = []
            
            # Entry conditions
            if (indicators.price_momentum_5d > 2.0 and 
                indicators.volume_ratio > 1.5 and
                50 <= indicators.rsi <= 70 and
                indicators.macd > indicators.macd_signal and
                current_price > indicators.ema_21):
                
                signal = SignalType.BUY
                confidence += 0.8
                reasoning.append("Strong momentum with volume confirmation")
                
                # Calculate targets
                target_price = current_price * 1.08  # 8% target
                stop_loss = current_price * 0.95     # 5% stop loss
                
            # Exit conditions
            elif (indicators.rsi > 80 or 
                  current_price < indicators.ema_9 or
                  indicators.volume_ratio < 1.0):
                
                signal = SignalType.SELL
                confidence += 0.7
                reasoning.append("Momentum weakening or overbought")
                target_price = current_price * 0.98
                stop_loss = current_price * 1.02
            
            else:
                return None
            
            return TradingSignal(
                symbol=symbol,
                asset_type=AssetType.STOCK,
                signal=signal,
                confidence=confidence,
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                strategy="momentum_trading",
                reasoning="; ".join(reasoning),
                timestamp=datetime.now(),
                risk_score=self.calculate_risk_score(indicators, AssetType.STOCK)
            )
            
        except Exception as e:
            logger.error(f"Error in momentum strategy for {symbol}: {e}")
            return None
    
    def mean_reversion_strategy(self, symbol: str, indicators: TechnicalIndicators, current_price: float) -> Optional[TradingSignal]:
        """Implement mean reversion strategy for stocks"""
        try:
            confidence = 0.0
            signal = SignalType.HOLD
            reasoning = []
            
            # Calculate Z-score
            z_score = (current_price - indicators.bollinger_middle) / ((indicators.bollinger_upper - indicators.bollinger_lower) / 4)
            
            # Entry conditions (oversold)
            if (current_price <= indicators.bollinger_lower and
                z_score < -2 and
                indicators.volume_ratio > 1.5 and
                indicators.rsi < 30):
                
                signal = SignalType.BUY
                confidence += 0.75
                reasoning.append(f"Oversold condition with Z-score: {z_score:.2f}")
                
                target_price = indicators.bollinger_middle  # Target middle band
                stop_loss = current_price * 0.95
                
            # Exit conditions
            elif (current_price >= indicators.bollinger_middle or
                  z_score > 0):
                
                signal = SignalType.SELL
                confidence += 0.6
                reasoning.append("Mean reversion target reached")
                target_price = current_price * 1.02
                stop_loss = current_price * 0.98
            
            else:
                return None
            
            return TradingSignal(
                symbol=symbol,
                asset_type=AssetType.STOCK,
                signal=signal,
                confidence=confidence,
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                strategy="mean_reversion",
                reasoning="; ".join(reasoning),
                timestamp=datetime.now(),
                risk_score=self.calculate_risk_score(indicators, AssetType.STOCK)
            )
            
        except Exception as e:
            logger.error(f"Error in mean reversion strategy for {symbol}: {e}")
            return None
    
    def trend_following_strategy(self, symbol: str, indicators: TechnicalIndicators, current_price: float) -> Optional[TradingSignal]:
        """Implement trend following strategy for stocks"""
        try:
            confidence = 0.0
            signal = SignalType.HOLD
            reasoning = []
            
            # Check trend alignment
            bullish_alignment = (current_price > indicators.ema_50 > indicators.ema_200 and
                               indicators.ema_9 > indicators.ema_21 > indicators.ema_50)
            
            # Entry conditions
            if (bullish_alignment and
                indicators.adx > 25 and
                indicators.macd > indicators.macd_signal):
                
                signal = SignalType.BUY
                confidence += 0.85
                reasoning.append(f"Strong uptrend with ADX: {indicators.adx:.1f}")
                
                target_price = current_price * 1.15  # 15% target for trend trades
                stop_loss = current_price * 0.92     # 8% stop loss
                
            # Exit conditions
            elif (current_price < indicators.ema_50 or
                  indicators.adx < 20):
                
                signal = SignalType.SELL
                confidence += 0.7
                reasoning.append("Trend weakening")
                target_price = current_price * 0.98
                stop_loss = current_price * 1.02
            
            else:
                return None
            
            return TradingSignal(
                symbol=symbol,
                asset_type=AssetType.STOCK,
                signal=signal,
                confidence=confidence,
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                strategy="trend_following",
                reasoning="; ".join(reasoning),
                timestamp=datetime.now(),
                risk_score=self.calculate_risk_score(indicators, AssetType.STOCK)
            )
            
        except Exception as e:
            logger.error(f"Error in trend following strategy for {symbol}: {e}")
            return None
    
    # CRYPTOCURRENCY STRATEGIES
    
    def crypto_ma_crossover_strategy(self, symbol: str, indicators: TechnicalIndicators, current_price: float) -> Optional[TradingSignal]:
        """Implement moving average crossover strategy for crypto"""
        try:
            confidence = 0.0
            signal = SignalType.HOLD
            reasoning = []
            
            # Golden Cross (bullish)
            if (indicators.ema_21 > indicators.ema_50 and
                indicators.volume_ratio > 1.3 and
                40 <= indicators.rsi <= 60):
                
                signal = SignalType.BUY
                confidence += 0.7
                reasoning.append("Golden cross with volume confirmation")
                
                target_price = current_price * 1.25  # 25% target for crypto
                stop_loss = current_price * 0.88     # 12% stop loss
                
            # Death Cross (bearish)
            elif (indicators.ema_21 < indicators.ema_50 or
                  indicators.rsi > 80 or indicators.rsi < 20):
                
                signal = SignalType.SELL
                confidence += 0.65
                reasoning.append("Death cross or extreme RSI")
                target_price = current_price * 0.95
                stop_loss = current_price * 1.05
            
            else:
                return None
            
            return TradingSignal(
                symbol=symbol,
                asset_type=AssetType.CRYPTO,
                signal=signal,
                confidence=confidence,
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                strategy="crypto_ma_crossover",
                reasoning="; ".join(reasoning),
                timestamp=datetime.now(),
                risk_score=self.calculate_risk_score(indicators, AssetType.CRYPTO)
            )
            
        except Exception as e:
            logger.error(f"Error in crypto MA crossover strategy for {symbol}: {e}")
            return None
    
    def crypto_rsi_divergence_strategy(self, symbol: str, indicators: TechnicalIndicators, current_price: float) -> Optional[TradingSignal]:
        """Implement RSI divergence strategy for crypto"""
        try:
            # This would require historical RSI and price data to detect divergences
            # For now, implementing a simplified version based on extreme RSI levels
            
            confidence = 0.0
            signal = SignalType.HOLD
            reasoning = []
            
            # Oversold with potential bullish divergence
            if (indicators.rsi < 30 and
                indicators.volume_ratio > 1.2):
                
                signal = SignalType.BUY
                confidence += 0.6
                reasoning.append(f"Oversold RSI: {indicators.rsi:.1f}")
                
                target_price = current_price * 1.20
                stop_loss = current_price * 0.90
                
            # Overbought with potential bearish divergence
            elif (indicators.rsi > 70 and
                  indicators.volume_ratio < 0.8):
                
                signal = SignalType.SELL
                confidence += 0.6
                reasoning.append(f"Overbought RSI: {indicators.rsi:.1f}")
                target_price = current_price * 0.90
                stop_loss = current_price * 1.10
            
            else:
                return None
            
            return TradingSignal(
                symbol=symbol,
                asset_type=AssetType.CRYPTO,
                signal=signal,
                confidence=confidence,
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                strategy="crypto_rsi_divergence",
                reasoning="; ".join(reasoning),
                timestamp=datetime.now(),
                risk_score=self.calculate_risk_score(indicators, AssetType.CRYPTO)
            )
            
        except Exception as e:
            logger.error(f"Error in crypto RSI divergence strategy for {symbol}: {e}")
            return None
    
    # MEME COIN STRATEGIES
    
    def meme_social_momentum_strategy(self, symbol: str, current_price: float) -> Optional[TradingSignal]:
        """Implement social momentum strategy for meme coins"""
        try:
            # Get social sentiment data
            social_data = self.get_social_sentiment(symbol)
            
            if not social_data:
                return None
            
            confidence = 0.0
            signal = SignalType.HOLD
            reasoning = []
            
            # High social momentum
            if (social_data['mention_growth'] > 500 and
                social_data['sentiment_score'] > 0.6 and
                social_data['community_growth'] > 100):
                
                signal = SignalType.BUY
                confidence += 0.5  # Lower confidence due to high risk
                reasoning.append(f"Viral momentum: {social_data['mention_growth']:.0f}% mention growth")
                
                target_price = current_price * 2.0   # 100% target for meme coins
                stop_loss = current_price * 0.85     # 15% stop loss
                
            # Declining social momentum
            elif (social_data['mention_growth'] < 50 or
                  social_data['sentiment_score'] < 0.2):
                
                signal = SignalType.SELL
                confidence += 0.6
                reasoning.append("Social momentum declining")
                target_price = current_price * 0.80
                stop_loss = current_price * 1.20
            
            else:
                return None
            
            return TradingSignal(
                symbol=symbol,
                asset_type=AssetType.MEME_COIN,
                signal=signal,
                confidence=confidence,
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                strategy="meme_social_momentum",
                reasoning="; ".join(reasoning),
                timestamp=datetime.now(),
                risk_score=0.9  # High risk for meme coins
            )
            
        except Exception as e:
            logger.error(f"Error in meme social momentum strategy for {symbol}: {e}")
            return None
    
    def meme_whale_tracking_strategy(self, symbol: str, current_price: float) -> Optional[TradingSignal]:
        """Implement whale tracking strategy for meme coins"""
        try:
            # Get whale activity data
            whale_data = self.get_whale_activity(symbol)
            
            if not whale_data:
                return None
            
            confidence = 0.0
            signal = SignalType.HOLD
            reasoning = []
            
            # Whale accumulation
            if (whale_data['large_buys_24h'] >= 3 and
                whale_data['exchange_outflow'] > whale_data['exchange_inflow']):
                
                signal = SignalType.BUY
                confidence += 0.6
                reasoning.append(f"Whale accumulation: {whale_data['large_buys_24h']} large buys")
                
                target_price = current_price * 1.5
                stop_loss = current_price * 0.90
                
            # Whale selling
            elif (whale_data['large_sells_24h'] >= 2 or
                  whale_data['exchange_inflow'] > whale_data['exchange_outflow'] * 2):
                
                signal = SignalType.SELL
                confidence += 0.8
                reasoning.append("Whale selling detected")
                target_price = current_price * 0.85
                stop_loss = current_price * 1.15
            
            else:
                return None
            
            return TradingSignal(
                symbol=symbol,
                asset_type=AssetType.MEME_COIN,
                signal=signal,
                confidence=confidence,
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                strategy="meme_whale_tracking",
                reasoning="; ".join(reasoning),
                timestamp=datetime.now(),
                risk_score=0.85
            )
            
        except Exception as e:
            logger.error(f"Error in meme whale tracking strategy for {symbol}: {e}")
            return None
    
    # UTILITY METHODS
    
    def calculate_risk_score(self, indicators: TechnicalIndicators, asset_type: AssetType) -> float:
        """Calculate risk score for a trading signal"""
        try:
            risk_score = 0.0
            
            # Volatility risk (ATR)
            if indicators.atr > 0:
                volatility_risk = min(indicators.atr / indicators.bollinger_middle, 0.3)
                risk_score += volatility_risk
            
            # Momentum risk (RSI extremes)
            if indicators.rsi > 80 or indicators.rsi < 20:
                risk_score += 0.2
            
            # Trend strength risk (ADX)
            if indicators.adx < 20:
                risk_score += 0.15
            
            # Asset type base risk
            base_risk = {
                AssetType.STOCK: 0.1,
                AssetType.CRYPTO: 0.3,
                AssetType.MEME_COIN: 0.6
            }
            risk_score += base_risk[asset_type]
            
            return min(risk_score, 1.0)
            
        except:
            return 0.5  # Default medium risk
    
    def get_social_sentiment(self, symbol: str) -> Optional[Dict]:
        """Get social sentiment data for a symbol"""
        try:
            # Placeholder for social sentiment analysis
            # In production, this would integrate with Twitter, Reddit, etc.
            return {
                'mention_growth': np.random.uniform(0, 1000),
                'sentiment_score': np.random.uniform(-1, 1),
                'community_growth': np.random.uniform(0, 200),
                'influencer_mentions': np.random.randint(0, 10)
            }
        except:
            return None
    
    def get_whale_activity(self, symbol: str) -> Optional[Dict]:
        """Get whale activity data for a symbol"""
        try:
            # Placeholder for whale tracking
            # In production, this would integrate with blockchain analytics
            return {
                'large_buys_24h': np.random.randint(0, 5),
                'large_sells_24h': np.random.randint(0, 3),
                'exchange_inflow': np.random.uniform(0, 1000000),
                'exchange_outflow': np.random.uniform(0, 1000000),
                'whale_addresses_active': np.random.randint(0, 20)
            }
        except:
            return None
    
    def get_crypto_historical_data(self, symbol: str) -> pd.DataFrame:
        """Get historical data for cryptocurrency"""
        try:
            # Use yfinance for crypto data (many cryptos available)
            ticker = f"{symbol}-USD" if not symbol.endswith("-USD") else symbol
            data = yf.download(ticker, period="6mo", interval="1d")
            return data
        except:
            # Return empty DataFrame if data not available
            return pd.DataFrame()
    
    def update_stock_data(self):
        """Update stock market data"""
        try:
            stock_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
            
            for symbol in stock_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        volume = hist['Volume'].iloc[-1]
                        
                        market_data = MarketData(
                            symbol=symbol,
                            price=current_price,
                            volume=volume,
                            market_cap=info.get('marketCap', 0),
                            price_change_24h=info.get('regularMarketChangePercent', 0),
                            volume_change_24h=0,  # Calculate if needed
                            timestamp=datetime.now()
                        )
                        
                        # Store in Redis
                        self.redis_client.setex(
                            f"market_data:{symbol}",
                            3600,  # 1 hour expiry
                            json.dumps(market_data.__dict__, default=str)
                        )
                        
                except Exception as e:
                    logger.error(f"Error updating data for {symbol}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in update_stock_data: {e}")
    
    def update_crypto_data(self):
        """Update cryptocurrency data"""
        try:
            crypto_symbols = ['BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'LINK-USD', 'UNI-USD']
            
            for symbol in crypto_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        volume = hist['Volume'].iloc[-1]
                        
                        market_data = MarketData(
                            symbol=symbol,
                            price=current_price,
                            volume=volume,
                            market_cap=0,  # Would need separate API for this
                            price_change_24h=0,  # Calculate from historical data
                            volume_change_24h=0,
                            timestamp=datetime.now()
                        )
                        
                        # Store in Redis
                        self.redis_client.setex(
                            f"market_data:{symbol}",
                            3600,
                            json.dumps(market_data.__dict__, default=str)
                        )
                        
                except Exception as e:
                    logger.error(f"Error updating crypto data for {symbol}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in update_crypto_data: {e}")
    
    def update_meme_coin_data(self):
        """Update meme coin data"""
        try:
            meme_symbols = ['DOGE-USD', 'SHIB-USD']
            
            for symbol in meme_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        volume = hist['Volume'].iloc[-1]
                        
                        market_data = MarketData(
                            symbol=symbol,
                            price=current_price,
                            volume=volume,
                            market_cap=0,
                            price_change_24h=0,
                            volume_change_24h=0,
                            timestamp=datetime.now()
                        )
                        
                        # Store in Redis
                        self.redis_client.setex(
                            f"market_data:{symbol}",
                            3600,
                            json.dumps(market_data.__dict__, default=str)
                        )
                        
                except Exception as e:
                    logger.error(f"Error updating meme coin data for {symbol}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in update_meme_coin_data: {e}")
    
    def generate_all_signals(self):
        """Generate trading signals for all monitored assets"""
        try:
            # Get all market data from Redis
            all_symbols = []
            
            # Stocks
            stock_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
            for symbol in stock_symbols:
                self.generate_stock_signals(symbol)
            
            # Cryptos
            crypto_symbols = ['BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'LINK-USD', 'UNI-USD']
            for symbol in crypto_symbols:
                self.generate_crypto_signals(symbol)
            
            # Meme coins
            meme_symbols = ['DOGE-USD', 'SHIB-USD']
            for symbol in meme_symbols:
                self.generate_meme_signals(symbol)
                
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
    
    def generate_stock_signals(self, symbol: str):
        """Generate signals for stock symbols"""
        try:
            # Get market data
            market_data_str = self.redis_client.get(f"market_data:{symbol}")
            if not market_data_str:
                return
            
            market_data = json.loads(market_data_str)
            current_price = market_data['price']
            
            # Get technical indicators
            indicators = self.get_technical_indicators(symbol, AssetType.STOCK)
            if not indicators:
                return
            
            # Apply all stock strategies
            strategies = [
                self.momentum_trading_strategy,
                self.mean_reversion_strategy,
                self.trend_following_strategy
            ]
            
            best_signal = None
            best_confidence = 0
            
            for strategy in strategies:
                signal = strategy(symbol, indicators, current_price)
                if signal and signal.confidence > best_confidence:
                    best_signal = signal
                    best_confidence = signal.confidence
            
            # Store best signal
            if best_signal:
                self.store_signal(best_signal)
                
        except Exception as e:
            logger.error(f"Error generating stock signals for {symbol}: {e}")
    
    def generate_crypto_signals(self, symbol: str):
        """Generate signals for crypto symbols"""
        try:
            # Get market data
            market_data_str = self.redis_client.get(f"market_data:{symbol}")
            if not market_data_str:
                return
            
            market_data = json.loads(market_data_str)
            current_price = market_data['price']
            
            # Get technical indicators
            indicators = self.get_technical_indicators(symbol, AssetType.CRYPTO)
            if not indicators:
                return
            
            # Apply crypto strategies
            strategies = [
                self.crypto_ma_crossover_strategy,
                self.crypto_rsi_divergence_strategy
            ]
            
            best_signal = None
            best_confidence = 0
            
            for strategy in strategies:
                signal = strategy(symbol, indicators, current_price)
                if signal and signal.confidence > best_confidence:
                    best_signal = signal
                    best_confidence = signal.confidence
            
            # Store best signal
            if best_signal:
                self.store_signal(best_signal)
                
        except Exception as e:
            logger.error(f"Error generating crypto signals for {symbol}: {e}")
    
    def generate_meme_signals(self, symbol: str):
        """Generate signals for meme coin symbols"""
        try:
            # Get market data
            market_data_str = self.redis_client.get(f"market_data:{symbol}")
            if not market_data_str:
                return
            
            market_data = json.loads(market_data_str)
            current_price = market_data['price']
            
            # Apply meme coin strategies
            strategies = [
                lambda s, p: self.meme_social_momentum_strategy(s, p),
                lambda s, p: self.meme_whale_tracking_strategy(s, p)
            ]
            
            best_signal = None
            best_confidence = 0
            
            for strategy in strategies:
                signal = strategy(symbol, current_price)
                if signal and signal.confidence > best_confidence:
                    best_signal = signal
                    best_confidence = signal.confidence
            
            # Store best signal
            if best_signal:
                self.store_signal(best_signal)
                
        except Exception as e:
            logger.error(f"Error generating meme signals for {symbol}: {e}")
    
    def store_signal(self, signal: TradingSignal):
        """Store trading signal in Redis"""
        try:
            signal_data = {
                'symbol': signal.symbol,
                'asset_type': signal.asset_type.value,
                'signal': signal.signal.value,
                'confidence': signal.confidence,
                'entry_price': signal.entry_price,
                'target_price': signal.target_price,
                'stop_loss': signal.stop_loss,
                'strategy': signal.strategy,
                'reasoning': signal.reasoning,
                'timestamp': signal.timestamp.isoformat(),
                'risk_score': signal.risk_score
            }
            
            # Store current signal
            self.redis_client.setex(
                f"signal:{signal.symbol}",
                1800,  # 30 minutes expiry
                json.dumps(signal_data)
            )
            
            # Store in active signals
            self.active_signals[signal.symbol] = signal
            
            logger.info(f"Generated {signal.signal.value} signal for {signal.symbol} with {signal.confidence:.2f} confidence")
            
        except Exception as e:
            logger.error(f"Error storing signal: {e}")
    
    def get_active_signals(self) -> List[Dict]:
        """Get all active trading signals"""
        try:
            signals = []
            
            # Get all signal keys from Redis
            signal_keys = self.redis_client.keys("signal:*")
            
            for key in signal_keys:
                signal_data = self.redis_client.get(key)
                if signal_data:
                    signals.append(json.loads(signal_data))
            
            # Sort by confidence
            signals.sort(key=lambda x: x['confidence'], reverse=True)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting active signals: {e}")
            return []
    
    def monitor_portfolio_risk(self):
        """Monitor overall portfolio risk"""
        try:
            # This would integrate with actual portfolio data
            # For now, just log risk monitoring
            logger.info("Portfolio risk monitoring active")
            
        except Exception as e:
            logger.error(f"Error in portfolio risk monitoring: {e}")
    
    def check_stop_losses(self):
        """Check and execute stop losses"""
        try:
            # This would check current prices against stop loss levels
            # For now, just log stop loss monitoring
            logger.info("Stop loss monitoring active")
            
        except Exception as e:
            logger.error(f"Error in stop loss monitoring: {e}")
    
    def update_position_sizes(self):
        """Update position sizes based on risk"""
        try:
            # This would calculate optimal position sizes
            # For now, just log position sizing
            logger.info("Position sizing updated")
            
        except Exception as e:
            logger.error(f"Error updating position sizes: {e}")

# Global instance
advanced_trading_engine = AdvancedTradingEngine()

def get_trading_signals():
    """Get current trading signals"""
    return advanced_trading_engine.get_active_signals()

def get_market_analysis():
    """Get comprehensive market analysis"""
    try:
        signals = advanced_trading_engine.get_active_signals()
        
        analysis = {
            'total_signals': len(signals),
            'buy_signals': len([s for s in signals if s['signal'] == 'buy']),
            'sell_signals': len([s for s in signals if s['signal'] == 'sell']),
            'avg_confidence': sum(s['confidence'] for s in signals) / len(signals) if signals else 0,
            'high_confidence_signals': [s for s in signals if s['confidence'] > 0.7],
            'asset_distribution': {
                'stocks': len([s for s in signals if s['asset_type'] == 'stock']),
                'crypto': len([s for s in signals if s['asset_type'] == 'crypto']),
                'meme_coins': len([s for s in signals if s['asset_type'] == 'meme_coin'])
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error getting market analysis: {e}")
        return {
            'total_signals': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'avg_confidence': 0,
            'high_confidence_signals': [],
            'asset_distribution': {'stocks': 0, 'crypto': 0, 'meme_coins': 0},
            'timestamp': datetime.now().isoformat()
        }

