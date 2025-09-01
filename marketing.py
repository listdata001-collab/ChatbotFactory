import os
import json
import logging
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from flask import Blueprint, request, jsonify, render_template_string
from flask_login import login_required, current_user
from app import db, app
from models import User, Bot, Payment
from utils import format_currency, format_date

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

marketing_bp = Blueprint('marketing', __name__)

class EmailService:
    """Email yuborish xizmati"""
    
    def __init__(self):
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_user = os.environ.get('SMTP_USER', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@botfactory.uz')
        
        # SendGrid API (alternative)
        self.sendgrid_api_key = os.environ.get('SENDGRID_API_KEY', '')
        self.sendgrid_url = "https://api.sendgrid.com/v3/mail/send"
    
    def send_smtp_email(self, to_email, subject, html_content, text_content=""):
        """SMTP orqali email yuborish"""
        try:
            # Email yaratish
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Text va HTML qismlar
            if text_content:
                part1 = MimeText(text_content, 'plain', 'utf-8')
                msg.attach(part1)
            
            part2 = MimeText(html_content, 'html', 'utf-8')
            msg.attach(part2)
            
            # SMTP orqali yuborish
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"SMTP email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP email error: {str(e)}")
            return False
    
    def send_sendgrid_email(self, to_email, subject, html_content, text_content=""):
        """SendGrid API orqali email yuborish"""
        try:
            headers = {
                'Authorization': f'Bearer {self.sendgrid_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'personalizations': [{
                    'to': [{'email': to_email}],
                    'subject': subject
                }],
                'from': {'email': self.from_email, 'name': 'BotFactory AI'},
                'content': [
                    {'type': 'text/plain', 'value': text_content},
                    {'type': 'text/html', 'value': html_content}
                ]
            }
            
            response = requests.post(
                self.sendgrid_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 202:
                logger.info(f"SendGrid email sent to {to_email}")
                return True
            else:
                logger.error(f"SendGrid error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid email error: {str(e)}")
            return False
    
    def send_email(self, to_email, subject, html_content, text_content=""):
        """Email yuborish (SMTP yoki SendGrid)"""
        if self.sendgrid_api_key:
            return self.send_sendgrid_email(to_email, subject, html_content, text_content)
        else:
            return self.send_smtp_email(to_email, subject, html_content, text_content)

class SMSService:
    """SMS yuborish xizmati (O'zbekiston)"""
    
    def __init__(self):
        # Uzbekistan SMS providers
        self.eskiz_email = os.environ.get('ESKIZ_EMAIL', '')
        self.eskiz_password = os.environ.get('ESKIZ_PASSWORD', '')
        self.eskiz_api_url = "https://notify.eskiz.uz/api"
        self.eskiz_token = None
        
        # PlayMobile SMS
        self.playmobile_login = os.environ.get('PLAYMOBILE_LOGIN', '')
        self.playmobile_password = os.environ.get('PLAYMOBILE_PASSWORD', '')
        self.playmobile_api_url = "https://api.playmobile.uz"
    
    def get_eskiz_token(self):
        """Eskiz SMS token olish"""
        try:
            response = requests.post(
                f"{self.eskiz_api_url}/auth/login",
                data={
                    'email': self.eskiz_email,
                    'password': self.eskiz_password
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.eskiz_token = data.get('data', {}).get('token')
                return True
            return False
            
        except Exception as e:
            logger.error(f"Eskiz token error: {str(e)}")
            return False
    
    def send_eskiz_sms(self, phone_number, message):
        """Eskiz orqali SMS yuborish"""
        try:
            if not self.eskiz_token:
                if not self.get_eskiz_token():
                    return False
            
            headers = {
                'Authorization': f'Bearer {self.eskiz_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'mobile_phone': phone_number,
                'message': message,
                'from': '4546',
                'callback_url': url_for('marketing.sms_callback', _external=True)
            }
            
            response = requests.post(
                f"{self.eskiz_api_url}/message/sms/send",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    logger.info(f"Eskiz SMS sent to {phone_number}")
                    return True
            
            logger.error(f"Eskiz SMS error: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"Eskiz SMS error: {str(e)}")
            return False
    
    def send_playmobile_sms(self, phone_number, message):
        """PlayMobile orqali SMS yuborish"""
        try:
            data = {
                'login': self.playmobile_login,
                'password': self.playmobile_password,
                'data': [{
                    'phone': phone_number,
                    'text': message
                }]
            }
            
            response = requests.post(
                f"{self.playmobile_api_url}/send",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'ok':
                    logger.info(f"PlayMobile SMS sent to {phone_number}")
                    return True
            
            logger.error(f"PlayMobile SMS error: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"PlayMobile SMS error: {str(e)}")
            return False
    
    def send_sms(self, phone_number, message):
        """SMS yuborish"""
        # Clean phone number
        phone_number = phone_number.replace('+', '').replace(' ', '').replace('-', '')
        
        # Try Eskiz first, then PlayMobile
        if self.eskiz_email:
            return self.send_eskiz_sms(phone_number, message)
        elif self.playmobile_login:
            return self.send_playmobile_sms(phone_number, message)
        else:
            logger.error("No SMS provider configured")
            return False

class MarketingCampaigns:
    """Marketing kampaniyalari"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
    
    def send_welcome_email(self, user):
        """Xush kelibsiz emaili"""
        subject = "🎉 BotFactory AI ga xush kelibsiz!"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Xush kelibsiz</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2563eb;">🤖 BotFactory AI</h1>
                <h2>Salom, {{ username }}!</h2>
                
                <p>BotFactory AI platformasiga xush kelibsiz! Siz endi o'zingizning AI chatbotlaringizni yaratishingiz mumkin.</p>
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>🎁 14 kunlik bepul sinov:</h3>
                    <ul>
                        <li>✅ 1 ta bot yaratish</li>
                        <li>✅ Telegram integratsiyasi</li>
                        <li>✅ O'zbek tilida AI javoblar</li>
                        <li>✅ Bilim bazasi yuklash</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://botfactory.uz/dashboard" 
                       style="background: #2563eb; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 8px; font-weight: bold;">
                        🚀 Birinchi botingizni yarating
                    </a>
                </div>
                
                <h3>💎 Premium imkoniyatlar:</h3>
                <ul>
                    <li>🤖 5 ta bot yaratish</li>
                    <li>🌍 3 tilda AI (O'zbek/Rus/Ingliz)</li>
                    <li>📱 Barcha platformalar (Telegram/Instagram/WhatsApp)</li>
                    <li>📞 Prioritet yordam</li>
                </ul>
                
                <p>Savollaringiz bo'lsa, <a href="mailto:support@botfactory.uz">support@botfactory.uz</a> ga yozing.</p>
                
                <hr style="margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">
                    BotFactory AI - O'zbekistondagi birinchi AI chatbot platformasi<br>
                    <a href="https://botfactory.uz">botfactory.uz</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        html_content = render_template_string(html_template, username=user.username)
        
        text_content = f"""
Salom, {user.username}!

BotFactory AI ga xush kelibsiz! Siz endi o'zingizning AI chatbotlaringizni yaratishingiz mumkin.

14 kunlik bepul sinov:
- 1 ta bot yaratish
- Telegram integratsiyasi  
- O'zbek tilida AI javoblar

Birinchi botingizni yaratish: https://botfactory.uz/dashboard

Savollar: support@botfactory.uz
        """
        
        return self.email_service.send_email(user.email, subject, html_content, text_content)
    
    def send_subscription_reminder(self, user, days_left):
        """Obuna tugashi haqida eslatma"""
        subject = f"⏰ Obunangiz {days_left} kundan keyin tugaydi"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Obuna eslatmasi</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #dc2626;">⏰ Obuna tugash eslatmasi</h1>
                
                <p>Hurmatli {{ username }},</p>
                
                <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0;">
                    <p><strong>Sizning {{ subscription_type }} obunangiz {{ days_left }} kundan keyin tugaydi!</strong></p>
                    <p>Tugash sanasi: {{ end_date }}</p>
                </div>
                
                <p>Xizmatlarimizdan uzluksiz foydalanish uchun obunangizni yangilang:</p>
                
                <div style="display: flex; gap: 15px; margin: 30px 0;">
                    <div style="flex: 1; background: #f3f4f6; padding: 20px; border-radius: 8px;">
                        <h3 style="color: #059669;">💰 Basic - 290,000 so'm/oy</h3>
                        <ul>
                            <li>1 ta bot</li>
                            <li>Barcha platformalar</li>
                            <li>3 til AI</li>
                        </ul>
                    </div>
                    <div style="flex: 1; background: #fef3c7; padding: 20px; border-radius: 8px;">
                        <h3 style="color: #d97706;">💎 Premium - 590,000 so'm/oy</h3>
                        <ul>
                            <li>5 ta bot</li>
                            <li>Barcha platformalar</li>
                            <li>3 til AI</li>
                            <li>Prioritet yordam</li>
                        </ul>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://botfactory.uz/subscription" 
                       style="background: #dc2626; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 8px; font-weight: bold;">
                        💳 Obunani yangilash
                    </a>
                </div>
                
                <p>Yordam kerakmi? <a href="mailto:support@botfactory.uz">support@botfactory.uz</a></p>
            </div>
        </body>
        </html>
        """
        
        html_content = render_template_string(
            html_template,
            username=user.username,
            subscription_type=user.subscription_type.title(),
            days_left=days_left,
            end_date=format_date(user.subscription_end_date)
        )
        
        return self.email_service.send_email(user.email, subject, html_content)
    
    def send_trial_ending_sms(self, user, days_left):
        """Sinov tugashi SMS"""
        message = f"""🤖 BotFactory AI
        
Hurmatli {user.username}, sinov muddatingiz {days_left} kundan keyin tugaydi.

Davom etish uchun: botfactory.uz

Basic: 290,000 so'm
Premium: 590,000 so'm"""
        
        # Get phone number from user
        phone = getattr(user, 'phone_number', None)
        if phone:
            return self.sms_service.send_sms(phone, message)
        return False
    
    def send_free_user_marketing(self, user):
        """Bepul foydalanuvchilarga marketing"""
        subject = "🚀 Botlaringizni yangi darajaga ko'taring!"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Premium taklif</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #7c3aed;">🚀 Yangi imkoniyatlar!</h1>
                
                <p>Salom, {{ username }}!</p>
                
                <p>Siz BotFactory AI dan yaxshi foydalanyapsiz. Ko'proq imkoniyatlar qanday?</p>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 30px; border-radius: 15px; margin: 30px 0;">
                    <h2 style="margin-top: 0;">✨ Premium bilan yangi dunyo:</h2>
                    <ul style="font-size: 16px;">
                        <li>🤖 <strong>5 ta bot</strong> yarating</li>
                        <li>🌍 <strong>3 tilda AI</strong> (O'zbek/Rus/Ingliz)</li>
                        <li>📱 <strong>Instagram va WhatsApp</strong> ham</li>
                        <li>📞 <strong>Prioritet yordam</strong></li>
                        <li>📊 <strong>Tahlil va statistika</strong></li>
                    </ul>
                </div>
                
                <div style="background: #fef9e7; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>🎁 Maxsus taklif:</h3>
                    <p>Birinchi oy uchun <strong>30% chegirma</strong>!</p>
                    <p>Premium: <strike>590,000</strike> → <strong style="color: #dc2626;">413,000 so'm</strong></p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://botfactory.uz/subscription?promo=PREMIUM30" 
                       style="background: #7c3aed; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 8px; font-weight: bold;">
                        💎 Premium olish
                    </a>
                </div>
                
                <p><small>Taklifning amal qilish muddati: {{ expiry_date }}</small></p>
            </div>
        </body>
        </html>
        """
        
        expiry_date = (datetime.utcnow() + timedelta(days=7)).strftime("%d.%m.%Y")
        html_content = render_template_string(
            html_template, 
            username=user.username,
            expiry_date=expiry_date
        )
        
        return self.email_service.send_email(user.email, subject, html_content)
    
    def send_bulk_marketing(self, user_ids, campaign_type):
        """Ommaviy marketing xabarlari"""
        success_count = 0
        total_count = len(user_ids)
        
        with app.app_context():
            users = User.query.filter(User.id.in_(user_ids)).all()
            
            for user in users:
                try:
                    if campaign_type == 'welcome':
                        success = self.send_welcome_email(user)
                    elif campaign_type == 'marketing':
                        success = self.send_free_user_marketing(user)
                    else:
                        success = False
                    
                    if success:
                        success_count += 1
                        
                except Exception as e:
                    logger.error(f"Bulk marketing error for user {user.id}: {str(e)}")
        
        return {
            'total': total_count,
            'success': success_count,
            'failed': total_count - success_count
        }

# Marketing campaigns instance
campaigns = MarketingCampaigns()

# Flask routes
@marketing_bp.route('/send/welcome/<int:user_id>', methods=['POST'])
@login_required
def send_welcome(user_id):
    """Xush kelibsiz emaili yuborish"""
    if not current_user.is_admin:
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    
    try:
        with app.app_context():
            user = User.query.get_or_404(user_id)
            success = campaigns.send_welcome_email(user)
            
            return jsonify({
                'success': success,
                'message': 'Xabar yuborildi' if success else 'Xabar yuborishda xato'
            })
    
    except Exception as e:
        logger.error(f"Send welcome error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/send/reminder/<int:user_id>/<int:days>', methods=['POST'])
@login_required  
def send_reminder(user_id, days):
    """Obuna eslatmasi yuborish"""
    if not current_user.is_admin:
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    
    try:
        with app.app_context():
            user = User.query.get_or_404(user_id)
            success = campaigns.send_subscription_reminder(user, days)
            
            return jsonify({
                'success': success,
                'message': 'Eslatma yuborildi' if success else 'Eslatma yuborishda xato'
            })
    
    except Exception as e:
        logger.error(f"Send reminder error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/send/bulk', methods=['POST'])
@login_required
def send_bulk():
    """Ommaviy xabar yuborish"""
    if not current_user.is_admin:
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    
    try:
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        campaign_type = data.get('campaign_type', 'marketing')
        
        result = campaigns.send_bulk_marketing(user_ids, campaign_type)
        
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Bulk marketing error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/sms/callback', methods=['POST'])
def sms_callback():
    """SMS yuborish callback"""
    try:
        data = request.get_json()
        logger.info(f"SMS callback: {data}")
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        logger.error(f"SMS callback error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@marketing_bp.route('/stats')
@login_required
def marketing_stats():
    """Marketing statistikalari"""
    if not current_user.is_admin:
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    
    try:
        with app.app_context():
            stats = {
                'total_users': User.query.count(),
                'free_users': User.query.filter_by(subscription_type='free').count(),
                'trial_ending_soon': User.query.filter(
                    User.subscription_type == 'free',
                    User.subscription_end_date <= datetime.utcnow() + timedelta(days=3),
                    User.subscription_end_date > datetime.utcnow()
                ).count(),
                'expired_subscriptions': User.query.filter(
                    User.subscription_end_date <= datetime.utcnow(),
                    User.subscription_type.in_(['basic', 'premium'])
                ).count()
            }
            
            return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Marketing stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500