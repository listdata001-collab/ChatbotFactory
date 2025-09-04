# BotFactory AI - Telegram Chatbot Platform

O'zbek tilida AI chatbot yaratish platformasi.

## Render.com ga Deploy qilish

### 1. Repository tayyorlash
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin your-repository-url
git push -u origin main
```

### 2. Render.com da setup
1. Render.com da yangi Web Service yarating
2. GitHub repository ni bog'lang
3. Quyidagi sozlamalarni kiriting:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app`

### 3. Environment Variables
Quyidagi environment variables ni Render.com dashboard da sozlang:

```
SESSION_SECRET=your-secret-key-here
GOOGLE_API_KEY=your-google-api-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
DATABASE_URL=postgresql://... (Render automatically provides this)
```

### 4. Database Setup
1. Render.com da PostgreSQL database yarating
2. DATABASE_URL avtomatik ravishda sozlanadi
3. Birinchi deploy qilinganda tables avtomatik yaratiladi

## Local Development

### Requirements
- Python 3.11+
- PostgreSQL (production) yoki SQLite (development)

### Setup
```bash
# Virtual environment yaratish
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows

# Dependencies o'rnatish
pip install -r requirements.txt

# Environment variables sozlash
cp .env.example .env
# .env faylini to'ldiring

# Dasturni ishga tushirish
python main.py
```

## Features
- ✅ Telegram AI chatbot
- ✅ Multi-language support (Uzbek, Russian, English)
- ✅ Subscription management
- ✅ Knowledge base upload
- ✅ Google Gemini AI integration
- ✅ Admin panel
- ✅ Payment integration (PayMe, Click, Uzum)

## Architecture
- **Backend**: Flask + SQLAlchemy
- **Database**: PostgreSQL (production), SQLite (development)  
- **AI**: Google Gemini API
- **Deployment**: Render.com
- **Frontend**: Bootstrap 5 + Vanilla JS