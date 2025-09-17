import os
import logging
from datetime import datetime
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Professional logging tizimini ishga tushirish
try:
    from logging_config import setup_logging, error_tracker, ContextLogger
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Chatbot Factory AI application starting with professional logging")
except Exception as e:
    # Fallback basic logging for any error
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.warning(f"Using fallback logging configuration due to: {e}")

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    logger.error("SESSION_SECRET environment variable is required!")
    raise ValueError("SESSION_SECRET environment variable must be set for security")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Cache control for different environments
@app.after_request
def after_request(response):
    # Always disable cache in development for Replit
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache" 
    response.headers["Expires"] = "0"
    
    # Add CORS headers for Replit iframe
    response.headers["X-Frame-Options"] = "ALLOWALL"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
    return response

# Configure the database - PostgreSQL for production performance
database_url = os.environ.get("DATABASE_URL")
if database_url and not database_url.startswith('sqlite'):
    # Normalize postgres:// to postgresql:// for SQLAlchemy compatibility
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # PostgreSQL connection with optimized pooling for high load
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 10,          # Reasonable pool size for Replit
        "max_overflow": 20,       # Allow extra connections under load
        "pool_timeout": 30,       # Wait up to 30s for connection
        "pool_recycle": 3600,     # Recycle connections every hour
        "pool_pre_ping": True,    # Verify connections before use
        "echo": False
    }
    logger.info("Using PostgreSQL with optimized connection pooling")
else:
    # Fallback to SQLite for development
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir, exist_ok=True)
    
    database_path = os.path.join(instance_dir, 'botfactory.db')
    database_url = f"sqlite:///{database_path}"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "echo": False,
        "connect_args": {"check_same_thread": False}
    }
    logger.info("Using SQLite database for development")

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # type: ignore
login_manager.login_message = 'Iltimos, tizimga kiring.'
login_manager.login_message_category = 'info'

# Make datetime available in templates
app.jinja_env.globals['datetime'] = datetime

# Import routes after app creation to avoid circular imports
from routes import main_bp
from auth import auth_bp
from payments import payment_bp
from instagram_bot import instagram_bp
from whatsapp_bot import whatsapp_bp
from marketing import marketing_bp
from bot_status import bot_status_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(payment_bp, url_prefix='/payment')
app.register_blueprint(instagram_bp, url_prefix='/instagram')
app.register_blueprint(whatsapp_bp, url_prefix='/whatsapp')
app.register_blueprint(marketing_bp, url_prefix='/marketing')
app.register_blueprint(bot_status_bp, url_prefix='/admin')

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models to ensure tables are created
    import models
    
    # Create tables
    try:
        db.create_all()
        logging.info("Database schema up to date")
        
        # Create admin user only if environment variables are provided (for initial setup)
        admin_email = os.environ.get("ADMIN_EMAIL")
        admin_password = os.environ.get("ADMIN_PASSWORD")
        
        if admin_email and admin_password:
            from models import User
            from werkzeug.security import generate_password_hash
            
            admin = User.query.filter_by(email=admin_email).first()
            if not admin:
                admin = User()
                admin.username = admin_email.split('@')[0]  # Use email prefix as username
                admin.email = admin_email
                admin.password_hash = generate_password_hash(admin_password)
                admin.language = 'uz'
                admin.subscription_type = 'admin'
                admin.is_admin = True
                db.session.add(admin)
                db.session.commit()
                logging.info(f"Admin user created successfully for {admin_email}")
            else:
                logging.info(f"Admin user already exists for {admin_email}")
        else:
            logging.info("No admin credentials provided via ADMIN_EMAIL/ADMIN_PASSWORD - skipping admin user creation")
            
    except Exception as e:
        logging.error(f"Database initialization error: {e}")
        # Try creating the file manually
        import sqlite3
        try:
            conn = sqlite3.connect('instance/botfactory.db')
            conn.close()
            logging.info("SQLite file created manually, retrying database setup")
            db.create_all()
            logging.info("Database setup successful after manual file creation")
        except Exception as manual_error:
            logging.error(f"Manual database creation also failed: {manual_error}")
    
    # Initialize Bot Manager - Start all active bots polling in background
    try:
        logger.info("🤖 Initializing BotFactory AI Bot Manager...")
        from bot_manager import initialize_bot_manager
        global_bot_manager = initialize_bot_manager()
        
        if global_bot_manager:
            logger.info("✅ Bot manager successfully initialized - all active bots will start polling!")
        else:
            logger.warning("⚠️ Bot manager initialization failed - bots will not auto-start")
            
    except Exception as bot_manager_error:
        logger.error(f"❌ Critical error initializing bot manager: {bot_manager_error}")
        logger.warning("⚠️ Application will continue without bot polling - bots will not respond to messages!")
