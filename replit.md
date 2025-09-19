# Chatbot Factory AI

## Overview
Chatbot Factory AI is a Telegram AI chatbot platform designed for Uzbek language users. It enables users to create and manage AI-powered chatbots with subscription-based features and multi-language support. The platform integrates with Google Gemini AI for natural language processing and utilizes a tiered subscription model to offer varying levels of functionality. The project aims to provide a robust, scalable, and user-friendly solution for AI chatbot creation, particularly for the Uzbek market.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture
### Core System
- **Backend Framework**: Flask with an MVC architecture pattern.
- **Database**: SQLAlchemy ORM, supporting both PostgreSQL (production) and SQLite (development).
- **Authentication**: Flask-Login for user authentication with bcrypt hashing.
- **AI Integration**: Google Gemini API (gemini-2.5-flash) for AI responses.
- **Telegram Integration**: `python-telegram-bot` library for managing Telegram bots.
- **File Uploads**: Supports `.txt` and `.docx` for knowledge base, with validation for extension and size (16MB limit).
- **Subscription Model**: Four tiers (Free/Test, Starter, Basic, Premium) with varying bot limits, platform support, language options, and features.
- **AI Response System**: Includes automatic language detection, knowledge base integration for context, plain text response formatting (no Markdown, uses emojis), and fallback handling.

### User Interface
- **Frontend**: Jinja2 templates.
- **UI Framework**: Bootstrap 5 for responsive design.
- **Icons**: Font Awesome.
- **Styling**: Custom CSS with variables.
- **Client-side functionality**: Vanilla JavaScript.

### Key Features
- **User Management**: Registration, login, session management, role-based access (admin panel).
- **Bot Management**: Creation, configuration, and deployment of individual chatbot instances.
- **Knowledge Base**: Document upload and processing for bot training.
- **Payment System**: Integration with local Uzbek payment gateways for subscription management.
- **Chat History**: Logging conversations for analytics.
- **Performance Optimizations**: Typing indicators, optimized AI configuration (prompt, knowledge base, chat history limits), and faster database queries for improved response speed.

## External Dependencies
### AI Services
- **Google Gemini API**: Used for natural language processing and chatbot response generation.

### Messaging Platforms
- **Telegram Bot API**: Primary platform for chatbot deployment and interaction.
- **Instagram & WhatsApp**: Supported integrations for higher subscription tiers.

### Payment Processors
- **PayMe**: Uzbekistan payment gateway.
- **Click**: Local payment processor.
- **Uzum**: Additional local payment method.
- **Paynet**: Local payment system with QR code support and manual verification.

### Python Libraries
- **Flask Ecosystem**: `Flask`, `Flask-SQLAlchemy`, `Flask-Login`.
- **Telegram**: `python-telegram-bot`.
- **Google AI**: `google-genai`.
- **Document Processing**: `python-docx`.
- **WSGI Server**: `Gunicorn` (for production).

### Frontend Libraries
- **Bootstrap 5**: UI framework (CDN).
- **Font Awesome**: Icon library (CDN).

### Databases
- **SQLite**: Default for development.
- **PostgreSQL**: Production database option.