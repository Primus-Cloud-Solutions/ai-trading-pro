"""
Social Engagement Models
Database models for real social media engagement features
"""

from database import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

class SocialInfluencer(db.Model):
    """Model for tracking social media influencers"""
    __tablename__ = 'social_influencers'
    
    id = Column(Integer, primary_key=True)
    handle = Column(String(100), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    platform = Column(String(50), nullable=False)  # twitter, telegram, discord, instagram
    category = Column(String(50), nullable=False)  # stocks, crypto, meme, forex
    followers = Column(String(20))  # e.g., "572.9K", "1.2M"
    verified = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    opinions = relationship("SocialOpinion", back_populates="influencer", cascade="all, delete-orphan")

class SocialOpinion(db.Model):
    """Model for storing social media opinions/posts"""
    __tablename__ = 'social_opinions'
    
    id = Column(Integer, primary_key=True)
    external_id = Column(String(100))  # Original post ID from platform
    influencer_id = Column(Integer, ForeignKey('social_influencers.id'), nullable=False)
    content = Column(Text, nullable=False)
    symbol = Column(String(20))  # Stock/crypto symbol mentioned
    sentiment = Column(String(20))  # bullish, bearish, neutral
    platform = Column(String(50), nullable=False)
    original_timestamp = Column(DateTime)  # When posted on original platform
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Engagement metrics
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    clicks_count = Column(Integer, default=0)
    
    # Relationships
    influencer = relationship("SocialInfluencer", back_populates="opinions")
    comments = relationship("OpinionComment", back_populates="opinion", cascade="all, delete-orphan")
    likes = relationship("OpinionLike", back_populates="opinion", cascade="all, delete-orphan")

class OpinionComment(db.Model):
    """Model for user comments on social opinions"""
    __tablename__ = 'opinion_comments'
    
    id = Column(Integer, primary_key=True)
    opinion_id = Column(Integer, ForeignKey('social_opinions.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Nullable for anonymous comments
    author_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    sentiment = Column(String(20))  # bullish, bearish, neutral
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    opinion = relationship("SocialOpinion", back_populates="comments")
    user = relationship("User", backref="opinion_comments")

class OpinionLike(db.Model):
    """Model for tracking likes on social opinions"""
    __tablename__ = 'opinion_likes'
    
    id = Column(Integer, primary_key=True)
    opinion_id = Column(Integer, ForeignKey('social_opinions.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user_identifier = Column(String(100))  # For anonymous users (IP, session, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    opinion = relationship("SocialOpinion", back_populates="likes")
    user = relationship("User", backref="opinion_likes")

class SocialActivity(db.Model):
    """Model for tracking social media activity feed"""
    __tablename__ = 'social_activities'
    
    id = Column(Integer, primary_key=True)
    activity_type = Column(String(50), nullable=False)  # opinion, news, trade, etc.
    title = Column(String(200), nullable=False)
    description = Column(Text)
    author = Column(String(100))
    platform = Column(String(50))
    category = Column(String(50))  # stocks, crypto, meme, forex
    symbol = Column(String(20))
    engagement_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class TelegramChannel(db.Model):
    """Model for tracking Telegram channels"""
    __tablename__ = 'telegram_channels'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    username = Column(String(100))  # @channel_username
    category = Column(String(50), nullable=False)  # stocks, crypto, meme, forex
    subscribers = Column(String(20))  # e.g., "100K+", "45K"
    description = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("TelegramMessage", back_populates="channel", cascade="all, delete-orphan")

class TelegramMessage(db.Model):
    """Model for storing Telegram channel messages"""
    __tablename__ = 'telegram_messages'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('telegram_channels.id'), nullable=False)
    external_id = Column(String(100))  # Original message ID
    content = Column(Text, nullable=False)
    symbol = Column(String(20))
    sentiment = Column(String(20))
    original_timestamp = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Engagement metrics
    views_count = Column(Integer, default=0)
    reactions_count = Column(Integer, default=0)
    forwards_count = Column(Integer, default=0)
    
    # Relationships
    channel = relationship("TelegramChannel", back_populates="messages")

class SocialEngagementMetrics(db.Model):
    """Model for tracking overall social engagement metrics"""
    __tablename__ = 'social_engagement_metrics'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    platform = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    
    # Daily metrics
    total_opinions = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    avg_sentiment_score = Column(Integer, default=0)  # -100 to 100
    top_symbols = Column(JSON)  # List of most mentioned symbols
    
    created_at = Column(DateTime, default=datetime.utcnow)

