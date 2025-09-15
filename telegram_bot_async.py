"""
Async-optimized Telegram bot integration
Uses Celery tasks for non-blocking AI processing
"""
import logging
from typing import Optional
from telegram_bot import TelegramBotHandler, get_dependencies

# Import async tasks
from tasks import generate_ai_response, save_chat_history
from redis_cache import (
    cached_knowledge_base, cache_knowledge_base, 
    cached_user_context, cache_user_context,
    rate_limit_check
)

logger = logging.getLogger(__name__)

class AsyncTelegramBotHandler(TelegramBotHandler):
    """
    Optimized Telegram bot handler with async AI processing
    """
    
    async def handle_message_async(self, update, context) -> None:
        """
        Handle messages with async AI processing for better performance
        """
        if not update or not update.effective_user or not update.message:
            return
            
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        chat_id = update.effective_chat.id
        
        if not message_text:
            return
        
        # Rate limiting check
        if not rate_limit_check(int(user_id), limit=5, window=60):
            await update.message.reply_text(
                "⚠️ Juda ko'p xabar yuboryapsiz. Iltimos, bir oz kuting."
            )
            return
        
        # Send immediate typing indicator
        try:
            await context.bot.send_chat_action(chat_id=chat_id, action='typing')
        except Exception as e:
            logger.error(f"Failed to send typing action: {e}")
        
        get_ai_response, process_knowledge_base, User, Bot, ChatHistory, db, app = get_dependencies()
        
        with app.app_context():
            # Check cache for user context first
            user_context = cached_user_context(int(user_id), self.bot_id)
            
            if not user_context:
                # Get user info and cache it
                db_user = User.query.filter_by(telegram_id=user_id).first()
                if not db_user:
                    await update.message.reply_text("❌ Foydalanuvchi topilmadi! /start buyrug'ini ishlating.")
                    return
                
                # Get bot info
                bot = Bot.query.get(self.bot_id)
                if not bot:
                    await update.message.reply_text("❌ Bot topilmadi!")
                    return
                
                # Cache user context
                user_context = {
                    'user_id': db_user.id,
                    'language': db_user.language,
                    'subscription_active': db_user.subscription_active(),
                    'bot_name': bot.name
                }
                cache_user_context(int(user_id), self.bot_id, user_context)
            
            # Check subscription
            if not user_context.get('subscription_active'):
                await update.message.reply_text("❌ Obunangiz tugagan! Iltimos, obunani yangilang.")
                return
            
            # Send immediate feedback
            await update.message.reply_text(
                "🤖 Javobingizni tayyorlayapman...",
                reply_to_message_id=update.message.message_id
            )
            
            # Get cached knowledge base
            knowledge_base = cached_knowledge_base(self.bot_id)
            if not knowledge_base:
                # Process and cache knowledge base
                knowledge_base = process_knowledge_base(self.bot_id)
                if knowledge_base:
                    cache_knowledge_base(self.bot_id, knowledge_base)
            
            # Get recent chat history (optimized query)
            recent_history = ""
            try:
                history_entries = ChatHistory.query.filter_by(
                    bot_id=self.bot_id, 
                    user_telegram_id=user_id
                ).order_by(ChatHistory.created_at.desc()).limit(3).all()
                
                if history_entries:
                    history_parts = []
                    for entry in reversed(history_entries):
                        history_parts.append(f"Foydalanuvchi: {entry.message}")
                        if entry.response:
                            history_parts.append(f"Bot: {entry.response}")
                    recent_history = "\n".join(history_parts)
            except Exception as e:
                logger.error(f"Chat history error: {e}")
                recent_history = ""
            
            # Save user message to chat history immediately
            try:
                save_chat_history.apply_async(args=[
                    user_context['user_id'], 
                    chat_id, 
                    message_text
                ])
            except Exception as e:
                logger.error(f"Failed to save chat history: {e}")
            
            # Generate AI response asynchronously
            try:
                task = generate_ai_response.apply_async(args=[
                    message_text,
                    user_context.get('bot_name', 'Bot'),
                    user_context.get('language', 'uz'),
                    knowledge_base or "",
                    recent_history,
                    chat_id,
                    user_context['user_id']
                ])
                
                logger.info(f"AI task queued: {task.id} for chat {chat_id}")
                
                # Don't wait for result - the task will send response directly
                # This allows the bot to handle other messages immediately
                
            except Exception as e:
                logger.error(f"Failed to queue AI task: {e}")
                await update.message.reply_text(
                    "❌ Javob tayyorlashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
                )

    async def handle_voice_message_async(self, update, context):
        """
        Handle voice messages with async processing
        """
        user_id = str(update.effective_user.id)
        chat_id = update.effective_chat.id
        
        # Rate limiting
        if not rate_limit_check(int(user_id), limit=3, window=60):
            await update.message.reply_text(
                "⚠️ Juda ko'p ovozli xabar yuboryapsiz. Iltimos, bir oz kuting."
            )
            return
        
        get_ai_response, process_knowledge_base, User, Bot, ChatHistory, db, app = get_dependencies()
        
        with app.app_context():
            # Check user context (cached)
            user_context = cached_user_context(int(user_id), self.bot_id)
            
            if not user_context:
                db_user = User.query.filter_by(telegram_id=user_id).first()
                if not db_user:
                    await update.message.reply_text("❌ Foydalanuvchi topilmadi!")
                    return
                    
                if not db_user.subscription_active():
                    await update.message.reply_text("❌ Obunangiz tugagan!")
                    return
                
                bot = Bot.query.get(self.bot_id)
                user_context = {
                    'user_id': db_user.id,
                    'language': db_user.language,
                    'bot_name': bot.name if bot else 'Bot'
                }
            
            # Send immediate feedback
            processing_msg = await update.message.reply_text(
                "🎤 Ovozli xabaringizni qayta ishlamoqdaman...",
                reply_to_message_id=update.message.message_id
            )
            
            try:
                # Get voice file
                voice = update.message.voice
                file = await context.bot.get_file(voice.file_id)
                file_url = file.file_path
                
                # Queue audio processing task
                from tasks import process_audio
                task = process_audio.apply_async(args=[
                    file_url,
                    chat_id,
                    user_context['user_id']
                ])
                
                logger.info(f"Audio processing task queued: {task.id}")
                
                # Update processing message
                await processing_msg.edit_text(
                    "🎤 Ovozli xabaringiz qabul qilindi va qayta ishlanmoqda..."
                )
                
            except Exception as e:
                logger.error(f"Voice processing error: {e}")
                await processing_msg.edit_text(
                    "❌ Ovozli xabarni qayta ishlashda xatolik yuz berdi!"
                )

def create_optimized_bot_handler(bot_id: int, token: str) -> AsyncTelegramBotHandler:
    """
    Create optimized bot handler with async processing
    """
    handler = AsyncTelegramBotHandler(bot_id, token)
    
    # Override message handling methods with async versions
    handler.handle_message = handler.handle_message_async
    handler.handle_voice_message = handler.handle_voice_message_async
    
    logger.info(f"Created optimized bot handler for bot {bot_id}")
    return handler