import os
import json
import logging
import requests
import hmac
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from flask import Blueprint, request, jsonify, url_for
from flask_login import login_required, current_user
from app import db, app
from models import User, Bot, ChatHistory, BotCustomer
from ai import get_ai_response, process_knowledge_base
from audio_processor import download_and_process_audio


def _wa_get_or_create_customer(bot_id, from_number, default_language='uz'):
    """Upsert a BotCustomer for a WhatsApp end-user."""
    customer = BotCustomer.query.filter_by(
        bot_id=bot_id,
        platform='whatsapp',
        platform_user_id=str(from_number),
    ).first()
    if customer is None:
        customer = BotCustomer(
            bot_id=bot_id,
            platform='whatsapp',
            platform_user_id=str(from_number),
            phone_number=str(from_number),
            language=default_language,
            is_active=True,
            message_count=0,
        )
        db.session.add(customer)
    return customer


def _wa_bot_owner_subscription_active(bot):
    owner = getattr(bot, 'owner', None)
    if owner is None and bot and bot.user_id:
        owner = User.query.get(bot.user_id)
    return bool(owner and owner.subscription_active())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint('whatsapp', __name__)

def _can_manage_bot(bot: Bot) -> bool:
    """Return True when the current web user owns this bot or is an admin."""
    return bool(
        current_user.is_authenticated and
        (current_user.is_admin or bot.user_id == current_user.id)
    )

def _get_app_secret() -> str:
    """Meta webhook signature secret, shared by WhatsApp/Instagram if desired."""
    return (
        os.environ.get('WHATSAPP_APP_SECRET')
        or os.environ.get('META_APP_SECRET')
        or ''
    )

def _verify_meta_signature(raw_body: bytes) -> bool:
    """Verify Meta's X-Hub-Signature-256 header when a secret is configured."""
    app_secret = _get_app_secret()
    if not app_secret:
        logger.warning("WHATSAPP_APP_SECRET/META_APP_SECRET is not configured; webhook signature check skipped")
        return True

    received = request.headers.get('X-Hub-Signature-256', '')
    if not received.startswith('sha256='):
        return False

    expected = hmac.new(app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(received.split('=', 1)[1], expected)

def _get_or_create_runtime_bot(bot_model: Bot) -> Optional['WhatsAppBot']:
    """Use the running bot if present, otherwise build a stateless handler for webhooks."""
    runtime_bot = whatsapp_manager.get_bot(bot_model.id)
    if runtime_bot:
        return runtime_bot
    if not bot_model.whatsapp_token or not bot_model.whatsapp_phone_id:
        return None
    return WhatsAppBot(bot_model.whatsapp_token, bot_model.whatsapp_phone_id, bot_model.id)

class WhatsAppBot:
    """WhatsApp Business API integratsiyasi"""
    
    def __init__(self, access_token: str, phone_number_id: str, bot_id: int):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.bot_id = bot_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.verify_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'botfactory_whatsapp_2024')
    
    def send_message(self, to_number: str, message_text: str) -> bool:
        """WhatsApp xabar yuborish"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': 'text',
                'text': {'body': message_text}
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent to {to_number}")
                return True
            else:
                logger.error(f"WhatsApp send error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp send message error: {str(e)}")
            return False
    
    def send_template_message(self, to_number: str, template_name: str, language_code: str = "uz") -> bool:
        """Template xabar yuborish"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {'code': language_code}
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"WhatsApp template sent to {to_number}")
                return True
            else:
                logger.error(f"WhatsApp template error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp template error: {str(e)}")
            return False
    
    def send_interactive_message(self, to_number: str, message_text: str, buttons: List[Dict[str, str]]) -> bool:
        """Interaktiv tugmalar bilan xabar yuborish"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            interactive_buttons = []
            for i, button in enumerate(buttons):
                interactive_buttons.append({
                    'type': 'reply',
                    'reply': {
                        'id': f'btn_{i}',
                        'title': button['title']
                    }
                })
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': 'interactive',
                'interactive': {
                    'type': 'button',
                    'body': {'text': message_text},
                    'action': {
                        'buttons': interactive_buttons
                    }
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"WhatsApp interactive message sent to {to_number}")
                return True
            else:
                logger.error(f"WhatsApp interactive error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp interactive error: {str(e)}")
            return False
    
    def send_media_message(self, to_number: str, media_type: str, media_url: str, caption: str = "") -> bool:
        """Media xabar yuborish (rasm, video, document)"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': media_type,
                media_type: {
                    'link': media_url
                }
            }
            
            if caption and media_type in ['image', 'video', 'document']:
                payload[media_type]['caption'] = caption
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"WhatsApp media sent to {to_number}")
                return True
            else:
                logger.error(f"WhatsApp media error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp media error: {str(e)}")
            return False
    
    def send_location_message(self, to_number: str, latitude: float, longitude: float, name: str = "", address: str = "") -> bool:
        """Joylashuv xabar yuborish"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': 'location',
                'location': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'name': name,
                    'address': address
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"WhatsApp location sent to {to_number}")
                return True
            else:
                logger.error(f"WhatsApp location error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp location error: {str(e)}")
            return False
    
    def handle_message(self, from_number: str, message_text: str, message_type: str = "text") -> bool:
        """WhatsApp xabarini qayta ishlash"""
        try:
            with app.app_context():
                bot = Bot.query.get(self.bot_id)
                if not bot:
                    return False

                # End-user gate: only the bot OWNER needs an active subscription.
                if not _wa_bot_owner_subscription_active(bot):
                    self.send_message(
                        from_number,
                        "Bu bot vaqtincha ishlamaydi (bot egasining obunasi tugagan).",
                    )
                    return True

                customer = _wa_get_or_create_customer(self.bot_id, from_number)
                customer.last_interaction = datetime.utcnow()
                customer.message_count = (customer.message_count or 0) + 1
                customer.is_active = True
                db.session.commit()
                customer_language = customer.language or 'uz'

                # AI javobini olish
                knowledge_base = process_knowledge_base(self.bot_id)

                ai_response = get_ai_response(
                    message=message_text,
                    bot_name=bot.name,
                    user_language=customer_language,
                    knowledge_base=knowledge_base
                )

                # Chat tarixini saqlash
                chat_history = ChatHistory()
                chat_history.bot_id = self.bot_id
                chat_history.user_whatsapp_number = from_number
                chat_history.message = message_text
                chat_history.response = ai_response
                chat_history.language = customer_language
                chat_history.created_at = datetime.utcnow()
                db.session.add(chat_history)
                db.session.commit()

                # Javobni yuborish
                if ai_response:
                    self.send_message(from_number, ai_response)

                    # Marketing: nudge only if the bot owner is still free.
                    owner = bot.owner if getattr(bot, 'owner', None) else User.query.get(bot.user_id)
                    if owner and owner.subscription_type == 'free':
                        marketing_message = """✨ Ko'proq imkoniyatlar istaysizmi?
                        
🌍 AI 3 tilda (O'zbek/Rus/Ingliz)
🤖 5 ta bot yarating
📱 Barcha platformalarda
💎 Premium obuna"""
                        
                        self.send_interactive_message(
                            from_number,
                            marketing_message,
                            [
                                {'title': '💎 Premium'},
                                {'title': '📞 Aloqa'},
                                {'title': '❌ Keyinroq'}
                            ]
                        )
                else:
                    fallback_message = "Kechirasiz, hozir javob bera olmayapman. Keyinroq urinib ko'ring. 🤖"
                    self.send_message(from_number, fallback_message)
                
                return True
                
        except Exception as e:
            logger.error(f"WhatsApp message handling error: {str(e)}")
            return False
    
    def handle_audio_message(self, from_number: str, audio_data: Dict[str, Any]) -> bool:
        """Handle audio messages - convert to text and get AI response"""
        try:
            # Get audio URL and metadata
            audio_id = audio_data.get('id')
            mime_type = audio_data.get('mime_type', 'audio/ogg')
            
            if not audio_id:
                logger.error("Audio ID not found in message")
                self.send_message(from_number, "❌ Audio fayl ID topilmadi!")
                return False
            
            # Get audio file URL
            audio_url = self._get_media_url(audio_id)
            if not audio_url:
                self.send_message(from_number, "❌ Audio faylni yuklab olishda xatolik yuz berdi!")
                return False
            
            # Send processing message
            self.send_message(from_number, "🎤 Ovozli xabaringizni qayta ishlamoqdaman...")
            
            with app.app_context():
                bot = Bot.query.get(self.bot_id)
                if not bot:
                    self.send_message(from_number, "❌ Bot topilmadi!")
                    return False

                # End-user gate: bot OWNER must be subscribed.
                if not _wa_bot_owner_subscription_active(bot):
                    self.send_message(
                        from_number,
                        "Bu bot vaqtincha ishlamaydi (bot egasining obunasi tugagan).",
                    )
                    return False

                customer = _wa_get_or_create_customer(self.bot_id, from_number)
                db.session.commit()
                customer_language = customer.language or 'uz'

                # Determine file extension from mime type
                file_ext = '.ogg'
                if 'mp4' in mime_type:
                    file_ext = '.mp4'
                elif 'mpeg' in mime_type:
                    file_ext = '.mp3'
                elif 'wav' in mime_type:
                    file_ext = '.wav'

                # Process audio
                ai_response = download_and_process_audio(
                    audio_url=audio_url,
                    user_id=from_number,
                    language=customer_language,
                    file_extension=file_ext
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
                chat_history.user_whatsapp_id = from_number
                chat_history.message = f"[AUDIO] {user_text}"
                chat_history.response = ai_text
                chat_history.language = customer_language
                chat_history.created_at = datetime.utcnow()
                db.session.add(chat_history)
                db.session.commit()
                
                # Send response
                self.send_message(from_number, ai_response)
                
                logger.info(f"WhatsApp audio message processed for user {from_number}")
                return True
                
        except Exception as e:
            logger.error(f"WhatsApp audio handling error: {str(e)}")
            self.send_message(from_number, "❌ Ovozli xabarni qayta ishlashda xatolik yuz berdi!")
            return False
    
    def _get_media_url(self, media_id: str) -> Optional[str]:
        """Get media file URL from WhatsApp API"""
        try:
            url = f"{self.base_url}/{media_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('url')
            else:
                logger.error(f"Failed to get media URL: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting media URL: {str(e)}")
            return None
    
    def handle_button_click(self, from_number, button_id, button_text):
        """Tugma bosilgan holni qayta ishlash"""
        try:
            if 'Premium' in button_text:
                premium_message = """💎 Premium tarif:
                
✅ 5 ta bot yaratish
✅ Barcha platformalar (Telegram/Instagram/WhatsApp)  
✅ 3 til AI (O'zbek/Rus/Ingliz)
✅ Prioritet texnik yordam
✅ Kengaytirilgan bilim bazasi
                
💰 Narx: 590,000 so'm/oy
🌐 BotFactory.uz dan obuna bo'ling"""
                
                self.send_message(from_number, premium_message)
                
            elif 'Basic' in button_text:
                basic_message = """💰 Basic tarif:
                
✅ 1 ta bot yaratish
✅ Barcha platformalar
✅ 3 til AI qo'llab-quvvatlash
✅ Texnik yordam
                
💰 Narx: 290,000 so'm/oy
🌐 BotFactory.uz dan obuna bo'ling"""
                
                self.send_message(from_number, basic_message)
                
            elif 'Aloqa' in button_text:
                contact_message = """📞 Biz bilan bog'lanish:
                
🌐 Veb-sayt: BotFactory.uz
📧 Email: support@botfactory.uz
📱 Telegram: @BotFactorySupport
📞 Telefon: +998 90 123 45 67
🕒 Ish vaqti: 9:00-18:00 (Dush-Juma)"""
                
                self.send_message(from_number, contact_message)
            
            return True
            
        except Exception as e:
            logger.error(f"WhatsApp button click error: {str(e)}")
            return False

# WhatsApp Bot Manager
class WhatsAppBotManager:
    """WhatsApp botlarni boshqarish"""
    
    def __init__(self):
        self.running_bots = {}
    
    def start_bot(self, bot_id, access_token, phone_number_id):
        """WhatsApp botni ishga tushirish"""
        try:
            if bot_id not in self.running_bots:
                bot = WhatsAppBot(access_token, phone_number_id, bot_id)
                self.running_bots[bot_id] = bot
                logger.info(f"WhatsApp bot {bot_id} started")
                return True
            return True
        except Exception as e:
            logger.error(f"WhatsApp bot start error: {str(e)}")
            return False
    
    def stop_bot(self, bot_id):
        """WhatsApp botni to'xtatish"""
        try:
            if bot_id in self.running_bots:
                del self.running_bots[bot_id]
                logger.info(f"WhatsApp bot {bot_id} stopped")
            return True
        except Exception as e:
            logger.error(f"WhatsApp bot stop error: {str(e)}")
            return False
    
    def get_bot(self, bot_id):
        """WhatsApp botni olish"""
        return self.running_bots.get(bot_id)

# Global WhatsApp bot manager
whatsapp_manager = WhatsAppBotManager()

# Flask routes
@whatsapp_bp.route('/webhook/<int:bot_id>', methods=['GET', 'POST'])
def whatsapp_webhook(bot_id):
    """WhatsApp webhook endpoint"""
    try:
        bot_model = Bot.query.get(bot_id)
        if not bot_model:
            return 'Bot not found', 404

        if request.method == 'GET':
            # Webhook verification
            verify_token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')

            expected_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'botfactory_whatsapp_2024')
            if verify_token == expected_token:
                return challenge
            else:
                return 'Verification failed', 403
        
        elif request.method == 'POST':
            raw_body = request.get_data()
            if not _verify_meta_signature(raw_body):
                return 'Invalid signature', 403

            # Message processing
            data = request.get_json(silent=True)
            
            if data and 'entry' in data:
                for entry in data['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if change['field'] == 'messages':
                                messages = change['value'].get('messages', [])
                                
                                for message in messages:
                                    from_number = message['from']
                                    message_id = message['id']
                                    
                                    bot = _get_or_create_runtime_bot(bot_model)
                                    if not bot:
                                        continue
                                    
                                    # Text messages
                                    if message.get('type') == 'text':
                                        message_text = message.get('text', {}).get('body', '')
                                        if message_text:
                                            bot.handle_message(from_number, message_text)
                                    
                                    # Button interactions
                                    elif message.get('type') == 'interactive':
                                        interactive_data = message.get('interactive', {})
                                        if interactive_data.get('type') == 'button_reply':
                                            button_reply = interactive_data.get('button_reply', {})
                                            button_id = button_reply.get('id', '')
                                            button_title = button_reply.get('title', '')
                                            if button_id and button_title:
                                                bot.handle_button_click(from_number, button_id, button_title)
                                    
                                    # Mark message as read
                                    _mark_message_as_read(bot, message_id)
            
            return 'OK', 200
    
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {str(e)}")
        return 'Internal Server Error', 500

def _mark_message_as_read(bot, message_id):
    """Xabarni o'qilgan deb belgilash"""
    try:
        url = f"{bot.base_url}/{bot.phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {bot.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'status': 'read',
            'message_id': message_id
        }
        
        requests.post(url, headers=headers, json=payload, timeout=10)
        
    except Exception as e:
        logger.error(f"Mark as read error: {str(e)}")

@whatsapp_bp.route('/start/<int:bot_id>', methods=['POST'])
@login_required
def start_whatsapp_bot(bot_id):
    """WhatsApp botni ishga tushirish"""
    try:
        with app.app_context():
            bot = Bot.query.get_or_404(bot_id)
            if not _can_manage_bot(bot):
                return jsonify({'success': False, 'error': 'Ruxsat yo\'q'}), 403
            
            if not bot.whatsapp_token or not bot.whatsapp_phone_id:
                return jsonify({'success': False, 'error': 'WhatsApp token yoki telefon ID topilmadi'})
            
            success = whatsapp_manager.start_bot(bot_id, bot.whatsapp_token, bot.whatsapp_phone_id)
            
            if success:
                bot.is_active = True
                db.session.commit()
                return jsonify({'success': True, 'message': 'WhatsApp bot ishga tushdi'})
            else:
                return jsonify({'success': False, 'error': 'Botni ishga tushirishda xato'})
    
    except Exception as e:
        logger.error(f"Start WhatsApp bot error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@whatsapp_bp.route('/stop/<int:bot_id>', methods=['POST'])
@login_required
def stop_whatsapp_bot(bot_id):
    """WhatsApp botni to'xtatish"""
    try:
        with app.app_context():
            bot = Bot.query.get_or_404(bot_id)
            if not _can_manage_bot(bot):
                return jsonify({'success': False, 'error': 'Ruxsat yo\'q'}), 403
            
            success = whatsapp_manager.stop_bot(bot_id)
            
            if success:
                bot.is_active = False
                db.session.commit()
                return jsonify({'success': True, 'message': 'WhatsApp bot to\'xtatildi'})
            else:
                return jsonify({'success': False, 'error': 'Botni to\'xtatishda xato'})
    
    except Exception as e:
        logger.error(f"Stop WhatsApp bot error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@whatsapp_bp.route('/status/<int:bot_id>')
@login_required
def whatsapp_bot_status(bot_id):
    """WhatsApp bot holatini tekshirish"""
    try:
        is_running = bot_id in whatsapp_manager.running_bots
        
        with app.app_context():
            bot = Bot.query.get(bot_id)
            if not bot:
                return jsonify({'error': 'Bot topilmadi'}), 404
            if not _can_manage_bot(bot):
                return jsonify({'error': 'Ruxsat yo\'q'}), 403
            
            return jsonify({
                'bot_id': bot_id,
                'is_running': is_running,
                'is_active': bot.is_active if bot else False,
                'platform': 'WhatsApp'
            })
    
    except Exception as e:
        logger.error(f"WhatsApp status error: {str(e)}")
        return jsonify({'error': str(e)}), 500
