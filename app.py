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

# Cache control for different environments
@app.after_request
def after_request(response):
    # Only disable cache in development, enable in production for static assets
    if app.config.get('DEVELOPMENT', False):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache" 
        response.headers["Expires"] = "0"
    else:
        # Production cache control - allow caching for static files
        if request.endpoint and 'static' in request.endpoint:
            response.headers["Cache-Control"] = "public, max-age=31536000"  # 1 year
        else:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# Configure the database with UTF-8 support
import os
if not os.path.exists('instance'):
    os.makedirs('instance', exist_ok=True)

database_url = os.environ.get("DATABASE_URL", "sqlite:///instance/botfactory.db")

# PostgreSQL URL ni to'g'rilash agar kerak bo'lsa
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

# Database configuration based on URL type
if database_url.startswith('postgresql'):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "echo": False,
        "pool_timeout": 20,
        "pool_size": 10,
        "max_overflow": 20,
        "connect_args": {
            "connect_timeout": 10,
            "application_name": "BotFactory_AI"
        }
    }
else:
    # SQLite configuration for development
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "echo": False,
        "connect_args": {
            "check_same_thread": False,
            "isolation_level": None,
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
    
    # Create/update tables with retry mechanism
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Test database connection first
            db.engine.connect()
            
            # Create tables
            db.create_all()
            logging.info("Database schema up to date")
        
            # Create admin user if not exists
            from models import User
            from werkzeug.security import generate_password_hash
            
            try:
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
            except Exception as user_error:
                logging.warning(f"Admin user creation skipped: {user_error}")
                
            break  # Success, exit retry loop
            
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                logging.error(f"Database initialization failed after {max_retries} retries: {e}")
                # Fallback agar PostgreSQL ishlamasa
                if database_url.startswith('postgresql'):
                    logging.warning("Falling back to SQLite due to PostgreSQL connection issues")
                    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/botfactory.db"
                    # SQLite konfiguratsiyasini o'rnatish
                    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
                        "pool_recycle": 300,
                        "pool_pre_ping": True,
                        "echo": False,
                        "connect_args": {
                            "check_same_thread": False,
                            "isolation_level": None,
                        }
                    }
                    # SQLite uchun qayta urinish
                    try:
                        db.create_all()
                        logging.info("Fallback to SQLite successful")
                    except Exception as sqlite_error:
                        logging.error(f"SQLite fallback also failed: {sqlite_error}")
                break
            else:
                import time
                wait_time = 2 ** retry_count  # Exponential backoff
                logging.warning(f"Database connection failed (attempt {retry_count}/{max_retries}), retrying in {wait_time} seconds...")
                time.sleep(wait_time)
