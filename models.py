from typing import Optional, List
from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from sqlalchemy import Text

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    language = db.Column(db.String(2), default='uz')  # uz/ru/en
    subscription_type = db.Column(db.String(20), default='free')  # free/basic/premium/admin
    subscription_end_date = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)
    _is_active = db.Column('is_active', db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    telegram_id = db.Column(db.String(50), unique=True)
    instagram_id = db.Column(db.String(50), unique=True)
    whatsapp_number = db.Column(db.String(20), unique=True)
    phone_number = db.Column(db.String(20))
    
    # Relationships
    bots = db.relationship('Bot', backref='owner', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def is_active(self):
        """Override UserMixin's is_active property"""
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        """Allow setting is_active"""
        self._is_active = value
    
    def can_create_bot(self) -> bool:
        if self.subscription_type == 'admin':
            return True
        # Query orqali botlar sonini olish (relationship emas)
        bot_count = Bot.query.filter_by(user_id=self.id).count()
        if self.subscription_type == 'free' and bot_count >= 1:
            return False
        elif self.subscription_type in ['starter', 'basic'] and bot_count >= 1:
            return False
        elif self.subscription_type == 'premium' and bot_count >= 5:
            return False
        return True
    
    def can_use_language(self, lang: str) -> bool:
        if self.subscription_type in ['free']:
            return lang == 'uz'
        elif self.subscription_type in ['starter', 'basic', 'premium', 'admin']:
            return lang in ['uz', 'ru', 'en']
        return False
    
    def subscription_active(self) -> bool:
        if self.subscription_type in ['admin']:
            return True
        if self.subscription_type == 'free':
            return True
        if self.subscription_type in ['starter', 'basic', 'premium'] and self.subscription_end_date and self.subscription_end_date > datetime.utcnow():
            return True
        return False

class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(20), default='Telegram')  # Telegram/Instagram/WhatsApp
    telegram_token = db.Column(db.String(200))
    telegram_username = db.Column(db.String(100))
    instagram_token = db.Column(db.String(200))
    whatsapp_token = db.Column(db.String(200))
    whatsapp_phone_id = db.Column(db.String(100))
    daily_messages = db.Column(db.Integer, default=0)
    weekly_messages = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    knowledge_base = db.relationship('KnowledgeBase', backref='bot', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Bot {self.name}>'

class KnowledgeBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'), nullable=False)
    content = db.Column(Text, nullable=False)
    filename = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<KnowledgeBase {self.filename}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(20), nullable=False)  # Payme/Click/Uzum
    status = db.Column(db.String(20), default='pending')  # pending/completed/failed
    transaction_id = db.Column(db.String(100))
    subscription_type = db.Column(db.String(20))  # basic/premium
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.amount} {self.method}>'

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'), nullable=False)
    user_telegram_id = db.Column(db.String(50))
    user_instagram_id = db.Column(db.String(50))
    user_whatsapp_number = db.Column(db.String(20))
    message = db.Column(Text)
    response = db.Column(Text)
    language = db.Column(db.String(2), default='uz')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatHistory {self.user_telegram_id}>'

class BroadcastMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_text = db.Column(Text, nullable=False)
    target_type = db.Column(db.String(20), default='all')  # all/customers/bot_users
    sent_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')  # pending/sending/completed/failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<BroadcastMessage {self.id}>'
