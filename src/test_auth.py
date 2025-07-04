#!/usr/bin/env python3
"""
Test script to debug authentication issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from models.user import User, SubscriptionPlan, Subscription
from models.trading import Portfolio
from services.auth_service import auth_service
from main import create_app
import json

def test_auth():
    """Test authentication functionality"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Testing Authentication System")
        print("=" * 50)
        
        # Check if admin user exists
        admin_user = User.query.filter_by(email='admin@aitradingpro.com').first()
        if admin_user:
            print(f"✅ Admin user found: {admin_user.email}")
            print(f"   - ID: {admin_user.id}")
            print(f"   - Username: {admin_user.username}")
            print(f"   - Active: {admin_user.is_active}")
            print(f"   - Verified: {admin_user.is_verified}")
            
            # Test password
            if admin_user.check_password('admin123'):
                print("✅ Admin password is correct")
            else:
                print("❌ Admin password is incorrect")
                
            # Test login service
            success, message, user_data = auth_service.login_user('admin@aitradingpro.com', 'admin123')
            if success:
                print("✅ Auth service login successful")
                print(f"   - Message: {message}")
                print(f"   - User data keys: {list(user_data.keys()) if user_data else 'None'}")
            else:
                print(f"❌ Auth service login failed: {message}")
        else:
            print("❌ Admin user not found")
            
        # Check subscription plans
        plans = SubscriptionPlan.query.all()
        print(f"\n📋 Subscription Plans: {len(plans)} found")
        for plan in plans:
            print(f"   - {plan.name}: ${plan.price}/{plan.billing_cycle}")
            
        # Check all users
        users = User.query.all()
        print(f"\n👥 Total Users: {len(users)}")
        for user in users:
            print(f"   - {user.email} ({user.username}) - Active: {user.is_active}")
            
        # Test creating a new user
        print(f"\n🆕 Testing user registration...")
        success, message, new_user = auth_service.register_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        if success:
            print("✅ User registration successful")
            print(f"   - Message: {message}")
            print(f"   - User ID: {new_user.id if new_user else 'None'}")
            
            # Test login with new user
            success2, message2, user_data2 = auth_service.login_user('test@example.com', 'testpass123')
            if success2:
                print("✅ New user login successful")
            else:
                print(f"❌ New user login failed: {message2}")
        else:
            print(f"❌ User registration failed: {message}")

if __name__ == '__main__':
    test_auth()

