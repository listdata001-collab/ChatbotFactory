import os
import logging
import asyncio
import requests
import tempfile
from typing import Optional
from audio_processor import download_and_process_audio, process_audio_message

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
            import json
            # Convert reply_markup to JSON if it's an object
            if hasattr(reply_markup, 'to_dict'):
                data['reply_markup'] = json.dumps(reply_markup.to_dict())
            elif isinstance(reply_markup, dict):
                data['reply_markup'] = json.dumps(reply_markup)
            else:
                data['reply_markup'] = reply_markup
        
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            # Ultra-safe logging
            try:
                logger.error("Error sending message occurred")
            except:
                pass
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
            # Ultra-safe logging
            try:
                logger.error("Error getting updates occurred")
            except:
                pass
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
                elif 'link' in self.handlers and cmd == 'link':
                    for handler in self.handlers['link']:
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
                # Ultra-safe logging
                try:
                    error_safe = str(e).encode('ascii', errors='ignore').decode('ascii')
                    logger.error(f"Polling error: {error_safe}")
                except:
                    logger.error("Polling error: encoding issue")
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
        self.application.add_handler(CommandHandler("link", self.link_account_command))
        self.application.add_handler(CallbackQueryHandler(self.language_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context) -> None:
        """Handle /start command"""
        if not update or not update.effective_user or not update.message:
            return
        
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
            
            if update.message:
                await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context) -> None:
        """Handle /help command"""
        help_text = """
🤖 BotFactory AI Yordam

📋 Mavjud buyruqlar:
/start - Botni qayta ishga tushirish
/help - Yordam ma'lumotlari
/language - Tilni tanlash
/link - Web hisobni Telegram bilan bog'lash

💬 Oddiy xabar yuborib, men bilan suhbatlashishingiz mumkin!

🔗 Hisobni bog'lash:
Agar siz web-saytda Basic yoki Premium obunani sotib olgan bo'lsangiz, 
quyidagi buyruq orqali hisobingizni bog'lang:

/link username password

🌐 Qo'llab-quvvatlanadigan tillar:
• O'zbek tili (bepul)
• Rus tili (Starter/Basic/Premium)
• Ingliz tili (Starter/Basic/Premium)
        """
        if update and update.message:
            await update.message.reply_text(help_text)
    
    async def language_command(self, update: Update, context) -> None:
        """Handle /language command"""
        if not update or not update.effective_user or not update.message:
            return
        
        user_id = str(update.effective_user.id)
        
        get_ai_response, process_knowledge_base, User, Bot, ChatHistory, db, app = get_dependencies()
        with app.app_context():
            db_user = User.query.filter_by(telegram_id=user_id).first()
            if not db_user:
                if update.message:
                    await update.message.reply_text("❌ Foydalanuvchi topilmadi!")
                return
            
            # Create language selection keyboard
            keyboard = []
            
            # Always show Uzbek (available for everyone)
            keyboard.append([InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")])
            
            # Show other languages only for Starter/Basic/Premium users
            if db_user.subscription_type in ['starter', 'basic', 'premium', 'admin']:
                keyboard.append([InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")])
                keyboard.append([InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")])
            else:
                keyboard.append([InlineKeyboardButton("🔒 Русский (Starter/Basic/Premium)", callback_data="lang_locked")])
                keyboard.append([InlineKeyboardButton("🔒 English (Starter/Basic/Premium)", callback_data="lang_locked")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            current_lang = db_user.language
            lang_names = {'uz': "O'zbek", 'ru': "Русский", 'en': "English"}
            
            default_lang = "O'zbek"
            message = f"🌐 Joriy til: {lang_names.get(current_lang, default_lang)}\n"
            message += "Tilni tanlang:"
            
            if update.message:
                await update.message.reply_text(message, reply_markup=reply_markup)
    
    async def language_callback(self, update: Update, context) -> None:
        """Handle language selection callback"""
        if not update or not update.callback_query:
            return
        
        query = update.callback_query
        await query.answer()
        
        if not query.from_user or not query.data:
            return
        
        user_id = str(query.from_user.id)
        language = query.data.split('_')[1] if '_' in query.data else None
        
        if query.data == "lang_locked":
            if query:
                await query.edit_message_text("🔒 Bu til faqat Starter, Basic yoki Premium obunachi uchun mavjud!")
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
                
                if query:
                    await query.edit_message_text(success_messages.get(language, success_messages['uz']))
            else:
                if query:
                    await query.edit_message_text("❌ Bu tilni tanlash uchun obunangizni yangilang!")
    
    async def link_account_command(self, update: Update, context) -> None:
        """Handle /link command to connect Telegram account with web account"""
        if not update or not update.effective_user or not update.message:
            return
        
        user_id = str(update.effective_user.id)
        
        # Check if arguments provided
        if not context.args or len(context.args) < 2:
            message = """🔗 Hisobni bog'lash

Telegram hisobingizni web-saytdagi hisobingiz bilan bog'lash uchun quyidagi formatda yozing:

/link username password

Masalan:
/link onlinemobi mypassword

❗️ Bu buyruqdan foydalangach, obunangiz yangilanadi va barcha premium imkoniyatlar ochiladi!"""
            if update.message:
                await update.message.reply_text(message)
            return
        
        username = context.args[0]
        password = context.args[1]
        
        get_ai_response, process_knowledge_base, User, Bot, ChatHistory, db, app = get_dependencies()
        with app.app_context():
            from werkzeug.security import check_password_hash
            
            # Find user by username
            web_user = User.query.filter_by(username=username).first()
            
            if not web_user:
                if update.message:
                    await update.message.reply_text("❌ Bunday foydalanuvchi nomi topilmadi!")
                return
            
            # Check password
            if not check_password_hash(web_user.password_hash, password):
                if update.message:
                    await update.message.reply_text("❌ Noto'g'ri parol!")
                return
            
            # Check if this telegram account is already linked to someone else
            existing_tg_user = User.query.filter_by(telegram_id=user_id).first()
            if existing_tg_user and existing_tg_user.id != web_user.id:
                if update.message:
                    await update.message.reply_text("❌ Bu Telegram hisob boshqa foydalanuvchiga bog'langan!")
                return
            
            # Link telegram account to web account
            web_user.telegram_id = user_id
            db.session.commit()
            
            # Send success message with subscription info
            subscription_names = {
                'free': 'Bepul (Test)',
                'starter': 'Starter',
                'basic': 'Basic',
                'premium': 'Premium',
                'admin': 'Admin'
            }
            
            unknown_text = "Noma'lum"
            success_message = f"""✅ Hisoblar muvaffaqiyatli bog'landi!

👤 Foydalanuvchi: {web_user.username}
📦 Obuna: {subscription_names.get(web_user.subscription_type, unknown_text)}"""
            
            if web_user.subscription_type in ['starter', 'basic', 'premium', 'admin']:
                success_message += "\n\n🌐 Endi /language buyrug'i bilan tilni tanlashingiz mumkin!"
            
            if update.message:
                await update.message.reply_text(success_message)
    
    async def handle_message(self, update: Update, context) -> None:
        """Handle regular text messages"""
        if not update or not update.effective_user or not update.message:
            return
        
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        if not message_text:
            return
        
        get_ai_response, process_knowledge_base, User, Bot, ChatHistory, db, app = get_dependencies()
        logger.info("DEBUG: Dependencies loaded")
        
        with app.app_context():
            # Get user info
            db_user = User.query.filter_by(telegram_id=user_id).first()
            if not db_user:
                logger.info("DEBUG: User not found")
                if update.message:
                    await update.message.reply_text("❌ Foydalanuvchi topilmadi! /start buyrug'ini ishlating.")
                return
            
            logger.info("DEBUG: User found")
            
            # Get bot info
            bot = Bot.query.get(self.bot_id)
            if not bot:
                logger.info("DEBUG: Bot not found")
                if update.message:
                    await update.message.reply_text("❌ Bot topilmadi!")
                return
            
            logger.info("DEBUG: Bot found")
            
            # Check subscription
            if not db_user.subscription_active():
                logger.info("DEBUG: Subscription not active")
                if update.message:
                    await update.message.reply_text("❌ Obunangiz tugagan! Iltimos, obunani yangilang.")
                return
            
            logger.info("DEBUG: Subscription active")
            
            # Get knowledge base
            knowledge_base = process_knowledge_base(self.bot_id)
            logger.info("DEBUG: Knowledge base processed")
            
            # Generate AI response
            try:
                logger.info("DEBUG: Starting AI response generation")
                
                ai_response = get_ai_response(
                    message=message_text,
                    bot_name=bot.name,
                    user_language=db_user.language,
                    knowledge_base=knowledge_base
                )
                
                logger.info("DEBUG: AI response received")
                
                # Save chat history
                chat_history = ChatHistory()
                chat_history.bot_id = self.bot_id
                chat_history.user_telegram_id = user_id
                chat_history.message = message_text
                chat_history.response = ai_response
                chat_history.language = db_user.language
                db.session.add(chat_history)
                db.session.commit()
                
                logger.info("DEBUG: Chat history saved")
                
                # Clean and send response safely
                if ai_response:
                    try:
                        # Keep emojis but ensure safe encoding
                        import re
                        
                        # Replace problematic unicode characters
                        unicode_replacements = {
                            '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
                            '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u00a0': ' ',
                            '\u2010': '-', '\u2011': '-', '\u2012': '-', '\u2015': '-'
                        }
                        
                        cleaned_response = ai_response
                        for unicode_char, replacement in unicode_replacements.items():
                            cleaned_response = cleaned_response.replace(unicode_char, replacement)
                        
                        # Fallback if empty
                        if not cleaned_response.strip():
                            cleaned_response = "Javob tayyor!"
                        
                        # Send the response
                        if update.message:
                            await update.message.reply_text(cleaned_response)
                    except:
                        # Final fallback
                        if update.message:
                            await update.message.reply_text("Javob tayyor!")
                else:
                    await update.message.reply_text("Javob berishda xatolik yuz berdi!")
                    
            except Exception as e:
                # Debug: log which step failed
                try:
                    error_str = str(e)[:200]  # First 200 chars only
                    logger.error(f"DEBUG: Message handling failed: {error_str}")
                except:
                    logger.error("DEBUG: Message handling failed with encoding error")
                
                # Send simple error message
                try:
                    await update.message.reply_text("Xatolik yuz berdi!")
                except:
                    print("[ERROR] Cannot send error message to user")
    
    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages - convert to text and get AI response"""
        user_id = str(update.effective_user.id)
        
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
            
            try:
                # Send processing message
                processing_msg = await update.message.reply_text("🎤 Ovozli xabaringizni qayta ishlamoqdaman...")
                
                # Get voice file
                voice = update.message.voice
                if not voice:
                    await processing_msg.edit_text("❌ Ovozli xabar topilmadi!")
                    return
                
                # Get file URL from Telegram API
                file_url = await self._get_telegram_file_url(voice.file_id)
                if not file_url:
                    await processing_msg.edit_text("❌ Audio faylni yuklab olishda xatolik yuz berdi!")
                    return
                
                # Process audio
                ai_response = download_and_process_audio(
                    audio_url=file_url,
                    user_id=user_id,
                    language=db_user.language,
                    file_extension='.ogg'
                )
                
                # Extract the text part and AI response
                if "🎤 Sizning xabaringiz:" in ai_response:
                    parts = ai_response.split("\n\n", 1)
                    if len(parts) == 2:
                        user_text = parts[0].replace("🎤 Sizning xabaringiz: \"", "").replace("\"", "")
                        ai_text = parts[1]
                    else:
                        user_text = "Audio xabar"
                        ai_text = ai_response
                else:
                    user_text = "Audio xabar"
                    ai_text = ai_response
                
                # Save chat history
                chat_history = ChatHistory()
                chat_history.bot_id = self.bot_id
                chat_history.user_telegram_id = user_id
                chat_history.message = f"[AUDIO] {user_text}"
                chat_history.response = ai_text
                chat_history.language = db_user.language
                db.session.add(chat_history)
                db.session.commit()
                
                # Send final response
                await processing_msg.edit_text(ai_response)
                
            except Exception as e:
                logger.error(f"Voice message handling error: {str(e)}")
                try:
                    await processing_msg.edit_text("❌ Ovozli xabarni qayta ishlashda xatolik yuz berdi!")
                except:
                    await update.message.reply_text("❌ Ovozli xabarni qayta ishlashda xatolik yuz berdi!")
    
    async def _get_telegram_file_url(self, file_id):
        """Get file URL from Telegram API"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getFile"
            response = requests.get(url, params={'file_id': file_id})
            data = response.json()
            
            if data.get('ok') and 'result' in data:
                file_path = data['result']['file_path']
                return f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            else:
                logger.error(f"Telegram getFile API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Telegram file URL: {str(e)}")
            return None
    
    def run(self):
        """Start the bot"""
        try:
            self.application.run_polling()
        except Exception as e:
            # Ultra-safe logging
            try:
                error_safe = str(e).encode('ascii', errors='ignore').decode('ascii')
                logger.error(f"Bot running error: {error_safe}")
            except:
                logger.error("Bot running error: encoding issue")

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
        # Basic token format check
        if not token or len(token) < 20:
            return False
            
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('ok', False)
        return False
    except Exception as e:
        logger.warning(f"Token validation error: {e}")
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

def send_admin_message_to_user(telegram_id, message_text):
    """Send a message from admin to a specific user"""
    try:
        # Get any bot token to send message (we'll use the first available bot)
        get_ai_response, process_knowledge_base, User, Bot, ChatHistory, db, app = get_dependencies()
        
        with app.app_context():
            bot = Bot.query.first()
            if not bot or not bot.telegram_token:
                return False
            
            # Create HTTP bot instance
            http_bot = TelegramHTTPBot(bot.telegram_token)
            
            # Send message
            response = http_bot.send_message(telegram_id, f"📢 Admin xabari:\n\n{message_text}")
            
            if response and response.get('ok'):
                return True
            return False
            
    except Exception as e:
        logger.error(f"Error sending admin message: {e}")
        return False
