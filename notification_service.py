import os
import requests
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramNotificationService:
    """Telegram orqali real-time bildirishnomalar yuborish xizmati"""
    
    def __init__(self):
        # Asosiy bot tokenini olish (bildirishnoma uchun)
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if self.bot_token:
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        else:
            logger.warning("TELEGRAM_BOT_TOKEN not configured for notifications")
    
    def send_chat_notification(self, admin_chat_id: str, channel_id: str, 
                             bot_name: str, user_id: str, user_message: str, 
                             bot_response: str, platform: str = "Telegram") -> bool:
        """
        Yangi yozishma haqida bildirishnoma yuborish
        """
        if not self.bot_token:
            return False
            
        # Xabar formatini tayyorlash
        notification_text = self._format_chat_notification(
            bot_name, user_id, user_message, bot_response, platform
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
                                 platform: str) -> str:
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
        
        notification = f"""🔔 **Yangi suhbat!**

{platform_icon} **Bot:** {bot_name}
👤 **Mijoz:** {user_id} 
⏰ **Vaqt:** {current_time}

📩 **Mijoz xabari:**
{short_message}

🤖 **Bot javobi:**
{short_response}

━━━━━━━━━━━━━━━━━━━
_BotFactory AI - Suhbat Kuzatuvi_
        """.strip()
        
        return notification
    
    def _send_message(self, chat_id: str, text: str) -> bool:
        """Telegram orqali xabar yuborish"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'Markdown',
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
    
    def test_notification(self, chat_id: str) -> bool:
        """Test notification yuborish"""
        test_message = """
🧪 **Test Bildirishnoma**

Bu test xabaridir. Agar bu xabarni olgan bo'lsangiz, bildirishnomalar tizimi to'g'ri ishlayapti! ✅

_BotFactory AI Platform_
        """.strip()
        
        return self._send_message(chat_id, test_message)

# Global service instance
notification_service = TelegramNotificationService()