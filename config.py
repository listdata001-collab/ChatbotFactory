import os
from datetime import timedelta

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///botfactory.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Security
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'botfactory-secret-key-2024')
    WTF_CSRF_ENABLED = True
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # File uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'docx'}
    
    # AI
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'default_key')
    
    # Telegram
    TELEGRAM_API_URL = 'https://api.telegram.org/bot'
    
    # Payment
    PAYME_MERCHANT_ID = os.environ.get('PAYME_MERCHANT_ID', '')
    CLICK_MERCHANT_ID = os.environ.get('CLICK_MERCHANT_ID', '')
    UZUM_MERCHANT_ID = os.environ.get('UZUM_MERCHANT_ID', '')
    
    # Subscription prices (in UZS)
    SUBSCRIPTION_PRICES = {
        'basic': 290000,
        'premium': 590000
    }
    
    # Bot limits
    BOT_LIMITS = {
        'free': 1,
        'basic': 1,
        'premium': 5
    }
    
    # Language restrictions
    LANGUAGE_RESTRICTIONS = {
        'free': ['uz'],
        'basic': ['uz', 'ru', 'en'],
        'premium': ['uz', 'ru', 'en'],
        'admin': ['uz', 'ru', 'en']
    }

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True

class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
