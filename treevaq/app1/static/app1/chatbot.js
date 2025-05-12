// Create a new file: static/app1/chatbot.js

document.addEventListener('DOMContentLoaded', function() {
    // Chat elements
    const chatbotButton = document.getElementById('chatbot-button');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const deleteChat = document.getElementById('delete-chat');
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const typingIndicator = document.getElementById('typing-indicator');
    
    // Chat history
    let chatHistory = [];
    
    // Check if we have any saved chat history
    const savedChat = localStorage.getItem('treevaq_chat_history');
    if (savedChat) {
        try {
            chatHistory = JSON.parse(savedChat);
            // Render saved messages
            chatHistory.forEach(msg => {
                appendMessage(msg.message, msg.sender);
            });
        } catch (e) {
            console.error('Failed to load chat history', e);
            localStorage.removeItem('treevaq_chat_history');
        }
    } else {
        // Add a welcome message if there's no history
        const welcomeMessage = "Hi there! I'm Treevaq's assistant. How can I help you with your shopping today?";
        appendMessage(welcomeMessage, 'bot');
        chatHistory.push({ message: welcomeMessage, sender: 'bot' });
        saveChat();
    }
    
    // Toggle chat window
    chatbotButton.addEventListener('click', function() {
        chatWindow.classList.toggle('open');
        if (chatWindow.classList.contains('open')) {
            messageInput.focus();
            // Scroll to the latest message
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    });
    
    // Close chat window
    closeChat.addEventListener('click', function() {
        chatWindow.classList.remove('open');
    });
    
    // Delete chat history
    deleteChat.addEventListener('click', function() {
        showDeleteConfirmation();
    });
    
    // Send message on Enter key
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey && messageInput.value.trim() !== '') {
            sendMessage();
        }
    });
    
    // Send message on button click
    sendButton.addEventListener('click', function() {
        if (messageInput.value.trim() !== '') {
            sendMessage();
        }
    });
    
    // Function to show delete confirmation dialog
    function showDeleteConfirmation() {
        // Create confirmation dialog if it doesn't exist
        let confirmDialog = document.getElementById('delete-confirmation');
        if (!confirmDialog) {
            confirmDialog = document.createElement('div');
            confirmDialog.id = 'delete-confirmation';
            confirmDialog.className = 'delete-confirmation';
            
            confirmDialog.innerHTML = `
                <p>Are you sure you want to delete all chat history?</p>
                <div class="delete-confirmation-buttons">
                    <button class="confirm-delete">Delete</button>
                    <button class="cancel-delete">Cancel</button>
                </div>
            `;
            
            chatWindow.appendChild(confirmDialog);
            
            // Add event listeners to confirmation buttons
            confirmDialog.querySelector('.confirm-delete').addEventListener('click', function() {
                clearChatHistory();
                confirmDialog.classList.remove('show');
            });
            
            confirmDialog.querySelector('.cancel-delete').addEventListener('click', function() {
                confirmDialog.classList.remove('show');
            });
        }
        
        // Show the confirmation dialog
        confirmDialog.classList.add('show');
    }
    
    // Function to clear chat history
    function clearChatHistory() {
        // Clear chat history
        chatHistory = [];
        localStorage.removeItem('treevaq_chat_history');
        
        // Clear chat messages from DOM
        while (chatMessages.firstChild) {
            if (chatMessages.firstChild.id === 'typing-indicator') {
                // Skip the typing indicator
                chatMessages.insertBefore(chatMessages.firstChild, null);
            } else {
                chatMessages.removeChild(chatMessages.firstChild);
            }
        }
        
        // Add a fresh welcome message
        const welcomeMessage = "Chat history cleared. How can I help you today?";
        appendMessage(welcomeMessage, 'bot');
        chatHistory.push({ message: welcomeMessage, sender: 'bot' });
        saveChat();
    }
    
    // Function to send message to the server
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message === '') return;
        
        // Append user message to chat
        appendMessage(message, 'user');
        
        // Add to history
        chatHistory.push({ message, sender: 'user' });
        saveChat();
        
        // Clear input
        messageInput.value = '';
        
        // Show typing indicator
        typingIndicator.classList.add('active');
        
        // Disable input while waiting for response
        messageInput.disabled = true;
        sendButton.disabled = true;
        
        // Extract just the messages from history for context
        const messageHistory = chatHistory.map(item => item.message);
        
        // Send message to Django backend
        fetch('/api/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ 
                message,
                history: messageHistory
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide typing indicator
            typingIndicator.classList.remove('active');
            
            // Enable input
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
            
            if (data.status === 'success') {
                // Add bot response
                appendMessage(data.response, 'bot');
                chatHistory.push({ message: data.response, sender: 'bot' });
                saveChat();
            } else {
                // Handle error
                appendMessage("Sorry, I'm having trouble understanding right now. Please try again later.", 'bot');
                console.error('Error from chatbot API:', data.error);
            }
        })
        .catch(error => {
            // Hide typing indicator
            typingIndicator.classList.remove('active');
            
            // Enable input
            messageInput.disabled = false;
            sendButton.disabled = false;
            
            // Show error message
            appendMessage("I'm sorry, there was a problem connecting to my brain. Please try again later.", 'bot');
            console.error('Fetch error:', error);
        });
    }
    
    // Function to append message to the chat
    function appendMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(sender + '-message');
        messageElement.textContent = message;
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to save chat history to localStorage
    function saveChat() {
        // Limit history to the last 50 messages to avoid localStorage quota issues
        if (chatHistory.length > 50) {
            chatHistory = chatHistory.slice(-50);
        }
        localStorage.setItem('treevaq_chat_history', JSON.stringify(chatHistory));
    }
    
    // Function to get CSRF token from cookies
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
});