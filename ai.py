import os
import logging
from typing import Optional

try:
    import google.generativeai as genai
    # Initialize Gemini client
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "default_key"))
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI library not available. Install with: pip install google-generativeai")

def get_ai_response(message: str, bot_name: str = "BotFactory AI", user_language: str = "uz", knowledge_base: str = "") -> Optional[str]:
    """
    Generate AI response using Google Gemini
    """
    try:
        # Language-specific system prompts
        language_prompts = {
            'uz': f"Sen {bot_name} nomli chatbot san. Har doim o'zbek tilida javob ber. Dostona, foydali va emotsiyalik bo'ling. Emoji ishlating. Markdown formatini ishlamang, faqat oddiy matn.",
            'ru': f"Ты чатбот по имени {bot_name}. Всегда отвечай на русском языке. Будь дружелюбным, полезным и эмоциональным. Используй эмодзи. Не используй формат Markdown, только простой текст.",
            'en': f"You are a chatbot named {bot_name}. Always respond in English. Be friendly, helpful and emotional. Use emojis. Don't use Markdown format, only plain text."
        }
        
        system_prompt = language_prompts.get(user_language, language_prompts['uz'])
        
        # Add knowledge base context if available
        if knowledge_base:
            system_prompt += f"\n\nQo'shimcha ma'lumot: {knowledge_base[:2000]}"  # Limit knowledge base length
        
        # Create the prompt
        full_prompt = f"{system_prompt}\n\nFoydalanuvchi savoli: {message}"
        
        # Generate response using Gemini
        if not GEMINI_AVAILABLE:
            return get_fallback_response(user_language)
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_prompt)
        
        if response.text:
            return response.text
        else:
            return get_fallback_response(user_language)
            
    except Exception as e:
        # Safe error logging to prevent encoding issues  
        error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8')
        logging.error(f"AI response error: {error_msg}")
        return get_fallback_response(user_language)

def get_fallback_response(language: str = "uz") -> str:
    """
    Fallback responses when AI fails
    """
    fallback_responses = {
        'uz': "Kechirasiz, hozir javob bera olmayapman. Iltimos, keyinroq urinib ko'ring. 🤖",
        'ru': "Извините, сейчас не могу ответить. Пожалуйста, попробуйте позже. 🤖",
        'en': "Sorry, I can't respond right now. Please try again later. 🤖"
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
        
        for entry in knowledge_entries:
            combined_knowledge += f"{entry.content}\n\n"
        
        return combined_knowledge.strip()
    except Exception as e:
        logging.error(f"Knowledge base processing error: {str(e)}")
        return ""

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
