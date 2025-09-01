import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from flask import Blueprint, request, jsonify, url_for
from app import db, app
from models import User, Bot, ChatHistory
from ai import get_ai_response, process_knowledge_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint('whatsapp', __name__)

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
                # Foydalanuvchini topish yoki yaratish
                user = User.query.filter_by(whatsapp_number=from_number).first()
                if not user:
                    # Yangi WhatsApp foydalanuvchisi
                    user = User()
                    user.username = f"wa_{from_number.replace('+', '')}"
                    user.email = f"wa_{from_number.replace('+', '')}@whatsapp.bot"
                    user.password_hash = "whatsapp_user"
                    user.whatsapp_number = from_number
                    user.language = 'uz'
                    user.subscription_type = 'free'
                    db.session.add(user)
                    db.session.commit()
                
                # Bot ma'lumotlarini olish
                bot = Bot.query.get(self.bot_id)
                if not bot:
                    return False
                
                # Obunani tekshirish
                if not user.subscription_active():
                    expired_message = """🔒 Obunangiz tugagan!
                    
Yangi obunani BotFactory.uz saytidan sotib oling.
                    
📋 Tariflar:
• Basic: 290,000 so'm/oy
• Premium: 590,000 so'm/oy
                    
🌐 Sayt: BotFactory.uz"""
                    
                    self.send_interactive_message(
                        from_number,
                        expired_message,
                        [
                            {'title': '💰 Basic'},
                            {'title': '💎 Premium'},
                            {'title': '📞 Aloqa'}
                        ]
                    )
                    return True
                
                # AI javobini olish
                knowledge_base = process_knowledge_base(self.bot_id)
                
                ai_response = get_ai_response(
                    message=message_text,
                    bot_name=bot.name,
                    user_language=user.language,
                    knowledge_base=knowledge_base
                )
                
                # Chat tarixini saqlash
                chat_history = ChatHistory()
                chat_history.bot_id = self.bot_id
                chat_history.user_whatsapp_number = from_number
                chat_history.message = message_text
                chat_history.response = ai_response
                chat_history.language = user.language
                chat_history.created_at = datetime.utcnow()
                db.session.add(chat_history)
                db.session.commit()
                
                # Javobni yuborish
                if ai_response:
                    self.send_message(from_number, ai_response)
                    
                    # Bepul foydalanuvchi uchun marketing
                    if user.subscription_type == 'free':
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
        if request.method == 'GET':
            # Webhook verification
            verify_token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            bot = whatsapp_manager.get_bot(bot_id)
            if bot and verify_token == bot.verify_token:
                return challenge
            else:
                return 'Verification failed', 403
        
        elif request.method == 'POST':
            # Message processing
            data = request.get_json()
            
            if data and 'entry' in data:
                for entry in data['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if change['field'] == 'messages':
                                messages = change['value'].get('messages', [])
                                
                                for message in messages:
                                    from_number = message['from']
                                    message_id = message['id']
                                    
                                    bot = whatsapp_manager.get_bot(bot_id)
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
def start_whatsapp_bot(bot_id):
    """WhatsApp botni ishga tushirish"""
    try:
        with app.app_context():
            bot = Bot.query.get_or_404(bot_id)
            
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
def stop_whatsapp_bot(bot_id):
    """WhatsApp botni to'xtatish"""
    try:
        with app.app_context():
            bot = Bot.query.get_or_404(bot_id)
            
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
def whatsapp_bot_status(bot_id):
    """WhatsApp bot holatini tekshirish"""
    try:
        is_running = bot_id in whatsapp_manager.running_bots
        
        with app.app_context():
            bot = Bot.query.get(bot_id)
            
            return jsonify({
                'bot_id': bot_id,
                'is_running': is_running,
                'is_active': bot.is_active if bot else False,
                'platform': 'WhatsApp'
            })
    
    except Exception as e:
        logger.error(f"WhatsApp status error: {str(e)}")
        return jsonify({'error': str(e)}), 500