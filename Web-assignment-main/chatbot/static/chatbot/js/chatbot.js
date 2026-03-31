document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('chatbot-toggle');
    const closeBtn = document.getElementById('chatbot-close');
    const windowEl = document.getElementById('chatbot-window');
    const inputField = document.getElementById('chatbot-input-field');
    const sendBtn = document.getElementById('chatbot-send');
    const messagesContainer = document.getElementById('chatbot-messages');

    // Session ID management
    let sessionId = localStorage.getItem('chatbot_session_id');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chatbot_session_id', sessionId);
    }

    // Toggle Chat
    toggleBtn.addEventListener('click', () => {
        windowEl.classList.toggle('active');
        if (windowEl.classList.contains('active')) {
            inputField.focus();
            scrollToBottom();
        }
    });

    closeBtn.addEventListener('click', () => {
        windowEl.classList.remove('active');
    });

    // Send Message
    function sendMessage() {
        const message = inputField.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        inputField.value = '';

        // Show typing indicator
        showTyping();

        // API Call
        const formData = new FormData();
        formData.append('message', message);
        formData.append('session_id', sessionId);

        fetch('/chatbot/message/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
            .then(response => response.json())
            .then(data => {
                removeTyping();
                if (data.success) {
                    addMessage(data.response, 'assistant');
                } else {
                    addMessage("Sorry, I encountered an error. Please try again.", 'assistant');
                }
            })
            .catch(error => {
                removeTyping();
                console.error('Error:', error);
                addMessage("Network error. Please check your connection.", 'assistant');
            });
    }

    sendBtn.addEventListener('click', sendMessage);
    inputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Helpers
    function addMessage(text, role) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        div.innerHTML = `<div class="bubble">${formatText(text)}</div>`;
        messagesContainer.appendChild(div);
        scrollToBottom();
    }

    function showTyping() {
        const div = document.createElement('div');
        div.id = 'typing-indicator';
        div.className = 'message assistant';
        div.innerHTML = `
            <div class="typing-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        `;
        messagesContainer.appendChild(div);
        scrollToBottom();
    }

    function removeTyping() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function formatText(text) {
        // Simple formatting for links and line breaks
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    function getCookie(name) {
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
});
