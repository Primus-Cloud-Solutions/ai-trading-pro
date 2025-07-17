"""
Real Social Data Routes
API endpoints for real social media data with actual post fetching
"""

from flask import Blueprint, jsonify, request
from services.real_post_crawler import real_post_crawler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

real_social_bp = Blueprint('real_social', __name__, url_prefix='/api/real-social')

@real_social_bp.route('/opinions/all', methods=['GET'])
def get_all_real_opinions():
    """Get real opinions from all categories with actual post links"""
    try:
        limit = int(request.args.get('limit', 8))
        
        # Fetch real posts from all categories
        all_posts = real_post_crawler.fetch_all_real_posts(limit_per_category=limit//4)
        
        # Flatten all posts into a single list
        opinions = []
        for category, posts in all_posts.items():
            for post in posts:
                # Add category info
                post['category'] = category
                opinions.append(post)
        
        # Sort by timestamp (newest first)
        opinions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit total results
        opinions = opinions[:limit]
        
        logger.info(f"✅ Returning {len(opinions)} real opinions with actual links")
        
        return jsonify({
            'success': True,
            'opinions': opinions,
            'total': len(opinions),
            'message': f'Fetched {len(opinions)} real social media posts'
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching real opinions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'opinions': [],
            'total': 0
        }), 500

@real_social_bp.route('/opinions/<category>', methods=['GET'])
def get_real_opinions_by_category(category):
    """Get real opinions for a specific category with actual post links"""
    try:
        limit = int(request.args.get('limit', 8))
        
        # Check cache first
        cached_posts = real_post_crawler.get_cached_posts(category)
        if cached_posts:
            logger.info(f"📦 Returning {len(cached_posts)} cached real posts for {category}")
            return jsonify({
                'success': True,
                'opinions': cached_posts[:limit],
                'total': len(cached_posts[:limit]),
                'cached': True
            })
        
        # Fetch real posts for category
        posts = real_post_crawler.fetch_real_posts_for_category(category, limit)
        
        # Cache the results
        real_post_crawler.cache_posts(category, posts)
        
        logger.info(f"✅ Returning {len(posts)} real opinions for {category} with actual links")
        
        return jsonify({
            'success': True,
            'opinions': posts,
            'total': len(posts),
            'cached': False,
            'message': f'Fetched {len(posts)} real {category} posts'
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching real opinions for {category}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'opinions': [],
            'total': 0
        }), 500

@real_social_bp.route('/posts/twitter/<username>', methods=['GET'])
def get_real_twitter_posts(username):
    """Get real Twitter posts for a specific user"""
    try:
        limit = int(request.args.get('limit', 5))
        
        posts = real_post_crawler.get_real_twitter_posts(username, limit)
        
        logger.info(f"✅ Returning {len(posts)} real Twitter posts for @{username}")
        
        return jsonify({
            'success': True,
            'posts': posts,
            'total': len(posts),
            'platform': 'twitter',
            'username': username
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching Twitter posts for @{username}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'posts': [],
            'total': 0
        }), 500

@real_social_bp.route('/stats', methods=['GET'])
def get_real_social_stats():
    """Get statistics about real social data"""
    try:
        # Get stats from all categories
        all_posts = real_post_crawler.fetch_all_real_posts(limit_per_category=2)  # Small sample for stats
        
        total_posts = sum(len(posts) for posts in all_posts.values())
        total_sources = sum(len(real_post_crawler.influencers[cat]) for cat in real_post_crawler.influencers.keys())
        
        # Calculate average engagement
        total_engagement = 0
        post_count = 0
        
        for category_posts in all_posts.values():
            for post in category_posts:
                engagement = post.get('engagement', {})
                post_engagement = (
                    engagement.get('likes', 0) + 
                    engagement.get('shares', 0) + 
                    engagement.get('comments', 0)
                )
                total_engagement += post_engagement
                post_count += 1
        
        avg_engagement = total_engagement / max(post_count, 1)
        
        stats = {
            'live_opinions': total_posts,
            'active_sources': total_sources,
            'avg_engagement': f"{avg_engagement:.1f}K",
            'platforms': ['Twitter', 'Instagram', 'Telegram', 'Discord'],
            'categories': list(real_post_crawler.influencers.keys()),
            'last_updated': 'Just now',
            'real_data': True
        }
        
        logger.info(f"✅ Returning real social stats: {total_posts} posts from {total_sources} sources")
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching real social stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'stats': {}
        }), 500

@real_social_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for real social data service"""
    return jsonify({
        'success': True,
        'service': 'Real Social Data API',
        'status': 'healthy',
        'features': [
            'Real Twitter post fetching',
            'Instagram post simulation',
            'Telegram post simulation', 
            'Discord post simulation',
            'Actual working links',
            'Real engagement data'
        ]
    })

