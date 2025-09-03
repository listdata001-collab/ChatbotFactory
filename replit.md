# BotFactory AI

## Overview

BotFactory AI is a Telegram AI chatbot platform designed for Uzbek language users. The system allows users to create and manage AI-powered chatbots with subscription-based features and multi-language support. The platform integrates with Google Gemini AI for natural language processing and uses a tiered subscription model offering different levels of functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask with MVC architecture pattern
- **Database**: SQLAlchemy ORM with support for both PostgreSQL and SQLite
- **Authentication**: Flask-Login with bcrypt password hashing
- **Session Management**: Flask sessions with 7-day persistence
- **AI Integration**: Google Gemini API (gemini-2.5-flash model) for chatbot responses
- **Telegram Integration**: python-telegram-bot library for bot management

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **UI Framework**: Bootstrap 5 for responsive design
- **Icons**: Font Awesome for consistent iconography
- **Styling**: Custom CSS with CSS variables for theming
- **JavaScript**: Vanilla JavaScript for client-side functionality

### Database Design
The system uses a relational database with the following key entities:
- **User**: Stores user accounts with subscription types (free, basic, premium, admin)
- **Bot**: Manages individual chatbot instances with platform-specific tokens
- **KnowledgeBase**: Handles document uploads for bot training
- **Payment**: Tracks subscription payments and billing
- **ChatHistory**: Logs bot conversations for analytics

### Authentication & Authorization
- **User Registration**: Username/email with password confirmation
- **Login System**: Session-based authentication with "remember me" functionality
- **Role-Based Access**: Admin panel access for administrators
- **Subscription Management**: Feature access based on subscription tiers

### Subscription Model
Three-tier subscription system:
- **Free/Test (14 days)**: 1 bot, Telegram only, Uzbek language AI responses
- **Basic (290,000 UZS/month)**: 1 bot, multiple platforms, multilingual AI (Uzbek/Russian/English)
- **Premium (590,000 UZS/month)**: 5 bots, all platforms, multilingual AI support

### AI Response System
- **Language Detection**: Automatic language routing based on user subscription
- **Context Management**: Knowledge base integration for domain-specific responses
- **Response Formatting**: Plain text with emoji enhancement, avoiding Markdown
- **Fallback Handling**: Error recovery with localized fallback messages

### File Upload System
- **Supported Formats**: .txt and .docx files for knowledge base
- **File Validation**: Extension and size checking (16MB limit)
- **Content Processing**: Text extraction from documents for AI training

## Recent Changes
- **September 03, 2025**: Successfully migrated to Replit environment and import completed
  - Installed all Python dependencies using uv from pyproject.toml
  - Ensured gunicorn is properly installed for the WSGI server
  - Configured Flask application for Replit hosting with ProxyFix middleware
  - Set up workflow for development server on port 5000 with webview output
  - Configured deployment for autoscaling production environment
  - Application running successfully with admin user auto-created
  - Using SQLite database (PostgreSQL ready via environment variable)
  - Cache control headers configured to prevent browser caching issues
  - Google API key configured for AI chatbot responses
  - **Import Status**: ✅ COMPLETED - Application fully functional in Replit environment
  - **Setup Status**: ✅ READY FOR USE - All core features operational

## External Dependencies

### AI Services
- **Google Gemini API**: Primary AI service for generating chatbot responses using the gemini-2.5-flash model

### Messaging Platforms
- **Telegram Bot API**: Core integration for Telegram bot functionality
- **Instagram & WhatsApp**: Full integrations available for all subscription tiers

### Payment Processors
- **PayMe**: Uzbekistan payment gateway integration
- **Click**: Local payment processor support
- **Uzum**: Additional payment method for subscriptions

### Python Libraries
- **Flask**: Web framework and extensions (Flask-SQLAlchemy, Flask-Login)
- **python-telegram-bot**: Telegram API wrapper
- **google-genai**: Google Gemini AI client
- **python-docx**: Document processing for knowledge base uploads
- **Werkzeug**: Security utilities and WSGI support
- **Gunicorn**: Production WSGI server

### Frontend Dependencies
- **Bootstrap 5**: UI framework via CDN
- **Font Awesome**: Icon library via CDN
- **Vanilla JavaScript**: No additional frontend frameworks

### Database Options
- **SQLite**: Default development database (currently active)
- **PostgreSQL**: Production database option (configurable via DATABASE_URL)

### Development Tools
- **Environment Variables**: Configuration management for API keys and secrets
- **Logging**: Built-in Python logging for debugging and monitoring
- **File Handling**: Werkzeug utilities for secure file uploads

## Replit Configuration
- **Development Server**: Gunicorn on port 5000 with auto-reload
- **Production Deployment**: Autoscale configuration for web hosting
- **Cache Control**: Configured to prevent caching issues in development
- **Proxy Support**: ProxyFix middleware enabled for proper URL generation