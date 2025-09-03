import os
import logging
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Professional logging tizimini ishga tushirish
try:
    from logging_config import setup_logging, error_tracker, ContextLogger
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("BotFactory AI application starting with professional logging")
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
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Cache busting for templates  
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache" 
    response.headers["Expires"] = "0"
    return response

# Configure the database with UTF-8 support - force SQLite for now
database_url = "sqlite:///botfactory.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "echo": False,
    # UTF-8 support for SQLite with proper encoding
    "connect_args": {
        "check_same_thread": False,
        "isolation_level": None,  # Autocommit mode for SQLite
    }
}

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

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(payment_bp, url_prefix='/payment')
app.register_blueprint(instagram_bp, url_prefix='/instagram')
app.register_blueprint(whatsapp_bp, url_prefix='/whatsapp')
app.register_blueprint(marketing_bp, url_prefix='/marketing')

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models to ensure tables are created
    import models
    
    # Create/update tables
    try:
        db.create_all()
        
        # Add new columns if they don't exist (for notification settings)
        try:
            from sqlalchemy import text
            
            # Check and add admin_chat_id column
            result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='admin_chat_id'"))
            if not result.fetchone():
                db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN admin_chat_id VARCHAR(50)"))
                db.session.commit()
                logging.info("Added admin_chat_id column")
            
            # Check and add notification_channel column
            result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='notification_channel'"))
            if not result.fetchone():
                db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN notification_channel VARCHAR(100)"))
                db.session.commit()
                logging.info("Added notification_channel column")
            
            # Check and add notifications_enabled column
            result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='notifications_enabled'"))
            if not result.fetchone():
                db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN notifications_enabled BOOLEAN DEFAULT FALSE"))
                db.session.commit()
                logging.info("Added notifications_enabled column")
                
        except Exception as col_error:
            logging.warning(f"Column migration warning: {col_error}")
    
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
            
    except Exception as e:
        logging.error(f"Database initialization error: {e}")
