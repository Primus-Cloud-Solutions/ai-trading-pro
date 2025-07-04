"""
Subscription Management Routes for AI Trading SaaS Platform
Subscription plans, billing, upgrades, and payment processing
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import logging
import stripe
import os

from services.auth_service import auth_service
from models.user import User, Subscription, SubscriptionPlan
from database import db

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_dummy_key')

subscription_bp = Blueprint('subscription', __name__, url_prefix='/api/subscription')

@subscription_bp.route('/plans', methods=['GET'])
def get_subscription_plans():
    """Get all available subscription plans"""
    try:
        plans = SubscriptionPlan.query.filter_by(is_active=True).all()
        
        return jsonify({
            'plans': [plan.to_dict() for plan in plans]
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting subscription plans: {e}")
        return jsonify({'error': 'Failed to get subscription plans'}), 500

@subscription_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_subscription():
    """Get user's current subscription"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        subscription = user.subscription
        if not subscription:
            return jsonify({'subscription': None}), 200
        
        return jsonify({
            'subscription': subscription.to_dict(),
            'plan': subscription.plan.to_dict() if subscription.plan else None,
            'usage': {
                'trades_today': subscription.get_trades_today(),
                'portfolio_value': user.portfolio.total_value if user.portfolio else 0,
                'max_trades_per_day': subscription.plan.max_trades_per_day if subscription.plan else 0,
                'max_portfolio_value': subscription.plan.max_portfolio_value if subscription.plan else 0
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting current subscription: {e}")
        return jsonify({'error': 'Failed to get subscription'}), 500

@subscription_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe_to_plan():
    """Subscribe to a plan"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data or 'plan_id' not in data:
            return jsonify({'error': 'Plan ID is required'}), 400
        
        plan_id = data['plan_id']
        payment_method_id = data.get('payment_method_id')
        
        # Get the subscription plan
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan or not plan.is_active:
            return jsonify({'error': 'Invalid subscription plan'}), 400
        
        # Check if user already has an active subscription
        existing_subscription = user.subscription
        if existing_subscription and existing_subscription.is_active():
            return jsonify({'error': 'User already has an active subscription'}), 400
        
        # Handle free trial
        if plan.price == 0:
            # Create free subscription
            subscription = Subscription(
                user_id=user.id,
                plan_id=plan.id,
                status='active',
                billing_cycle=plan.billing_cycle,
                expires_at=datetime.utcnow() + timedelta(days=7)  # 7-day trial
            )
            db.session.add(subscription)
            db.session.commit()
            
            logger.info(f"✅ Free trial subscription created for user {user.email}")
            
            return jsonify({
                'message': 'Successfully subscribed to free trial',
                'subscription': subscription.to_dict()
            }), 200
        
        # Handle paid subscription with Stripe
        if not payment_method_id:
            return jsonify({'error': 'Payment method is required for paid plans'}), 400
        
        try:
            # Create Stripe customer if not exists
            if not user.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=f"{user.first_name} {user.last_name}",
                    metadata={'user_id': user.id}
                )
                user.stripe_customer_id = customer.id
                db.session.commit()
            
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=user.stripe_customer_id
            )
            
            # Create subscription in Stripe
            stripe_subscription = stripe.Subscription.create(
                customer=user.stripe_customer_id,
                items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': plan.name,
                            'description': plan.description
                        },
                        'unit_amount': int(plan.price * 100),  # Convert to cents
                        'recurring': {
                            'interval': 'month' if plan.billing_cycle == 'monthly' else 'year'
                        }
                    }
                }],
                default_payment_method=payment_method_id,
                expand=['latest_invoice.payment_intent']
            )
            
            # Create subscription in database
            subscription = Subscription(
                user_id=user.id,
                plan_id=plan.id,
                status='active',
                billing_cycle=plan.billing_cycle,
                stripe_subscription_id=stripe_subscription.id,
                expires_at=datetime.utcnow() + timedelta(days=30 if plan.billing_cycle == 'monthly' else 365)
            )
            db.session.add(subscription)
            db.session.commit()
            
            logger.info(f"✅ Paid subscription created for user {user.email} - Plan: {plan.name}")
            
            return jsonify({
                'message': f'Successfully subscribed to {plan.name}',
                'subscription': subscription.to_dict(),
                'payment_intent': stripe_subscription.latest_invoice.payment_intent
            }), 200
            
        except stripe.error.StripeError as e:
            logger.error(f"❌ Stripe error: {e}")
            return jsonify({'error': 'Payment processing failed'}), 400
        
    except Exception as e:
        logger.error(f"❌ Error in subscribe_to_plan: {e}")
        return jsonify({'error': 'Failed to create subscription'}), 500

@subscription_bp.route('/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription():
    """Upgrade to a higher tier plan"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.subscription:
            return jsonify({'error': 'No active subscription found'}), 404
        
        data = request.get_json()
        if not data or 'plan_id' not in data:
            return jsonify({'error': 'Plan ID is required'}), 400
        
        new_plan_id = data['plan_id']
        new_plan = SubscriptionPlan.query.get(new_plan_id)
        
        if not new_plan or not new_plan.is_active:
            return jsonify({'error': 'Invalid subscription plan'}), 400
        
        current_subscription = user.subscription
        current_plan = current_subscription.plan
        
        # Check if it's actually an upgrade
        if new_plan.price <= current_plan.price:
            return jsonify({'error': 'Can only upgrade to higher tier plans'}), 400
        
        # Update subscription
        if current_subscription.stripe_subscription_id:
            # Update Stripe subscription
            stripe.Subscription.modify(
                current_subscription.stripe_subscription_id,
                items=[{
                    'id': current_subscription.stripe_subscription_id,
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': new_plan.name,
                            'description': new_plan.description
                        },
                        'unit_amount': int(new_plan.price * 100),
                        'recurring': {
                            'interval': 'month' if new_plan.billing_cycle == 'monthly' else 'year'
                        }
                    }
                }],
                proration_behavior='create_prorations'
            )
        
        # Update database
        current_subscription.plan_id = new_plan.id
        current_subscription.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"✅ Subscription upgraded for user {user.email} to {new_plan.name}")
        
        return jsonify({
            'message': f'Successfully upgraded to {new_plan.name}',
            'subscription': current_subscription.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in upgrade_subscription: {e}")
        return jsonify({'error': 'Failed to upgrade subscription'}), 500

@subscription_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel current subscription"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user or not user.subscription:
            return jsonify({'error': 'No active subscription found'}), 404
        
        subscription = user.subscription
        
        # Cancel in Stripe if it's a paid subscription
        if subscription.stripe_subscription_id:
            stripe.Subscription.delete(subscription.stripe_subscription_id)
        
        # Update subscription status
        subscription.status = 'cancelled'
        subscription.cancelled_at = datetime.utcnow()
        subscription.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"✅ Subscription cancelled for user {user.email}")
        
        return jsonify({
            'message': 'Subscription cancelled successfully',
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in cancel_subscription: {e}")
        return jsonify({'error': 'Failed to cancel subscription'}), 500

@subscription_bp.route('/usage', methods=['GET'])
@jwt_required()
def get_subscription_usage():
    """Get current subscription usage statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        subscription = user.subscription
        if not subscription:
            return jsonify({'error': 'No active subscription'}), 404
        
        # Calculate usage statistics
        today = datetime.utcnow().date()
        trades_today = Trade.query.filter(
            Trade.portfolio_id == user.portfolio.id,
            Trade.executed_at >= today
        ).count() if user.portfolio else 0
        
        portfolio_value = user.portfolio.total_value if user.portfolio else 0
        
        plan = subscription.plan
        usage_stats = {
            'trades_today': trades_today,
            'max_trades_per_day': plan.max_trades_per_day,
            'trades_remaining': max(0, plan.max_trades_per_day - trades_today),
            'portfolio_value': portfolio_value,
            'max_portfolio_value': plan.max_portfolio_value,
            'portfolio_usage_percent': (portfolio_value / plan.max_portfolio_value * 100) if plan.max_portfolio_value > 0 else 0,
            'subscription_expires': subscription.expires_at.isoformat() if subscription.expires_at else None,
            'days_remaining': (subscription.expires_at - datetime.utcnow()).days if subscription.expires_at else None
        }
        
        return jsonify({
            'usage': usage_stats,
            'plan': plan.to_dict(),
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting subscription usage: {e}")
        return jsonify({'error': 'Failed to get usage statistics'}), 500

@subscription_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        
        if not endpoint_secret:
            logger.warning("⚠️ Stripe webhook secret not configured")
            return jsonify({'status': 'success'}), 200
        
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            logger.error("❌ Invalid payload in Stripe webhook")
            return jsonify({'error': 'Invalid payload'}), 400
        except stripe.error.SignatureVerificationError:
            logger.error("❌ Invalid signature in Stripe webhook")
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Handle the event
        if event['type'] == 'invoice.payment_succeeded':
            # Payment succeeded - extend subscription
            subscription_id = event['data']['object']['subscription']
            subscription = Subscription.query.filter_by(
                stripe_subscription_id=subscription_id
            ).first()
            
            if subscription:
                # Extend subscription period
                if subscription.plan.billing_cycle == 'monthly':
                    subscription.expires_at = datetime.utcnow() + timedelta(days=30)
                else:
                    subscription.expires_at = datetime.utcnow() + timedelta(days=365)
                
                subscription.status = 'active'
                db.session.commit()
                
                logger.info(f"✅ Subscription renewed for user {subscription.user.email}")
        
        elif event['type'] == 'invoice.payment_failed':
            # Payment failed - handle accordingly
            subscription_id = event['data']['object']['subscription']
            subscription = Subscription.query.filter_by(
                stripe_subscription_id=subscription_id
            ).first()
            
            if subscription:
                subscription.status = 'past_due'
                db.session.commit()
                
                logger.warning(f"⚠️ Payment failed for user {subscription.user.email}")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"❌ Error in Stripe webhook: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

