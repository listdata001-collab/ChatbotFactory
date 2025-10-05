/**
 * Jivo ga o'xshash mijozlar qo'llab-quvvatlash chat bot sistemi
 * Chatbot Factory AI uchun
 */

class SupportChatBot {
    constructor() {
        this.isOpen = false;
        this.currentStep = 'greeting';
        this.userName = '';
        this.userEmail = '';
        this.userQuestion = '';
        
        // Knowledge base
        this.knowledgeBase = {
            pricing: {
                title: "💰 Narxlar va Ta'riflar",
                content: `
<div class="kb-section">
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
                content: `
<div class="kb-section">
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
                content: `
<div class="kb-section">
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
                content: `
<div class="kb-section">
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
                content: `
<div class="kb-section">
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
        };
        
        this.init();
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
                                <small>Yordam markazi</small>
                            </div>
                        </div>
                        <button id="chat-close" class="chat-close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="chat-body" id="chat-body">
                        <!-- Messages will be added here -->
                    </div>
                    
                    <div class="chat-footer">
                        <div class="quick-actions" id="quick-actions">
                            <!-- Quick action buttons will be added here -->
                        </div>
                        <div class="chat-input-container" id="chat-input-container" style="display: none;">
                            <input type="text" id="chat-input" placeholder="Xabar yozing..." />
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
            }
            
            .chat-header small {
                opacity: 0.9;
            }
            
            .chat-close {
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: background 0.2s;
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
        this.addBotMessage(`
            Assalomu alaykum! 👋
            
            <strong>Chatbot Factory AI</strong> yordam markaziga xush kelibsiz!
            
            Men sizga qanday yordam bera olaman?
        `);
        
        this.showQuickActions([
            { id: 'pricing', icon: 'fas fa-tags', text: 'Narxlar va ta\'riflar' },
            { id: 'features', icon: 'fas fa-star', text: 'Funksiyalar' },
            { id: 'setup', icon: 'fas fa-cog', text: 'Bot sozlash' },
            { id: 'trial', icon: 'fas fa-gift', text: 'Bepul sinov' },
            { id: 'contact', icon: 'fas fa-phone', text: 'Kontakt' },
            { id: 'custom', icon: 'fas fa-comment', text: 'Boshqa savol' }
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
        const actionTexts = {
            pricing: 'Narxlar va ta\'riflar',
            features: 'Funksiyalar',
            setup: 'Bot sozlash',
            trial: 'Bepul sinov',
            contact: 'Kontakt ma\'lumotlari',
            custom: 'Boshqa savol'
        };
        
        this.addUserMessage(actionTexts[actionId]);
        
        if (actionId === 'custom') {
            this.currentStep = 'custom_question';
            this.addBotMessage(`
                Savolingizni yozing, men sizga javob berishga harakat qilaman! 📝
                
                Yoki to'g'ridan-to'g'ri bizning qo'llab-quvvatlash xizmatimiz bilan bog'laning:
                📞 +998 99 644-84-44
                💬 @akramjon0011
            `);
            this.showChatInput();
        } else {
            // Show knowledge base content
            const kb = this.knowledgeBase[actionId];
            if (kb) {
                this.addBotMessage(`
                    <strong>${kb.title}</strong>
                    ${kb.content}
                    
                    Boshqa savollaringiz bormi?
                `);
                
                this.showQuickActions([
                    { id: 'pricing', icon: 'fas fa-tags', text: 'Narxlar' },
                    { id: 'features', icon: 'fas fa-star', text: 'Funksiyalar' },
                    { id: 'setup', icon: 'fas fa-cog', text: 'Sozlash' },
                    { id: 'contact', icon: 'fas fa-phone', text: 'Kontakt' },
                    { id: 'custom', icon: 'fas fa-comment', text: 'Boshqa savol' }
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
                this.addBotMessage(`
                    Savolingiz uchun rahmat! 🙏
                    
                    Sizning so'rovingiz qabul qilindi. Bizning mutaxassislarimiz tez orada sizga javob berishadi.
                    
                    To'g'ridan-to'g'ri bog'lanish uchun:
                    📞 +998 99 644-84-44
                    💬 @akramjon0011
                    📧 info@botfactory.uz
                    
                    Yana biror narsa kerakmi?
                `);
                
                this.showQuickActions([
                    { id: 'pricing', icon: 'fas fa-tags', text: 'Narxlar' },
                    { id: 'features', icon: 'fas fa-star', text: 'Funksiyalar' },
                    { id: 'contact', icon: 'fas fa-phone', text: 'Kontakt' }
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
        return new Date().toLocaleTimeString('uz-UZ', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
}

// Initialize chat bot when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.supportChat = new SupportChatBot();
});