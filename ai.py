import os
import logging
import re
from typing import Optional

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

try:
    from google import genai
    from google.genai import types as genai_types
    api_key = os.environ.get("GOOGLE_API_KEY")
    _gemini_client = genai.Client(api_key=api_key) if api_key else None
    GEMINI_AVAILABLE = _gemini_client is not None
    if not GEMINI_AVAILABLE:
        logging.warning("GOOGLE_API_KEY is not set — Gemini client unavailable")
    else:
        logging.info(f"Gemini client initialized with model: {GEMINI_MODEL}")
except ImportError:
    GEMINI_AVAILABLE = False
    _gemini_client = None
    genai_types = None
    logging.warning("google-genai library not available. Install with: pip install google-genai")

def extract_price_information(knowledge_base: str) -> str:
    """
    Extract price-related lines from knowledge base to prioritize pricing information
    """
    if not knowledge_base:
        return ""
    
    # Patterns to match price information
    price_patterns = [
        r'.*[Nn]arx\s*:\s*.+',  # Narx: pattern
        r'.*[Pp]rice\s*:\s*.+',  # Price: pattern
        r'.*Цена\s*:\s*.+',      # Russian price pattern
        r'.*\d+[\s,]*UZS\b.*',   # UZS currency
        r'.*\d+[\s,]*so\'m\b.*', # so'm currency
        r'.*\d+[\s,]*som\b.*',   # som currency
        r'.*\$\s*\d+.*',         # Dollar prices
        r'.*\d+[\s,]*USD\b.*'    # USD currency
    ]
    
    price_lines = []
    lines = knowledge_base.split('\n')
    
    for i, line in enumerate(lines):
        # Check if line matches any price pattern
        for pattern in price_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Include context: previous line + price line + next line for better understanding
                context_start = max(0, i-1)
                context_end = min(len(lines), i+2)
                context_lines = lines[context_start:context_end]
                price_lines.extend(context_lines)
                break
    
    # Remove duplicates while preserving order
    seen = set()
    unique_price_lines = []
    for line in price_lines:
        if line not in seen:
            unique_price_lines.append(line)
            seen.add(line)
    
    return '\n'.join(unique_price_lines)

def get_ai_response(message: str, bot_name: str = "Chatbot Factory AI", user_language: str = "uz", knowledge_base: str = "", chat_history: str = "") -> Optional[str]:
    """
    Generate AI response using Google Gemini with chat history context
    """
    try:
        # Language-specific system prompts
        language_prompts = {
            'uz': f"Sen {bot_name} nomli chatbot san. Har doim o'zbek tilida javob ber. Dostona, foydali va emotsiyalik bo'ling. Emoji ishlating. HECH QACHON ** yoki * yoki ` kabi markdown belgilarini ishlatma! Faqat oddiy matn, emoji va qator ajratish. Mahsulot ro'yxatini chiroyli formatda yoz: • yoki - bilan boshlash, har bir mahsulotni alohida qatorda yoz. Foydalanuvchi bilan oldingi suhbatlarni eslab qoling. MUHIM: Agar foydalanuvchi 'narx', 'narxi', 'qancha', 'qancha turadi', 'pul' yoki shunga o'xshash narx haqida so'rasa, ALBATTA bilim bazasidan aniq narx ma'lumotlarini toping va ko'rsating! 'Narx:', 'Price:', 'Цена:' qatorlarini izlab, UZS, so'm, som, $, USD belgilarini qidiring. Agar narx ma'lum bo'lsa, uni aniq va to'liq ko'rsating.",
            'ru': f"Ты чатбот по имени {bot_name}. Всегда отвечай на русском языке. Будь дружелюбным, полезным и эмоциональным. Используй эмодзи. НИКОГДА не используй ** или * или ` и другие markdown символы! Только простой текст, эмодзи и переносы строк. Список товаров пиши в красивом формате: начинай с • или -, каждый товар на отдельной строке. Помни предыдущие разговоры с пользователем. ВАЖНО: Если пользователь спрашивает о цене ('цена', 'стоимость', 'сколько стоит', 'деньги'), ОБЯЗАТЕЛЬНО найди точную информацию о цене из базы знаний! Ищи строки 'Narx:', 'Price:', 'Цена:', а также символы UZS, сом, so'm, $, USD. Если цена известна, покажи её точно и полностью.",
            'en': f"You are a chatbot named {bot_name}. Always respond in English. Be friendly, helpful and emotional. Use emojis. NEVER use ** or * or ` or any markdown symbols! Only plain text, emojis and line breaks. Format product lists nicely: start with • or -, each product on separate line. Remember previous conversations with the user. IMPORTANT: If user asks about price ('price', 'cost', 'how much', 'money'), ALWAYS find exact pricing information from knowledge base! Look for 'Narx:', 'Price:', 'Цена:' lines and currency symbols like UZS, so'm, som, $, USD. If price is available, show it accurately and completely."
        }
        
        system_prompt = language_prompts.get(user_language, language_prompts['uz'])
        
        # Add knowledge base context if available with price-aware processing
        if knowledge_base:
            # Extract price information first to ensure it's always included
            price_lines = extract_price_information(knowledge_base)
            
            # Increased knowledge base limit for complete information
            kb_limit = 8000  # Increased to ensure pricing data isn't cut off
            
            # Prioritize price information by putting it first
            if price_lines:
                limited_kb = f"=== NARX MA'LUMOTLARI ===\n{price_lines}\n\n=== TO'LIQ BILIM BAZASI ===\n{knowledge_base[:kb_limit-len(price_lines)-100]}"
                logging.info(f"DEBUG: Price information prioritized - {len(price_lines.split(chr(10)))} price lines found")
            else:
                limited_kb = knowledge_base[:kb_limit]
                logging.info(f"DEBUG: No specific price lines found, using full KB")
                
            system_prompt += f"\n\nSizda quyidagi bilim bazasi mavjud:\n{limited_kb}\n\nAgar foydalanuvchi yuqoridagi ma'lumotlar haqida so'rasa, aniq va to'liq javob bering."
            
            # Debug: log knowledge base uzunligi
            logging.info(f"DEBUG: Knowledge base length: {len(knowledge_base)}, Limited to: {len(limited_kb)}")
        
        # Add chat history context if available
        if chat_history:
            system_prompt += f"\n\nOldingi suhbatlar:\n{chat_history}\n\nYuqoridagi suhbatlarni eslab qoling va kontekst asosida javob bering."
        
        # Create the prompt (increased limit to preserve pricing info)
        if len(system_prompt) > 12000:  # Increased limit to preserve price information
            system_prompt = system_prompt[:12000] + "..."
        
        full_prompt = f"{system_prompt}\n\nFoydalanuvchi savoli: {message}"
        
        # Generate response using Gemini with optimization settings
        if not GEMINI_AVAILABLE or _gemini_client is None:
            return get_fallback_response(user_language)

        generation_config = genai_types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=500,
            top_p=0.9,
            top_k=40,
        )

        response = _gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=full_prompt,
            config=generation_config,
        )

        if response.text:
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
    Find the most relevant product image based on user's message
    Returns only the best matching product, not all products
    """
    from models import KnowledgeBase
    
    try:
        # Get products that match user's message
        products = KnowledgeBase.query.filter_by(bot_id=bot_id, content_type='product').all()
        
        if not products:
            return []
        
        user_message_lower = user_message.lower()
        user_words = [word.strip() for word in user_message_lower.split() if len(word.strip()) > 2]
        
        best_match = None
        best_score = 0
        
        for product in products:
            product_content = product.content.lower()
            product_name = (product.source_name or "").lower()
            
            # Calculate relevance score
            score = 0
            
            # Extract product name from content
            lines = product.content.split('\n')
            actual_product_name = ""
            for line in lines:
                if line.startswith('Mahsulot:'):
                    actual_product_name = line.replace('Mahsulot:', '').strip().lower()
                    break
            
            # High score for exact product name match
            if actual_product_name:
                for user_word in user_words:
                    if user_word in actual_product_name:
                        score += 10
                        
            # Medium score for source name match
            if product_name:
                for user_word in user_words:
                    if user_word in product_name:
                        score += 5
                        
            # Low score for content match (but avoid generic words)
            generic_words = ['mahsulot', 'narx', 'som', 'dollar', 'paket', 'zip', 'rasm', 'tavsif', 'haqida']
            for user_word in user_words:
                if user_word not in generic_words and user_word in product_content:
                    score += 1
            
            # Only consider products with images
            has_image = False
            image_url = ""
            for line in lines:
                if line.startswith('Rasm:') and 'http' in line:
                    image_url = line.replace('Rasm:', '').strip()
                    has_image = True
                    break
            
            # Update best match if this product scores higher and has an image
            if has_image and score > best_score:
                best_score = score
                best_match = {
                    'url': image_url,
                    'product_name': product.source_name or actual_product_name or 'Mahsulot',
                    'caption': f"📦 {product.source_name or actual_product_name or 'Mahsulot'}"
                }
        
        # Return only the best match, or empty list if no good match found
        if best_match and best_score >= 3:  # Minimum score threshold
            return [best_match]
        else:
            return []
            
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
