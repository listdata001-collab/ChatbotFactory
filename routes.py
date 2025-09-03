from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import User, Bot, KnowledgeBase, Payment, ChatHistory, BroadcastMessage
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import docx

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    bots = Bot.query.filter_by(user_id=current_user.id).all()
    bot_count = len(bots)
    
    # Get subscription info
    subscription_info = {
        'type': current_user.subscription_type,
        'end_date': current_user.subscription_end_date,
        'active': current_user.subscription_active(),
        'can_create': current_user.can_create_bot()
    }
    
    return render_template('dashboard.html', bots=bots, bot_count=bot_count, 
                         subscription_info=subscription_info)

@main_bp.route('/admin')
@main_bp.route('/admin/')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Sizda admin huquqi yo\'q!', 'error')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    payments = Payment.query.order_by(Payment.created_at.desc()).limit(50).all()
    bots = Bot.query.all()
    
    # Statistics
    stats = {
        'total_users': User.query.count(),
        'active_subscriptions': User.query.filter(User.subscription_type.in_(['starter', 'basic', 'premium'])).count(),
        'total_bots': Bot.query.count(),
        'total_payments': Payment.query.filter_by(status='completed').count(),
        'monthly_revenue': Payment.query.filter(
            Payment.status == 'completed',
            Payment.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
    }
    
    # Get broadcast messages
    broadcasts = BroadcastMessage.query.order_by(BroadcastMessage.created_at.desc()).limit(10).all()
    
    return render_template('admin.html', users=users, payments=payments, 
                         bots=bots, stats=stats, broadcasts=broadcasts)

@main_bp.route('/admin/broadcast', methods=['POST'])
@login_required
def send_broadcast():
    if not current_user.is_admin:
        flash('Sizda admin huquqi yo\'q!', 'error')
        return redirect(url_for('main.dashboard'))
    
    message_text = request.form.get('message_text')
    target_type = request.form.get('target_type', 'all')
    
    if not message_text:
        flash('Xabar matni kiritilishi shart!', 'error')
        return redirect(url_for('main.admin'))
    
    # Create broadcast message record
    broadcast = BroadcastMessage()
    broadcast.admin_id = current_user.id
    broadcast.message_text = message_text
    broadcast.target_type = target_type
    broadcast.status = 'sending'
    broadcast.sent_at = datetime.utcnow()
    
    db.session.add(broadcast)
    db.session.commit()
    
    # Send messages
    try:
        sent_count = send_broadcast_messages(broadcast.id, message_text, target_type)
        
        # Update broadcast record
        broadcast.sent_count = sent_count
        broadcast.status = 'completed'
        db.session.commit()
        
        flash(f'Xabar muvaffaqiyatli yuborildi! {sent_count} ta foydalanuvchiga yetkazildi.', 'success')
    except Exception as e:
        broadcast.status = 'failed'
        db.session.commit()
        flash('Xabar yuborishda xatolik yuz berdi!', 'error')
    
    return redirect(url_for('main.admin'))

@main_bp.route('/admin/change-subscription', methods=['POST'])
@login_required
def change_user_subscription():
    if not current_user.is_admin:
        flash('Sizda admin huquqi yo\'q!', 'error')
        return redirect(url_for('main.dashboard'))
    
    user_id = request.form.get('user_id')
    subscription_type = request.form.get('subscription_type')
    subscription_duration = request.form.get('subscription_duration', '30')  # Default 30 days
    
    if not user_id or not subscription_type:
        flash('Xatolik: Ma\'lumotlar to\'liq emas!', 'error')
        return redirect(url_for('main.admin'))
    
    user = User.query.get_or_404(user_id)
    
    # Don't allow changing admin subscription or setting subscription to free
    if user.subscription_type == 'admin' or subscription_type == 'free':
        flash('Xatolik: Admin obunasini yoki bepul ta\'rifni o\'zgartirib bo\'lmaydi!', 'error')
        return redirect(url_for('main.admin'))
    
    # Set new subscription
    user.subscription_type = subscription_type
    
    # Calculate end date based on duration
    if subscription_type in ['basic', 'premium']:
        days = int(subscription_duration)
        user.subscription_end_date = datetime.utcnow() + timedelta(days=days)
    
    try:
        db.session.commit()
        
        # Create payment record for manual subscription change
        payment = Payment()
        payment.user_id = user.id
        payment.amount = 0  # Manual change by admin
        payment.method = 'Admin'
        payment.status = 'completed'
        payment.subscription_type = subscription_type
        payment.transaction_id = f'ADMIN_{current_user.id}_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
        
        db.session.add(payment)
        db.session.commit()
        
        subscription_names = {
            'basic': 'Basic',
            'premium': 'Premium'
        }
        
        flash(f'{user.username} foydalanuvchisining obunasi {subscription_names.get(subscription_type, subscription_type)} ga o\'zgartirildi ({subscription_duration} kun)', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Obunani o\'zgartirishda xatolik yuz berdi!', 'error')
    
    return redirect(url_for('main.admin'))

def send_broadcast_messages(broadcast_id, message_text, target_type):
    """Send broadcast message to users"""
    sent_count = 0
    
    if target_type == 'customers':
        # Send to paying customers only
        users = User.query.filter(User.subscription_type.in_(['starter', 'basic', 'premium'])).all()
    else:
        # Send to all telegram users who have interacted with bots
        users = User.query.filter(User.telegram_id.isnot(None)).all()
    
    # Import telegram bot for sending messages
    try:
        from telegram_bot import send_admin_message_to_user
        
        for user in users:
            if user.telegram_id:
                try:
                    success = send_admin_message_to_user(user.telegram_id, message_text)
                    if success:
                        sent_count += 1
                except:
                    continue
                        
    except Exception as e:
        pass
    
    return sent_count

@main_bp.route('/bot/create', methods=['GET', 'POST'])
@login_required
def create_bot():
    if not current_user.can_create_bot():
        flash('Siz maksimal bot soni yaratdingiz!', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        platform = request.form.get('platform', 'Telegram')
        telegram_token = request.form.get('telegram_token')
        instagram_token = request.form.get('instagram_token')
        whatsapp_token = request.form.get('whatsapp_token')
        whatsapp_phone_id = request.form.get('whatsapp_phone_id')
        
        if not name:
            flash('Bot nomi kiritilishi shart!', 'error')
            return render_template('bot_create.html')
        
        bot = Bot()
        bot.user_id = current_user.id
        bot.name = name
        bot.platform = platform
        bot.telegram_token = telegram_token
        bot.instagram_token = instagram_token
        bot.whatsapp_token = whatsapp_token
        bot.whatsapp_phone_id = whatsapp_phone_id
        
        db.session.add(bot)
        db.session.commit()
        
        # Platform uchun avtomatik ishga tushirish
        if platform == 'Telegram' and telegram_token:
            try:
                from telegram_bot import start_bot_automatically
                success = start_bot_automatically(bot.id, telegram_token)
                if success:
                    bot.is_active = True
                    db.session.commit()
                    flash('Telegram bot muvaffaqiyatli yaratildi va ishga tushirildi!', 'success')
                else:
                    flash('Bot yaratildi, lekin token noto\'g\'ri yoki ishga tushirishda muammo!', 'warning')
            except Exception as e:
                flash(f'Bot yaratildi, lekin aktivlashtirish xatoligi: {str(e)}', 'warning')
        elif platform == 'Instagram' and instagram_token:
            try:
                from instagram_bot import start_instagram_bot_automatically
                success = start_instagram_bot_automatically(bot.id, instagram_token)
                if success:
                    bot.is_active = True
                    db.session.commit()
                    flash('Instagram bot muvaffaqiyatli yaratildi va ishga tushirildi!', 'success')
                else:
                    flash('Bot yaratildi, lekin token noto\'g\'ri yoki ishga tushirishda muammo!', 'warning')
            except Exception as e:
                flash(f'Bot yaratildi, lekin aktivlashtirish xatoligi: {str(e)}', 'warning')
        elif platform == 'WhatsApp' and whatsapp_token and whatsapp_phone_id:
            try:
                from whatsapp_bot import start_whatsapp_bot_automatically
                success = start_whatsapp_bot_automatically(bot.id, whatsapp_token, whatsapp_phone_id)
                if success:
                    bot.is_active = True
                    db.session.commit()
                    flash('WhatsApp bot muvaffaqiyatli yaratildi va ishga tushirildi!', 'success')
                else:
                    flash('Bot yaratildi, lekin token noto\'g\'ri yoki ishga tushirishda muammo!', 'warning')
            except Exception as e:
                flash(f'Bot yaratildi, lekin aktivlashtirish xatoligi: {str(e)}', 'warning')
        else:
            flash('Bot muvaffaqiyatli yaratildi!', 'success')
        
        return redirect(url_for('main.dashboard'))
    
    return render_template('bot_create.html')

@main_bp.route('/bot/<int:bot_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bot(bot_id):
    bot = Bot.query.get_or_404(bot_id)
    
    if bot.user_id != current_user.id and not current_user.is_admin:
        flash('Sizda bu botni tahrirlash huquqi yo\'q!', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        bot.name = request.form.get('name', bot.name)
        bot.platform = request.form.get('platform', bot.platform)
        bot.telegram_token = request.form.get('telegram_token', bot.telegram_token)
        
        # Agar Telegram bot token o'zgargan bo'lsa, qayta ishga tushirish
        if bot.platform == 'Telegram' and bot.telegram_token:
            try:
                from telegram_bot import start_bot_automatically
                success = start_bot_automatically(bot.id, bot.telegram_token)
                if success:
                    bot.is_active = True
                else:
                    bot.is_active = False
                    flash('Bot ma\'lumotlari yangilandi, lekin token noto\'g\'ri!', 'warning')
            except Exception as e:
                flash(f'Bot yangilandi, lekin qayta ishga tushirishda xatolik: {str(e)}', 'warning')
        
        db.session.commit()
        flash('Bot ma\'lumotlari yangilandi!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('bot_edit.html', bot=bot)

@main_bp.route('/bot/<int:bot_id>/start', methods=['POST'])
@login_required
def start_bot(bot_id):
    """Botni qo'lbola ishga tushirish"""
    bot = Bot.query.get_or_404(bot_id)
    
    if bot.user_id != current_user.id and not current_user.is_admin:
        flash('Sizda bu botni ishga tushirish huquqi yo\'q!', 'error')
        return redirect(url_for('main.dashboard'))
    
    if bot.platform == 'Telegram' and bot.telegram_token:
        try:
            from telegram_bot import start_bot_automatically
            success = start_bot_automatically(bot.id, bot.telegram_token)
            if success:
                bot.is_active = True
                db.session.commit()
                flash('Bot muvaffaqiyatli ishga tushirildi!', 'success')
            else:
                flash('Bot ishga tushirishda muammo yuz berdi!', 'error')
        except Exception as e:
            flash(f'Xatolik: {str(e)}', 'error')
    else:
        flash('Bot tokenini tekshiring!', 'error')
    
    return redirect(url_for('main.dashboard'))

@main_bp.route('/bot/<int:bot_id>/stop', methods=['POST'])
@login_required
def stop_bot(bot_id):
    """Botni to'xtatish"""
    bot = Bot.query.get_or_404(bot_id)
    
    if bot.user_id != current_user.id and not current_user.is_admin:
        flash('Sizda bu botni to\'xtatish huquqi yo\'q!', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        from telegram_bot import bot_manager
        success = bot_manager.stop_bot(bot.id)
        if success:
            bot.is_active = False
            db.session.commit()
            flash('Bot to\'xtatildi!', 'success')
        else:
            flash('Bot to\'xtatishda muammo yuz berdi!', 'error')
    except Exception as e:
        flash(f'Xatolik: {str(e)}', 'error')
    
    return redirect(url_for('main.dashboard'))

@main_bp.route('/bot/<int:bot_id>/knowledge', methods=['POST'])
@login_required
def upload_knowledge(bot_id):
    bot = Bot.query.get_or_404(bot_id)
    
    if bot.user_id != current_user.id and not current_user.is_admin:
        flash('Sizda bu botga ma\'lumot yuklash huquqi yo\'q!', 'error')
        return redirect(url_for('main.dashboard'))
    
    if 'file' not in request.files:
        flash('Fayl tanlanmagan!', 'error')
        return redirect(url_for('main.edit_bot', bot_id=bot_id))
    
    file = request.files['file']
    if file.filename == '':
        flash('Fayl tanlanmagan!', 'error')
        return redirect(url_for('main.edit_bot', bot_id=bot_id))
    
    if file:
        filename = secure_filename(file.filename or 'unknown')
        content = ""
        content_type = "file"
        
        try:
            # Check if it's an image file
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                # Save image to static folder
                import uuid
                from datetime import datetime
                
                # Generate unique filename
                file_extension = filename.split('.')[-1].lower()
                unique_filename = f"kb_{bot_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
                file_path = os.path.join('static', 'uploads', unique_filename)
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Save the file
                file.save(file_path)
                
                # Store the URL path for the AI to use
                content = f"/static/uploads/{unique_filename}"
                content_type = "image"
                
            elif filename.endswith('.txt'):
                # Handle different encodings for text files
                try:
                    content = file.read().decode('utf-8')
                except UnicodeDecodeError:
                    # Try with different encoding if UTF-8 fails
                    file.seek(0)
                    try:
                        content = file.read().decode('cp1251')  # Windows Cyrillic
                    except UnicodeDecodeError:
                        file.seek(0)
                        content = file.read().decode('latin-1', errors='ignore')
                
                # Clean problematic Unicode characters
                unicode_replacements = {
                    '\u2019': "'",  # Right single quotation mark
                    '\u2018': "'",  # Left single quotation mark
                    '\u201c': '"',  # Left double quotation mark
                    '\u201d': '"',  # Right double quotation mark
                    '\u2013': '-',  # En dash
                    '\u2014': '-',  # Em dash
                    '\u2026': '...',  # Horizontal ellipsis
                    '\u00a0': ' ',  # Non-breaking space
                    '\u2010': '-',  # Hyphen
                    '\u2011': '-',  # Non-breaking hyphen
                    '\u2012': '-',  # Figure dash
                    '\u2015': '-',  # Horizontal bar
                }
                
                for unicode_char, replacement in unicode_replacements.items():
                    content = content.replace(unicode_char, replacement)
                    
                content_type = "file"
                
            elif filename.endswith('.docx'):
                doc = docx.Document(file.stream)
                paragraphs = []
                for paragraph in doc.paragraphs:
                    # Clean Unicode characters from each paragraph
                    text = paragraph.text
                    unicode_replacements = {
                        '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
                        '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u00a0': ' ',
                        '\u2010': '-', '\u2011': '-', '\u2012': '-', '\u2015': '-'
                    }
                    
                    for unicode_char, replacement in unicode_replacements.items():
                        text = text.replace(unicode_char, replacement)
                    paragraphs.append(text)
                content = '\n'.join(paragraphs)
            else:
                flash('Faqat .txt, .docx, .jpg, .png, .gif formatdagi fayllar qo\'llab-quvvatlanadi!', 'error')
                return redirect(url_for('main.edit_bot', bot_id=bot_id))
            
            knowledge = KnowledgeBase()
            knowledge.bot_id = bot_id
            knowledge.content = content
            knowledge.filename = filename
            knowledge.content_type = content_type
            
            db.session.add(knowledge)
            db.session.commit()
            
            flash('Bilim bazasi muvaffaqiyatli yuklandi!', 'success')
        except Exception as e:
            # Safe error message handling to prevent encoding issues
            error_msg = 'Fayl yuklashda xatolik yuz berdi.'
            try:
                # Safely convert error to string, handling Unicode characters
                error_details = str(e)
                unicode_replacements = {
                    '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
                    '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u00a0': ' ',
                    '\u2010': '-', '\u2011': '-', '\u2012': '-', '\u2015': '-'
                }
                
                for unicode_char, replacement in unicode_replacements.items():
                    error_details = error_details.replace(unicode_char, replacement)
                
                # Remove any remaining problematic Unicode characters
                error_details = error_details.encode('ascii', errors='ignore').decode('ascii')
                if error_details.strip():
                    error_msg = f'Fayl yuklashda xatolik: {error_details}'
            except:
                pass
            flash(error_msg, 'error')
    
    return redirect(url_for('main.edit_bot', bot_id=bot_id))

@main_bp.route('/bot/<int:bot_id>/knowledge/text', methods=['POST'])
@login_required
def add_text_knowledge(bot_id):
    bot = Bot.query.get_or_404(bot_id)
    
    if bot.user_id != current_user.id and not current_user.is_admin:
        flash('Sizda bu botga ma\'lumot qo\'shish huquqi yo\'q!', 'error')
        return redirect(url_for('main.dashboard'))
    
    content = request.form.get('content', '').strip()
    source_name = request.form.get('source_name', '').strip()
    
    if not content:
        flash('Matn maydoni bo\'sh bo\'lishi mumkin emas!', 'error')
        return redirect(url_for('main.edit_bot', bot_id=bot_id))
    
    if not source_name:
        source_name = f'Matn kirish - {datetime.utcnow().strftime("%d.%m.%Y %H:%M")}'
    
    try:
        # Clean problematic Unicode characters from user input
        unicode_replacements = {
            '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
            '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u00a0': ' ',
            '\u2010': '-', '\u2011': '-', '\u2012': '-', '\u2015': '-'
        }
        
        for unicode_char, replacement in unicode_replacements.items():
            content = content.replace(unicode_char, replacement)
            source_name = source_name.replace(unicode_char, replacement)
        
        knowledge = KnowledgeBase()
        knowledge.bot_id = bot_id
        knowledge.content = content
        knowledge.content_type = 'text'
        knowledge.source_name = source_name
        
        db.session.add(knowledge)
        db.session.commit()
        
        flash('Matn muvaffaqiyatli qo\'shildi!', 'success')
    except Exception as e:
        error_msg = 'Matn qo\'shishda xatolik yuz berdi.'
        try:
            error_details = str(e)
            unicode_replacements = {
                '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
                '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u00a0': ' ',
                '\u2010': '-', '\u2011': '-', '\u2012': '-', '\u2015': '-'
            }
            
            for unicode_char, replacement in unicode_replacements.items():
                error_details = error_details.replace(unicode_char, replacement)
            
            error_details = error_details.encode('ascii', errors='ignore').decode('ascii')
            if error_details.strip():
                error_msg = f'Matn qo\'shishda xatolik: {error_details}'
        except:
            pass
        flash(error_msg, 'error')
    
    return redirect(url_for('main.edit_bot', bot_id=bot_id))

@main_bp.route('/bot/<int:bot_id>/knowledge/image', methods=['POST'])
@login_required
def add_image_knowledge(bot_id):
    bot = Bot.query.get_or_404(bot_id)
    
    if bot.user_id != current_user.id and not current_user.is_admin:
        flash('Sizda bu botga rasm qo\'shish huquqi yo\'q!', 'error')
        return redirect(url_for('main.dashboard'))
    
    image_url = request.form.get('image_url', '').strip()
    source_name = request.form.get('source_name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not image_url:
        flash('Rasm havolasi bo\'sh bo\'lishi mumkin emas!', 'error')
        return redirect(url_for('main.edit_bot', bot_id=bot_id))
    
    # Basic URL validation
    if not (image_url.startswith('http://') or image_url.startswith('https://')):
        flash('Yaroqli rasm havolasi kiriting (http:// yoki https:// bilan boshlanishi kerak)!', 'error')
        return redirect(url_for('main.edit_bot', bot_id=bot_id))
    
    if not source_name:
        source_name = f'Rasm havolasi - {datetime.utcnow().strftime("%d.%m.%Y %H:%M")}'
    
    # Combine image URL and description for content
    content = f"Rasm havolasi: {image_url}"
    if description:
        content += f"\nTavsif: {description}"
    
    try:
        knowledge = KnowledgeBase()
        knowledge.bot_id = bot_id
        knowledge.content = content
        knowledge.content_type = 'image_link'
        knowledge.source_name = source_name
        
        db.session.add(knowledge)
        db.session.commit()
        
        flash('Rasm havolasi muvaffaqiyatli qo\'shildi!', 'success')
    except Exception as e:
        flash('Rasm havolasini qo\'shishda xatolik yuz berdi.', 'error')
    
    return redirect(url_for('main.edit_bot', bot_id=bot_id))

@main_bp.route('/subscription')
@login_required
def subscription():
    return render_template('subscription.html')

@main_bp.route('/payment/<subscription_type>', methods=['POST'])
@login_required
def process_payment(subscription_type):
    method = request.form.get('method')
    
    amounts = {
        'starter': 165000,
        'basic': 290000,
        'premium': 590000
    }
    
    if subscription_type not in amounts:
        flash('Noto\'g\'ri tarif turi!', 'error')
        return redirect(url_for('main.subscription'))
    
    payment = Payment()
    payment.user_id = current_user.id
    payment.amount = amounts[subscription_type]
    payment.method = method
    payment.subscription_type = subscription_type
    payment.status = 'pending'
    
    db.session.add(payment)
    db.session.commit()
    
    # Here you would integrate with actual payment providers
    # For now, we'll simulate successful payment
    payment.status = 'completed'
    payment.transaction_id = f'TXN_{payment.id}_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
    
    # Update user subscription
    current_user.subscription_type = subscription_type
    if subscription_type == 'starter':
        current_user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
    elif subscription_type == 'basic':
        current_user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
    elif subscription_type == 'premium':
        current_user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
    
    db.session.commit()
    
    flash('To\'lov muvaffaqiyatli amalga oshirildi!', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/api/dashboard/refresh')
@login_required
def dashboard_api():
    """API endpoint for dashboard data refresh"""
    bots = Bot.query.filter_by(user_id=current_user.id).all()
    active_bots = sum(1 for bot in bots if bot.is_active)
    
    return jsonify({
        'bot_count': len(bots),
        'active_bots': active_bots,
        'subscription_type': current_user.subscription_type,
        'subscription_active': current_user.subscription_active()
    })

@main_bp.route('/bot/<int:bot_id>/delete', methods=['POST'])
@login_required
def delete_bot(bot_id):
    bot = Bot.query.get_or_404(bot_id)
    
    if bot.user_id != current_user.id and not current_user.is_admin:
        flash('Sizda bu botni o\'chirish huquqi yo\'q!', 'error')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(bot)
    db.session.commit()
    
    flash('Bot muvaffaqiyatli o\'chirildi!', 'success')
    return redirect(url_for('main.dashboard'))
