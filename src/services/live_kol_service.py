"""
Live KOL Opinion Service
Provides real-time updates for KOL opinions organized by asset classes
"""

import random
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class LiveKOLService:
    def __init__(self):
        self.active_feeds = {}
        self.opinion_cache = {}
        self.update_interval = 15  # seconds
        self.running = False
        self.update_thread = None
        
        # Asset class configurations
        self.asset_classes = {
            'stocks': {
                'symbols': ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA', 'META', 'AMZN', 'NFLX'],
                'kols': [
                    {'name': 'StockGuru', 'platform': 'twitter', 'handle': '@stockguru_pro', 'followers': 125000},
                    {'name': 'WallStreetWiz', 'platform': 'telegram', 'handle': 'WallStreetWiz_Official', 'followers': 89000},
                    {'name': 'TechAnalyst', 'platform': 'twitter', 'handle': '@tech_analyst_ai', 'followers': 156000},
                    {'name': 'MarketMaven', 'platform': 'discord', 'handle': 'MarketMaven#1234', 'followers': 67000}
                ]
            },
            'crypto': {
                'symbols': ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'DOT-USD', 'LINK-USD'],
                'kols': [
                    {'name': 'CryptoKing', 'platform': 'twitter', 'handle': '@cryptoking_pro', 'followers': 234000},
                    {'name': 'BlockchainBull', 'platform': 'telegram', 'handle': 'BlockchainBull_Channel', 'followers': 178000},
                    {'name': 'DeFiDegen', 'platform': 'twitter', 'handle': '@defi_degen_alpha', 'followers': 98000},
                    {'name': 'CryptoWhale', 'platform': 'discord', 'handle': 'CryptoWhale#9999', 'followers': 145000}
                ]
            },
            'meme': {
                'symbols': ['DOGE-USD', 'SHIB-USD', 'PEPE-USD', 'FLOKI-USD', 'BONK-USD'],
                'kols': [
                    {'name': 'MemeKing', 'platform': 'twitter', 'handle': '@meme_king_official', 'followers': 89000},
                    {'name': 'DogeWhisperer', 'platform': 'telegram', 'handle': 'DogeWhisperer_Alpha', 'followers': 67000},
                    {'name': 'ShibArmy', 'platform': 'twitter', 'handle': '@shib_army_leader', 'followers': 123000},
                    {'name': 'PepeMaster', 'platform': 'discord', 'handle': 'PepeMaster#4200', 'followers': 45000}
                ]
            },
            'forex': {
                'symbols': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD'],
                'kols': [
                    {'name': 'ForexPro', 'platform': 'twitter', 'handle': '@forex_pro_trader', 'followers': 78000},
                    {'name': 'CurrencyMaster', 'platform': 'telegram', 'handle': 'CurrencyMaster_FX', 'followers': 56000},
                    {'name': 'FXAnalyst', 'platform': 'twitter', 'handle': '@fx_analyst_live', 'followers': 92000}
                ]
            }
        }
        
        # Opinion templates for realistic content generation
        self.opinion_templates = {
            'bullish': [
                "{symbol} looking incredibly strong here. The fundamentals are solid and technical analysis shows clear upward momentum. Expecting significant gains in the coming days.",
                "Just analyzed {symbol} and the setup is perfect for a breakout. Volume is increasing and all indicators are aligning bullish. This could be the start of a major move.",
                "{symbol} has been consolidating beautifully. The next leg up should take us to new highs. Risk/reward is excellent at current levels.",
                "Strong accumulation happening in {symbol}. Smart money is positioning for the next rally. Don't miss this opportunity.",
                "Technical analysis on {symbol} shows a perfect bull flag formation. Expecting a 15-20% move higher in the next few weeks."
            ],
            'bearish': [
                "{symbol} showing signs of weakness. Distribution pattern is forming and momentum is fading. Consider taking profits or reducing exposure.",
                "Warning signs flashing for {symbol}. Volume is declining and we're seeing bearish divergence. A correction seems imminent.",
                "{symbol} has reached overbought levels. Historical data suggests a pullback is due. Waiting for better entry points.",
                "Concerned about {symbol} here. The rally looks exhausted and we're seeing selling pressure from institutional players.",
                "Technical breakdown in {symbol}. Support levels are failing and the trend is turning bearish. Time to be cautious."
            ],
            'neutral': [
                "{symbol} is in a consolidation phase. Waiting for a clear direction before making any moves. Patience is key in this market.",
                "Mixed signals on {symbol} right now. Some indicators bullish, others bearish. Need more confirmation before taking a position.",
                "{symbol} trading in a tight range. Breakout could go either way. Watching key levels for the next move.",
                "Sideways action in {symbol} continues. Market seems indecisive. Better opportunities elsewhere for now.",
                "No clear trend in {symbol} at the moment. Staying on the sidelines until we get more clarity."
            ]
        }
        
        self.initialize_cache()
    
    def initialize_cache(self):
        """Initialize opinion cache with sample data"""
        for asset_class, config in self.asset_classes.items():
            self.opinion_cache[asset_class] = []
            
            # Generate initial opinions for each asset class
            for _ in range(random.randint(3, 6)):
                opinion = self.generate_opinion(asset_class, config)
                self.opinion_cache[asset_class].append(opinion)
    
    def generate_opinion(self, asset_class: str, config: Dict) -> Dict[str, Any]:
        """Generate a realistic KOL opinion"""
        kol = random.choice(config['kols'])
        symbol = random.choice(config['symbols'])
        sentiment = random.choice(['bullish', 'bearish', 'neutral'])
        
        # Weight sentiments based on market conditions
        sentiment_weights = {'bullish': 0.4, 'bearish': 0.3, 'neutral': 0.3}
        sentiment = random.choices(
            list(sentiment_weights.keys()),
            weights=list(sentiment_weights.values())
        )[0]
        
        template = random.choice(self.opinion_templates[sentiment])
        content = template.format(symbol=symbol)
        
        # Add some variation to content
        if asset_class == 'meme':
            emojis = ['🚀', '🌙', '💎', '🙌', '🔥', '⚡', '💪', '🎯']
            content += f" {random.choice(emojis)}"
        
        # Generate realistic timestamps
        minutes_ago = random.randint(1, 180)
        timestamp = datetime.now() - timedelta(minutes=minutes_ago)
        
        return {
            'id': int(time.time() * 1000) + random.randint(1, 999),
            'name': kol['name'],
            'platform': kol['platform'],
            'platform_handle': kol['handle'],
            'content': content,
            'symbol': symbol,
            'asset_class': asset_class,
            'sentiment': sentiment,
            'timestamp': timestamp.isoformat(),
            'time_ago': self.format_time_ago(minutes_ago),
            'engagement_score': random.randint(50, kol['followers'] // 10),
            'likes': random.randint(10, 500),
            'retweets': random.randint(5, 200),
            'replies': random.randint(2, 50),
            'verified': random.choice([True, False]),
            'trending': random.choice([True, False]) if random.random() < 0.2 else False
        }
    
    def format_time_ago(self, minutes: int) -> str:
        """Format time ago string"""
        if minutes < 60:
            return f"{minutes} min ago"
        elif minutes < 1440:  # 24 hours
            hours = minutes // 60
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = minutes // 1440
            return f"{days} day{'s' if days > 1 else ''} ago"
    
    def start_live_feed(self):
        """Start the live opinion feed"""
        if self.running:
            return
        
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        logger.info("🔴 Live KOL opinion feed started")
    
    def stop_live_feed(self):
        """Stop the live opinion feed"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        logger.info("⏹️ Live KOL opinion feed stopped")
    
    def _update_loop(self):
        """Main update loop for live opinions"""
        while self.running:
            try:
                # Add new opinions randomly
                if random.random() < 0.7:  # 70% chance to add new opinion
                    asset_class = random.choice(list(self.asset_classes.keys()))
                    config = self.asset_classes[asset_class]
                    new_opinion = self.generate_opinion(asset_class, config)
                    
                    # Add to cache and limit size
                    self.opinion_cache[asset_class].insert(0, new_opinion)
                    if len(self.opinion_cache[asset_class]) > 20:
                        self.opinion_cache[asset_class] = self.opinion_cache[asset_class][:20]
                    
                    logger.info(f"📢 New {asset_class} opinion from {new_opinion['name']}: {new_opinion['symbol']}")
                
                # Update engagement scores for existing opinions
                self._update_engagement_scores()
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in KOL update loop: {e}")
                time.sleep(5)
    
    def _update_engagement_scores(self):
        """Update engagement scores for existing opinions"""
        for asset_class in self.opinion_cache:
            for opinion in self.opinion_cache[asset_class]:
                # Simulate engagement growth
                if random.random() < 0.3:  # 30% chance to update
                    opinion['likes'] += random.randint(0, 10)
                    opinion['retweets'] += random.randint(0, 5)
                    opinion['replies'] += random.randint(0, 3)
                    opinion['engagement_score'] = opinion['likes'] + opinion['retweets'] * 2 + opinion['replies'] * 3
    
    def get_opinions_by_asset_class(self, asset_class: str = 'all', limit: int = 10) -> List[Dict[str, Any]]:
        """Get opinions filtered by asset class"""
        if asset_class == 'all':
            all_opinions = []
            for opinions in self.opinion_cache.values():
                all_opinions.extend(opinions)
            
            # Sort by timestamp (newest first)
            all_opinions.sort(key=lambda x: x['timestamp'], reverse=True)
            return all_opinions[:limit]
        
        if asset_class in self.opinion_cache:
            return self.opinion_cache[asset_class][:limit]
        
        return []
    
    def get_trending_opinions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get trending opinions across all asset classes"""
        all_opinions = []
        for opinions in self.opinion_cache.values():
            all_opinions.extend([op for op in opinions if op.get('trending', False)])
        
        # Sort by engagement score
        all_opinions.sort(key=lambda x: x['engagement_score'], reverse=True)
        return all_opinions[:limit]
    
    def get_live_activity_feed(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get live activity feed for the activity stream"""
        activities = []
        
        # Recent opinions
        recent_opinions = self.get_opinions_by_asset_class('all', limit // 2)
        for opinion in recent_opinions:
            activities.append({
                'type': 'opinion',
                'icon': 'comment',
                'text': f"{opinion['name']} shared insights on {opinion['symbol']}",
                'time': opinion['time_ago'],
                'sentiment': opinion['sentiment'],
                'platform': opinion['platform']
            })
        
        # Simulated market events
        market_events = [
            {'type': 'whale_movement', 'icon': 'whale', 'text': 'Large BTC movement detected: $2.5M transfer', 'time': '5 min ago'},
            {'type': 'volume_spike', 'icon': 'chart-bar', 'text': 'TSLA volume spike: 300% above average', 'time': '12 min ago'},
            {'type': 'news_alert', 'icon': 'newspaper', 'text': 'Breaking: Fed announces new policy changes', 'time': '18 min ago'},
            {'type': 'social_buzz', 'icon': 'fire', 'text': 'DOGE trending on Twitter with 50K mentions', 'time': '25 min ago'}
        ]
        
        # Add some market events
        for event in random.sample(market_events, min(3, len(market_events))):
            activities.append(event)
        
        # Sort by recency (simulated)
        random.shuffle(activities)
        return activities[:limit]
    
    def get_asset_class_stats(self) -> Dict[str, Any]:
        """Get statistics for each asset class"""
        stats = {}
        total_opinions = 0
        total_sources = 0
        
        for asset_class, opinions in self.opinion_cache.items():
            opinion_count = len(opinions)
            unique_sources = len(set(op['name'] for op in opinions))
            
            stats[asset_class] = {
                'opinion_count': opinion_count,
                'unique_sources': unique_sources,
                'avg_engagement': sum(op['engagement_score'] for op in opinions) / max(1, opinion_count),
                'sentiment_distribution': self._calculate_sentiment_distribution(opinions)
            }
            
            total_opinions += opinion_count
            total_sources += unique_sources
        
        stats['total'] = {
            'total_opinions': total_opinions,
            'total_sources': total_sources,
            'active_feeds': len([ac for ac in self.asset_classes.keys() if self.opinion_cache.get(ac)])
        }
        
        return stats
    
    def _calculate_sentiment_distribution(self, opinions: List[Dict]) -> Dict[str, float]:
        """Calculate sentiment distribution for opinions"""
        if not opinions:
            return {'bullish': 0, 'bearish': 0, 'neutral': 0}
        
        sentiment_counts = {'bullish': 0, 'bearish': 0, 'neutral': 0}
        for opinion in opinions:
            sentiment_counts[opinion['sentiment']] += 1
        
        total = len(opinions)
        return {
            sentiment: (count / total) * 100
            for sentiment, count in sentiment_counts.items()
        }

# Global instance
live_kol_service = LiveKOLService()

