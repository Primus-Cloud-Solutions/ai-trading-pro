"""
Authentication API Routes for AI Trading SaaS Platform
Complete user authentication, registration, and profile management
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import logging

from services.auth_service import auth_service
from models.user import User

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract required fields
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        # Validate required fields
        if not all([email, username, password, first_name, last_name]):
            return jsonify({
                'error': 'Email, username, password, first name, and last name are required'
            }), 400
        
        # Register user
        success, message, user = auth_service.register_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=data.get('phone'),
            country=data.get('country'),
            timezone=data.get('timezone', 'UTC')
        )
        
        if success:
            return jsonify({
                'message': message,
                'user': user.to_dict() if user else None
            }), 201
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"❌ Error in register endpoint: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Handle both 'email' and 'email_or_username' field names
        email_or_username = data.get('email') or data.get('email_or_username')
        password = data.get('password')
        
        if not email_or_username or not password:
            return jsonify({'success': False, 'message': 'Email/username and password are required'}), 400
        
        # Authenticate user
        success, message, user_data = auth_service.login_user(email_or_username, password)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'user': user_data,
                'redirect': '/dashboard'
            }), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        logger.error(f"❌ Error in login endpoint: {e}")
        return jsonify({'success': False, 'message': 'Login failed. Please check your credentials.'}), 400

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        
        success, message, access_token = auth_service.refresh_token(current_user_id)
        
        if success:
            return jsonify({
                'message': message,
                'access_token': access_token,
                'expires_in': 24 * 3600  # 24 hours
            }), 200
        else:
            return jsonify({'error': message}), 401
            
    except Exception as e:
        logger.error(f"❌ Error in refresh endpoint: {e}")
        return jsonify({'error': 'Token refresh failed'}), 500

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify user email with token"""
    try:
        data = request.get_json()
        
        if not data or 'token' not in data:
            return jsonify({'error': 'Verification token is required'}), 400
        
        token = data['token']
        
        success, message = auth_service.verify_email(token)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"❌ Error in verify_email endpoint: {e}")
        return jsonify({'error': 'Email verification failed'}), 500

@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    """Request password reset"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email']
        
        success, message = auth_service.request_password_reset(email)
        
        return jsonify({'message': message}), 200
            
    except Exception as e:
        logger.error(f"❌ Error in request_password_reset endpoint: {e}")
        return jsonify({'error': 'Password reset request failed'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        
        if not data or 'token' not in data or 'password' not in data:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        token = data['token']
        new_password = data['password']
        
        success, message = auth_service.reset_password(token, new_password)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"❌ Error in reset_password endpoint: {e}")
        return jsonify({'error': 'Password reset failed'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(),
            'portfolio': user.portfolio.to_dict() if user.portfolio else None,
            'subscription': user.subscription.to_dict() if user.subscription else None,
            'trading_settings': user.trading_settings.to_dict() if user.trading_settings else None
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_profile endpoint: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success, message, user = auth_service.update_user_profile(current_user_id, **data)
        
        if success:
            return jsonify({
                'message': message,
                'user': user.to_dict() if user else None
            }), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"❌ Error in update_profile endpoint: {e}")
        return jsonify({'error': 'Profile update failed'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        success, message = auth_service.change_password(current_user_id, current_password, new_password)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"❌ Error in change_password endpoint: {e}")
        return jsonify({'error': 'Password change failed'}), 500

@auth_bp.route('/trading-settings', methods=['GET'])
@jwt_required()
def get_trading_settings():
    """Get user trading settings"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        settings = user.trading_settings
        if not settings:
            return jsonify({'error': 'Trading settings not found'}), 404
        
        return jsonify({'trading_settings': settings.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_trading_settings endpoint: {e}")
        return jsonify({'error': 'Failed to get trading settings'}), 500

@auth_bp.route('/trading-settings', methods=['PUT'])
@jwt_required()
def update_trading_settings():
    """Update user trading settings"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success, message, settings = auth_service.update_trading_settings(current_user_id, **data)
        
        if success:
            return jsonify({
                'message': message,
                'trading_settings': settings.to_dict() if settings else None
            }), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"❌ Error in update_trading_settings endpoint: {e}")
        return jsonify({'error': 'Trading settings update failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (placeholder for token blacklisting)"""
    try:
        # In a production app, you would blacklist the token here
        jti = get_jwt()['jti']  # JWT ID
        
        # TODO: Add token to blacklist
        # blacklist.add(jti)
        
        return jsonify({'message': 'Successfully logged out'}), 200
        
    except Exception as e:
        logger.error(f"❌ Error in logout endpoint: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/deactivate', methods=['POST'])
@jwt_required()
def deactivate_account():
    """Deactivate user account"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Require password confirmation
        if not data or 'password' not in data:
            return jsonify({'error': 'Password confirmation is required'}), 400
        
        user = auth_service.get_user_by_id(current_user_id)
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid password'}), 401
        
        success, message = auth_service.deactivate_user(current_user_id)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"❌ Error in deactivate_account endpoint: {e}")
        return jsonify({'error': 'Account deactivation failed'}), 500

# Error handlers
@auth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@auth_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@auth_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@auth_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

