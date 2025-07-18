"""
Fund Management Service
Handles user fund deposits, withdrawals, and balance management
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from decimal import Decimal

from database import db
from models.user import User, Transaction
from models.trading import Portfolio

logger = logging.getLogger(__name__)

class FundManagementService:
    """Service for managing user funds and transactions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def add_funds(self, user_id: int, amount: float, payment_method: str = "demo", 
                  transaction_id: Optional[str] = None) -> Dict:
        """Add funds to user's account"""
        try:
            if amount <= 0:
                return {'success': False, 'error': 'Amount must be positive'}
            
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            portfolio = user.portfolio
            if not portfolio:
                portfolio = Portfolio(
                    user_id=user_id,
                    balance=0.0,
                    total_value=0.0
                )
                db.session.add(portfolio)
                db.session.flush()
            
            transaction = Transaction(
                user_id=user_id,
                transaction_type='deposit',
                amount=amount,
                payment_method=payment_method,
                status='completed',
                description=f"Fund deposit via {payment_method}"
            )
            
            portfolio.balance += amount
            portfolio.total_value += amount
            portfolio.updated_at = datetime.utcnow()
            
            db.session.add(transaction)
            db.session.commit()
            
            self.logger.info(f"✅ Added ${amount} to user {user_id} balance")
            
            return {
                'success': True,
                'transaction': transaction.to_dict(),
                'new_balance': portfolio.balance,
                'message': f'Successfully added ${amount:.2f} to your account'
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Error adding funds: {e}")
            return {'success': False, 'error': str(e)}
    
    def withdraw_funds(self, user_id: int, amount: float, withdrawal_method: str = "demo") -> Dict:
        """Withdraw funds from user's account"""
        try:
            if amount <= 0:
                return {'success': False, 'error': 'Amount must be positive'}
            
            user = User.query.get(user_id)
            if not user or not user.portfolio:
                return {'success': False, 'error': 'User or portfolio not found'}
            
            portfolio = user.portfolio
            
            if portfolio.balance < amount:
                return {'success': False, 'error': 'Insufficient funds'}
            
            transaction = Transaction(
                user_id=user_id,
                transaction_type='withdrawal',
                amount=amount,
                payment_method=withdrawal_method,
                status='completed',
                description=f"Fund withdrawal via {withdrawal_method}"
            )
            
            portfolio.balance -= amount
            portfolio.total_value -= amount
            portfolio.updated_at = datetime.utcnow()
            
            db.session.add(transaction)
            db.session.commit()
            
            self.logger.info(f"✅ Withdrew ${amount} from user {user_id} balance")
            
            return {
                'success': True,
                'transaction': transaction.to_dict(),
                'new_balance': portfolio.balance,
                'message': f'Successfully withdrew ${amount:.2f} from your account'
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Error withdrawing funds: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_balance(self, user_id: int) -> Dict:
        """Get user's current balance and portfolio value"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            portfolio = user.portfolio
            if not portfolio:
                return {
                    'success': True,
                    'balance': 0.0,
                    'total_value': 0.0,
                    'available_balance': 0.0
                }
            
            from models.trading import Position
            positions = Position.query.filter_by(portfolio_id=portfolio.id, is_active=True).all()
            
            positions_value = sum(pos.quantity * pos.current_price for pos in positions)
            total_value = portfolio.balance + positions_value
            
            return {
                'success': True,
                'balance': portfolio.balance,
                'total_value': total_value,
                'available_balance': portfolio.balance,
                'positions_value': positions_value
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting balance: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_transaction_history(self, user_id: int, limit: int = 50) -> Dict:
        """Get user's transaction history"""
        try:
            transactions = Transaction.query.filter_by(user_id=user_id)\
                                          .order_by(Transaction.created_at.desc())\
                                          .limit(limit).all()
            
            return {
                'success': True,
                'transactions': [t.to_dict() for t in transactions],
                'total': len(transactions)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting transaction history: {e}")
            return {'success': False, 'error': str(e)}

# Global instance
fund_management_service = FundManagementService()
