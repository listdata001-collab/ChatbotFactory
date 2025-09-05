import os
import requests
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramNotificationService:
    """Telegram orqali real-time bildirishnomalar yuborish xizmati"""
    
    def __init__(self, bot_token=None):
        # Bot tokenini parameter orqali yoki environment variable dan olish
        self.bot_token = bot_token or os.environ.get('TELEGRAM_BOT_TOKEN')
        if self.bot_token:
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        else:
            logger.warning("Bot token not provided for notifications")
    
    def send_chat_notification(self, admin_chat_id: str, channel_id: str, 
                             bot_name: str, user_id: str, user_message: str, 
                             bot_response: str, platform: str = "Telegram", username: str = "") -> bool:
        """
        Yangi yozishma haqida bildirishnoma yuborish
        """
        if not self.bot_token:
            return False
            
        # Xabar formatini tayyorlash
        notification_text = self._format_chat_notification(
            bot_name, user_id, user_message, bot_response, platform, username
        )
        
        success = True
        
        # Admin chat ID ga yuborish
        if admin_chat_id and admin_chat_id.strip():
            if not self._send_message(admin_chat_id, notification_text):
                success = False
        
        # Kanal ID ga yuborish (agar mavjud bo'lsa)
        if channel_id and channel_id.strip():
            if not self._send_message(channel_id, notification_text):
                success = False
                
        return success
    
    def _format_chat_notification(self, bot_name: str, user_id: str, 
                                 user_message: str, bot_response: str, 
                                 platform: str, username: str = "") -> str:
        """Bildirishnoma matnini formatlash"""
        
        # Platform ikonkasi
        platform_icon = {
            'Telegram': '📱',
            'Instagram': '📷', 
            'WhatsApp': '💬'
        }.get(platform, '🤖')
        
        # Vaqt
        current_time = datetime.now().strftime('%H:%M')
        
        # Xabar va javobni qisqartirish
        short_message = user_message[:100] + "..." if len(user_message) > 100 else user_message
        short_response = bot_response[:150] + "..." if len(bot_response) > 150 else bot_response
        
        # Mijoz ma'lumotini formatlash
        customer_info = f"{user_id}"
        if username and username.strip():
            customer_info = f"@{username} ({user_id})"
        
        notification = f"""🔔 Yangi suhbat!

{platform_icon} Bot: {bot_name}
👤 Mijoz: {customer_info}
⏰ Vaqt: {current_time}

📩 Mijoz xabari:
{short_message}

🤖 Bot javobi:
{short_response}

━━━━━━━━━━━━━━━━━━━
Chatbot Factory AI - Suhbat Kuzatuvi
        """.strip()
        
        return notification
    
    def _send_message(self, chat_id: str, text: str) -> bool:
        """Telegram orqali xabar yuborish"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if response.status_code == 200 and result.get('ok'):
                logger.info(f"Notification sent successfully to {chat_id}")
                return True
            else:
                error_desc = result.get('description', 'Unknown error')
                if 'chat not found' in error_desc.lower():
                    logger.error(f"Chat/Channel not found for {chat_id}. Bot must be added as administrator to the channel!")
                elif 'bot is not a member' in error_desc.lower():
                    logger.error(f"Bot is not a member of {chat_id}. Add bot as administrator first!")
                else:
                    logger.error(f"Failed to send notification to {chat_id}: {error_desc}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification to {chat_id}: {str(e)}")
            return False
    
    def send_subscription_reminder(self, admin_chat_id: str, user_info: dict, days_left: int) -> bool:
        """Obuna tugashi haqida Telegram orqali eslatma yuborish"""
        if not self.bot_token:
            return False
            
        # Obuna turi nomlarini formatlash
        subscription_names = {
            'free': 'Bepul (Test)',
            'starter': 'Starter',
            'basic': 'Basic',
            'premium': 'Premium',
            'admin': 'Admin'
        }
        
        subscription_name = subscription_names.get(user_info.get('subscription_type', 'free'), 'Noma\'lum')
        username = user_info.get('username', 'Noma\'lum')
        end_date = user_info.get('subscription_end_date', 'Noma\'lum')
        
        # Xabar matni
        if days_left <= 1:
            urgency_icon = "🚨"
            urgency_text = "SHOSHILINCH!"
        elif days_left <= 3:
            urgency_icon = "⚠️"
            urgency_text = "MUHIM ESLATMA"
        else:
            urgency_icon = "⏰"
            urgency_text = "Eslatma"
        
        notification_text = f"""{urgency_icon} {urgency_text}

📋 Obuna tugash eslatmasi
━━━━━━━━━━━━━━━━━━━

👤 Foydalanuvchi: {username}
💼 Obuna turi: {subscription_name}
📅 Tugash sanasi: {end_date}
⏳ Qolgan kunlar: {days_left} kun

{"🔴 Obunangiz bugun tugaydi!" if days_left <= 1 else f"📢 Obunangiz {days_left} kundan keyin tugaydi!"}

💡 Xizmatlardan uzluksiz foydalanish uchun obunani yangilang:
• Starter: 165,000 so'm/oy
• Basic: 290,000 so'm/oy
• Premium: 590,000 so'm/oy

🔗 Yangilash: https://botfactory.uz/subscription

━━━━━━━━━━━━━━━━━━━
Chatbot Factory AI - Obuna boshqaruvi"""
        
        return self._send_message(admin_chat_id, notification_text)
    
    def send_payment_success_notification(self, admin_chat_id: str, payment_info: dict) -> bool:
        """To'lov muvaffaqiyatli amalga oshirilgani haqida bildirishnoma"""
        if not self.bot_token:
            return False
            
        username = payment_info.get('username', 'Noma\'lum')
        amount = payment_info.get('amount', 0)
        method = payment_info.get('method', 'Noma\'lum')
        subscription_type = payment_info.get('subscription_type', 'basic')
        
        subscription_names = {
            'starter': 'Starter',
            'basic': 'Basic',
            'premium': 'Premium'
        }
        
        subscription_name = subscription_names.get(subscription_type, subscription_type)
        
        notification_text = f"""✅ YANGI TO'LOV!

💰 To'lov muvaffaqiyatli qabul qilindi
━━━━━━━━━━━━━━━━━━━

👤 Foydalanuvchi: {username}
💳 Summa: {amount:,.0f} so'm
🏦 Usul: {method.upper()}
📦 Obuna: {subscription_name}
📅 Vaqt: {datetime.now().strftime('%d.%m.%Y %H:%M')}

🎉 Foydalanuvchi 30 kunlik obunaga ega bo'ldi!

━━━━━━━━━━━━━━━━━━━
Chatbot Factory AI - To'lovlar"""
        
        return self._send_message(admin_chat_id, notification_text)
    
    def send_subscription_expired_notification(self, admin_chat_id: str, user_info: dict) -> bool:
        """Obuna tugagani haqida bildirishnoma"""
        if not self.bot_token:
            return False
            
        username = user_info.get('username', 'Noma\'lum')
        old_subscription = user_info.get('old_subscription_type', 'basic')
        
        notification_text = f"""❌ OBUNA TUGADI

📋 Foydalanuvchi obunasi tugadi
━━━━━━━━━━━━━━━━━━━

👤 Foydalanuvchi: {username}
📦 Eski obuna: {old_subscription.upper()}
🔄 Yangi holat: BEPUL
📅 Tugash vaqti: {datetime.now().strftime('%d.%m.%Y %H:%M')}

⚠️ Telegram bo'lmagan botlar deaktivatsiya qilindi!

━━━━━━━━━━━━━━━━━━━
Chatbot Factory AI - Obuna boshqaruvi"""
        
        return self._send_message(admin_chat_id, notification_text)

    def test_notification(self, chat_id: str) -> bool:
        """Test notification yuborish"""
        test_message = """
🧪 Test Bildirishnoma

Bu test xabaridir. Agar bu xabarni olgan bo'lsangiz, bildirishnomalar tizimi to'g'ri ishlayapti! ✅

Chatbot Factory AI Platform
        """.strip()
        
        return self._send_message(chat_id, test_message)

# Global service instance (fallback uchun)
notification_service = TelegramNotificationService()