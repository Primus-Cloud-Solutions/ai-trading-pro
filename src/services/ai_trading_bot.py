"""
AI Trading Bot
Automated trading with AI signals and social sentiment analysis
"""

import logging
import time
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import random
import math

from services.real_trading_engine import real_trading_engine, TradeOrder
from services.multi_platform_crawler import multi_platform_crawler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradingSignal:
    """AI Trading Signal"""
    symbol: str
    action: str  # 'buy', 'sell', 'hold'
    confidence: float  # 0.0 to 1.0
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None
    reasoning: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class BotConfig:
    """Trading Bot Configuration"""
    enabled: bool = False
    max_position_size: float = 1000.0  # Max $ per position
    risk_per_trade: float = 0.02  # 2% risk per trade
    stop_loss_pct: float = 0.05  # 5% stop loss
    take_profit_pct: float = 0.10  # 10% take profit
    min_confidence: float = 0.7  # Minimum signal confidence
    symbols: List[str] = None
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ['BTC', 'ETH', 'AAPL', 'TSLA', 'NVDA']

class AITradingBot:
    """
    AI Trading Bot with automated signal generation and execution
    """
    
    def __init__(self):
        self.config = BotConfig()
        self.is_running = False
        self.signals_history: List[TradingSignal] = []
        self.active_positions: Dict[str, Dict] = {}
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0
        }
        
        # AI Model weights (simplified)
        self.model_weights = {
            'social_sentiment': 0.3,
            'technical_analysis': 0.4,
            'market_momentum': 0.2,
            'volatility': 0.1
        }
        
        logger.info("🤖 AI Trading Bot initialized")
    
    def start_bot(self, user_id: str, config: Optional[BotConfig] = None):
        """
        Start the automated trading bot
        """
        try:
            if config:
                self.config = config
            
            if not self.config.enabled:
                logger.warning("⚠️ Bot is disabled in config")
                return False
            
            self.user_id = user_id
            self.is_running = True
            
            # Start bot thread
            bot_thread = threading.Thread(target=self._bot_loop, daemon=True)
            bot_thread.start()
            
            logger.info(f"🚀 AI Trading Bot started for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting bot: {str(e)}")
            return False
    
    def stop_bot(self):
        """
        Stop the automated trading bot
        """
        self.is_running = False
        logger.info("🛑 AI Trading Bot stopped")
    
    def _bot_loop(self):
        """
        Main bot loop for signal generation and execution
        """
        while self.is_running:
            try:
                # Generate signals for each symbol
                for symbol in self.config.symbols:
                    signal = self._generate_ai_signal(symbol)
                    
                    if signal and signal.confidence >= self.config.min_confidence:
                        self._process_signal(signal)
                
                # Check existing positions for exit signals
                self._check_position_exits()
                
                # Wait before next iteration
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Bot loop error: {str(e)}")
                time.sleep(60)  # Wait longer on error
    
    def _generate_ai_signal(self, symbol: str) -> Optional[TradingSignal]:
        """
        Generate AI trading signal for a symbol
        """
        try:
            # Get market data
            market_data = self._get_market_data(symbol)
            if not market_data:
                return None
            
            # Get social sentiment
            social_sentiment = self._analyze_social_sentiment(symbol)
            
            # Technical analysis
            technical_score = self._technical_analysis(symbol, market_data)
            
            # Market momentum
            momentum_score = self._analyze_momentum(symbol, market_data)
            
            # Volatility analysis
            volatility_score = self._analyze_volatility(symbol, market_data)
            
            # Combine signals using AI model weights
            combined_score = (
                social_sentiment * self.model_weights['social_sentiment'] +
                technical_score * self.model_weights['technical_analysis'] +
                momentum_score * self.model_weights['market_momentum'] +
                volatility_score * self.model_weights['volatility']
            )
            
            # Determine action and confidence
            if combined_score > 0.7:
                action = 'buy'
                confidence = min(combined_score, 0.95)
            elif combined_score < -0.7:
                action = 'sell'
                confidence = min(abs(combined_score), 0.95)
            else:
                action = 'hold'
                confidence = 0.5
            
            # Skip hold signals
            if action == 'hold':
                return None
            
            # Calculate price targets
            current_price = market_data['price']
            if action == 'buy':
                price_target = current_price * (1 + self.config.take_profit_pct)
                stop_loss = current_price * (1 - self.config.stop_loss_pct)
            else:
                price_target = current_price * (1 - self.config.take_profit_pct)
                stop_loss = current_price * (1 + self.config.stop_loss_pct)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(symbol, social_sentiment, technical_score, momentum_score, action)
            
            signal = TradingSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                price_target=price_target,
                stop_loss=stop_loss,
                reasoning=reasoning
            )
            
            self.signals_history.append(signal)
            logger.info(f"📊 Generated signal: {action.upper()} {symbol} (confidence: {confidence:.2f})")
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Error generating signal for {symbol}: {str(e)}")
            return None
    
    def _get_market_data(self, symbol: str) -> Optional[Dict]:
        """
        Get market data for symbol
        """
        try:
            # Simulate market data (in real implementation, use actual market data API)
            base_prices = {
                'BTC': 42000.0,
                'ETH': 2600.0,
                'AAPL': 185.0,
                'TSLA': 247.0,
                'NVDA': 890.0,
                'GOOGL': 144.0,
                'META': 328.0
            }
            
            if symbol not in base_prices:
                return None
            
            # Add some realistic price movement
            base_price = base_prices[symbol]
            price_change = random.uniform(-0.05, 0.05)  # ±5% random movement
            current_price = base_price * (1 + price_change)
            
            return {
                'symbol': symbol,
                'price': current_price,
                'change_24h': price_change * 100,
                'volume': random.randint(1000000, 10000000),
                'high_24h': current_price * 1.03,
                'low_24h': current_price * 0.97
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting market data for {symbol}: {str(e)}")
            return None
    
    def _analyze_social_sentiment(self, symbol: str) -> float:
        """
        Analyze social sentiment for symbol
        """
        try:
            # Get social media opinions
            opinions = multi_platform_crawler.fetch_all_platform_posts()
            
            sentiment_score = 0.0
            relevant_posts = 0
            
            for opinion in opinions:
                content = opinion.get('content', '').lower()
                
                # Check if post mentions the symbol
                if symbol.lower() in content or self._get_symbol_keywords(symbol, content):
                    relevant_posts += 1
                    
                    # Simple sentiment analysis
                    positive_words = ['bullish', 'buy', 'moon', 'pump', 'up', 'rise', 'gain', 'profit']
                    negative_words = ['bearish', 'sell', 'dump', 'down', 'fall', 'loss', 'crash']
                    
                    positive_count = sum(1 for word in positive_words if word in content)
                    negative_count = sum(1 for word in negative_words if word in content)
                    
                    if positive_count > negative_count:
                        sentiment_score += 0.1
                    elif negative_count > positive_count:
                        sentiment_score -= 0.1
            
            # Normalize sentiment score
            if relevant_posts > 0:
                sentiment_score = max(-1.0, min(1.0, sentiment_score))
            
            return sentiment_score
            
        except Exception as e:
            logger.error(f"❌ Error analyzing sentiment for {symbol}: {str(e)}")
            return 0.0
    
    def _get_symbol_keywords(self, symbol: str, content: str) -> bool:
        """
        Check if content mentions symbol-related keywords
        """
        keywords = {
            'BTC': ['bitcoin', 'btc'],
            'ETH': ['ethereum', 'eth'],
            'AAPL': ['apple', 'aapl'],
            'TSLA': ['tesla', 'tsla', 'elon'],
            'NVDA': ['nvidia', 'nvda'],
            'GOOGL': ['google', 'googl', 'alphabet'],
            'META': ['meta', 'facebook', 'fb']
        }
        
        symbol_keywords = keywords.get(symbol, [])
        return any(keyword in content for keyword in symbol_keywords)
    
    def _technical_analysis(self, symbol: str, market_data: Dict) -> float:
        """
        Perform technical analysis
        """
        try:
            # Simplified technical analysis
            price = market_data['price']
            high_24h = market_data['high_24h']
            low_24h = market_data['low_24h']
            
            # RSI-like indicator
            price_position = (price - low_24h) / (high_24h - low_24h)
            
            # Generate score based on price position
            if price_position > 0.8:
                return -0.5  # Overbought
            elif price_position < 0.2:
                return 0.5   # Oversold
            else:
                return 0.0   # Neutral
                
        except Exception as e:
            logger.error(f"❌ Error in technical analysis for {symbol}: {str(e)}")
            return 0.0
    
    def _analyze_momentum(self, symbol: str, market_data: Dict) -> float:
        """
        Analyze market momentum
        """
        try:
            change_24h = market_data['change_24h']
            volume = market_data['volume']
            
            # Momentum based on price change and volume
            momentum_score = change_24h / 100  # Normalize to -1 to 1
            
            # Boost momentum if high volume
            if volume > 5000000:  # High volume threshold
                momentum_score *= 1.2
            
            return max(-1.0, min(1.0, momentum_score))
            
        except Exception as e:
            logger.error(f"❌ Error analyzing momentum for {symbol}: {str(e)}")
            return 0.0
    
    def _analyze_volatility(self, symbol: str, market_data: Dict) -> float:
        """
        Analyze volatility
        """
        try:
            high_24h = market_data['high_24h']
            low_24h = market_data['low_24h']
            price = market_data['price']
            
            # Calculate volatility
            volatility = (high_24h - low_24h) / price
            
            # High volatility can be opportunity or risk
            if volatility > 0.1:  # High volatility
                return 0.2  # Slight positive for opportunities
            else:
                return -0.1  # Slight negative for low volatility
                
        except Exception as e:
            logger.error(f"❌ Error analyzing volatility for {symbol}: {str(e)}")
            return 0.0
    
    def _generate_reasoning(self, symbol: str, sentiment: float, technical: float, momentum: float, action: str) -> str:
        """
        Generate human-readable reasoning for the signal
        """
        reasons = []
        
        if sentiment > 0.1:
            reasons.append("positive social sentiment")
        elif sentiment < -0.1:
            reasons.append("negative social sentiment")
        
        if technical > 0.1:
            reasons.append("oversold technical conditions")
        elif technical < -0.1:
            reasons.append("overbought technical conditions")
        
        if momentum > 0.1:
            reasons.append("strong upward momentum")
        elif momentum < -0.1:
            reasons.append("strong downward momentum")
        
        if not reasons:
            reasons.append("mixed market signals")
        
        return f"AI recommends {action.upper()} {symbol} based on: {', '.join(reasons)}"
    
    def _process_signal(self, signal: TradingSignal):
        """
        Process and execute trading signal
        """
        try:
            # Check if we already have a position in this symbol
            if signal.symbol in self.active_positions:
                logger.info(f"⚠️ Already have position in {signal.symbol}, skipping signal")
                return
            
            # Calculate position size
            position_size = self._calculate_position_size(signal)
            if position_size <= 0:
                logger.warning(f"⚠️ Position size too small for {signal.symbol}")
                return
            
            # Create trade order
            order = TradeOrder(
                symbol=signal.symbol,
                side=signal.action,
                quantity=position_size,
                order_type='market',
                stop_loss=signal.stop_loss,
                take_profit=signal.price_target
            )
            
            # Execute trade
            result = real_trading_engine.execute_trade(self.user_id, order)
            
            if result.success:
                # Track position
                self.active_positions[signal.symbol] = {
                    'side': signal.action,
                    'quantity': position_size,
                    'entry_price': result.executed_price,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.price_target,
                    'timestamp': datetime.now(),
                    'signal': signal
                }
                
                self.performance_metrics['total_trades'] += 1
                
                logger.info(f"✅ Executed {signal.action.upper()} {signal.symbol}: {position_size} @ ${result.executed_price}")
                
            else:
                logger.error(f"❌ Failed to execute signal for {signal.symbol}: {result.message}")
                
        except Exception as e:
            logger.error(f"❌ Error processing signal for {signal.symbol}: {str(e)}")
    
    def _calculate_position_size(self, signal: TradingSignal) -> float:
        """
        Calculate position size based on risk management
        """
        try:
            # Get account info
            account_info = real_trading_engine.get_account_info(self.user_id)
            if 'error' in account_info:
                return 0.0
            
            balance = account_info.get('balance', 0)
            if balance <= 0:
                return 0.0
            
            # Risk-based position sizing
            risk_amount = balance * self.config.risk_per_trade
            max_position = min(self.config.max_position_size, balance * 0.1)  # Max 10% of balance
            
            # Get current price
            market_data = self._get_market_data(signal.symbol)
            if not market_data:
                return 0.0
            
            current_price = market_data['price']
            
            # Calculate position size based on stop loss
            if signal.stop_loss:
                price_diff = abs(current_price - signal.stop_loss)
                if price_diff > 0:
                    position_value = risk_amount / (price_diff / current_price)
                    position_value = min(position_value, max_position)
                    
                    # Convert to quantity
                    if signal.symbol in ['BTC', 'ETH']:  # Crypto
                        return position_value / current_price
                    else:  # Stocks
                        return int(position_value / current_price)
            
            # Fallback: use max position size
            if signal.symbol in ['BTC', 'ETH']:
                return max_position / current_price
            else:
                return int(max_position / current_price)
                
        except Exception as e:
            logger.error(f"❌ Error calculating position size: {str(e)}")
            return 0.0
    
    def _check_position_exits(self):
        """
        Check existing positions for exit conditions
        """
        try:
            positions_to_close = []
            
            for symbol, position in self.active_positions.items():
                market_data = self._get_market_data(symbol)
                if not market_data:
                    continue
                
                current_price = market_data['price']
                entry_price = position['entry_price']
                side = position['side']
                
                should_exit = False
                exit_reason = ""
                
                # Check stop loss
                if side == 'buy' and current_price <= position['stop_loss']:
                    should_exit = True
                    exit_reason = "stop loss triggered"
                elif side == 'sell' and current_price >= position['stop_loss']:
                    should_exit = True
                    exit_reason = "stop loss triggered"
                
                # Check take profit
                if side == 'buy' and current_price >= position['take_profit']:
                    should_exit = True
                    exit_reason = "take profit triggered"
                elif side == 'sell' and current_price <= position['take_profit']:
                    should_exit = True
                    exit_reason = "take profit triggered"
                
                # Check time-based exit (24 hours)
                if datetime.now() - position['timestamp'] > timedelta(hours=24):
                    should_exit = True
                    exit_reason = "time-based exit (24h)"
                
                if should_exit:
                    self._close_position(symbol, position, exit_reason)
                    positions_to_close.append(symbol)
            
            # Remove closed positions
            for symbol in positions_to_close:
                del self.active_positions[symbol]
                
        except Exception as e:
            logger.error(f"❌ Error checking position exits: {str(e)}")
    
    def _close_position(self, symbol: str, position: Dict, reason: str):
        """
        Close a position
        """
        try:
            # Create exit order (opposite side)
            exit_side = 'sell' if position['side'] == 'buy' else 'buy'
            
            order = TradeOrder(
                symbol=symbol,
                side=exit_side,
                quantity=position['quantity'],
                order_type='market'
            )
            
            result = real_trading_engine.execute_trade(self.user_id, order)
            
            if result.success:
                # Calculate P&L
                entry_price = position['entry_price']
                exit_price = result.executed_price
                quantity = position['quantity']
                
                if position['side'] == 'buy':
                    pnl = (exit_price - entry_price) * quantity
                else:
                    pnl = (entry_price - exit_price) * quantity
                
                self.performance_metrics['total_pnl'] += pnl
                
                if pnl > 0:
                    self.performance_metrics['winning_trades'] += 1
                
                # Update win rate
                if self.performance_metrics['total_trades'] > 0:
                    self.performance_metrics['win_rate'] = (
                        self.performance_metrics['winning_trades'] / 
                        self.performance_metrics['total_trades']
                    )
                
                logger.info(f"✅ Closed {symbol} position: {exit_side.upper()} @ ${exit_price} | P&L: ${pnl:.2f} | Reason: {reason}")
                
            else:
                logger.error(f"❌ Failed to close {symbol} position: {result.message}")
                
        except Exception as e:
            logger.error(f"❌ Error closing position for {symbol}: {str(e)}")
    
    def get_bot_status(self) -> Dict[str, Any]:
        """
        Get bot status and performance
        """
        return {
            'is_running': self.is_running,
            'config': {
                'enabled': self.config.enabled,
                'symbols': self.config.symbols,
                'max_position_size': self.config.max_position_size,
                'risk_per_trade': self.config.risk_per_trade,
                'min_confidence': self.config.min_confidence
            },
            'active_positions': len(self.active_positions),
            'performance': self.performance_metrics,
            'recent_signals': [
                {
                    'symbol': signal.symbol,
                    'action': signal.action,
                    'confidence': signal.confidence,
                    'reasoning': signal.reasoning,
                    'timestamp': signal.timestamp.isoformat()
                }
                for signal in self.signals_history[-10:]  # Last 10 signals
            ]
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Update bot configuration
        """
        try:
            if 'enabled' in new_config:
                self.config.enabled = new_config['enabled']
            if 'max_position_size' in new_config:
                self.config.max_position_size = float(new_config['max_position_size'])
            if 'risk_per_trade' in new_config:
                self.config.risk_per_trade = float(new_config['risk_per_trade'])
            if 'min_confidence' in new_config:
                self.config.min_confidence = float(new_config['min_confidence'])
            if 'symbols' in new_config:
                self.config.symbols = new_config['symbols']
            
            logger.info("✅ Bot configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating bot config: {str(e)}")
            return False

# Global AI trading bot instance
ai_trading_bot = AITradingBot()

