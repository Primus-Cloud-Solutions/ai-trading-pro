"""
Social Features Models for AI Trading Platform
Handles comments, KOL opinions, and social interactions
"""

from datetime import datetime
from database import db

class Comment(db.Model):
    """Model for user comments on predictions"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, index=True)
    author_name = db.Column(db.String(100), nullable=False)
    author_email = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=True)  # bullish, bearish, neutral
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    likes = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'author_name': self.author_name,
            'content': self.content,
            'sentiment': self.sentiment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'likes': self.likes,
            'time_ago': self._get_time_ago()
        }
    
    def _get_time_ago(self):
        """Get human-readable time difference"""
        if not self.created_at:
            return "Unknown"
        
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

class KOLOpinion(db.Model):
    """Model for KOL (Key Opinion Leader) opinions and insights"""
    __tablename__ = 'kol_opinions'
    
    id = db.Column(db.Integer, primary_key=True)
    kol_name = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # twitter, telegram, discord, etc.
    platform_handle = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)
    symbol = db.Column(db.String(10), nullable=True, index=True)  # Related stock/crypto symbol
    sentiment = db.Column(db.String(20), nullable=False)  # bullish, bearish, neutral
    confidence_score = db.Column(db.Float, nullable=True)  # 0-1 confidence in the opinion
    source_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    engagement_score = db.Column(db.Integer, default=0)  # likes, retweets, etc.
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.kol_name,
            'platform': self.platform,
            'platform_handle': self.platform_handle,
            'content': self.content,
            'symbol': self.symbol,
            'sentiment': self.sentiment,
            'confidence_score': self.confidence_score,
            'source_url': self.source_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'engagement_score': self.engagement_score,
            'time': self._get_time_ago()
        }
    
    def _get_time_ago(self):
        """Get human-readable time difference"""
        if not self.created_at:
            return "Unknown"
        
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

class SocialMetrics(db.Model):
    """Model for tracking social engagement metrics"""
    __tablename__ = 'social_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    total_comments = db.Column(db.Integer, default=0)
    bullish_sentiment = db.Column(db.Integer, default=0)
    bearish_sentiment = db.Column(db.Integer, default=0)
    neutral_sentiment = db.Column(db.Integer, default=0)
    kol_mentions = db.Column(db.Integer, default=0)
    engagement_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'date': self.date.isoformat() if self.date else None,
            'total_comments': self.total_comments,
            'bullish_sentiment': self.bullish_sentiment,
            'bearish_sentiment': self.bearish_sentiment,
            'neutral_sentiment': self.neutral_sentiment,
            'kol_mentions': self.kol_mentions,
            'engagement_score': self.engagement_score
        }

