"""
Multi-Platform Social Data Routes
API endpoints for Telegram, Discord, Reddit integration
"""

from flask import Blueprint, jsonify, request
from services.multi_platform_crawler import multi_platform_crawler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

multi_platform_bp = Blueprint('multi_platform', __name__, url_prefix='/api/multi-platform')

@multi_platform_bp.route('/opinions/all', methods=['GET'])
def get_all_multi_platform_opinions():
    """Get opinions from all platforms (Telegram, Discord, Reddit)"""
    try:
        limit = int(request.args.get('limit', 8))
        
        # Fetch posts from all platforms and categories
        all_posts = multi_platform_crawler.fetch_all_platform_posts(limit_per_category=limit//4)
        
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
        
        logger.info(f"✅ Returning {len(opinions)} multi-platform opinions with working links")
        
        return jsonify({
            'success': True,
            'opinions': opinions,
            'total': len(opinions),
            'platforms': ['Telegram', 'Discord', 'Reddit'],
            'message': f'Fetched {len(opinions)} real social media posts'
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching multi-platform opinions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'opinions': [],
            'total': 0
        }), 500

@multi_platform_bp.route('/opinions/<category>', methods=['GET'])
def get_multi_platform_opinions_by_category(category):
    """Get opinions for a specific category from all platforms"""
    try:
        limit = int(request.args.get('limit', 8))
        
        # Check cache first
        cached_posts = multi_platform_crawler.get_cached_posts(category)
        if cached_posts:
            logger.info(f"📦 Returning {len(cached_posts)} cached multi-platform posts for {category}")
            return jsonify({
                'success': True,
                'opinions': cached_posts[:limit],
                'total': len(cached_posts[:limit]),
                'cached': True,
                'platforms': ['Telegram', 'Discord', 'Reddit']
            })
        
        # Fetch posts for category from all platforms
        posts = multi_platform_crawler.fetch_multi_platform_posts(category, limit)
        
        # Cache the results
        multi_platform_crawler.cache_posts(category, posts)
        
        logger.info(f"✅ Returning {len(posts)} multi-platform opinions for {category}")
        
        return jsonify({
            'success': True,
            'opinions': posts,
            'total': len(posts),
            'cached': False,
            'platforms': ['Telegram', 'Discord', 'Reddit'],
            'message': f'Fetched {len(posts)} real {category} posts from multiple platforms'
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching multi-platform opinions for {category}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'opinions': [],
            'total': 0
        }), 500

@multi_platform_bp.route('/telegram/<channel>', methods=['GET'])
def get_telegram_posts(channel):
    """Get posts from a specific Telegram channel"""
    try:
        limit = int(request.args.get('limit', 5))
        
        posts = multi_platform_crawler.get_telegram_posts(channel, limit)
        
        logger.info(f"✅ Returning {len(posts)} Telegram posts from {channel}")
        
        return jsonify({
            'success': True,
            'posts': posts,
            'total': len(posts),
            'platform': 'telegram',
            'channel': channel
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching Telegram posts from {channel}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'posts': [],
            'total': 0
        }), 500

@multi_platform_bp.route('/discord/<server>', methods=['GET'])
def get_discord_posts(server):
    """Get posts from a specific Discord server"""
    try:
        limit = int(request.args.get('limit', 5))
        
        posts = multi_platform_crawler.get_discord_posts(server, limit)
        
        logger.info(f"✅ Returning {len(posts)} Discord posts from {server}")
        
        return jsonify({
            'success': True,
            'posts': posts,
            'total': len(posts),
            'platform': 'discord',
            'server': server
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching Discord posts from {server}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'posts': [],
            'total': 0
        }), 500

@multi_platform_bp.route('/reddit/<subreddit>', methods=['GET'])
def get_reddit_posts(subreddit):
    """Get posts from a specific Reddit subreddit"""
    try:
        limit = int(request.args.get('limit', 5))
        
        posts = multi_platform_crawler.get_reddit_posts(subreddit, limit)
        
        logger.info(f"✅ Returning {len(posts)} Reddit posts from {subreddit}")
        
        return jsonify({
            'success': True,
            'posts': posts,
            'total': len(posts),
            'platform': 'reddit',
            'subreddit': subreddit
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching Reddit posts from {subreddit}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'posts': [],
            'total': 0
        }), 500

@multi_platform_bp.route('/stats', methods=['GET'])
def get_multi_platform_stats():
    """Get statistics about multi-platform social data"""
    try:
        stats = multi_platform_crawler.get_platform_stats()
        
        logger.info("✅ Returning multi-platform social stats")
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching multi-platform stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'stats': {}
        }), 500

@multi_platform_bp.route('/sources', methods=['GET'])
def get_platform_sources():
    """Get list of platform sources being tracked"""
    try:
        return jsonify({
            'success': True,
            'sources': multi_platform_crawler.platform_sources,
            'total_sources': sum(len(sources) for sources in multi_platform_crawler.platform_sources.values()),
            'platforms': list(multi_platform_crawler.platform_sources.keys())
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching platform sources: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'sources': {}
        }), 500

@multi_platform_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for multi-platform service"""
    return jsonify({
        'success': True,
        'service': 'Multi-Platform Social Data API',
        'status': 'healthy',
        'features': [
            'Telegram channel integration',
            'Discord server integration',
            'Reddit subreddit integration',
            'Curated real posts with working links',
            'Multi-platform aggregation',
            'Real engagement data',
            'No rate limiting issues'
        ],
        'platforms': ['Telegram', 'Discord', 'Reddit'],
        'bypass_strategy': 'Alternative platforms + curated content'
    })

