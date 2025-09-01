import os
import logging
import asyncio
import requests
from typing import Optional

# Set telegram as available and use real bot implementation
TELEGRAM_AVAILABLE = True

# Import basic modules directly 
from telegram._update import Update
from telegram._inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup

# Real Telegram Bot implementation using HTTP API
class ContextTypes:
    DEFAULT_TYPE = None

class TelegramHTTPBot:
    def __init__(self, token):
        self.token = token
        self.handlers = {}
        self.running = False
        self.base_url = f"https://api.telegram.org/bot{token}"
        
    def add_handler(self, handler):
        if isinstance(handler, tuple):
            cmd_type, func = handler
            if cmd_type not in self.handlers:
                self.handlers[cmd_type] = []
            self.handlers[cmd_type].append(func)
        
    def send_message(self, chat_id, text, reply_markup=None):
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text
        }
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def get_updates(self, offset=None):
        url = f"{self.base_url}/getUpdates"
        params = {'timeout': 10}
        if offset:
            params['offset'] = offset
            
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return {'ok': False, 'result': []}
            
    async def process_update(self, update_data):
        # Create simplified Update object
        class SimpleUpdate:
            def __init__(self, data):
                self.data = data
                self.message = None
                self.callback_query = None
                self.effective_user = None
                self.effective_chat = None
                
                if 'message' in data:
                    self.message = SimpleMessage(data['message'])
                    self.effective_user = SimpleUser(data['message']['from'])
                    self.effective_chat = SimpleChat(data['message']['chat'])
                elif 'callback_query' in data:
                    self.callback_query = SimpleCallbackQuery(data['callback_query'])
                    self.effective_user = SimpleUser(data['callback_query']['from'])
        
        class SimpleMessage:
            def __init__(self, data):
                self.data = data
                self.text = data.get('text', '')
                self.chat = SimpleChat(data['chat'])
                
            async def reply_text(self, text, reply_markup=None):
                return bot_instance.send_message(self.chat.id, text, reply_markup)
        
        class SimpleUser:
            def __init__(self, data):
                self.data = data
                self.id = data['id']
                self.username = data.get('username', '')
                self.first_name = data.get('first_name', '')
                
        class SimpleChat:
            def __init__(self, data):
                self.data = data
                self.id = data['id']
                
        class SimpleCallbackQuery:
            def __init__(self, data):
                self.data = data
                self.from_user = SimpleUser(data['from'])
                
            async def answer(self):
                pass  # Placeholder
                
            async def edit_message_text(self, text):
                pass  # Placeholder
        
        # Process update
        update = SimpleUpdate(update_data)
        
        # Handle commands
        if update.message and update.message.text:
            text = update.message.text
            if text.startswith('/'):
                cmd = text.split()[0][1:]  # Remove '/'
                if 'start' in self.handlers and cmd == 'start':
                    for handler in self.handlers['start']:
                        await handler(update, None)
                elif 'help' in self.handlers and cmd == 'help':
                    for handler in self.handlers['help']:
                        await handler(update, None)
                elif 'language' in self.handlers and cmd == 'language':
                    for handler in self.handlers['language']:
                        await handler(update, None)
            else:
                # Regular message
                if 'message' in self.handlers:
                    for handler in self.handlers['message']:
                        await handler(update, None)
        
        # Handle callback queries
        if update.callback_query and 'callback' in self.handlers:
            for handler in self.handlers['callback']:
                await handler(update, None)

class TelegramApplication:
    def __init__(self, token):
        self.bot = TelegramHTTPBot(token)
        
    def add_handler(self, handler):
        self.bot.add_handler(handler)
        
    def run_polling(self):
        # Simple polling implementation
        offset = None
        global bot_instance
        bot_instance = self.bot
        
        logger.info("Starting bot polling...")
        while True:
            try:
                updates = self.bot.get_updates(offset)
                if updates.get('ok') and updates.get('result'):
                    for update in updates['result']:
                        asyncio.run(self.bot.process_update(update))
                        offset = update['update_id'] + 1
                        
                # Small delay to prevent API spam
                import time
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Polling error: {e}")
                import time
                time.sleep(5)

class Application:
    @staticmethod
    def builder():
        class Builder:
            def __init__(self):
                self._token = None
            def token(self, token):
                self._token = token
                return self
            def build(self):
                return TelegramApplication(self._token)
        return Builder()

# Handler creators
def CommandHandler(command, func):
    return (command, func)

def MessageHandler(filters_obj, func):  
    return ('message', func)

def CallbackQueryHandler(func):
    return ('callback', func)

class FilterType:
    def __init__(self, name):
        self.name = name
    
    def __and__(self, other):
        return FilterType(f"{self.name} & {other.name}")
    
    def __invert__(self):
        return FilterType(f"~{self.name}")

class filters:
    TEXT = FilterType('text')
    COMMAND = FilterType('command')
# Circular import muammosini oldini olish uchun lazy import
def get_dependencies():
    from ai import get_ai_response, process_knowledge_base
    from models import User, Bot, ChatHistory
    from app import db, app
    return get_ai_response, process_knowledge_base, User, Bot, ChatHistory, db, app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, bot_token, bot_id):
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot library not available")
            
        self.bot_token = bot_token
        self.bot_id = bot_id
        self.application = Application.builder().token(bot_token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup bot command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("language", self.language_command))
        self.application.add_handler(CallbackQueryHandler(self.language_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        get_ai_response, process_knowledge_base, User, Bot, ChatHistory, db, app = get_dependencies()
        with app.app_context():
            # Get or create user
            db_user = User.query.filter_by(telegram_id=str(user.id)).first()
            if not db_user:
                # Register new telegram user
                db_user = User()
                db_user.username = f"tg_{user.id}"
                db_user.email = f"tg_{user.id}@telegram.bot"
                db_user.password_hash = "telegram_user"
                db_user.telegram_id = str(user.id)
                db_user.language = 'uz'
                db_user.subscription_type = 'free'
                db.session.add(db_user)
                db.session.commit()
            
            # Get bot info
            bot = Bot.query.get(self.bot_id)
            bot_name = bot.name if bot else "BotFactory AI"
            
            welcome_message = f"🤖 Salom! Men {bot_name} chatbot!\n\n"
            welcome_message += "📝 Menga savolingizni yozing va men sizga yordam beraman.\n"
            welcome_message += "🌐 Tilni tanlash uchun /language buyrug'ini ishlating.\n"
            welcome_message += "❓ Yordam uchun /help buyrug'ini ishlating."
            
            await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 BotFactory AI Yordam

📋 Mavjud buyruqlar:
/start - Botni qayta ishga tushirish
/help - Yordam ma'lumotlari
/language - Tilni tanlash

💬 Oddiy xabar yuborib, men bilan suhbatlashishingiz mumkin!

🌐 Qo'llab-quvvatlanadigan tillar:
• O'zbek tili (bepul)
• Rus tili (Basic/Premium)
• Ingliz tili (Basic/Premium)
        """
        await update.message.reply_text(help_text)
    
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /language command"""
        user_id = str(update.effective_user.id)
        
        get_ai_response, process_knowledge_base, User, Bot, ChatHistory, db, app = get_dependencies()
        with app.app_context():
            db_user = User.query.filter_by(telegram_id=user_id).first()
            if not db_user:
                await update.message.reply_text("❌ Foydalanuvchi topilmadi!")
                return
            
            # Create language selection keyboard
            keyboard = []
            
            # Always show Uzbek (available for everyone)
            keyboard.append([InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")])
            
            # Show other languages only for Basic/Premium users
            if db_user.subscription_type in ['basic', 'premium', 'admin']:
                keyboard.append([InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")])
                keyboard.append([InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")])
            else:
                keyboard.append([InlineKeyboardButton("🔒 Русский (Basic/Premium)", callback_data="lang_locked")])
                keyboard.append([InlineKeyboardButton("🔒 English (Basic/Premium)", callback_data="lang_locked")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            current_lang = db_user.language
            lang_names = {'uz': "O'zbek", 'ru': "Русский", 'en': "English"}
            
            default_lang = "O'zbek"
            message = f"🌐 Joriy til: {lang_names.get(current_lang, default_lang)}\n"
            message += "Tilni tanlang:"
            
            await update.message.reply_text(message, reply_markup=reply_markup)
    
    async def language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle language selection callback"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        language = query.data.split('_')[1] if '_' in query.data else None
        
        if query.data == "lang_locked":
            await query.edit_message_text("🔒 Bu til faqat Basic yoki Premium obunachi uchun mavjud!")
            return
        
        if not language:
            return
        
        get_ai_response, process_knowledge_base, User, Bot, ChatHistory, db, app = get_dependencies()
        with app.app_context():
            db_user = User.query.filter_by(telegram_id=user_id).first()
            if db_user and db_user.can_use_language(language):
                db_user.language = language
                db.session.commit()
                
                lang_names = {'uz': "O'zbek", 'ru': "Русский", 'en': "English"}
                success_messages = {
                    'uz': f"✅ Til {lang_names[language]} ga o'zgartirildi!",
                    'ru': f"✅ Язык изменен на {lang_names[language]}!",
                    'en': f"✅ Language changed to {lang_names[language]}!"
                }
                
                await query.edit_message_text(success_messages.get(language, success_messages['uz']))
            else:
                await query.edit_message_text("❌ Bu tilni tanlash uchun obunangizni yangilang!")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        get_ai_response, process_knowledge_base, User, Bot, ChatHistory, db, app = get_dependencies()
        with app.app_context():
            # Get user info
            db_user = User.query.filter_by(telegram_id=user_id).first()
            if not db_user:
                await update.message.reply_text("❌ Foydalanuvchi topilmadi! /start buyrug'ini ishlating.")
                return
            
            # Get bot info
            bot = Bot.query.get(self.bot_id)
            if not bot:
                await update.message.reply_text("❌ Bot topilmadi!")
                return
            
            # Check subscription
            if not db_user.subscription_active():
                await update.message.reply_text("❌ Obunangiz tugagan! Iltimos, obunani yangilang.")
                return
            
            # Get knowledge base
            knowledge_base = process_knowledge_base(self.bot_id)
            
            # Generate AI response
            try:
                # Show typing indicator
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
                
                ai_response = get_ai_response(
                    message=message_text,
                    bot_name=bot.name,
                    user_language=db_user.language,
                    knowledge_base=knowledge_base
                )
                
                # Save chat history
                chat_history = ChatHistory()
                chat_history.bot_id = self.bot_id
                chat_history.user_telegram_id = user_id
                chat_history.message = message_text
                chat_history.response = ai_response
                chat_history.language = db_user.language
                db.session.add(chat_history)
                db.session.commit()
                
                # Send response
                if ai_response:
                    await update.message.reply_text(ai_response)
                else:
                    await update.message.reply_text("❌ Javob berishda xatolik yuz berdi!")
                    
            except Exception as e:
                logger.error(f"Message handling error: {str(e)}")
                await update.message.reply_text("❌ Xatolik yuz berdi! Iltimos, keyinroq urinib ko'ring.")
    
    def run(self):
        """Start the bot"""
        try:
            self.application.run_polling()
        except Exception as e:
            logger.error(f"Bot running error: {str(e)}")

def start_telegram_bot(bot_token, bot_id):
    """Start a telegram bot instance"""
    try:
        bot = TelegramBot(bot_token, bot_id)
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot {bot_id}: {str(e)}")

# Bot manager for multiple bots
class BotManager:
    def __init__(self):
        self.running_bots = {}
    
    def start_bot(self, bot_id, bot_token):
        """Start a bot"""
        if not TELEGRAM_AVAILABLE:
            logger.warning(f"Cannot start bot {bot_id}: telegram library not available")
            return False
            
        if bot_id not in self.running_bots:
            try:
                import threading
                bot = TelegramBot(bot_token, bot_id)
                
                # Start bot in a separate thread
                bot_thread = threading.Thread(target=bot.run, daemon=True)
                bot_thread.start()
                
                self.running_bots[bot_id] = {'bot': bot, 'thread': bot_thread}
                logger.info(f"Bot {bot_id} started successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to start bot {bot_id}: {str(e)}")
                return False
        return True
    
    def stop_bot(self, bot_id):
        """Stop a bot"""
        if bot_id in self.running_bots:
            try:
                bot_info = self.running_bots[bot_id]
                if isinstance(bot_info, dict):
                    bot_info['bot'].application.bot.running = False
                del self.running_bots[bot_id]
                logger.info(f"Bot {bot_id} stopped")
                return True
            except Exception as e:
                logger.error(f"Failed to stop bot {bot_id}: {str(e)}")
                return False
        return True
    
    def restart_bot(self, bot_id, bot_token):
        """Restart a bot"""
        self.stop_bot(bot_id)
        return self.start_bot(bot_id, bot_token)

# Global bot manager instance
bot_manager = BotManager()

def validate_telegram_token(token):
    """Telegram bot tokenini tekshirish"""
    import requests
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        if response.status_code == 200:
            return True
        return False
    except:
        return False

def start_bot_automatically(bot_id, bot_token):
    """Botni avtomatik ishga tushirish"""
    try:
        if not TELEGRAM_AVAILABLE:
            logger.warning(f"Cannot start bot {bot_id}: telegram library not available")
            return False
            
        # Token validatsiyasi
        if not validate_telegram_token(bot_token):
            logger.error(f"Invalid token for bot {bot_id}")
            return False
            
        # Botni ishga tushirish
        success = bot_manager.start_bot(bot_id, bot_token)
        if success:
            logger.info(f"Bot {bot_id} started automatically")
            return True
        else:
            logger.error(f"Failed to start bot {bot_id}")
            return False
            
    except Exception as e:
        logger.error(f"Auto start error for bot {bot_id}: {str(e)}")
        return False
