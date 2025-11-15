/**
 * Multi-language Support Chat Bot System
 * Chatbot Factory AI
 */

class SupportChatBot {
    constructor() {
        this.isOpen = false;
        this.currentStep = 'greeting';
        this.currentLanguage = 'uz'; // Default language
        this.userName = '';
        this.userEmail = '';
        this.userQuestion = '';
        
        // Detect browser language
        const browserLang = navigator.language || navigator.userLanguage;
        if (browserLang.startsWith('ru')) {
            this.currentLanguage = 'ru';
        } else if (browserLang.startsWith('en')) {
            this.currentLanguage = 'en';
        }
        
        // Translations
        this.translations = {
            uz: {
                header: 'Yordam markazi',
                greeting: `Assalomu alaykum! 👋\n\n<strong>Chatbot Factory AI</strong> yordam markaziga xush kelibsiz!\n\nMen sizga qanday yordam bera olaman?`,
                inputPlaceholder: 'Xabar yozing...',
                buttons: {
                    pricing: "Narxlar va ta'riflar",
                    features: "Funksiyalar",
                    setup: "Bot sozlash",
                    trial: "Bepul sinov",
                    contact: "Kontakt",
                    custom: "Boshqa savol"
                },
                knowledge: {
                    pricing: {
                        title: "💰 Narxlar va Ta'riflar",
                        content: `<div class="kb-section">
    <h6>🚀 Starter - 165,000 so'm/oy</h6>
    <ul>
        <li>1 ta bot yaratish</li>
        <li>Faqat Telegram platformasi</li>
        <li>3 tilda AI (O'zbek/Rus/Ingliz)</li>
        <li>Bilim bazasi yuklash</li>
        <li>Asosiy qo'llab-quvvatlash</li>
    </ul>
    
    <h6>💰 Basic - 290,000 so'm/oy</h6>
    <ul>
        <li>1 ta bot yaratish</li>
        <li>Barcha platformalar (Telegram/Instagram/WhatsApp)</li>
        <li>3 tilda AI</li>
        <li>Bilim bazasi yuklash</li>
        <li>Asosiy qo'llab-quvvatlash</li>
    </ul>
    
    <h6>💎 Premium - 590,000 so'm/oy</h6>
    <ul>
        <li>5 ta bot yaratish</li>
        <li>Barcha platformalar</li>
        <li>3 tilda AI</li>
        <li>Prioritet qo'llab-quvvatlash</li>
        <li>Tahlil va statistika</li>
        <li>Maxsus funksiyalar</li>
    </ul>
</div>`
                    },
                    features: {
                        title: "🤖 Funksiyalar",
                        content: `<div class="kb-section">
    <h6>Asosiy imkoniyatlar:</h6>
    <ul>
        <li><strong>AI Chatbot:</strong> Google Gemini AI bilan ishlaydigan aqlli botlar</li>
        <li><strong>Ko'p til:</strong> O'zbek, Rus va Ingliz tillari</li>
        <li><strong>Ko'p platforma:</strong> Telegram, Instagram, WhatsApp</li>
        <li><strong>Bilim bazasi:</strong> PDF, DOCX fayllarni yuklash</li>
        <li><strong>Obuna tizimi:</strong> Avtomatik to'lov va eslatmalar</li>
        <li><strong>Admin panel:</strong> To'liq boshqaruv paneli</li>
        <li><strong>Statistika:</strong> Bot faoliyatini kuzatish</li>
    </ul>
</div>`
                    },
                    setup: {
                        title: "🛠 Bot Sozlash",
                        content: `<div class="kb-section">
    <h6>Bot yaratish bosqichlari:</h6>
    <ol>
        <li><strong>Ro'yxatdan o'tish:</strong> Platformaga registratsiya qiling</li>
        <li><strong>Bot yaratish:</strong> "Yangi bot" tugmasini bosing</li>
        <li><strong>Ma'lumotlar:</strong> Bot nomi va tavsifini kiriting</li>
        <li><strong>Platform tanlash:</strong> Telegram, Instagram yoki WhatsApp</li>
        <li><strong>Bilim bazasi:</strong> PDF/DOCX fayllarni yuklang</li>
        <li><strong>Test qilish:</strong> Botni sinab ko'ring</li>
        <li><strong>Aktivlashtirish:</strong> Botni real foydalanuvchilar uchun ishga tushiring</li>
    </ol>
</div>`
                    },
                    contact: {
                        title: "📞 Kontakt Ma'lumotlari",
                        content: `<div class="kb-section">
    <h6>Biz bilan bog'laning:</h6>
    <ul>
        <li><strong>📱 Telefon:</strong> +998 99 644-84-44</li>
        <li><strong>📧 Email:</strong> info@botfactory.uz</li>
        <li><strong>💬 Telegram:</strong> @akramjon0011</li>
        <li><strong>🌐 Sayt:</strong> https://botfactory.uz</li>
        <li><strong>🏢 Manzil:</strong> Toshkent, O'zbekiston</li>
        <li><strong>⏰ Ish vaqti:</strong> Dushanba-Juma 9:00-18:00</li>
    </ul>
    
    <h6>Qo'llab-quvvatlash:</h6>
    <p>Savollaringiz bo'lsa, biz bilan bog'lanishingiz mumkin. 24 soat ichida javob beramiz!</p>
</div>`
                    },
                    trial: {
                        title: "🆓 Bepul Sinov",
                        content: `<div class="kb-section">
    <h6>14 kunlik bepul sinov:</h6>
    <ul>
        <li>Registratsiyadan so'ng avtomatik boshlanadi</li>
        <li>Barcha funksiyalarga to'liq kirish</li>
        <li>1 ta bot yaratish imkoniyati</li>
        <li>Faqat Telegram platformasi</li>
        <li>To'lov talab qilinmaydi</li>
    </ul>
    
    <h6>Sinov tugagach:</h6>
    <p>To'lov ta'rifini tanlash kerak. Aks holda bot deaktivatsiya qilinadi.</p>
</div>`
                    }
                },
                customQuestion: `Savolingizni yozing, men sizga javob berishga harakat qilaman! 📝\n\nYoki to'g'ridan-to'g'ri bizning qo'llab-quvvatlash xizmatimiz bilan bog'laning:\n📞 +998 99 644-84-44\n💬 @akramjon0011`,
                thankYou: `Savolingiz uchun rahmat! 🙏\n\nSizning so'rovingiz qabul qilindi. Bizning mutaxassislarimiz tez orada sizga javob berishadi.\n\nTo'g'ridan-to'g'ri bog'lanish uchun:\n📞 +998 99 644-84-44\n💬 @akramjon0011\n📧 info@botfactory.uz\n\nYana biror narsa kerakmi?`,
                moreQuestions: 'Boshqa savollaringiz bormi?'
            },
            ru: {
                header: 'Центр помощи',
                greeting: `Здравствуйте! 👋\n\n<strong>Chatbot Factory AI</strong> - добро пожаловать в наш центр поддержки!\n\nКак я могу вам помочь?`,
                inputPlaceholder: 'Напишите сообщение...',
                buttons: {
                    pricing: "Цены и тарифы",
                    features: "Функции",
                    setup: "Настройка бота",
                    trial: "Бесплатная пробная версия",
                    contact: "Контакты",
                    custom: "Другой вопрос"
                },
                knowledge: {
                    pricing: {
                        title: "💰 Цены и Тарифы",
                        content: `<div class="kb-section">
    <h6>🚀 Starter - 165,000 сум/мес</h6>
    <ul>
        <li>Создание 1 бота</li>
        <li>Только Telegram платформа</li>
        <li>AI на 3 языках (Узбекский/Русский/Английский)</li>
        <li>Загрузка базы знаний</li>
        <li>Базовая поддержка</li>
    </ul>
    
    <h6>💰 Basic - 290,000 сум/мес</h6>
    <ul>
        <li>Создание 1 бота</li>
        <li>Все платформы (Telegram/Instagram/WhatsApp)</li>
        <li>AI на 3 языках</li>
        <li>Загрузка базы знаний</li>
        <li>Базовая поддержка</li>
    </ul>
    
    <h6>💎 Premium - 590,000 сум/мес</h6>
    <ul>
        <li>Создание 5 ботов</li>
        <li>Все платформы</li>
        <li>AI на 3 языках</li>
        <li>Приоритетная поддержка</li>
        <li>Аналитика и статистика</li>
        <li>Специальные функции</li>
    </ul>
</div>`
                    },
                    features: {
                        title: "🤖 Функции",
                        content: `<div class="kb-section">
    <h6>Основные возможности:</h6>
    <ul>
        <li><strong>AI Chatbot:</strong> Умные боты на базе Google Gemini AI</li>
        <li><strong>Мультиязычность:</strong> Узбекский, Русский и Английский языки</li>
        <li><strong>Мультиплатформа:</strong> Telegram, Instagram, WhatsApp</li>
        <li><strong>База знаний:</strong> Загрузка файлов PDF, DOCX</li>
        <li><strong>Система подписок:</strong> Автоматическая оплата и уведомления</li>
        <li><strong>Админ панель:</strong> Полная система управления</li>
        <li><strong>Статистика:</strong> Отслеживание активности ботов</li>
    </ul>
</div>`
                    },
                    setup: {
                        title: "🛠 Настройка Бота",
                        content: `<div class="kb-section">
    <h6>Этапы создания бота:</h6>
    <ol>
        <li><strong>Регистрация:</strong> Зарегистрируйтесь на платформе</li>
        <li><strong>Создание бота:</strong> Нажмите кнопку "Новый бот"</li>
        <li><strong>Данные:</strong> Введите имя и описание бота</li>
        <li><strong>Выбор платформы:</strong> Telegram, Instagram или WhatsApp</li>
        <li><strong>База знаний:</strong> Загрузите файлы PDF/DOCX</li>
        <li><strong>Тестирование:</strong> Протестируйте бота</li>
        <li><strong>Активация:</strong> Запустите бота для реальных пользователей</li>
    </ol>
</div>`
                    },
                    contact: {
                        title: "📞 Контактная Информация",
                        content: `<div class="kb-section">
    <h6>Свяжитесь с нами:</h6>
    <ul>
        <li><strong>📱 Телефон:</strong> +998 99 644-84-44</li>
        <li><strong>📧 Email:</strong> info@botfactory.uz</li>
        <li><strong>💬 Telegram:</strong> @akramjon0011</li>
        <li><strong>🌐 Сайт:</strong> https://botfactory.uz</li>
        <li><strong>🏢 Адрес:</strong> Ташкент, Узбекистан</li>
        <li><strong>⏰ Время работы:</strong> Пн-Пт 9:00-18:00</li>
    </ul>
    
    <h6>Поддержка:</h6>
    <p>Если у вас есть вопросы, свяжитесь с нами. Мы ответим в течение 24 часов!</p>
</div>`
                    },
                    trial: {
                        title: "🆓 Бесплатная Пробная Версия",
                        content: `<div class="kb-section">
    <h6>14-дневная бесплатная пробная версия:</h6>
    <ul>
        <li>Автоматически начинается после регистрации</li>
        <li>Полный доступ ко всем функциям</li>
        <li>Возможность создать 1 бота</li>
        <li>Только платформа Telegram</li>
        <li>Оплата не требуется</li>
    </ul>
    
    <h6>После окончания пробного периода:</h6>
    <p>Необходимо выбрать платный тариф. В противном случае бот будет деактивирован.</p>
</div>`
                    }
                },
                customQuestion: `Напишите ваш вопрос, я постараюсь вам помочь! 📝\n\nИли свяжитесь напрямую с нашей службой поддержки:\n📞 +998 99 644-84-44\n💬 @akramjon0011`,
                thankYou: `Спасибо за ваш вопрос! 🙏\n\nВаш запрос принят. Наши специалисты скоро свяжутся с вами.\n\nДля прямой связи:\n📞 +998 99 644-84-44\n💬 @akramjon0011\n📧 info@botfactory.uz\n\nЕще что-нибудь нужно?`,
                moreQuestions: 'Есть другие вопросы?'
            },
            en: {
                header: 'Help Center',
                greeting: `Hello! 👋\n\n<strong>Chatbot Factory AI</strong> - welcome to our support center!\n\nHow can I help you?`,
                inputPlaceholder: 'Write a message...',
                buttons: {
                    pricing: "Pricing & Plans",
                    features: "Features",
                    setup: "Bot Setup",
                    trial: "Free Trial",
                    contact: "Contact",
                    custom: "Other Question"
                },
                knowledge: {
                    pricing: {
                        title: "💰 Pricing & Plans",
                        content: `<div class="kb-section">
    <h6>🚀 Starter - 165,000 UZS/month</h6>
    <ul>
        <li>Create 1 bot</li>
        <li>Telegram platform only</li>
        <li>AI in 3 languages (Uzbek/Russian/English)</li>
        <li>Knowledge base upload</li>
        <li>Basic support</li>
    </ul>
    
    <h6>💰 Basic - 290,000 UZS/month</h6>
    <ul>
        <li>Create 1 bot</li>
        <li>All platforms (Telegram/Instagram/WhatsApp)</li>
        <li>AI in 3 languages</li>
        <li>Knowledge base upload</li>
        <li>Basic support</li>
    </ul>
    
    <h6>💎 Premium - 590,000 UZS/month</h6>
    <ul>
        <li>Create 5 bots</li>
        <li>All platforms</li>
        <li>AI in 3 languages</li>
        <li>Priority support</li>
        <li>Analytics and statistics</li>
        <li>Special features</li>
    </ul>
</div>`
                    },
                    features: {
                        title: "🤖 Features",
                        content: `<div class="kb-section">
    <h6>Main capabilities:</h6>
    <ul>
        <li><strong>AI Chatbot:</strong> Smart bots powered by Google Gemini AI</li>
        <li><strong>Multi-language:</strong> Uzbek, Russian and English languages</li>
        <li><strong>Multi-platform:</strong> Telegram, Instagram, WhatsApp</li>
        <li><strong>Knowledge base:</strong> Upload PDF, DOCX files</li>
        <li><strong>Subscription system:</strong> Automatic payments and notifications</li>
        <li><strong>Admin panel:</strong> Complete management system</li>
        <li><strong>Statistics:</strong> Track bot activity</li>
    </ul>
</div>`
                    },
                    setup: {
                        title: "🛠 Bot Setup",
                        content: `<div class="kb-section">
    <h6>Bot creation steps:</h6>
    <ol>
        <li><strong>Registration:</strong> Sign up on the platform</li>
        <li><strong>Create bot:</strong> Click "New bot" button</li>
        <li><strong>Details:</strong> Enter bot name and description</li>
        <li><strong>Choose platform:</strong> Telegram, Instagram or WhatsApp</li>
        <li><strong>Knowledge base:</strong> Upload PDF/DOCX files</li>
        <li><strong>Testing:</strong> Test your bot</li>
        <li><strong>Activation:</strong> Launch bot for real users</li>
    </ol>
</div>`
                    },
                    contact: {
                        title: "📞 Contact Information",
                        content: `<div class="kb-section">
    <h6>Get in touch:</h6>
    <ul>
        <li><strong>📱 Phone:</strong> +998 99 644-84-44</li>
        <li><strong>📧 Email:</strong> info@botfactory.uz</li>
        <li><strong>💬 Telegram:</strong> @akramjon0011</li>
        <li><strong>🌐 Website:</strong> https://botfactory.uz</li>
        <li><strong>🏢 Address:</strong> Tashkent, Uzbekistan</li>
        <li><strong>⏰ Working hours:</strong> Mon-Fri 9:00-18:00</li>
    </ul>
    
    <h6>Support:</h6>
    <p>If you have questions, contact us. We will respond within 24 hours!</p>
</div>`
                    },
                    trial: {
                        title: "🆓 Free Trial",
                        content: `<div class="kb-section">
    <h6>14-day free trial:</h6>
    <ul>
        <li>Automatically starts after registration</li>
        <li>Full access to all features</li>
        <li>Ability to create 1 bot</li>
        <li>Telegram platform only</li>
        <li>No payment required</li>
    </ul>
    
    <h6>After trial ends:</h6>
    <p>You need to choose a paid plan. Otherwise, the bot will be deactivated.</p>
</div>`
                    }
                },
                customQuestion: `Write your question, I'll try to help you! 📝\n\nOr contact our support service directly:\n📞 +998 99 644-84-44\n💬 @akramjon0011`,
                thankYou: `Thank you for your question! 🙏\n\nYour request has been received. Our specialists will contact you soon.\n\nFor direct contact:\n📞 +998 99 644-84-44\n💬 @akramjon0011\n📧 info@botfactory.uz\n\nAnything else you need?`,
                moreQuestions: 'Any other questions?'
            }
        };
        
        this.init();
    }
    
    t(key) {
        // Get translation by key
        const keys = key.split('.');
        let value = this.translations[this.currentLanguage];
        for (const k of keys) {
            value = value[k];
            if (!value) return key;
        }
        return value;
    }
    
    init() {
        this.createChatWidget();
        this.attachEventListeners();
    }
    
    createChatWidget() {
        // Chat widget HTML
        const chatHTML = `
            <div id="support-chat-widget" class="support-chat-widget">
                <!-- Chat trigger button -->
                <div id="chat-trigger" class="chat-trigger">
                    <i class="fas fa-comments"></i>
                    <span class="chat-badge">?</span>
                </div>
                
                <!-- Chat window -->
                <div id="chat-window" class="chat-window">
                    <div class="chat-header">
                        <div class="chat-header-info">
                            <div class="chat-avatar">
                                <i class="fas fa-robot"></i>
                            </div>
                            <div>
                                <h6>Chatbot Factory AI</h6>
                                <small id="chat-header-subtitle">${this.t('header')}</small>
                            </div>
                        </div>
                        <div class="header-buttons">
                            <div class="language-selector">
                                <button class="lang-btn ${this.currentLanguage === 'uz' ? 'active' : ''}" data-lang="uz">UZ</button>
                                <button class="lang-btn ${this.currentLanguage === 'ru' ? 'active' : ''}" data-lang="ru">RU</button>
                                <button class="lang-btn ${this.currentLanguage === 'en' ? 'active' : ''}" data-lang="en">EN</button>
                            </div>
                            <button id="chat-close" class="chat-close">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    
                    <div class="chat-body" id="chat-body">
                        <!-- Messages will be added here -->
                    </div>
                    
                    <div class="chat-footer">
                        <div class="quick-actions" id="quick-actions">
                            <!-- Quick action buttons will be added here -->
                        </div>
                        <div class="chat-input-container" id="chat-input-container" style="display: none;">
                            <input type="text" id="chat-input" placeholder="${this.t('inputPlaceholder')}" />
                            <button id="chat-send"><i class="fas fa-paper-plane"></i></button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', chatHTML);
        
        // Add CSS
        if (!document.getElementById('support-chat-css')) {
            const style = document.createElement('style');
            style.id = 'support-chat-css';
            style.textContent = this.getChatCSS();
            document.head.appendChild(style);
        }
    }
    
    getChatCSS() {
        return `
            .support-chat-widget {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 9999;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .chat-trigger {
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 4px 16px rgba(0,0,0,0.15);
                transition: all 0.3s ease;
                position: relative;
            }
            
            .chat-trigger:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 24px rgba(0,0,0,0.2);
            }
            
            .chat-trigger i {
                color: white;
                font-size: 24px;
            }
            
            .chat-badge {
                position: absolute;
                top: -5px;
                right: -5px;
                background: #ff4757;
                color: white;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
            }
            
            .chat-window {
                position: fixed;
                bottom: 90px;
                right: 20px;
                width: 350px;
                max-width: calc(100vw - 40px);
                height: 500px;
                max-height: calc(100vh - 120px);
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                display: none;
                flex-direction: column;
                border: 1px solid #e1e5e9;
                z-index: 9998;
            }
            
            .chat-window.open {
                display: flex;
                animation: slideUp 0.3s ease;
            }
            
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 16px;
                border-radius: 12px 12px 0 0;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .chat-header-info {
                display: flex;
                align-items: center;
                gap: 12px;
                flex: 1;
            }
            
            .header-buttons {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .language-selector {
                display: flex;
                gap: 4px;
                background: rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 2px;
            }
            
            .lang-btn {
                background: transparent;
                border: none;
                color: rgba(255,255,255,0.7);
                cursor: pointer;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
                transition: all 0.2s;
            }
            
            .lang-btn:hover {
                background: rgba(255,255,255,0.1);
                color: white;
            }
            
            .lang-btn.active {
                background: rgba(255,255,255,0.2);
                color: white;
            }
            
            .chat-avatar {
                width: 40px;
                height: 40px;
                background: rgba(255,255,255,0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .chat-avatar i {
                font-size: 20px;
            }
            
            .chat-header h6 {
                margin: 0;
                font-weight: 600;
                font-size: 14px;
            }
            
            .chat-header small {
                opacity: 0.9;
                font-size: 11px;
            }
            
            .chat-close {
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: background 0.2s;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .chat-close:hover {
                background: rgba(255,255,255,0.1);
            }
            
            .chat-body {
                flex: 1;
                padding: 16px;
                overflow-y: auto;
                overflow-x: hidden;
                background: #f8f9fa;
                word-wrap: break-word;
                max-width: 100%;
            }
            
            .chat-message {
                margin-bottom: 12px;
                display: flex;
                flex-direction: column;
            }
            
            .chat-message.bot {
                align-items: flex-start;
            }
            
            .chat-message.user {
                align-items: flex-end;
            }
            
            .message-bubble {
                max-width: 80%;
                padding: 12px 16px;
                border-radius: 18px;
                word-wrap: break-word;
            }
            
            .chat-message.bot .message-bubble {
                background: white;
                border: 1px solid #e1e5e9;
                border-bottom-left-radius: 6px;
            }
            
            .chat-message.user .message-bubble {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-bottom-right-radius: 6px;
            }
            
            .message-time {
                font-size: 11px;
                color: #8e9297;
                margin-top: 4px;
                padding: 0 8px;
            }
            
            .chat-footer {
                border-top: 1px solid #e1e5e9;
                background: white;
                border-radius: 0 0 12px 12px;
            }
            
            .quick-actions {
                padding: 16px;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .quick-action-btn {
                background: #f8f9fa;
                border: 1px solid #e1e5e9;
                padding: 12px 16px;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
                text-align: left;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 8px;
                word-wrap: break-word;
                white-space: normal;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .quick-action-btn:hover {
                background: #e9ecef;
                border-color: #667eea;
                transform: translateY(-1px);
            }
            
            .quick-action-btn i {
                color: #667eea;
                width: 16px;
            }
            
            .chat-input-container {
                padding: 16px;
                display: flex;
                gap: 8px;
                align-items: center;
            }
            
            .chat-input-container input {
                flex: 1;
                border: 1px solid #e1e5e9;
                border-radius: 20px;
                padding: 12px 16px;
                outline: none;
                font-size: 14px;
            }
            
            .chat-input-container input:focus {
                border-color: #667eea;
            }
            
            .chat-input-container button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                color: white;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.2s;
            }
            
            .chat-input-container button:hover {
                transform: scale(1.1);
            }
            
            .kb-section h6 {
                color: #495057;
                margin-bottom: 8px;
                font-weight: 600;
            }
            
            .kb-section ul, .kb-section ol {
                margin-bottom: 12px;
            }
            
            .kb-section li {
                margin-bottom: 4px;
                color: #6c757d;
            }
            
            .kb-section p {
                color: #6c757d;
                margin-bottom: 8px;
            }
            
            @media (max-width: 768px) {
                .chat-window {
                    width: calc(100vw - 30px);
                    height: calc(100vh - 100px);
                    max-width: 350px;
                    right: 15px;
                    bottom: 80px;
                }
                
                .support-chat-widget {
                    bottom: 15px;
                    right: 15px;
                }
                
                .quick-action-btn {
                    font-size: 13px;
                    padding: 10px 12px;
                }
            }
        `;
    }
    
    attachEventListeners() {
        // Toggle chat
        document.getElementById('chat-trigger').addEventListener('click', () => {
            this.toggleChat();
        });
        
        // Close chat
        document.getElementById('chat-close').addEventListener('click', () => {
            this.closeChat();
        });
        
        // Language switcher
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lang = e.target.dataset.lang;
                this.changeLanguage(lang);
            });
        });
        
        // Send message
        document.getElementById('chat-send').addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Enter key in input
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }
    
    changeLanguage(lang) {
        if (lang === this.currentLanguage) return;
        
        this.currentLanguage = lang;
        
        // Update language buttons
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });
        
        // Update header
        document.getElementById('chat-header-subtitle').textContent = this.t('header');
        
        // Update input placeholder
        document.getElementById('chat-input').placeholder = this.t('inputPlaceholder');
        
        // Clear and restart conversation
        document.getElementById('chat-body').innerHTML = '';
        this.currentStep = 'greeting';
        this.showGreeting();
    }
    
    toggleChat() {
        const chatWindow = document.getElementById('chat-window');
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }
    
    openChat() {
        this.isOpen = true;
        const chatWindow = document.getElementById('chat-window');
        chatWindow.classList.add('open');
        
        if (this.currentStep === 'greeting') {
            this.showGreeting();
        }
    }
    
    closeChat() {
        this.isOpen = false;
        const chatWindow = document.getElementById('chat-window');
        chatWindow.classList.remove('open');
    }
    
    showGreeting() {
        this.addBotMessage(this.t('greeting'));
        
        this.showQuickActions([
            { id: 'pricing', icon: 'fas fa-tags', text: this.t('buttons.pricing') },
            { id: 'features', icon: 'fas fa-star', text: this.t('buttons.features') },
            { id: 'setup', icon: 'fas fa-cog', text: this.t('buttons.setup') },
            { id: 'trial', icon: 'fas fa-gift', text: this.t('buttons.trial') },
            { id: 'contact', icon: 'fas fa-phone', text: this.t('buttons.contact') },
            { id: 'custom', icon: 'fas fa-comment', text: this.t('buttons.custom') }
        ]);
    }
    
    showQuickActions(actions) {
        const quickActions = document.getElementById('quick-actions');
        quickActions.innerHTML = '';
        
        actions.forEach(action => {
            const button = document.createElement('button');
            button.className = 'quick-action-btn';
            button.innerHTML = `<i class="${action.icon}"></i> ${action.text}`;
            button.onclick = () => this.handleQuickAction(action.id);
            quickActions.appendChild(button);
        });
        
        document.getElementById('chat-input-container').style.display = 'none';
    }
    
    handleQuickAction(actionId) {
        // Add user message
        const actionText = this.t(`buttons.${actionId}`);
        this.addUserMessage(actionText);
        
        if (actionId === 'custom') {
            this.currentStep = 'custom_question';
            this.addBotMessage(this.t('customQuestion'));
            this.showChatInput();
        } else {
            // Show knowledge base content
            const kb = this.t(`knowledge.${actionId}`);
            if (kb && typeof kb === 'object') {
                this.addBotMessage(`<strong>${kb.title}</strong>${kb.content}\n\n${this.t('moreQuestions')}`);
                
                this.showQuickActions([
                    { id: 'pricing', icon: 'fas fa-tags', text: this.t('buttons.pricing') },
                    { id: 'features', icon: 'fas fa-star', text: this.t('buttons.features') },
                    { id: 'setup', icon: 'fas fa-cog', text: this.t('buttons.setup') },
                    { id: 'contact', icon: 'fas fa-phone', text: this.t('buttons.contact') },
                    { id: 'custom', icon: 'fas fa-comment', text: this.t('buttons.custom') }
                ]);
            }
        }
    }
    
    showChatInput() {
        document.getElementById('quick-actions').innerHTML = '';
        document.getElementById('chat-input-container').style.display = 'flex';
        document.getElementById('chat-input').focus();
    }
    
    sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (message) {
            this.addUserMessage(message);
            input.value = '';
            
            // Simple response logic
            setTimeout(() => {
                this.addBotMessage(this.t('thankYou'));
                
                this.showQuickActions([
                    { id: 'pricing', icon: 'fas fa-tags', text: this.t('buttons.pricing') },
                    { id: 'features', icon: 'fas fa-star', text: this.t('buttons.features') },
                    { id: 'contact', icon: 'fas fa-phone', text: this.t('buttons.contact') }
                ]);
            }, 1000);
        }
    }
    
    addBotMessage(content) {
        const chatBody = document.getElementById('chat-body');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message bot';
        
        messageDiv.innerHTML = `
            <div class="message-bubble">${content}</div>
            <div class="message-time">${this.getCurrentTime()}</div>
        `;
        
        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }
    
    addUserMessage(content) {
        const chatBody = document.getElementById('chat-body');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message user';
        
        messageDiv.innerHTML = `
            <div class="message-bubble">${content}</div>
            <div class="message-time">${this.getCurrentTime()}</div>
        `;
        
        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }
    
    getCurrentTime() {
        return new Date().toLocaleTimeString(this.currentLanguage === 'uz' ? 'uz-UZ' : this.currentLanguage === 'ru' ? 'ru-RU' : 'en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
}

// Initialize chat bot when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.supportChat = new SupportChatBot();
});
