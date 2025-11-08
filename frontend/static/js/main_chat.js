/**
 * Main chat interface logic for khappha.online
 * Handles real-time chat with AI and travel plan generation
 */

// State
let currentMode = 'plan'; // Default mode: plan, ask, edit_plan
let currentPlan = null; // Store current plan for edit mode
let currentConversationId = null; // Track current conversation ID
let chatSessions = []; // Store all chat sessions

// DOM Elements
let chatMessagesContainer = null;
let messageInput = null;
let sendButton = null;
let planDisplay = null;
let modeDropdown = null;
let modeOptions = [];

// Initialize DOM elements after page load
function initializeDOMElements() {
    chatMessagesContainer = document.getElementById('chatMessages');
    planDisplay = document.getElementById('planDisplay');
    messageInput = document.getElementById('messageInput');
    sendButton = document.getElementById('sendButton');
    modeDropdown = document.getElementById('modeDropdown');
    modeOptions = document.querySelectorAll('.mode-option');
    
    console.log('DOM Elements initialized:', {
        chatMessages: !!chatMessagesContainer,
        planDisplay: !!planDisplay,
        messageInput: !!messageInput,
        sendButton: !!sendButton,
        modeDropdown: !!modeDropdown,
        modeOptions: modeOptions.length
    });
}

// Initialize chat
window.addEventListener('DOMContentLoaded', () => {
    initializeDOMElements();
    loadChatSessions();
    addWelcomeMessage();
    attachEventListeners();
    initializeMarkdown();
    applyViewportHeightFix();
    
    // Request user's location
    requestUserLocation();
    
    // Check for auto-send message from URL parameter (from Discover page)
    checkAutoSendMessage();
});

// Initialize Markdown renderer
function initializeMarkdown() {
    if (typeof marked !== 'undefined') {
        // Configure marked options
        marked.setOptions({
            breaks: true,
            gfm: true,
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (err) {}
                }
                return code;
            }
        });
    }
}

// Handle dynamic viewport height for iOS Safari and PWAs
function applyViewportHeightFix() {
    const root = document.documentElement;
    if (!root) return;

    const setAppHeight = () => {
        const viewport = window.visualViewport;
        const height = viewport ? viewport.height : window.innerHeight;
        root.style.setProperty('--app-height', `${Math.round(height)}px`);
    };

    setAppHeight();

    const viewport = window.visualViewport;
    if (viewport) {
        viewport.addEventListener('resize', setAppHeight);
        viewport.addEventListener('scroll', setAppHeight);
    } else {
        window.addEventListener('resize', setAppHeight);
    }

    window.addEventListener('orientationchange', setAppHeight);
    window.addEventListener('pageshow', setAppHeight);
}

// Show/hide mode dropdown
function showModeDropdown() {
    if (modeDropdown) {
        modeDropdown.classList.remove('hidden');
    }
}

function hideModeDropdown() {
    if (modeDropdown) {
        modeDropdown.classList.add('hidden');
    }
}

// Handle @ input for mode selection
function handleAtSymbol() {
    if (!messageInput) return;
    
    const value = messageInput.value;
    const cursorPos = messageInput.selectionStart;
    
    // Check if @ is at cursor position
    if (value[cursorPos - 1] === '@') {
        showModeDropdown();
    } else if (!value.includes('@')) {
        hideModeDropdown();
    }
}

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
    
    // Input events
    if (messageInput) {
        // Enter key
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                hideModeDropdown();
                handleSendMessage();
            }
        });
        
        // @ symbol detection
        messageInput.addEventListener('input', handleAtSymbol);
        
        // Hide dropdown when focus lost
        messageInput.addEventListener('blur', () => {
            setTimeout(hideModeDropdown, 200); // Delay to allow click on dropdown
        });
    } else {
        console.error('Message input not found!');
    }
    
    // Mode option buttons
    modeOptions.forEach(option => {
        option.addEventListener('click', () => {
            const prefix = option.dataset.prefix;
            const mode = option.dataset.mode;
            
            if (messageInput) {
                const value = messageInput.value;
                // Replace @ with mode prefix
                const newValue = value.replace(/@\s*$/, prefix + ' ');
                messageInput.value = newValue;
                messageInput.focus();
                currentMode = mode;
            }
            
            hideModeDropdown();
        });
    });
    // Suggestion buttons
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');
    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (messageInput) {
                messageInput.value = btn.textContent.trim();
                handleSendMessage();
            }
        });
    });
    
    // New chat button
    const newChatBtn = document.getElementById('newChatBtn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', createNewChatSession);
    }
}

// Handle send message
async function handleSendMessage() {
    const message = messageInput?.value.trim();
    if (!message) return;
    
    // Send message as-is, let backend LLM decide the mode
    // No need to add @plan prefix automatically
    console.log(`Sending message:`, message);
    
    // Disable input and button
    if (messageInput) messageInput.disabled = true;
    if (sendButton) sendButton.disabled = true;
    
    // Add user message (show original message without prefix)
    addUserMessage(message);
    
    // Clear input
    if (messageInput) {
        messageInput.value = '';
    }
    
    // Hide dropdown if visible
    hideModeDropdown();
    
    // Show loading
    const loadingMsg = addLoadingMessage();
    
    try {
        // Prepare request data
        const requestData = { 
            message: message,  // Send original message, let LLM analyze intent
            conversation_session_id: currentConversationId  // Send current conversation session ID
        };
        
        // Include current plan if in edit mode
        if (currentMode === 'edit_plan' && currentPlan) {
            requestData.current_plan = currentPlan;
        }
        
        console.log('Request data:', requestData);
        
        // Send to API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        // Remove loading
        loadingMsg.remove();
        if (data.success) {
            // Add bot response
            addBotMessage(data.response);
            
            // Update conversation ID from response (if returned by server)
            if (data.conversation_session_id) {
                currentConversationId = data.conversation_session_id;
            }
            
            // If has plan, update plan view and store it
            if (data.has_plan && data.plan_data) {
                currentPlan = data.plan_data;  // Store for edit mode
                updatePlanView(data.plan_data);
            }
            
            // Update header buttons based on whether we have a plan
            updateHeaderButtons();
            
            // Update session list after sending message
            loadChatSessions();
            
            // Auto-save session title if this is the first message in a new session
            if (currentConversationId && chatMessagesContainer.children.length === 4) {
                // 4 children = welcome message (2) + user message (1) + bot message (1)
                autoSaveSessionTitle(currentConversationId, message);
            }
        } else {
            addErrorMessage(data.error || 'Không thể gửi tin nhắn');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        loadingMsg.remove();
        addErrorMessage('Lỗi kết nối. Vui lòng thử lại.');
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
    
    // Render markdown
    let renderedContent;
    if (typeof marked !== 'undefined') {
        renderedContent = marked.parse(text);
    } else {
        renderedContent = escapeHtml(text).replace(/\n/g, '<br>');
    }
    
    msgDiv.innerHTML = `
        <div class="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 shrink-0" 
             style='background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuASndgVA3RbX1H4yCbbqk8hsJujYw-P6pZI-uQr7cNE6Fya18CrfnQF3Q6u5lkHGOdbnxRhwJZDcIr3QYn2d9_fHpzc12fDYZTMAQJ7TptH7Pyu-rlqSErcQwCOM7T7182tN0XX_l_KuPUmWhBcT3Qsf6Y1drq5VInxput-tgaNfjrS50WHYfdtTuf2Ofxb432HdB0uwEupfdrgBaK8ptf5_sLoNoRi-VRHoMj3O_yZSs2pThNsHrNSU7onQN-hig4FR913Omzgito");'></div>
        <div class="flex flex-1 flex-col gap-1 items-start">
            <p class="text-xs text-gray-500">TravelBot</p>
            <div class="markdown-content text-base font-normal leading-normal max-w-[480px] rounded-xl px-4 py-3 bg-gray-100 dark:bg-gray-700">${renderedContent}</div>
        </div>
    `;
    
    // Highlight code blocks if hljs is available
    if (typeof hljs !== 'undefined') {
        msgDiv.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }
    
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
    setTimeout(() => {
        notif.remove();
    }, 5000);
}

// Load all chat sessions
async function loadChatSessions() {
    try {
        const response = await fetch('/api/chat-sessions');
        const data = await response.json();
        
        if (data.success && data.sessions) {
            chatSessions = data.sessions;
            renderChatSessions();
            
            // DON'T auto-load session on page load
            // Only load if explicitly requested by user
        }
    } catch (error) {
        console.error('Error loading chat sessions:', error);
    }
}

// Render chat sessions list
function renderChatSessions() {
    const sessionsList = document.getElementById('chatSessionsList');
    if (!sessionsList) return;
    
    sessionsList.innerHTML = '';
    
    if (chatSessions.length === 0) {
        sessionsList.innerHTML = `
            <div class="px-3 py-2 text-xs text-text-secondary-light dark:text-text-secondary-dark text-center">
                Chưa có cuộc hội thoại nào
            </div>
        `;
        return;
    }
    
    chatSessions.forEach(session => {
        const sessionDiv = document.createElement('div');
        const isActive = currentConversationId === session.id;
        sessionDiv.className = `group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer ${
            isActive 
                ? 'bg-primary/20 dark:bg-primary/30 text-primary' 
                : 'text-text-light dark:text-text-dark hover:bg-gray-100 dark:hover:bg-gray-700'
        }`;
        
        sessionDiv.innerHTML = `
            <span class="material-symbols-outlined text-sm">chat_bubble</span>
            <div class="flex-1 min-w-0">
                <p class="text-sm font-medium truncate">${escapeHtml(session.title || 'Chat mới')}</p>
                <p class="text-xs opacity-70 truncate">${formatSessionTime(session.last_message_at || session.created_at)}</p>
            </div>
            <button class="delete-session-btn opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-500/20" data-session-id="${session.id}" title="Xóa">
                <span class="material-symbols-outlined text-sm text-red-500">delete</span>
            </button>
        `;
        
        // Click to load session
        sessionDiv.addEventListener('click', (e) => {
            if (!e.target.closest('.delete-session-btn')) {
                loadChatSession(session.id);
            }
        });
        
        // Delete button
        const deleteBtn = sessionDiv.querySelector('.delete-session-btn');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteChatSession(session.id);
        });
        
        sessionsList.appendChild(sessionDiv);
    });
}

// Load specific chat session
async function loadChatSession(sessionId) {
    try {
        const response = await fetch(`/api/chat-sessions/${sessionId}/messages`);
        const data = await response.json();
        
        if (data.success && data.messages) {
            currentConversationId = sessionId;
            
            // Clear current messages
            if (chatMessagesContainer) {
                chatMessagesContainer.innerHTML = '';
            }
            
            // Clear current plan first
            currentPlan = null;
            
            // Add messages and track the latest plan
            let latestPlan = null;
            data.messages.forEach(msg => {
                addUserMessage(msg.user_message);
                addBotMessage(msg.bot_response);
                
                // Track the latest plan in this session
                if (msg.plan_id && msg.plan_data) {
                    latestPlan = msg.plan_data;
                }
            });
            
            // Display the latest plan if found
            if (latestPlan) {
                currentPlan = latestPlan;
                updatePlanView(latestPlan);
                updateHeaderButtons();  // Enable save/share/edit buttons
                console.log('✅ Loaded plan from session:', latestPlan.plan_name || latestPlan.destination);
            } else {
                // Clear plan display if no plan found
                if (planDisplay) {
                    planDisplay.innerHTML = `
                        <div class="text-center py-12">
                            <span class="material-symbols-outlined text-gray-300 dark:text-gray-600" style="font-size: 64px;">event_note</span>
                            <p class="text-gray-500 dark:text-gray-400 mt-4">Kế hoạch của bạn sẽ xuất hiện ở đây</p>
                            <p class="text-sm text-gray-400 dark:text-gray-500">Bắt đầu chat để tạo kế hoạch du lịch!</p>
                        </div>
                    `;
                }
                updateHeaderButtons();  // Disable save/share/edit buttons
            }
            
            // Update UI
            renderChatSessions();
        }
    } catch (error) {
        console.error('Error loading chat session:', error);
        addErrorMessage('Không thể tải lịch sử chat');
    }
}

// Create new chat session
async function createNewChatSession() {
    try {
        const response = await fetch('/api/chat-sessions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: 'Chat mới'
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.session) {
            // Clear current chat
            currentConversationId = data.session.id;
            currentPlan = null;
            
            if (chatMessagesContainer) {
                chatMessagesContainer.innerHTML = '';
            }
            
            if (planDisplay) {
                planDisplay.innerHTML = `
                    <div class="text-center py-12">
                        <span class="material-symbols-outlined text-gray-300 dark:text-gray-600" style="font-size: 64px;">event_note</span>
                        <p class="text-gray-500 dark:text-gray-400 mt-4">Kế hoạch của bạn sẽ xuất hiện ở đây</p>
                        <p class="text-sm text-gray-400 dark:text-gray-500">Bắt đầu chat để tạo kế hoạch du lịch!</p>
                    </div>
                `;
            }
            
            // Disable header buttons (no plan yet)
            updateHeaderButtons();
            
            // Reload sessions list
            await loadChatSessions();
            
            // Add welcome message
            addWelcomeMessage();
            
            showNotification('success', 'Chat mới', 'Đã tạo cuộc hội thoại mới');
        }
    } catch (error) {
        console.error('Error creating chat session:', error);
        addErrorMessage('Không thể tạo chat mới');
    }
}

// Delete chat session
async function deleteChatSession(sessionId) {
    if (!confirm('Bạn có chắc muốn xóa cuộc hội thoại này?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/chat-sessions/${sessionId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // If deleting current session, create new one
            if (currentConversationId === sessionId) {
                await createNewChatSession();
            } else {
                await loadChatSessions();
            }
            
            showNotification('success', 'Đã xóa', 'Cuộc hội thoại đã được xóa');
        }
    } catch (error) {
        console.error('Error deleting chat session:', error);
        addErrorMessage('Không thể xóa chat');
    }
}

// Auto-save session title based on first message
async function autoSaveSessionTitle(sessionId, firstMessage) {
    try {
        // Extract a short title from the message (first 50 chars)
        const title = firstMessage.substring(0, 50).trim() + (firstMessage.length > 50 ? '...' : '');
        
        await fetch(`/api/chat-sessions/${sessionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title })
        });
    } catch (error) {
        console.error('Error auto-saving session title:', error);
    }
}

// Format session time
function formatSessionTime(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Vừa xong';
    if (diffMins < 60) return `${diffMins} phút trước`;
    if (diffHours < 24) return `${diffHours} giờ trước`;
    if (diffDays < 7) return `${diffDays} ngày trước`;
    
    return date.toLocaleDateString('vi-VN');
}

// ===== HEADER BUTTONS (Save, Share, Edit) =====

// Save Plan button (in header)
const savePlanBtn = document.getElementById('savePlanBtn');
if (savePlanBtn) {
    savePlanBtn.addEventListener('click', async () => {
        if (!currentPlan) {
            showNotification('error', 'Lỗi', 'Chưa có kế hoạch để lưu');
            return;
        }
        
        // Show loading
        const originalContent = savePlanBtn.innerHTML;
        savePlanBtn.disabled = true;
        savePlanBtn.innerHTML = `
            <span class="material-symbols-outlined animate-spin">progress_activity</span>
            <span>Đang lưu...</span>
        `;
        
        try {
            // Create plan data with explicit status override
            const planToSave = {
                ...currentPlan,
                status: 'active'  // Mark as active when user explicitly saves
            };
            
            // Ensure status is 'active' (double-check)
            planToSave.status = 'active';
            
            console.log('💾 Saving plan with status:', planToSave.status);
            
            const response = await fetch('/api/save-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(planToSave)
            });
            
            const data = await response.json();
            
            if (data.success) {
                showNotification('success', 'Thành công', 'Kế hoạch đã được lưu!');
                
                // Update currentPlan with saved data
                if (data.plan_id) {
                    currentPlan.id = data.plan_id;
                }
                // Update status to active since we just saved it as active
                currentPlan.status = 'active';
                
                console.log('✅ Plan saved successfully, status updated to:', currentPlan.status);
                
                // Re-enable with checkmark
                savePlanBtn.innerHTML = `
                    <span class="material-symbols-outlined">check_circle</span>
                    <span>Đã lưu</span>
                `;
                
                // Reset after 2 seconds
                setTimeout(() => {
                    savePlanBtn.innerHTML = originalContent;
                    savePlanBtn.disabled = false;
                }, 2000);
            } else {
                savePlanBtn.disabled = false;
                savePlanBtn.innerHTML = originalContent;
                showNotification('error', 'Lỗi', data.error || 'Không thể lưu kế hoạch');
            }
        } catch (error) {
            console.error('Save plan error:', error);
            savePlanBtn.disabled = false;
            savePlanBtn.innerHTML = originalContent;
            showNotification('error', 'Lỗi', 'Không thể kết nối với server');
        }
    });
}

// Share Plan button (in header)
const sharePlanBtn = document.getElementById('sharePlanBtn');
if (sharePlanBtn) {
    sharePlanBtn.addEventListener('click', () => {
        if (!currentPlan) {
            showNotification('error', 'Lỗi', 'Chưa có kế hoạch để chia sẻ');
            return;
        }
        
        // Generate shareable link
        const shareUrl = window.location.origin + '/plans/' + (currentPlan.id || 'draft');
        
        // Copy to clipboard
        if (navigator.clipboard) {
            navigator.clipboard.writeText(shareUrl).then(() => {
                showNotification('success', 'Đã sao chép', 'Link chia sẻ đã được sao chép vào clipboard!');
            }).catch(err => {
                console.error('Failed to copy:', err);
                showNotification('info', 'Link chia sẻ', shareUrl);
            });
        } else {
            // Fallback for browsers that don't support clipboard API
            prompt('Sao chép link này để chia sẻ:', shareUrl);
        }
    });
}

// Edit Plan button (in header)
const editPlanBtn = document.getElementById('editPlanBtn');
if (editPlanBtn) {
    editPlanBtn.addEventListener('click', () => {
        if (!currentPlan) {
            showNotification('error', 'Lỗi', 'Chưa có kế hoạch để chỉnh sửa');
            return;
        }
        
        if (currentPlan.id) {
            // If plan has ID, redirect to edit page
            window.location.href = `/plans/${currentPlan.id}/edit`;
        } else {
            // If no ID, prompt user to use chat to edit
            showNotification('info', 'Mẹo', 'Bạn có thể sử dụng @edit_plan trong chat để chỉnh sửa kế hoạch!');
            
            // Focus on message input
            const messageInput = document.getElementById('messageInput');
            if (messageInput) {
                messageInput.focus();
                messageInput.value = '@edit_plan ';
            }
        }
    });
}

// Function to enable/disable header buttons based on plan availability
function updateHeaderButtons() {
    const hasPlan = currentPlan !== null;
    
    if (savePlanBtn) savePlanBtn.disabled = !hasPlan;
    if (sharePlanBtn) sharePlanBtn.disabled = !hasPlan;
    if (editPlanBtn) editPlanBtn.disabled = !hasPlan;
}

// Request user's geolocation
function requestUserLocation() {
    // Check if geolocation is supported
    if (!navigator.geolocation) {
        console.log('❌ Geolocation is not supported by this browser');
        return;
    }
    
    // Request permission and get location
    navigator.geolocation.getCurrentPosition(
        // Success callback
        function(position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            const accuracy = position.coords.accuracy;
            
            console.log('📍 Location obtained:', {
                latitude,
                longitude,
                accuracy: accuracy + 'm'
            });
            
            // Send to server
            saveUserLocation(latitude, longitude);
        },
        // Error callback
        function(error) {
            console.log('⚠️ Location request denied or failed:', error.message);
            
            // Show friendly notification (optional)
            const errorMessages = {
                1: 'Bạn đã từ chối chia sẻ vị trí',
                2: 'Không thể xác định vị trí',
                3: 'Yêu cầu vị trí hết thời gian'
            };
            
            const message = errorMessages[error.code] || 'Không thể lấy vị trí';
            console.log('ℹ️', message);
        },
        // Options
        {
            enableHighAccuracy: true,  // Request best accuracy
            timeout: 10000,            // 10 second timeout
            maximumAge: 300000         // Accept cached position up to 5 minutes old
        }
    );
}

// Save user location to server
async function saveUserLocation(latitude, longitude) {
    try {
        const response = await fetch('/api/user/location', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                latitude,
                longitude
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ Location saved to server');
        } else {
            console.error('❌ Failed to save location:', data.error);
        }
    } catch (error) {
        console.error('❌ Error saving location:', error);
    }
}

// Check for auto-send message from URL parameter (from Discover page)
function checkAutoSendMessage() {
    const urlParams = new URLSearchParams(window.location.search);
    const autoMessage = urlParams.get('message');
    
    if (autoMessage && messageInput) {
        // Decode and set message
        messageInput.value = decodeURIComponent(autoMessage);
        
        // Show notification
        if (typeof showNotification === 'function') {
            showNotification('Đã tự động điền tin nhắn từ Discovery! 🗺️', 'info');
        }
        
        // Auto-send after a short delay (allow user to see the message first)
        setTimeout(() => {
            if (messageInput && messageInput.value.trim()) {
                handleSendMessage();
            }
        }, 500);
        
        // Clean URL (remove query parameter)
        const cleanUrl = window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
    }
}

