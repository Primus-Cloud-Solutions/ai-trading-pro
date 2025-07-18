"""
Fund Management Routes
API endpoints for fund deposits, withdrawals, and balance management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.fund_management_service import fund_management_service
import logging

logger = logging.getLogger(__name__)

fund_management_bp = Blueprint('fund_management', __name__, url_prefix='/api/funds')

@fund_management_bp.route('/add', methods=['POST'])
@jwt_required()
def add_funds():
    """Add funds to user account"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        amount = float(data.get('amount', 0))
        payment_method = data.get('payment_method', 'demo')
        
        result = fund_management_service.add_funds(
            user_id=user_id,
            amount=amount,
            payment_method=payment_method
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in add_funds endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fund_management_bp.route('/withdraw', methods=['POST'])
@jwt_required()
def withdraw_funds():
    """Withdraw funds from user account"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        amount = float(data.get('amount', 0))
        withdrawal_method = data.get('withdrawal_method', 'demo')
        
        result = fund_management_service.withdraw_funds(
            user_id=user_id,
            amount=amount,
            withdrawal_method=withdrawal_method
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in withdraw_funds endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fund_management_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_balance():
    """Get user's current balance and portfolio value"""
    try:
        user_id = get_jwt_identity()
        
        result = fund_management_service.get_balance(user_id)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"❌ Error in get_balance endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fund_management_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get user's transaction history"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 50))
        
        result = fund_management_service.get_transaction_history(user_id, limit)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"❌ Error in get_transactions endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fund_management_bp.route('/demo-add', methods=['POST'])
def demo_add_funds():
    """Demo endpoint to add funds without authentication (for testing)"""
    try:
        data = request.get_json()
        
        user_id = int(data.get('user_id', 1))  # Default to user 1 for demo
        amount = float(data.get('amount', 0))
        
        result = fund_management_service.add_funds(
            user_id=user_id,
            amount=amount,
            payment_method='demo'
        )
        
        return jsonify(result), 200 if result['success'] else 400
            
    except Exception as e:
        logger.error(f"❌ Error in demo_add_funds endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
