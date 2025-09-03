import os
import logging
from typing import Optional

try:
    import google.generativeai as genai
    # Initialize Gemini client
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", "default_key"))
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI library not available. Install with: pip install google-generativeai")

def get_ai_response(message: str, bot_name: str = "BotFactory AI", user_language: str = "uz", knowledge_base: str = "", chat_history: str = "") -> Optional[str]:
    """
    Generate AI response using Google Gemini with chat history context
    """
    try:
        # Language-specific system prompts
        language_prompts = {
            'uz': f"Sen {bot_name} nomli chatbot san. Har doim o'zbek tilida javob ber. Dostona, foydali va emotsiyalik bo'ling. Emoji ishlating. HECH QACHON ** yoki * yoki ` kabi markdown belgilarini ishlatma! Faqat oddiy matn, emoji va qator ajratish. Mahsulot ro'yxatini chiroyli formatda yoz: • yoki - bilan boshlash, har bir mahsulotni alohida qatorda yoz. Foydalanuvchi bilan oldingi suhbatlarni eslab qoling.",
            'ru': f"Ты чатбот по имени {bot_name}. Всегда отвечай на русском языке. Будь дружелюбным, полезным и эмоциональным. Используй эмодзи. НИКОГДА не используй ** или * или ` и другие markdown символы! Только простой текст, эмодзи и переносы строк. Список товаров пиши в красивом формате: начинай с • или -, каждый товар на отдельной строке. Помни предыдущие разговоры с пользователем.",
            'en': f"You are a chatbot named {bot_name}. Always respond in English. Be friendly, helpful and emotional. Use emojis. NEVER use ** or * or ` or any markdown symbols! Only plain text, emojis and line breaks. Format product lists nicely: start with • or -, each product on separate line. Remember previous conversations with the user."
        }
        
        system_prompt = language_prompts.get(user_language, language_prompts['uz'])
        
        # Add knowledge base context if available
        if knowledge_base:
            # Increase knowledge base limit for better product information
            kb_limit = 5000  # Increased from 3000 to include more products
            limited_kb = knowledge_base[:kb_limit]
            system_prompt += f"\n\nSizda quyidagi bilim bazasi mavjud:\n{limited_kb}\n\nAgar foydalanuvchi yuqoridagi ma'lumotlar haqida so'rasa, aniq va to'liq javob bering. Mahsulot narxlari va ma'lumotlarini aniq aytib bering."
            
            # Debug: log knowledge base uzunligi
            logging.info(f"DEBUG: Knowledge base length: {len(knowledge_base)}, Limited to: {len(limited_kb)}")
        
        # Add chat history context if available
        if chat_history:
            system_prompt += f"\n\nOldingi suhbatlar:\n{chat_history}\n\nYuqoridagi suhbatlarni eslab qoling va kontekst asosida javob bering."
        
        # Create the prompt
        full_prompt = f"{system_prompt}\n\nFoydalanuvchi savoli: {message}"
        
        # Generate response using Gemini
        if not GEMINI_AVAILABLE:
            return get_fallback_response(user_language)
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_prompt)
        
        if response.text:
            # Return response as-is, let Telegram handler deal with encoding
            return response.text
        else:
            return get_fallback_response(user_language)
            
    except Exception as e:
        # Safe error logging to prevent encoding issues  
        try:
            error_msg = str(e)
            unicode_replacements = {
                '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
                '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u00a0': ' ',
                '\u2010': '-', '\u2011': '-', '\u2012': '-', '\u2015': '-'
            }
            
            for unicode_char, replacement in unicode_replacements.items():
                error_msg = error_msg.replace(unicode_char, replacement)
            
            error_msg = error_msg.encode('ascii', errors='ignore').decode('ascii')
            logging.error(f"AI response error: {error_msg}")
        except:
            logging.error("AI response error: Unicode encoding issue")
        return get_fallback_response(user_language)

def get_fallback_response(language: str = "uz") -> str:
    """
    Fallback responses when AI fails
    """
    fallback_responses = {
        'uz': "Salom! Men BotFactory AI botiman. Hozir AI xizmat sozlanmoqda. Tez orada sizga yordam bera olaman! 🤖 Savollaringizni yuboring, men eslab qolaman.",
        'ru': "Привет! Я BotFactory AI бот. Сейчас настраивается AI сервис. Скоро смогу помочь вам! 🤖 Присылайте вопросы, я их запомню.",
        'en': "Hello! I'm BotFactory AI bot. AI service is being configured now. I'll be able to help you soon! 🤖 Send your questions, I'll remember them."
    }
    return fallback_responses.get(language, fallback_responses['uz'])

def process_knowledge_base(bot_id: int) -> str:
    """
    Process and combine knowledge base content for a bot
    """
    from models import KnowledgeBase
    
    try:
        knowledge_entries = KnowledgeBase.query.filter_by(bot_id=bot_id).all()
        combined_knowledge = ""
        
        # Debug: log bilim bazasi mavjudligi
        logging.info(f"DEBUG: Bot {bot_id} uchun {len(knowledge_entries)} ta bilim bazasi yozuvi topildi")
        
        for entry in knowledge_entries:
            logging.info(f"DEBUG: Processing entry - Type: {entry.content_type}, Source: {entry.source_name}")
            
            if entry.content_type == 'product':
                # For products, format them clearly for AI with detailed structure
                product_text = f"=== MAHSULOT MA'LUMOTI ===\n{entry.content}\n=== MAHSULOT OXIRI ===\n"
                combined_knowledge += product_text + "\n"
                logging.info(f"DEBUG: Product added to knowledge: {entry.source_name}")
            elif entry.content_type == 'image':
                # For images, add description about the image
                image_info = f"Rasm: {entry.filename or 'Yuklangan rasm'}"
                if entry.source_name:
                    image_info += f" ({entry.source_name})"
                image_info += f" - bu mahsulot/xizmat haqidagi vizual ma'lumot. Foydalanuvchi ushbu rasm haqida so'rasa, unga rasm haqida ma'lumot bering."
                combined_knowledge += f"{image_info}\n\n"
                logging.info(f"DEBUG: Image added to knowledge: {entry.source_name or entry.filename}")
            else:
                # For text and file content
                combined_knowledge += f"{entry.content}\n\n"
                logging.info(f"DEBUG: File content added to knowledge: {entry.filename}")
        
        logging.info(f"DEBUG: Combined knowledge length: {len(combined_knowledge)} characters")
        if combined_knowledge:
            logging.info(f"DEBUG: First 200 chars of knowledge: {combined_knowledge[:200]}...")
        
        return combined_knowledge.strip()
    except Exception as e:
        logging.error(f"Knowledge base processing error: {str(e)}")
        return ""

def find_relevant_product_images(bot_id: int, user_message: str) -> list:
    """
    Find product images relevant to user's message
    """
    from models import KnowledgeBase
    
    try:
        # Get products that match user's message
        products = KnowledgeBase.query.filter_by(bot_id=bot_id, content_type='product').all()
        
        relevant_images = []
        user_message_lower = user_message.lower()
        
        for product in products:
            product_content = product.content.lower()
            product_name = (product.source_name or "").lower()
            
            # Check if user's message relates to this product
            if any(keyword in user_message_lower for keyword in ['mahsulot', 'narx', 'paket', 'zip']) or \
               any(word in product_content for word in user_message_lower.split() if len(word) > 2) or \
               any(word in product_name for word in user_message_lower.split() if len(word) > 2):
                
                # Look for image URL in product content
                lines = product.content.split('\n')
                for line in lines:
                    if line.startswith('Rasm:') and 'http' in line:
                        image_url = line.replace('Rasm:', '').strip()
                        relevant_images.append({
                            'url': image_url,
                            'product_name': product.source_name or 'Mahsulot',
                            'caption': f"📦 {product.source_name or 'Mahsulot'}"
                        })
                        break
        
        return relevant_images
    except Exception as e:
        logging.error(f"Error finding product images: {str(e)}")
        return []

def validate_ai_response(response: Optional[str], max_length: int = 4000) -> Optional[str]:
    """
    Validate and clean AI response
    """
    if not response:
        return None
    
    # Remove markdown formatting
    response = response.replace('**', '').replace('*', '').replace('`', '')
    
    # Limit response length
    if len(response) > max_length:
        response = response[:max_length] + "..."
    
    return response.strip()
