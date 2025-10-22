/**
 * Main chat interface logic for khappha.online
 * Handles real-time chat with AI and travel plan generation
 */

// DOM Elements
let chatMessagesContainer = null;
let messageInput = null;
let sendButton = null;
let planDisplay = null;

// Initialize DOM elements after page load
function initializeDOMElements() {
    chatMessagesContainer = document.getElementById('chatMessages');
    planDisplay = document.getElementById('planDisplay');
    messageInput = document.querySelector('input[placeholder="Nhập yêu cầu của bạn..."]');
    
    // Find send button by looking for the send icon
    const buttons = document.querySelectorAll('button');
    for (let btn of buttons) {
        const icon = btn.querySelector('.material-symbols-outlined');
        if (icon && icon.textContent.trim() === 'send') {
            sendButton = btn;
            break;
        }
    }
    
    console.log('DOM Elements initialized:', {
        chatMessages: !!chatMessagesContainer,
        planDisplay: !!planDisplay,
        messageInput: !!messageInput,
        sendButton: !!sendButton
    });
}

// Initialize chat
window.addEventListener('DOMContentLoaded', () => {
    initializeDOMElements();
    addWelcomeMessage();
    attachEventListeners();
});

// Add welcome message
function addWelcomeMessage() {
    const welcomeMsg = createBotMessage('Xin chào! Tôi là trợ lý du lịch ảo của bạn. Bạn muốn đi đâu hôm nay? 😊');
    if (chatMessagesContainer) {
        chatMessagesContainer.appendChild(welcomeMsg);
    }
}

// Attach event listeners
function attachEventListeners() {
    // Send button
    if (sendButton) {
        sendButton.addEventListener('click', handleSendMessage);
    } else {
        console.error('Send button not found!');
    }
    
    // Enter key
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });
    } else {
        console.error('Message input not found!');
    }
    
    // Suggestion buttons - re-query to get fresh elements
    const suggestionBtns = document.querySelectorAll('.p-4.border-t button.text-sm');
    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const text = btn.textContent.trim();
            if (messageInput) {
                messageInput.value = text;
                handleSendMessage();
            }
        });
    });
}

// Handle send message
async function handleSendMessage() {
    const message = messageInput?.value.trim();
    if (!message) return;
    
    // Disable input and button
    if (messageInput) messageInput.disabled = true;
    if (sendButton) sendButton.disabled = true;
    
    // Add user message
    addUserMessage(message);
    
    // Clear input
    if (messageInput) {
        messageInput.value = '';
    }
    
    // Show loading
    const loadingMsg = addLoadingMessage();
    
    try {
        // Send to API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        // Remove loading
        loadingMsg.remove();
        
        if (data.success) {
            // Add bot response
            addBotMessage(data.response);
            
            // If has plan, update plan view
            if (data.has_plan && data.plan_data) {
                updatePlanView(data.plan_data);
            }
        } else {
            addErrorMessage(data.error || 'Đã có lỗi xảy ra');
        }
        
    } catch (error) {
        console.error('Error:', error);
        loadingMsg.remove();
        addErrorMessage('Không thể kết nối đến server');
    } finally {
        // Re-enable input and button
        if (messageInput) messageInput.disabled = false;
        if (sendButton) sendButton.disabled = false;
        if (messageInput) messageInput.focus();
    }
}

// Create bot message element
function createBotMessage(text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex items-end gap-3';
    msgDiv.innerHTML = `
        <div class="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 shrink-0" 
             style='background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuASndgVA3RbX1H4yCbbqk8hsJujYw-P6pZI-uQr7cNE6Fya18CrfnQF3Q6u5lkHGOdbnxRhwJZDcIr3QYn2d9_fHpzc12fDYZTMAQJ7TptH7Pyu-rlqSErcQwCOM7T7182tN0XX_l_KuPUmWhBcT3Qsf6Y1drq5VInxput-tgaNfjrS50WHYfdtTuf2Ofxb432HdB0uwEupfdrgBaK8ptf5_sLoNoRi-VRHoMj3O_yZSs2pThNsHrNSU7onQN-hig4FR913Omzgito");'></div>
        <div class="flex flex-1 flex-col gap-1 items-start">
            <p class="text-xs text-gray-500">TravelBot</p>
            <p class="text-base font-normal leading-normal max-w-[480px] rounded-xl px-4 py-3 bg-gray-100 dark:bg-gray-700">${escapeHtml(text)}</p>
        </div>
    `;
    return msgDiv;
}

// Add bot message
function addBotMessage(text) {
    const msg = createBotMessage(text);
    chatMessagesContainer?.appendChild(msg);
    scrollToBottom();
}

// Add user message
function addUserMessage(text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex items-end gap-3 justify-end';
    msgDiv.innerHTML = `
        <div class="flex flex-1 flex-col gap-1 items-end">
            <p class="text-xs text-gray-500 text-right">You</p>
            <p class="text-base font-normal leading-normal max-w-[480px] rounded-xl px-4 py-3 bg-primary text-white">${escapeHtml(text)}</p>
        </div>
        <div class="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 shrink-0" 
             style='background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuBosanAOWFXEW4ZcSVyk8DJD4GEcsZtNwT8jyFHtW9epmo75m8Ip0fceEELK_61J_A0jnT0SBD_1N8Yby2hQIJ1Ol2HoX98CwQJeGlB4wrxBWovBWWXeuFmmw0bTmMJE96rmgb403s3UrnsFTPicc7bAFAfAgy6ddDaQIEAhAfskZhUomc2NOMEsnIFQDlTRkPY0Mu9GMKpTWPPyiXfwrlK-Y2MZRg4ZyK8QD_r3LV5kVXsvRc3uYBkSBr9AgkVJR0CajN0Zh721R8");'></div>
    `;
    chatMessagesContainer?.appendChild(msgDiv);
    scrollToBottom();
}

// Add loading message
function addLoadingMessage() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex items-end gap-3';
    msgDiv.innerHTML = `
        <div class="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 shrink-0" 
             style='background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuBRuJrTvkl2INQTwGo91lodJKn3Ht2gD1Vt9kwBzj_2XCLp-7yaIjDeotE667P5aXx9bViXw2t1KJ9Vo3Wklf4oR-YYutjYF1qeW5aas0hHnPhjHnxSJo5fuTteGjrCV_c1slM9Dd9KqMQ38LU4G8BmPHVUlNjqNjESxub7rnDJsdNXxxgHGPDJfXpqOZnYFun9gEFataV49qrV8VcuoPO2BZdHv2UNEDLAmPTPhrHHCWTb0XvewoYDDgYH2jyTwcJ1PlEFC6BN0Gs");'></div>
        <div class="flex flex-1 flex-col gap-1 items-start">
            <div class="flex items-center gap-2">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse [animation-delay:0.2s]"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse [animation-delay:0.4s]"></div>
            </div>
        </div>
    `;
    chatMessagesContainer?.appendChild(msgDiv);
    scrollToBottom();
    return msgDiv;
}

// Add error message
function addErrorMessage(text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex justify-center';
    msgDiv.innerHTML = `
        <div class="bg-red-100 text-red-700 rounded-lg px-4 py-2 max-w-md">
            <p>❌ ${escapeHtml(text)}</p>
        </div>
    `;
    chatMessagesContainer?.appendChild(msgDiv);
    scrollToBottom();
}

// Update plan view
function updatePlanView(planData) {
    if (!planDisplay) {
        console.warn('Plan display element not found');
        return;
    }
    
    planDisplay.innerHTML = '';
    
    // Header
    const header = document.createElement('div');
    header.className = 'flex flex-col gap-2 border-b pb-3 mb-3';
    header.innerHTML = `
        <h3 class="text-xl font-bold text-gray-900 dark:text-white">📋 Kế hoạch của bạn</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">${planData.destination} - ${planData.duration_days} ngày</p>
    `;
    planDisplay.appendChild(header);
    
    // Budget summary
    if (planData.budget) {
        const budgetDiv = document.createElement('div');
        budgetDiv.className = 'bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-800 mb-3';
        budgetDiv.innerHTML = `
            <div class="flex items-center gap-2 mb-2">
                <span class="material-symbols-outlined text-blue-600 dark:text-blue-400">account_balance_wallet</span>
                <span class="font-semibold text-blue-900 dark:text-blue-100">Ngân sách</span>
            </div>
            <p class="text-2xl font-bold text-blue-700 dark:text-blue-300">${formatCurrency(planData.budget)}</p>
        `;
        planDisplay.appendChild(budgetDiv);
    }
    
    // Itinerary by day
    if (planData.itinerary && Array.isArray(planData.itinerary)) {
        planData.itinerary.forEach((day, index) => {
            const dayDiv = document.createElement('div');
            dayDiv.className = 'flex flex-col gap-2 mt-3';
            
            // Day header
            const dayHeader = document.createElement('div');
            dayHeader.className = 'flex items-center gap-2 bg-gray-100 dark:bg-gray-700 rounded-lg px-3 py-2';
            dayHeader.innerHTML = `
                <span class="material-symbols-outlined text-primary">calendar_today</span>
                <span class="font-bold text-gray-900 dark:text-white">Ngày ${day.day}</span>
            `;
            dayDiv.appendChild(dayHeader);
            
            // Activities
            if (day.activities && Array.isArray(day.activities)) {
                day.activities.forEach(activity => {
                    const activityDiv = document.createElement('div');
                    activityDiv.className = 'ml-6 pl-4 border-l-2 border-gray-200 dark:border-gray-600 py-2';
                    activityDiv.innerHTML = `
                        <div class="flex items-start gap-2">
                            <span class="material-symbols-outlined text-sm text-gray-500 mt-1">schedule</span>
                            <div class="flex-1">
                                <p class="font-semibold text-gray-900 dark:text-white">${activity.time || ''} - ${activity.title || activity.name}</p>
                                ${activity.description ? `<p class="text-sm text-gray-600 dark:text-gray-400 mt-1">${activity.description}</p>` : ''}
                                ${activity.cost ? `<p class="text-sm text-primary font-semibold mt-1">${formatCurrency(activity.cost)}</p>` : ''}
                            </div>
                        </div>
                    `;
                    dayDiv.appendChild(activityDiv);
                });
            }
            
            planDisplay.appendChild(dayDiv);
        });
    }
    
    // Save button
    const saveBtn = document.createElement('button');
    saveBtn.className = 'mt-4 w-full flex items-center justify-center gap-2 rounded-lg h-12 px-5 bg-primary text-white font-bold hover:bg-primary/90 transition-all';
    saveBtn.innerHTML = `
        <span class="material-symbols-outlined">bookmark</span>
        <span>Lưu kế hoạch</span>
    `;
    saveBtn.onclick = () => savePlan(planData);
    planDisplay.appendChild(saveBtn);
}

// Save plan
async function savePlan(planData) {
    // Validate plan data
    if (!planData || !planData.destination || !planData.itinerary) {
        addErrorMessage('Dữ liệu kế hoạch không hợp lệ');
        return;
    }
    
    // Show loading
    const saveBtn = event.target.closest('button');
    const originalContent = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = `
        <span class="material-symbols-outlined animate-spin">progress_activity</span>
        <span>Đang lưu...</span>
    `;
    
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
            // Show success message
            addBotMessage('✅ Đã lưu kế hoạch thành công! Đang chuyển đến trang kế hoạch...');
            
            // Show notification
            showNotification('success', 'Kế hoạch đã được lưu!', 'Bạn có thể xem lại trong mục "My Plans"');
            
            // Redirect after 1.5 seconds
            setTimeout(() => {
                window.location.href = '/plans';
            }, 1500);
        } else {
            saveBtn.disabled = false;
            saveBtn.innerHTML = originalContent;
            addErrorMessage(data.error || 'Không thể lưu kế hoạch');
            showNotification('error', 'Lỗi', data.error || 'Không thể lưu kế hoạch');
        }
    } catch (error) {
        console.error('Error:', error);
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalContent;
        addErrorMessage('Lỗi khi lưu kế hoạch');
        showNotification('error', 'Lỗi kết nối', 'Không thể kết nối đến server');
    }
}

// Utility functions
function scrollToBottom() {
    if (chatMessagesContainer) {
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatCurrency(amount) {
    if (!amount) return '0 ₫';
    return new Intl.NumberFormat('vi-VN', { 
        style: 'currency', 
        currency: 'VND',
        minimumFractionDigits: 0
    }).format(amount);
}

function showNotification(type, title, message) {
    // Create notification element
    const notif = document.createElement('div');
    const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';
    notif.className = `fixed top-4 right-4 ${bgColor} text-white rounded-lg shadow-lg p-4 max-w-sm z-50`;
    notif.innerHTML = `
        <div class="flex items-start gap-3">
            <span class="material-symbols-outlined">${type === 'success' ? 'check_circle' : 'error'}</span>
            <div class="flex-1">
                <p class="font-bold">${title}</p>
                <p class="text-sm mt-1">${message}</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="text-white/80 hover:text-white">
                <span class="material-symbols-outlined text-xl">close</span>
            </button>
        </div>
    `;
    document.body.appendChild(notif);
    
    // Auto remove after 5 seconds
    setTimeout(() => notif.remove(), 5000);
}
