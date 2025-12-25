// AI Chat Widget for EcoNest Interiors
(function() {
    'use strict';
    
    // Chat widget state
    let isOpen = false;
    let chatHistory = [];
    
    // Create chat widget HTML
    function createChatWidget() {
        const chatWidget = document.createElement('div');
        chatWidget.id = 'ai-chat-widget';
        chatWidget.innerHTML = `
            <div id="chat-button" class="chat-button">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H6L4 18V4H20V16Z" fill="currentColor"/>
                    <path d="M7 9H17V11H7V9ZM7 12H15V14H7V12Z" fill="currentColor"/>
                </svg>
                <span class="chat-badge">AI</span>
            </div>
            <div id="chat-window" class="chat-window">
                <div class="chat-header">
                    <div class="chat-header-content">
                        <div class="chat-avatar">🌿</div>
                        <div>
                            <h3>EcoNest AI Assistant</h3>
                            <p>Your virtual design assistant</p>
                        </div>
                    </div>
                    <button id="chat-close" class="chat-close" aria-label="Close chat">×</button>
                </div>
                <div id="chat-messages" class="chat-messages">
                    <div class="chat-message bot-message">
                        <div class="message-avatar">🌿</div>
                        <div class="message-content">
                            <p>Hello! I'm your virtual design assistant at EcoNest Interiors. I can help you with:</p>
                            <ul style="margin: 8px 0; padding-left: 20px;">
                                <li>Interior design queries</li>
                                <li>Eco-friendly material suggestions</li>
                                <li>Information about our services</li>
                                <li>Booking consultations</li>
                            </ul>
                            <p>How can I assist you today?</p>
                        </div>
                    </div>
                </div>
                <div class="chat-input-container">
                    <input 
                        type="text" 
                        id="chat-input" 
                        class="chat-input" 
                        placeholder="Type your message..."
                        autocomplete="off"
                    />
                    <button id="chat-send" class="chat-send" aria-label="Send message">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(chatWidget);
    }
    
    // Get CSRF token
    function getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Add message to chat
    function addMessage(text, isBot = false) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isBot ? 'bot-message' : 'user-message'}`;
        
        const avatar = isBot ? '🌿' : '👤';
        const content = isBot 
            ? `<div class="message-avatar">${avatar}</div><div class="message-content">${formatMessage(text)}</div>`
            : `<div class="message-content">${escapeHtml(text)}</div><div class="message-avatar">${avatar}</div>`;
        
        messageDiv.innerHTML = content;
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Store in history
        chatHistory.push({ text, isBot });
    }
    
    // Format bot message (support line breaks and links)
    function formatMessage(text) {
        // Convert line breaks to <br>
        let formatted = escapeHtml(text).replace(/\n/g, '<br>');
        
        // Convert URLs to links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        formatted = formatted.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener">$1</a>');
        
        // Convert markdown-style links [text](url) to HTML links
        const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
        formatted = formatted.replace(markdownLinkRegex, '<a href="$2" target="_blank" rel="noopener">$1</a>');
        
        return formatted;
    }
    
    // Escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Send message to AI
    async function sendMessage(message) {
        if (!message.trim()) return;
        
        // Add user message
        addMessage(message, false);
        
        // Show typing indicator
        const messagesContainer = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot-message typing-indicator';
        typingDiv.innerHTML = '<div class="message-avatar">🌿</div><div class="message-content"><div class="typing-dots"><span></span><span></span><span></span></div></div>';
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        try {
            const csrftoken = getCSRFToken();
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken || '',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ message: message }),
                credentials: 'same-origin'
            });
            
            // Remove typing indicator
            typingDiv.remove();
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            if (data.success && data.response) {
                addMessage(data.response, true);
            } else {
                addMessage('I apologize, but I encountered an error. Please try again or contact us directly.', true);
            }
        } catch (error) {
            console.error('Chat error:', error);
            typingDiv.remove();
            addMessage('I apologize, but I encountered an error. Please try again or contact us directly at +91 6301739482.', true);
        }
    }
    
    // Toggle chat window
    function toggleChat() {
        isOpen = !isOpen;
        const chatWindow = document.getElementById('chat-window');
        const chatButton = document.getElementById('chat-button');
        
        if (isOpen) {
            chatWindow.classList.add('open');
            chatButton.classList.add('active');
            document.getElementById('chat-input').focus();
        } else {
            chatWindow.classList.remove('open');
            chatButton.classList.remove('active');
        }
    }
    
    // Initialize chat widget
    function initChatWidget() {
        createChatWidget();
        
        // Event listeners
        document.getElementById('chat-button').addEventListener('click', toggleChat);
        document.getElementById('chat-close').addEventListener('click', toggleChat);
        document.getElementById('chat-send').addEventListener('click', () => {
            const input = document.getElementById('chat-input');
            sendMessage(input.value);
            input.value = '';
        });
        
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const input = document.getElementById('chat-input');
                sendMessage(input.value);
                input.value = '';
            }
        });
        
        // Quick action buttons
        const quickActions = [
            { text: 'What services do you offer?', label: 'Services' },
            { text: 'Suggest eco-friendly materials', label: 'Materials' },
            { text: 'How do I book a consultation?', label: 'Book Now' }
        ];
        
        const messagesContainer = document.getElementById('chat-messages');
        const quickActionsDiv = document.createElement('div');
        quickActionsDiv.className = 'quick-actions';
        quickActionsDiv.innerHTML = quickActions.map(action => 
            `<button class="quick-action-btn" data-message="${escapeHtml(action.text)}">${action.label}</button>`
        ).join('');
        messagesContainer.appendChild(quickActionsDiv);
        
        // Quick action button handlers
        quickActionsDiv.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                quickActionsDiv.remove();
                sendMessage(message);
            });
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChatWidget);
    } else {
        initChatWidget();
    }
})();





