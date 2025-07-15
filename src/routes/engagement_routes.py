"""
Engagement Routes for Social Features
"""
from flask import Blueprint, jsonify, request
import random

engagement_bp = Blueprint('engagement', __name__, url_prefix='/api/social/engagement')

# In-memory storage for engagement data
engagement_data = {}
comments_data = {}

@engagement_bp.route('/like', methods=['POST'])
def toggle_like():
    """Toggle like on a KOL opinion"""
    try:
        data = request.get_json()
        opinion_id = data.get('opinion_id')
        action = data.get('action')  # 'like' or 'unlike'
        
        if not opinion_id:
            return jsonify({'success': False, 'message': 'Opinion ID required'}), 400
        
        # Initialize engagement data if not exists
        if opinion_id not in engagement_data:
            engagement_data[opinion_id] = {
                'likes': random.randint(50, 500),
                'shares': random.randint(10, 100),
                'comments': random.randint(5, 50),
                'clicks': random.randint(100, 1000),
                'views': random.randint(500, 5000)
            }
        
        # Update like count
        if action == 'like':
            engagement_data[opinion_id]['likes'] += 1
        elif action == 'unlike':
            engagement_data[opinion_id]['likes'] = max(0, engagement_data[opinion_id]['likes'] - 1)
        
        return jsonify({
            'success': True,
            'likes': engagement_data[opinion_id]['likes'],
            'message': f'Opinion {action}d successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@engagement_bp.route('/share', methods=['POST'])
def share_opinion():
    """Share a KOL opinion"""
    try:
        data = request.get_json()
        opinion_id = data.get('opinion_id')
        
        if not opinion_id:
            return jsonify({'success': False, 'message': 'Opinion ID required'}), 400
        
        # Initialize engagement data if not exists
        if opinion_id not in engagement_data:
            engagement_data[opinion_id] = {
                'likes': random.randint(50, 500),
                'shares': random.randint(10, 100),
                'comments': random.randint(5, 50),
                'clicks': random.randint(100, 1000),
                'views': random.randint(500, 5000)
            }
        
        # Update share count
        engagement_data[opinion_id]['shares'] += 1
        
        return jsonify({
            'success': True,
            'shares': engagement_data[opinion_id]['shares'],
            'opinion': {
                'id': opinion_id,
                'url': f'/opinion/{opinion_id}'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@engagement_bp.route('/click', methods=['POST'])
def track_click():
    """Track click engagement"""
    try:
        data = request.get_json()
        opinion_id = data.get('opinion_id')
        
        if not opinion_id:
            return jsonify({'success': False, 'message': 'Opinion ID required'}), 400
        
        # Initialize engagement data if not exists
        if opinion_id not in engagement_data:
            engagement_data[opinion_id] = {
                'likes': random.randint(50, 500),
                'shares': random.randint(10, 100),
                'comments': random.randint(5, 50),
                'clicks': random.randint(100, 1000),
                'views': random.randint(500, 5000)
            }
        
        # Update click count
        engagement_data[opinion_id]['clicks'] += 1
        
        return jsonify({
            'success': True,
            'clicks': engagement_data[opinion_id]['clicks']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@engagement_bp.route('/bookmark', methods=['POST'])
def toggle_bookmark():
    """Toggle bookmark on a KOL opinion"""
    try:
        data = request.get_json()
        opinion_id = data.get('opinion_id')
        action = data.get('action')  # 'bookmark' or 'unbookmark'
        
        if not opinion_id:
            return jsonify({'success': False, 'message': 'Opinion ID required'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Opinion {action}ed successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

