/**
 * Chat interface logic for khappha.online
 */

const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loadingIndicator = document.getElementById('loadingIndicator');

// Add welcome message
window.addEventListener('DOMContentLoaded', () => {
    addBotMessage('Xin chào! Tôi là trợ lý du lịch AI. Bạn muốn đi đâu hôm nay? 😊');
});

// Handle form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    messageInput.value = '';
    
    // Disable send button
    setSending(true);
    
    try {
        // Send message to API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Add bot response
            addBotMessage(data.response);
            
            // If has plan data, show save button
            if (data.has_plan && data.plan_data) {
                addSavePlanButton(data.plan_data);
            }
        } else {
            addErrorMessage(data.error || 'Đã có lỗi xảy ra');
        }
        
    } catch (error) {
        console.error('Error:', error);
        addErrorMessage('Không thể kết nối đến server. Vui lòng thử lại.');
    } finally {
        setSending(false);
    }
});

// Add user message to chat
function addUserMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex justify-end';
    messageDiv.innerHTML = `
        <div class="bg-blue-600 text-white rounded-lg px-4 py-2 max-w-md">
            <p>${escapeHtml(message)}</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add bot message to chat
function addBotMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex justify-start';
    messageDiv.innerHTML = `
        <div class="bg-gray-200 text-gray-800 rounded-lg px-4 py-2 max-w-md">
            <p>${formatMessage(message)}</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add error message
function addErrorMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex justify-center';
    messageDiv.innerHTML = `
        <div class="bg-red-100 text-red-700 rounded-lg px-4 py-2 max-w-md">
            <p>❌ ${escapeHtml(message)}</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add save plan button
function addSavePlanButton(planData) {
    const buttonDiv = document.createElement('div');
    buttonDiv.className = 'flex justify-center my-4';
    buttonDiv.innerHTML = `
        <button onclick="savePlan(${JSON.stringify(planData).replace(/"/g, '&quot;')})" 
                class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition">
            💾 Lưu kế hoạch này
        </button>
    `;
    chatMessages.appendChild(buttonDiv);
    scrollToBottom();
}

// Save plan function
async function savePlan(planData) {
    try {
        const response = await fetch('/api/save-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(planData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            addBotMessage(`✅ Đã lưu kế hoạch thành công! <a href="/plans" class="underline">Xem kế hoạch</a>`);
        } else {
            addErrorMessage('Không thể lưu kế hoạch');
        }
    } catch (error) {
        console.error('Error saving plan:', error);
        addErrorMessage('Lỗi khi lưu kế hoạch');
    }
}

// Send sample message
function sendSample(message) {
    messageInput.value = message;
    chatForm.dispatchEvent(new Event('submit'));
}

// Set sending state
function setSending(isSending) {
    sendButton.disabled = isSending;
    messageInput.disabled = isSending;
    
    if (isSending) {
        loadingIndicator.classList.remove('hidden');
    } else {
        loadingIndicator.classList.add('hidden');
    }
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format message (preserve line breaks)
function formatMessage(message) {
    return escapeHtml(message).replace(/\n/g, '<br>');
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
