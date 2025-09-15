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
app.secret_key = os.environ.get("SESSION_SECRET", "botfactory-secret-key-2024")
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
# Temporarily force SQLite for Replit environment  
if False and database_url:
    # PostgreSQL connection with optimized pooling for high load
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 20,          # Increased from default 5
        "max_overflow": 40,       # Allow extra connections under load
        "pool_timeout": 30,       # Wait up to 30s for connection
        "pool_recycle": 3600,     # Recycle connections every hour
        "pool_pre_ping": True,    # Verify connections before use
        "echo": False
    }
    logger.info("Using PostgreSQL with optimized connection pooling")
else:
    # Fallback to SQLite for development (not recommended for production)
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
    logger.warning("Using SQLite fallback - not suitable for high load!")

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
        
        # Create admin user if not exists
        from models import User
        from werkzeug.security import generate_password_hash
        
        admin = User.query.filter_by(username='Akramjon').first()
        if not admin:
            admin = User()
            admin.username = 'Akramjon'
            admin.email = 'admin@botfactory.uz'
            admin.password_hash = generate_password_hash('Gisobot20141920*')
            admin.language = 'uz'
            admin.subscription_type = 'admin'
            admin.is_admin = True
            db.session.add(admin)
            db.session.commit()
            logging.info("Admin user created successfully")
        else:
            logging.info("Admin user already exists")
            
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
