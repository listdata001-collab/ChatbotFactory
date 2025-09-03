import os
import re
import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from models import User, Payment, Bot, ChatHistory
from app import db

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'txt', 'docx', 'csv'}

def format_currency(amount: float) -> str:
    """Format currency amount in UZS"""
    return f"{amount:,.0f} so'm"

def format_date(date: Optional[datetime]) -> str:
    """Format date for display"""
    if not date:
        return "Belgilanmagan"
    return date.strftime("%d.%m.%Y")

def calculate_subscription_end(subscription_type: str) -> Optional[datetime]:
    """Calculate subscription end date"""
    if subscription_type in ['basic', 'premium']:
        return datetime.utcnow() + timedelta(days=30)
    return None

def get_subscription_status(user: User) -> str:
    """Get user subscription status"""
    if user.subscription_type == 'admin':
        return 'Admin'
    elif user.subscription_type == 'free':
        return 'Bepul'
    elif not user.subscription_active():
        return 'Tugagan'
    elif user.subscription_end_date:
        days_left = (user.subscription_end_date - datetime.utcnow()).days
        return f"{days_left} kun qoldi"
    return 'Faol'

def validate_telegram_token(token: str) -> bool:
    """Validate Telegram bot token format"""
    if not token:
        return False
    
    # Telegram bot token format: number:alphanumeric_string
    pattern = r'^\d+:[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, token))

def send_notification_email(user_email: str, subject: str, message: str) -> bool:
    """Send notification email (placeholder for email service)"""
    # This would integrate with an email service like SendGrid, Mailgun, etc.
    logging.info(f"Email notification sent to {user_email}: {subject}")
    return True

def check_subscription_expiry() -> None:
    """Check for expiring subscriptions and send notifications"""
    with db.session() as session:
        # Find subscriptions expiring in 3 days
        three_days_from_now = datetime.utcnow() + timedelta(days=3)
        expiring_soon = User.query.filter(
            User.subscription_end_date <= three_days_from_now,
            User.subscription_end_date > datetime.utcnow(),
            User.subscription_type.in_(['basic', 'premium'])
        ).all()
        
        for user in expiring_soon:
            days_left = (user.subscription_end_date - datetime.utcnow()).days
            send_notification_email(
                user.email,
                "Obuna tugash haqida eslatma",
                f"Hurmatli {user.username}, sizning obunangiz {days_left} kundan keyin tugaydi."
            )
        
        # Find expired subscriptions
        expired = User.query.filter(
            User.subscription_end_date <= datetime.utcnow(),
            User.subscription_type.in_(['basic', 'premium'])
        ).all()
        
        for user in expired:
            user.subscription_type = 'free'
            send_notification_email(
                user.email,
                "Obuna tugadi",
                f"Hurmatli {user.username}, sizning obunangiz tugadi. Yangi obuna sotib oling."
            )
        
        session.commit()

def get_user_stats() -> Dict[str, int]:
    """Get user statistics"""
    return {
        'total_users': User.query.count(),
        'free_users': User.query.filter_by(subscription_type='free').count(),
        'basic_users': User.query.filter_by(subscription_type='basic').count(),
        'premium_users': User.query.filter_by(subscription_type='premium').count(),
        'active_users': User.query.filter_by(is_active=True).count()
    }

def get_payment_stats() -> Dict[str, Union[float, int]]:
    """Get payment statistics"""
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status='completed').scalar() or 0
    monthly_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.status == 'completed',
        Payment.created_at >= datetime.utcnow() - timedelta(days=30)
    ).scalar() or 0
    
    return {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'total_payments': Payment.query.filter_by(status='completed').count(),
        'pending_payments': Payment.query.filter_by(status='pending').count()
    }

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()

def generate_transaction_id(payment_id: int) -> str:
    """Generate transaction ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"BF_{payment_id}_{timestamp}"

def validate_subscription_upgrade(current_type: str, new_type: str) -> bool:
    """Validate subscription upgrade"""
    hierarchy = ['free', 'basic', 'premium']
    
    if current_type not in hierarchy or new_type not in hierarchy:
        return False
    
    return hierarchy.index(new_type) > hierarchy.index(current_type)
