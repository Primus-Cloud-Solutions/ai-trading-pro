"""
Social Features Routes for AI Trading Platform
Handles comments, KOL opinions, and social interactions
"""

from flask import Blueprint, request, jsonify, session
import logging
import random
from datetime import datetime, timedelta
from models.social import Comment, KOLOpinion, SocialMetrics
from database import db

logger = logging.getLogger(__name__)

social_bp = Blueprint('social', __name__, url_prefix='/api/social')

@social_bp.route('/comments/<symbol>', methods=['GET'])
def get_comments(symbol):
    """Get comments for a specific symbol"""
    try:
        comments = Comment.query.filter_by(
            symbol=symbol.upper(), 
            is_active=True
        ).order_by(Comment.created_at.desc()).limit(50).all()
        
        return jsonify([comment.to_dict() for comment in comments])
    
    except Exception as e:
        logger.error(f"Error getting comments for {symbol}: {str(e)}")
        return jsonify({'error': 'Failed to load comments'}), 500

@social_bp.route('/comments', methods=['POST'])
def add_comment():
    """Add a new comment"""
    try:
        data = request.get_json()
        
        if not data or not data.get('symbol') or not data.get('content'):
            return jsonify({'error': 'Symbol and content are required'}), 400
        
        # Create new comment
        comment = Comment(
            symbol=data['symbol'].upper(),
            author_name=data.get('author_name', 'Anonymous Trader'),
            author_email=data.get('author_email'),
            content=data['content'],
            sentiment=data.get('sentiment', 'neutral')
        )
        
        db.session.add(comment)
        db.session.commit()
        
        logger.info(f"New comment added for {comment.symbol} by {comment.author_name}")
        
        return jsonify({
            'success': True,
            'comment': comment.to_dict()
        })
    
    except Exception as e:
        logger.error(f"Error adding comment: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to add comment'}), 500

@social_bp.route('/comments/<int:comment_id>/like', methods=['POST'])
def like_comment(comment_id):
    """Like a comment"""
    try:
        comment = Comment.query.get_or_404(comment_id)
        comment.likes += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'likes': comment.likes
        })
    
    except Exception as e:
        logger.error(f"Error liking comment {comment_id}: {str(e)}")
        return jsonify({'error': 'Failed to like comment'}), 500

@social_bp.route('/kols/opinions', methods=['GET'])
def get_kol_opinions():
    """Get KOL opinions"""
    try:
        # Get recent KOL opinions
        opinions = KOLOpinion.query.filter_by(
            is_active=True
        ).order_by(KOLOpinion.created_at.desc()).limit(20).all()
        
        # If no opinions in database, return mock data
        if not opinions:
            return jsonify(get_mock_kol_opinions())
        
        return jsonify([opinion.to_dict() for opinion in opinions])
    
    except Exception as e:
        logger.error(f"Error getting KOL opinions: {str(e)}")
        # Return mock data on error
        return jsonify(get_mock_kol_opinions())

@social_bp.route('/kols/opinions', methods=['POST'])
def add_kol_opinion():
    """Add a new KOL opinion (for admin/automated systems)"""
    try:
        data = request.get_json()
        
        if not data or not data.get('kol_name') or not data.get('content'):
            return jsonify({'error': 'KOL name and content are required'}), 400
        
        # Create new KOL opinion
        opinion = KOLOpinion(
            kol_name=data['kol_name'],
            platform=data.get('platform', 'twitter'),
            platform_handle=data.get('platform_handle'),
            content=data['content'],
            symbol=data.get('symbol'),
            sentiment=data.get('sentiment', 'neutral'),
            confidence_score=data.get('confidence_score'),
            source_url=data.get('source_url'),
            engagement_score=data.get('engagement_score', 0)
        )
        
        db.session.add(opinion)
        db.session.commit()
        
        logger.info(f"New KOL opinion added: {opinion.kol_name} on {opinion.platform}")
        
        return jsonify({
            'success': True,
            'opinion': opinion.to_dict()
        })
    
    except Exception as e:
        logger.error(f"Error adding KOL opinion: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to add KOL opinion'}), 500

@social_bp.route('/metrics/<symbol>', methods=['GET'])
def get_social_metrics(symbol):
    """Get social metrics for a symbol"""
    try:
        # Get recent metrics
        metrics = SocialMetrics.query.filter_by(
            symbol=symbol.upper()
        ).order_by(SocialMetrics.date.desc()).limit(30).all()
        
        return jsonify([metric.to_dict() for metric in metrics])
    
    except Exception as e:
        logger.error(f"Error getting social metrics for {symbol}: {str(e)}")
        return jsonify({'error': 'Failed to load social metrics'}), 500

def get_mock_kol_opinions():
    """Generate mock KOL opinions for demonstration"""
    mock_opinions = [
        {
            'id': 1,
            'name': 'CryptoKing',
            'platform': 'twitter',
            'platform_handle': '@cryptoking_pro',
            'content': 'TSLA looking strong here. The AI revolution is just beginning and Tesla is at the forefront. Expecting a breakout above $250 soon. 🚀 #TSLA #AI',
            'symbol': 'TSLA',
            'sentiment': 'Bullish',
            'confidence_score': 0.85,
            'engagement_score': 1250,
            'time': '2 hours ago'
        },
        {
            'id': 2,
            'name': 'StockGuru',
            'platform': 'telegram',
            'platform_handle': 'StockGuru_Official',
            'content': 'AAPL earnings coming up next week. Historical data shows strong performance post-earnings. However, current market conditions suggest we should be cautious with position sizing.',
            'symbol': 'AAPL',
            'sentiment': 'Neutral',
            'confidence_score': 0.65,
            'engagement_score': 890,
            'time': '4 hours ago'
        },
        {
            'id': 3,
            'name': 'TradeMaster',
            'platform': 'twitter',
            'platform_handle': '@trademaster_ai',
            'content': 'NVDA pullback presents a great buying opportunity. AI demand isn\'t going anywhere. This dip is a gift for long-term investors. Loading up here! 💎🙌',
            'symbol': 'NVDA',
            'sentiment': 'Bullish',
            'confidence_score': 0.92,
            'engagement_score': 2100,
            'time': '6 hours ago'
        },
        {
            'id': 4,
            'name': 'BearishBob',
            'platform': 'telegram',
            'platform_handle': 'BearishBob_Trades',
            'content': 'Market looking overextended here. Fed policy uncertainty and geopolitical tensions suggest we might see a 10-15% correction soon. Cash is king right now.',
            'symbol': None,
            'sentiment': 'Bearish',
            'confidence_score': 0.78,
            'engagement_score': 567,
            'time': '8 hours ago'
        },
        {
            'id': 5,
            'name': 'MemeCoinMania',
            'platform': 'discord',
            'platform_handle': 'MemeCoinMania#1337',
            'content': 'DOGE community is stronger than ever! Elon\'s latest tweets are bullish AF. Expecting a pump to $0.12 soon. Diamond hands! 🐕🚀',
            'symbol': 'DOGE-USD',
            'sentiment': 'Bullish',
            'confidence_score': 0.70,
            'engagement_score': 3400,
            'time': '12 hours ago'
        },
        {
            'id': 6,
            'name': 'TechAnalyst',
            'platform': 'twitter',
            'platform_handle': '@tech_analyst_pro',
            'content': 'META breaking out of its consolidation pattern. Strong support at $480. If we hold above this level, next target is $520. Risk/reward looks favorable.',
            'symbol': 'META',
            'sentiment': 'Bullish',
            'confidence_score': 0.75,
            'engagement_score': 1680,
            'time': '1 day ago'
        }
    ]
    
    # Add some randomization to make it feel more live
    for opinion in mock_opinions:
        # Randomly adjust engagement scores
        opinion['engagement_score'] += random.randint(-50, 100)
        
        # Randomly update some timestamps
        if random.random() < 0.3:
            hours_ago = random.randint(1, 24)
            opinion['time'] = f"{hours_ago} hour{'s' if hours_ago > 1 else ''} ago"
    
    return mock_opinions

# Initialize some sample data
def init_sample_social_data():
    """Initialize sample social data"""
    try:
        # Check if we already have data
        if KOLOpinion.query.first():
            return
        
        # Add sample KOL opinions
        sample_opinions = [
            KOLOpinion(
                kol_name='CryptoKing',
                platform='twitter',
                platform_handle='@cryptoking_pro',
                content='TSLA looking strong here. The AI revolution is just beginning and Tesla is at the forefront. Expecting a breakout above $250 soon.',
                symbol='TSLA',
                sentiment='Bullish',
                confidence_score=0.85,
                engagement_score=1250,
                created_at=datetime.utcnow() - timedelta(hours=2)
            ),
            KOLOpinion(
                kol_name='StockGuru',
                platform='telegram',
                platform_handle='StockGuru_Official',
                content='AAPL earnings coming up. Historical data shows strong performance post-earnings. However, current market conditions suggest caution.',
                symbol='AAPL',
                sentiment='Neutral',
                confidence_score=0.65,
                engagement_score=890,
                created_at=datetime.utcnow() - timedelta(hours=4)
            ),
            KOLOpinion(
                kol_name='TradeMaster',
                platform='twitter',
                platform_handle='@trademaster_ai',
                content='NVDA pullback presents a great buying opportunity. AI demand isn\'t going anywhere. This dip is a gift for long-term investors.',
                symbol='NVDA',
                sentiment='Bullish',
                confidence_score=0.92,
                engagement_score=2100,
                created_at=datetime.utcnow() - timedelta(hours=6)
            )
        ]
        
        for opinion in sample_opinions:
            db.session.add(opinion)
        
        db.session.commit()
        logger.info("Sample social data initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing sample social data: {str(e)}")
        db.session.rollback()

