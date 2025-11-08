/**
 * Edit Plan Page Logic for khappha.online
 * Handles editing travel plan information with real functionality
 */

let currentPlan = null;
let planId = null;
let hasUnsavedChanges = false;

// Get plan ID from URL
function getPlanIdFromUrl() {
    const path = window.location.pathname;
    const match = path.match(/\/plans\/(\d+)\/edit/);
    return match ? parseInt(match[1]) : null;
}

// Load plan on page load
window.addEventListener('DOMContentLoaded', () => {
    planId = getPlanIdFromUrl();
    if (planId) {
        loadPlanData(planId);
    } else {
        showError('Không tìm thấy ID kế hoạch');
    }
    
    // Warn before leaving if there are unsaved changes
    window.addEventListener('beforeunload', (e) => {
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
});

// Load plan data from API
async function loadPlanData(id) {
    try {
        showLoading();
        const response = await fetch(`/api/plans/${id}`);
        const data = await response.json();
        
        if (data.success && data.plan) {
            currentPlan = data.plan;
            renderPlanData(currentPlan);
        } else {
            showError(data.error || 'Không tìm thấy kế hoạch');
        }
    } catch (error) {
        console.error('Error loading plan:', error);
        showError('Không thể tải dữ liệu kế hoạch');
    }
}

// Render plan data
function renderPlanData(plan) {
    hideLoading();
    
    // Update sidebar
    renderSidebar(plan);
    
    // Update budget section (editable)
    renderBudgetSection(plan);
    
    // Update cost breakdown (editable)
    renderCostBreakdown(plan);
    
    hasUnsavedChanges = false;
}

// Render sidebar
function renderSidebar(plan) {
    // Update avatar
    const avatar = document.getElementById('plan-avatar');
    if (avatar) {
        avatar.style.backgroundImage = `url("${getDestinationImage(plan.destination)}")`;
    }
    
    // Update title (editable)
    const title = document.getElementById('plan-title');
    if (title) {
        title.contentEditable = 'true';
        title.textContent = plan.plan_name || `Khám phá ${plan.destination}`;
        title.addEventListener('blur', () => {
            hasUnsavedChanges = true;
        });
    }
    
    // Update dates
    const dates = document.getElementById('plan-dates');
    if (dates) {
        if (plan.start_date && plan.end_date) {
            dates.innerHTML = `
                <input type="date" 
                       id="start-date-input" 
                       value="${formatDateForInput(plan.start_date)}"
                       class="bg-transparent text-[#617c89] dark:text-gray-400 text-sm border-none outline-none w-auto"
                       onchange="hasUnsavedChanges = true" />
                <span class="text-[#617c89] dark:text-gray-400"> - </span>
                <input type="date" 
                       id="end-date-input" 
                       value="${formatDateForInput(plan.end_date)}"
                       class="bg-transparent text-[#617c89] dark:text-gray-400 text-sm border-none outline-none w-auto"
                       onchange="hasUnsavedChanges = true" />
            `;
        } else {
            dates.textContent = `${plan.duration_days} Ngày`;
        }
    }
    
    // Render timeline
    renderTimeline(plan);
}

// Render timeline in sidebar (editable)
function renderTimeline(plan) {
    const timelineContainer = document.getElementById('timeline-sidebar');
    if (!timelineContainer) return;
    
    const itinerary = Array.isArray(plan.itinerary) ? plan.itinerary : 
                     (typeof plan.itinerary === 'string' ? JSON.parse(plan.itinerary) : []);
    
    if (!itinerary || itinerary.length === 0) {
        timelineContainer.innerHTML = '<p class="text-sm text-gray-500">Không có lịch trình</p>';
        return;
    }
    
    let html = '<div class="absolute left-2.5 top-2 bottom-2 w-0.5 bg-gray-200 dark:bg-gray-700"></div>';
    itinerary.forEach((day, index) => {
        const isLast = index === itinerary.length - 1;
        const dayNum = day.day || index + 1;
        const title = day.title || `Ngày ${dayNum}`;
        const firstActivity = day.activities && day.activities.length > 0 ? 
                             day.activities[0].title || day.activities[0].name : '';
        
        html += `
            <div class="relative ${isLast ? '' : 'mb-4'}" data-day="${dayNum}">
                <div class="absolute -left-[1.1rem] top-2 size-4 ${index === 0 ? 'bg-primary' : 'bg-gray-300 dark:bg-gray-600'} rounded-full border-4 border-white dark:border-background-dark"></div>
                <p class="font-bold text-[#111618] dark:text-white text-sm cursor-pointer hover:text-primary" onclick="editDayTitle(${dayNum}, '${title}')">${title}</p>
                ${firstActivity ? `<p class="text-xs text-[#617c89] dark:text-gray-400">${firstActivity}</p>` : ''}
            </div>
        `;
    });
    
    timelineContainer.innerHTML = html;
}

// Edit day title
function editDayTitle(dayNum, currentTitle) {
    showModal({
        title: 'Chỉnh sửa tên ngày',
        content: `
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Tên ngày ${dayNum}
                    </label>
                    <input type="text" 
                           id="modal-day-title-input"
                           value="${currentTitle}"
                           class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                           placeholder="Nhập tên ngày">
                </div>
            </div>
        `,
        onConfirm: () => {
            const input = document.getElementById('modal-day-title-input');
            if (input && input.value && input.value !== currentTitle) {
                const itinerary = Array.isArray(currentPlan.itinerary) ? currentPlan.itinerary : 
                                 (typeof currentPlan.itinerary === 'string' ? JSON.parse(currentPlan.itinerary) : []);
                
                const dayIndex = itinerary.findIndex(d => (d.day || itinerary.indexOf(d) + 1) === dayNum);
                if (dayIndex !== -1) {
                    itinerary[dayIndex].title = input.value;
                    currentPlan.itinerary = itinerary;
                    renderTimeline(currentPlan);
                    hasUnsavedChanges = true;
                }
            }
        }
    });
}

// Render budget section (editable)
function renderBudgetSection(plan) {
    const budget = plan.budget || 0;
    const totalCost = calculateTotalCost(plan);
    const percentage = budget > 0 ? Math.min((totalCost / budget) * 100, 100) : 0;
    
    // Budget input
    const budgetContainer = document.getElementById('budget-section');
    if (budgetContainer) {
        budgetContainer.innerHTML = `
            <h2 class="text-lg font-bold text-[#111618] dark:text-white mb-4">Ngân sách</h2>
            <div class="@container">
                <div class="relative flex w-full flex-col items-start justify-between gap-3 @[480px]:flex-row @[480px]:items-center">
                    <div class="flex w-full shrink-[3] items-center justify-between">
                        <p class="text-[#111618] dark:text-white text-base font-medium leading-normal">Tổng ngân sách</p>
                        <button onclick="openBudgetModal()" class="@[480px]:hidden px-4 py-2 bg-primary text-white rounded-lg text-sm hover:bg-primary/90">
                            ${formatCurrency(budget)}
                        </button>
                    </div>
                    <div class="flex h-4 w-full items-center gap-4">
                        <div class="flex h-2 flex-1 rounded-sm bg-[#dbe2e6] dark:bg-gray-700 relative cursor-pointer" onclick="openBudgetModal()">
                            <div class="h-full rounded-sm bg-primary transition-all duration-300" id="budget-progress" style="width: ${percentage}%"></div>
                            <div class="absolute top-1/2 -translate-y-1/2 transition-all duration-300" id="budget-slider" style="left: ${percentage}%">
                                <div class="size-5 rounded-full bg-primary ring-4 ring-primary/30 -ml-2.5 cursor-grab active:cursor-grabbing"></div>
                            </div>
                        </div>
                        <button onclick="openBudgetModal()" class="hidden @[480px]:flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90">
                            ${formatCurrency(budget)}
                        </button>
                    </div>
                </div>
                <div class="mt-4 flex justify-between text-sm">
                    <span class="text-gray-600 dark:text-gray-400">Chi phí thực tế: <strong>${formatCurrency(totalCost)}</strong></span>
                    <span class="${totalCost > budget ? 'text-red-600' : 'text-green-600'} font-semibold">
                        ${totalCost > budget ? 'Vượt ' : 'Còn lại '}${formatCurrency(Math.abs(budget - totalCost))}
                    </span>
                </div>
            </div>
        `;
        
        // Add slider functionality
        setupBudgetSlider();
    }
}

// Setup budget slider
function setupBudgetSlider() {
    const progressBar = document.querySelector('#budget-section .bg-\\[\\#dbe2e6\\]');
    const slider = document.getElementById('budget-slider');
    
    if (!progressBar || !slider) return;
    
    let isDragging = false;
    
    const updateBudgetFromSlider = (clientX) => {
        const rect = progressBar.getBoundingClientRect();
        const offsetX = clientX - rect.left;
        const percentage = Math.max(0, Math.min(100, (offsetX / rect.width) * 100));
        
        const totalCost = calculateTotalCost(currentPlan);
        const maxBudget = totalCost * 3 || 10000000; // Max 3x chi phí hoặc 10 triệu
        const newBudget = Math.round((percentage / 100) * maxBudget / 100000) * 100000; // Làm tròn 100k
        
        updateBudget(newBudget);
    };
    
    slider.addEventListener('mousedown', (e) => {
        isDragging = true;
        e.preventDefault();
    });
    
    progressBar.addEventListener('click', (e) => {
        if (!isDragging) {
            updateBudgetFromSlider(e.clientX);
        }
    });
    
    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            updateBudgetFromSlider(e.clientX);
        }
    });
    
    document.addEventListener('mouseup', () => {
        isDragging = false;
    });
}

// Update budget
function updateBudget(newBudget) {
    const budget = parseInt(newBudget) || 0;
    currentPlan.budget = budget;
    
    // Update progress bar
    const totalCost = calculateTotalCost(currentPlan);
    const percentage = budget > 0 ? Math.min((totalCost / budget) * 100, 100) : 0;
    const progress = document.getElementById('budget-progress');
    const slider = document.getElementById('budget-slider');
    
    if (progress) {
        progress.style.width = `${percentage}%`;
    }
    if (slider) {
        slider.style.left = `${percentage}%`;
    }
    
    hasUnsavedChanges = true;
    renderBudgetSection(currentPlan);
}

// Open budget modal
function openBudgetModal() {
    const currentBudget = currentPlan.budget || 0;
    showModal({
        title: 'Chỉnh sửa ngân sách',
        content: `
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Tổng ngân sách (VNĐ)
                    </label>
                    <input type="number" 
                           id="modal-budget-input"
                           value="${currentBudget}"
                           class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                           placeholder="Nhập số tiền">
                </div>
                <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                        Chi phí hiện tại: <strong>${formatCurrency(calculateTotalCost(currentPlan))}</strong>
                    </p>
                </div>
            </div>
        `,
        onConfirm: () => {
            const input = document.getElementById('modal-budget-input');
            if (input) {
                updateBudget(input.value);
            }
        }
    });
}

// Calculate total cost from itinerary
function calculateTotalCost(plan) {
    const itinerary = Array.isArray(plan.itinerary) ? plan.itinerary : 
                     (typeof plan.itinerary === 'string' ? JSON.parse(plan.itinerary) : []);
    
    let total = 0;
    itinerary.forEach(day => {
        const activities = day.activities || [];
        activities.forEach(activity => {
            total += (activity.cost || 0);
        });
    });
    
    return total;
}

// Render cost breakdown (editable)
function renderCostBreakdown(plan) {
    const breakdown = document.getElementById('cost-breakdown');
    if (!breakdown) return;
    
    const itinerary = Array.isArray(plan.itinerary) ? plan.itinerary : 
                     (typeof plan.itinerary === 'string' ? JSON.parse(plan.itinerary) : []);
    
    if (!itinerary || itinerary.length === 0) {
        breakdown.innerHTML = '<p class="text-sm text-gray-500 text-center py-4">Chưa có dữ liệu chi phí</p>';
        return;
    }
    
    let html = '<div class="space-y-3">';
    let grandTotal = 0;
    
    // Render each day's activities
    itinerary.forEach((day, dayIndex) => {
        const dayNum = day.day || dayIndex + 1;
        const activities = day.activities || [];
        
        if (activities.length > 0) {
            html += `
                <div class="border-b border-gray-200 dark:border-gray-700 pb-3">
                    <h3 class="font-bold text-[#111618] dark:text-white mb-2">Ngày ${dayNum}: ${day.title || ''}</h3>
            `;
            
            activities.forEach((activity, actIndex) => {
                const cost = activity.cost || 0;
                grandTotal += cost;
                const icon = getActivityIcon(activity);
                
                html += `
                    <div class="flex items-center gap-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg px-2">
                        <div class="text-primary flex items-center justify-center rounded-lg bg-primary/10 shrink-0 size-10">
                            <span class="material-symbols-outlined text-xl">${icon}</span>
                        </div>
                        <div class="flex-1">
                            <input type="text" 
                                   value="${activity.title || activity.name || ''}"
                                   onchange="updateActivityTitle(${dayIndex}, ${actIndex}, this.value)"
                                   class="text-[#111618] dark:text-white text-sm font-medium bg-transparent border-none outline-none w-full" />
                            <p class="text-[#617c89] dark:text-gray-400 text-xs">${activity.time || ''}</p>
                        </div>
                        <div class="flex items-center gap-2">
                            <input type="number" 
                                   value="${cost}"
                                   onchange="updateActivityCost(${dayIndex}, ${actIndex}, this.value)"
                                   class="text-[#111618] dark:text-white text-sm font-medium bg-transparent border-b border-gray-300 dark:border-gray-600 focus:border-primary outline-none w-28 text-right" />
                            <span class="text-[#111618] dark:text-white text-sm">VNĐ</span>
                            <button onclick="deleteActivity(${dayIndex}, ${actIndex})" 
                                    class="text-red-500 hover:text-red-700 p-1" 
                                    title="Xóa hoạt động">
                                <span class="material-symbols-outlined text-lg">delete</span>
                            </button>
                        </div>
                    </div>
                `;
            });
            
            html += `
                    <button onclick="addActivity(${dayIndex})" 
                            class="mt-2 text-primary hover:text-primary/80 text-sm flex items-center gap-1">
                        <span class="material-symbols-outlined text-lg">add_circle</span>
                        Thêm hoạt động
                    </button>
                </div>
            `;
        }
    });
    
    html += '</div>';
    
    // Add total
    html += `
        <div class="mt-4 pt-4 border-t-2 border-gray-300 dark:border-gray-600">
            <div class="flex justify-between items-center">
                <p class="text-lg font-bold text-[#111618] dark:text-white">Tổng chi phí</p>
                <p class="text-xl font-bold text-primary">${formatCurrency(grandTotal)}</p>
            </div>
        </div>
    `;
    
    breakdown.innerHTML = html;
}

// Update activity title
function updateActivityTitle(dayIndex, activityIndex, newTitle) {
    const itinerary = Array.isArray(currentPlan.itinerary) ? currentPlan.itinerary : 
                     (typeof currentPlan.itinerary === 'string' ? JSON.parse(currentPlan.itinerary) : []);
    
    if (itinerary[dayIndex] && itinerary[dayIndex].activities[activityIndex]) {
        itinerary[dayIndex].activities[activityIndex].title = newTitle;
        currentPlan.itinerary = itinerary;
        hasUnsavedChanges = true;
    }
}

// Update activity cost
function updateActivityCost(dayIndex, activityIndex, newCost) {
    const itinerary = Array.isArray(currentPlan.itinerary) ? currentPlan.itinerary : 
                     (typeof currentPlan.itinerary === 'string' ? JSON.parse(currentPlan.itinerary) : []);
    
    if (itinerary[dayIndex] && itinerary[dayIndex].activities[activityIndex]) {
        itinerary[dayIndex].activities[activityIndex].cost = parseInt(newCost) || 0;
        currentPlan.itinerary = itinerary;
        hasUnsavedChanges = true;
        
        // Re-render to update totals
        renderBudgetSection(currentPlan);
        renderCostBreakdown(currentPlan);
    }
}

// Add activity
function addActivity(dayIndex) {
    showModal({
        title: 'Thêm hoạt động mới',
        content: `
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Tên hoạt động <span class="text-red-500">*</span>
                    </label>
                    <input type="text" 
                           id="modal-activity-title"
                           class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                           placeholder="Ví dụ: Tham quan Hồ Xuân Hương">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Thời gian
                    </label>
                    <input type="text" 
                           id="modal-activity-time"
                           class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                           placeholder="Ví dụ: 9:00 - 12:00">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Chi phí (VNĐ)
                    </label>
                    <input type="number" 
                           id="modal-activity-cost"
                           value="0"
                           class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                           placeholder="0">
                </div>
            </div>
        `,
        onConfirm: () => {
            const title = document.getElementById('modal-activity-title')?.value;
            const time = document.getElementById('modal-activity-time')?.value || '';
            const cost = document.getElementById('modal-activity-cost')?.value || '0';
            
            if (!title) {
                showNotification('Vui lòng nhập tên hoạt động', 'error');
                return false;
            }
            
            const itinerary = Array.isArray(currentPlan.itinerary) ? currentPlan.itinerary : 
                             (typeof currentPlan.itinerary === 'string' ? JSON.parse(currentPlan.itinerary) : []);
            
            if (itinerary[dayIndex]) {
                if (!itinerary[dayIndex].activities) {
                    itinerary[dayIndex].activities = [];
                }
                
                itinerary[dayIndex].activities.push({
                    title: title,
                    cost: parseInt(cost) || 0,
                    time: time,
                    description: ''
                });
                
                currentPlan.itinerary = itinerary;
                hasUnsavedChanges = true;
                
                // Re-render
                renderBudgetSection(currentPlan);
                renderCostBreakdown(currentPlan);
            }
            
            return true;
        }
    });
}

// Get activity icon
function getActivityIcon(activity) {
    const title = (activity.title || activity.name || '').toLowerCase();
    
    if (title.includes('ăn') || title.includes('nhà hàng') || title.includes('quán')) return 'restaurant';
    if (title.includes('khách sạn') || title.includes('check')) return 'hotel';
    if (title.includes('bãi biển') || title.includes('biển')) return 'beach_access';
    if (title.includes('chùa') || title.includes('đền')) return 'temple_buddhist';
    if (title.includes('bảo tàng')) return 'museum';
    if (title.includes('mua sắm')) return 'shopping_bag';
    if (title.includes('cà phê')) return 'local_cafe';
    if (title.includes('bay') || title.includes('taxi') || title.includes('xe')) return 'flight';
    
    return 'place';
}

// Save changes
async function saveChanges() {
    if (!currentPlan || !planId) {
        showNotification('Không tìm thấy thông tin kế hoạch', 'error');
        return;
    }
    
    try {
        showLoading('Đang lưu thay đổi...');
        
        // Get updated data
        const planName = document.getElementById('plan-title')?.textContent || currentPlan.plan_name;
        const startDate = document.getElementById('start-date-input')?.value || currentPlan.start_date;
        const endDate = document.getElementById('end-date-input')?.value || currentPlan.end_date;
        
        const updatedPlan = {
            plan_name: planName,
            start_date: startDate,
            end_date: endDate,
            budget: currentPlan.budget,
            itinerary: currentPlan.itinerary
        };
        
        const response = await fetch(`/api/plans/${planId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedPlan)
        });
        
        const data = await response.json();
        
        if (data.success) {
            hasUnsavedChanges = false;
            hideLoading();
            showNotification('Đã lưu thay đổi thành công!', 'success');
            
            setTimeout(() => {
                window.location.href = `/plans/${planId}`;
            }, 1500);
        } else {
            hideLoading();
            showNotification(data.error || 'Không thể lưu thay đổi', 'error');
        }
    } catch (error) {
        console.error('Error saving changes:', error);
        hideLoading();
        showNotification('Không thể lưu thay đổi', 'error');
    }
}

// Button handlers
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('cancelBtn')?.addEventListener('click', () => {
        if (hasUnsavedChanges && !confirm('Bạn có thay đổi chưa lưu. Bạn có chắc muốn hủy?')) {
            return;
        }
        
        if (planId) {
            window.location.href = `/plans/${planId}`;
        } else {
            window.location.href = '/plans';
        }
    });

    document.getElementById('downloadPdfBtn')?.addEventListener('click', () => {
        showNotification('Tính năng tải PDF sẽ được cập nhật sớm!', 'info');
    });

    document.getElementById('saveChangesBtn')?.addEventListener('click', saveChanges);
});

// Utility functions
function formatCurrency(amount) {
    if (!amount) return '0 VNĐ';
    return new Intl.NumberFormat('vi-VN').format(amount) + ' VNĐ';
}

function formatDateForInput(dateStr) {
    if (!dateStr) return '';
    
    // If already in YYYY-MM-DD format
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
        return dateStr;
    }
    
    // If in DD/MM/YYYY format
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateStr)) {
        const [day, month, year] = dateStr.split('/');
        return `${year}-${month}-${day}`;
    }
    
    // Try to parse as Date
    try {
        const date = new Date(dateStr);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    } catch (error) {
        return '';
    }
}

function getDestinationImage(destination) {
    const images = {
        'Đà Lạt': 'https://lh3.googleusercontent.com/aida-public/AB6AXuBl4yfGCvMNncCqvEmgITcJeF7fh2BDC4gN06d2CnWngdCY1bkqXMsGRXfxWKYz1-aQErPpR9owyY4qXIfQVemgGDRKAFvziyWh7G6913ayP-zYXamHW3uNBmFCr_o_qT_jvGsDwpFjYnGopf-8-CwtI8N_IdDTuu4AwZ6A14h_zChPUwv47EK5N-7cIT3u3HPew7uiUex6BqTDvM6eps_E3oLo1YM79zuRQ_9VwPA4ok3UDw1v6MynDPZ5zKM2CKdxFC-BBAkPDjw',
        'Hà Nội': 'https://images.unsplash.com/photo-1509023464722-18d996393ca8',
        'Hồ Chí Minh': 'https://images.unsplash.com/photo-1583417319070-4a69db38a482'
    };
    return images[destination] || 'https://lh3.googleusercontent.com/aida-public/AB6AXuBl4yfGCvMNncCqvEmgITcJeF7fh2BDC4gN06d2CnWngdCY1bkqXMsGRXfxWKYz1-aQErPpR9owyY4qXIfQVemgGDRKAFvziyWh7G6913ayP-zYXamHW3uNBmFCr_o_qT_jvGsDwpFjYnGopf-8-CwtI8N_IdDTuu4AwZ6A14h_zChPUwv47EK5N-7cIT3u3HPew7uiUex6BqTDvM6eps_E3oLo1YM79zuRQ_9VwPA4ok3UDw1v6MynDPZ5zKM2CKdxFC-BBAkPDjw';
}

function showError(message) {
    const mainContent = document.querySelector('main .layout-content-container');
    if (mainContent) {
        mainContent.innerHTML = `
            <div class="flex flex-col items-center justify-center min-h-[400px] gap-4">
                <span class="material-symbols-outlined text-8xl text-red-500">error</span>
                <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Lỗi</h2>
                <p class="text-gray-600 dark:text-gray-400">${message}</p>
                <a href="/plans" class="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90">
                    <span class="material-symbols-outlined">arrow_back</span>
                    <span>Quay lại danh sách</span>
                </a>
            </div>
        `;
    }
}

// Show modal
function showModal({ title, content, onConfirm, confirmText = 'Xác nhận', cancelText = 'Hủy' }) {
    // Remove existing modal if any
    const existingModal = document.getElementById('custom-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.id = 'custom-modal';
    modal.className = 'fixed inset-0 bg-black/50 z-[9999] flex items-center justify-center p-4 animate-fadeIn';
    modal.innerHTML = `
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full animate-slideUp">
            <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h3 class="text-xl font-bold text-gray-900 dark:text-white">${title}</h3>
            </div>
            <div class="px-6 py-4">
                ${content}
            </div>
            <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
                <button id="modal-cancel-btn" class="px-6 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium">
                    ${cancelText}
                </button>
                <button id="modal-confirm-btn" class="px-6 py-2.5 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors font-medium">
                    ${confirmText}
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .animate-fadeIn { animation: fadeIn 0.2s ease-out; }
        .animate-slideUp { animation: slideUp 0.3s ease-out; }
    `;
    document.head.appendChild(style);
    
    // Auto-focus first input
    setTimeout(() => {
        const firstInput = modal.querySelector('input, textarea');
        if (firstInput) {
            firstInput.focus();
        }
    }, 100);
    
    // Handle cancel
    const closeModal = () => {
        modal.style.opacity = '0';
        setTimeout(() => modal.remove(), 200);
    };
    
    document.getElementById('modal-cancel-btn').addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Handle confirm
    document.getElementById('modal-confirm-btn').addEventListener('click', () => {
        if (onConfirm) {
            const shouldClose = onConfirm();
            if (shouldClose !== false) {
                closeModal();
            }
        } else {
            closeModal();
        }
    });
    
    // Handle Enter key
    modal.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            document.getElementById('modal-confirm-btn').click();
        } else if (e.key === 'Escape') {
            closeModal();
        }
    });
}

function showNotification(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500'
    };
    
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-[9999] transition-opacity duration-300 ${colors[type]} text-white`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showLoading(message = 'Đang tải...') {
    let loader = document.getElementById('global-loader');
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.className = 'fixed inset-0 bg-black/50 z-[9998] flex items-center justify-center';
        loader.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-xl p-6 flex flex-col items-center gap-3">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                <p class="text-gray-700 dark:text-gray-300">${message}</p>
            </div>
        `;
        document.body.appendChild(loader);
    }
}

function hideLoading() {
    const loader = document.getElementById('global-loader');
    if (loader) {
        loader.remove();
    }
}

function showError(message) {
    const mainContent = document.querySelector('main .layout-content-container');
    if (mainContent) {
        mainContent.innerHTML = `
            <div class="flex flex-col items-center justify-center min-h-[400px] gap-4">
                <span class="material-symbols-outlined text-8xl text-red-500">error</span>
                <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Lỗi</h2>
                <p class="text-gray-600 dark:text-gray-400">${message}</p>
                <a href="/plans" class="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90">
                    <span class="material-symbols-outlined">arrow_back</span>
                    <span>Quay lại danh sách</span>
                </a>
            </div>
        `;
    }
}
