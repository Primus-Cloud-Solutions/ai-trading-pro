"""
Real Social Data Routes
API endpoints for fetching live data from real trading influencers
"""

from flask import Blueprint, jsonify, request
from services.real_social_crawler import real_social_crawler
import logging

logger = logging.getLogger(__name__)

real_social_bp = Blueprint('real_social', __name__, url_prefix='/api/real-social')

@real_social_bp.route('/opinions/stocks', methods=['GET'])
def get_stock_opinions():
    """Get live stock trading opinions from real influencers"""
    try:
        limit = request.args.get('limit', 10, type=int)
        opinions = real_social_crawler.get_live_stock_opinions(limit)
        
        return jsonify({
            "success": True,
            "data": opinions,
            "count": len(opinions),
            "category": "stocks",
            "last_updated": opinions[0]["timestamp"] if opinions else None
        })
    except Exception as e:
        logger.error(f"Error fetching stock opinions: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@real_social_bp.route('/opinions/crypto', methods=['GET'])
def get_crypto_opinions():
    """Get live crypto trading opinions from real influencers"""
    try:
        limit = request.args.get('limit', 10, type=int)
        opinions = real_social_crawler.get_live_crypto_opinions(limit)
        
        return jsonify({
            "success": True,
            "data": opinions,
            "count": len(opinions),
            "category": "crypto",
            "last_updated": opinions[0]["timestamp"] if opinions else None
        })
    except Exception as e:
        logger.error(f"Error fetching crypto opinions: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@real_social_bp.route('/opinions/meme', methods=['GET'])
def get_meme_opinions():
    """Get live meme coin opinions from real influencers"""
    try:
        limit = request.args.get('limit', 10, type=int)
        opinions = real_social_crawler.get_live_meme_opinions(limit)
        
        return jsonify({
            "success": True,
            "data": opinions,
            "count": len(opinions),
            "category": "meme",
            "last_updated": opinions[0]["timestamp"] if opinions else None
        })
    except Exception as e:
        logger.error(f"Error fetching meme opinions: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@real_social_bp.route('/opinions/forex', methods=['GET'])
def get_forex_opinions():
    """Get live forex trading opinions from real influencers"""
    try:
        limit = request.args.get('limit', 10, type=int)
        opinions = real_social_crawler.get_live_forex_opinions(limit)
        
        return jsonify({
            "success": True,
            "data": opinions,
            "count": len(opinions),
            "category": "forex",
            "last_updated": opinions[0]["timestamp"] if opinions else None
        })
    except Exception as e:
        logger.error(f"Error fetching forex opinions: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@real_social_bp.route('/opinions/all', methods=['GET'])
def get_all_opinions():
    """Get live opinions from all categories"""
    try:
        limit_per_category = request.args.get('limit', 5, type=int)
        all_opinions = real_social_crawler.get_all_live_opinions(limit_per_category)
        
        # Calculate total count
        total_count = sum(len(opinions) for opinions in all_opinions.values())
        
        return jsonify({
            "success": True,
            "data": all_opinions,
            "total_count": total_count,
            "categories": list(all_opinions.keys()),
            "last_updated": max([
                opinions[0]["timestamp"] for opinions in all_opinions.values() if opinions
            ]) if any(all_opinions.values()) else None
        })
    except Exception as e:
        logger.error(f"Error fetching all opinions: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@real_social_bp.route('/telegram/updates', methods=['GET'])
def get_telegram_updates():
    """Get updates from Telegram channels"""
    try:
        limit = request.args.get('limit', 5, type=int)
        updates = real_social_crawler.get_telegram_updates(limit)
        
        return jsonify({
            "success": True,
            "data": updates,
            "count": len(updates),
            "platform": "telegram",
            "last_updated": updates[0]["timestamp"] if updates else None
        })
    except Exception as e:
        logger.error(f"Error fetching telegram updates: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@real_social_bp.route('/activity/feed', methods=['GET'])
def get_activity_feed():
    """Get live activity feed combining all platforms"""
    try:
        limit = request.args.get('limit', 10, type=int)
        activities = real_social_crawler.get_live_activity_feed(limit)
        
        return jsonify({
            "success": True,
            "data": activities,
            "count": len(activities),
            "last_updated": activities[0]["timestamp"] if activities else None
        })
    except Exception as e:
        logger.error(f"Error fetching activity feed: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@real_social_bp.route('/stats', methods=['GET'])
def get_social_stats():
    """Get real-time social media statistics"""
    try:
        # Get sample data to calculate stats
        all_opinions = real_social_crawler.get_all_live_opinions(limit_per_category=10)
        
        # Calculate statistics
        total_influencers = (
            len(real_social_crawler.stock_influencers) +
            len(real_social_crawler.crypto_influencers) +
            len(real_social_crawler.meme_influencers) +
            len(real_social_crawler.forex_influencers)
        )
        
        total_opinions = sum(len(opinions) for opinions in all_opinions.values())
        
        # Calculate average engagement
        total_engagement = 0
        opinion_count = 0
        for opinions in all_opinions.values():
            for opinion in opinions:
                total_engagement += opinion["engagement"]["likes"]
                opinion_count += 1
        
        avg_engagement = total_engagement / opinion_count if opinion_count > 0 else 0
        
        stats = {
            "total_influencers": total_influencers,
            "active_platforms": 4,  # Twitter, Telegram, Discord, Instagram
            "live_opinions": total_opinions,
            "avg_engagement": int(avg_engagement),
            "categories": {
                "stocks": len(real_social_crawler.stock_influencers),
                "crypto": len(real_social_crawler.crypto_influencers),
                "meme": len(real_social_crawler.meme_influencers),
                "forex": len(real_social_crawler.forex_influencers)
            },
            "telegram_channels": len(real_social_crawler.telegram_channels),
            "last_updated": max([
                opinions[0]["timestamp"] for opinions in all_opinions.values() if opinions
            ]) if any(all_opinions.values()) else None
        }
        
        return jsonify({
            "success": True,
            "data": stats
        })
    except Exception as e:
        logger.error(f"Error fetching social stats: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@real_social_bp.route('/influencers/list', methods=['GET'])
def get_influencers_list():
    """Get list of all tracked influencers"""
    try:
        category = request.args.get('category', 'all')
        
        influencers = {}
        
        if category == 'all' or category == 'stocks':
            influencers['stocks'] = real_social_crawler.stock_influencers
        
        if category == 'all' or category == 'crypto':
            influencers['crypto'] = real_social_crawler.crypto_influencers
        
        if category == 'all' or category == 'meme':
            influencers['meme'] = real_social_crawler.meme_influencers
        
        if category == 'all' or category == 'forex':
            influencers['forex'] = real_social_crawler.forex_influencers
        
        return jsonify({
            "success": True,
            "data": influencers,
            "total_count": sum(len(inf_list) for inf_list in influencers.values())
        })
    except Exception as e:
        logger.error(f"Error fetching influencers list: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

