/**
 * Plans list page logic for khappha.online
 */

const plansGrid = document.querySelector('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3');
const emptyState = document.querySelector('.hidden.flex-col.items-center');
const searchInput = document.querySelector('input[placeholder*="Tìm"]');
const filterButtons = document.querySelectorAll('button:has(.material-symbols-outlined:contains("expand_more"))');
const createPlanButton = document.querySelector('a[href="/chat"]');
let allPlans = [];
let currentFilter = 'all'; // 'all', 'upcoming', 'completed'

// Load plans on page load
window.addEventListener('DOMContentLoaded', () => {
    loadPlans();
    initializeFilters();
});

// Search functionality
if (searchInput) {
    searchInput.addEventListener('input', handleSearch);
}

// Initialize filter buttons
function initializeFilters() {
    if (!filterButtons || filterButtons.length === 0) return;
    
    filterButtons.forEach((btn, index) => {
        btn.addEventListener('click', () => {
            const filters = ['upcoming', 'completed', 'all'];
            currentFilter = filters[index];
            filterPlans();
        });
    });
}

// Load plans from API
async function loadPlans() {
    try {
        const response = await fetch('/api/plans?limit=50');
        const data = await response.json();
        
        if (data.success && data.plans.length > 0) {
            allPlans = data.plans;
            renderPlans(allPlans);
            hideEmptyState();
        } else {
            showEmptyState();
        }
    } catch (error) {
        console.error('Error loading plans:', error);
        showEmptyState();
    }
}

// Render plans
function renderPlans(plans) {
    if (!plansGrid) return;
    
    plansGrid.innerHTML = '';
    
    plans.forEach(plan => {
        const planCard = createPlanCard(plan);
        plansGrid.appendChild(planCard);
    });
}

// Create plan card
function createPlanCard(plan) {
    const card = document.createElement('div');
    card.className = 'p-0 @container';
    
    const itinerary = typeof plan.itinerary === 'string' ? JSON.parse(plan.itinerary) : plan.itinerary;
    const imageUrl = getDestinationImage(plan.destination);
    const dateRange = formatDateRange(plan.created_at, plan.duration_days);
    
    card.innerHTML = `
        <div class="flex flex-col items-stretch justify-start rounded-xl shadow-[0_4px_12px_rgba(0,0,0,0.05)] bg-white dark:bg-gray-800 transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
            <div class="w-full bg-center bg-no-repeat aspect-video bg-cover rounded-t-xl" 
                 style='background-image: url("${imageUrl}");'></div>
            <div class="flex w-full grow flex-col items-stretch justify-center gap-2 p-4">
                <p class="text-[#111618] dark:text-white text-lg font-bold leading-tight tracking-[-0.015em]">
                    ${plan.plan_name || 'Khám phá ' + plan.destination}
                </p>
                <div class="flex flex-col gap-1 text-[#617c89] dark:text-gray-400 text-sm">
                    <p>${dateRange} (${plan.duration_days} ngày)</p>
                    <p>${plan.destination}, Việt Nam</p>
                </div>
                <div class="flex items-center justify-between mt-2">
                    <button onclick="viewPlan(${plan.id})" 
                            class="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-9 px-4 bg-primary text-white text-sm font-medium">
                        <span class="truncate">Xem chi tiết</span>
                    </button>
                    <button onclick="showMenu(${plan.id})" 
                            class="flex items-center justify-center size-9 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 text-[#617c89] dark:text-gray-400">
                        <span class="material-symbols-outlined">more_vert</span>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

// View plan
function viewPlan(planId) {
    window.location.href = `/plans/${planId}`;
}

// Show menu
function showMenu(planId) {
    // Create context menu
    const existingMenu = document.querySelector('.context-menu');
    if (existingMenu) existingMenu.remove();
    
    const menu = document.createElement('div');
    menu.className = 'context-menu fixed bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50 py-2';
    menu.style.minWidth = '200px';
    menu.innerHTML = `
        <button onclick="viewPlan(${planId}); this.parentElement.remove();" 
                class="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-3">
            <span class="material-symbols-outlined text-blue-600">visibility</span>
            <span>Xem chi tiết</span>
        </button>
        <button onclick="editPlan(${planId}); this.parentElement.remove();" 
                class="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-3">
            <span class="material-symbols-outlined text-green-600">edit</span>
            <span>Chỉnh sửa</span>
        </button>
        <hr class="my-1 border-gray-200 dark:border-gray-700">
        <button onclick="deletePlan(${planId}); this.parentElement.remove();" 
                class="w-full px-4 py-2 text-left hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center gap-3 text-red-600">
            <span class="material-symbols-outlined">delete</span>
            <span>Xóa kế hoạch</span>
        </button>
    `;
    
    // Position menu at cursor
    const rect = event.target.closest('button').getBoundingClientRect();
    menu.style.top = `${rect.bottom + 5}px`;
    menu.style.right = `${window.innerWidth - rect.right}px`;
    
    document.body.appendChild(menu);
    
    // Close menu on click outside
    setTimeout(() => {
        document.addEventListener('click', function closeMenu(e) {
            if (!menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            }
        });
    }, 0);
}

// Edit plan
function editPlan(planId) {
    window.location.href = `/plans/${planId}/edit`;
}

// Delete plan
async function deletePlan(planId) {
    if (!confirm('🗑️ Bạn có chắc muốn xóa kế hoạch này?\n\nHành động này không thể hoàn tác!')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/plans/${planId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show success notification
            showNotification('success', 'Đã xóa kế hoạch', 'Kế hoạch đã được xóa thành công');
            
            // Reload plans
            await loadPlans();
        } else {
            alert('❌ Lỗi: ' + (data.error || 'Không thể xóa kế hoạch'));
        }
    } catch (error) {
        console.error('Error deleting plan:', error);
        alert('❌ Không thể kết nối đến server');
    }
}
    
// Handle search
function handleSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    filterPlans(query);
}

// Filter plans by status and search query
function filterPlans(searchQuery = '') {
    let filtered = [...allPlans];
    
    // Apply status filter
    if (currentFilter === 'upcoming') {
        const now = new Date();
        filtered = filtered.filter(plan => {
            const planDate = new Date(plan.created_at);
            planDate.setDate(planDate.getDate() + plan.duration_days);
            return planDate > now;
        });
    } else if (currentFilter === 'completed') {
        const now = new Date();
        filtered = filtered.filter(plan => {
            const planDate = new Date(plan.created_at);
            planDate.setDate(planDate.getDate() + plan.duration_days);
            return planDate <= now;
        });
    }
    
    // Apply search filter
    if (searchQuery) {
        const query = searchQuery.toLowerCase().trim();
        filtered = filtered.filter(plan => {
            const name = (plan.plan_name || '').toLowerCase();
            const dest = (plan.destination || '').toLowerCase();
            const prefs = (plan.preferences || '').toLowerCase();
            return name.includes(query) || dest.includes(query) || prefs.includes(query);
        });
    } else if (searchInput && searchInput.value) {
        const query = searchInput.value.toLowerCase().trim();
        filtered = filtered.filter(plan => {
            const name = (plan.plan_name || '').toLowerCase();
            const dest = (plan.destination || '').toLowerCase();
            return name.includes(query) || dest.includes(query);
        });
    }
    
    renderPlans(filtered);
    
    if (filtered.length === 0) {
        showEmptyState();
    } else {
        hideEmptyState();
    }
}

// Show/hide empty state
function showEmptyState() {
    if (emptyState) {
        emptyState.classList.remove('hidden');
        emptyState.classList.add('flex');
    }
    if (plansGrid) {
        plansGrid.classList.add('hidden');
    }
}

function hideEmptyState() {
    if (emptyState) {
        emptyState.classList.add('hidden');
        emptyState.classList.remove('flex');
    }
    if (plansGrid) {
        plansGrid.classList.remove('hidden');
    }
}

// Utility functions
function getDestinationImage(destination) {
    const images = {
        'Đà Lạt': 'https://lh3.googleusercontent.com/aida-public/AB6AXuC7N7VoGqXmCE_xTG-tHnfXCsT6TiHXEnb78cYiG6wIN7KRbEyx6sDwE9MQln91NolhXdovFlN3UQ_eckloJVYRGTfODpca0_x5zRkbhI6yzoWvPsykr6SZT9YW8Ei1sETchTtJqPNvegsb9qVia_qAqt_A_C_tcDJS8ZQx-_2EENaani9oNspkWc-QZBEXCQ00Mjc-fTU1vydTmh1Tus7lMQej6ba3oBEpFthiMHAYdn7TZTxv5-pd7Gh9an5JuVdUTayVnHuyIWo',
        'Hà Nội': 'https://lh3.googleusercontent.com/aida-public/AB6AXuCpyhLTCSZTVWPC0nU5bgn9fdDQbWQPrGSI_k_uh4F_juLXuvOq8duySIAZmoYZeLRWPoJ-7CffdsDdz-uTQBcwnYYWJjWsbOLXYCOUWSt0Kvyq-eSfAEtbg9y5AzUZ2n9mIgaHgal0k_e4bybNu8HnSoPs16_2Q9XHqwJRuRH137AQ0ZAs14vOAoitfN9QWQTg5jk1ZzxRso4xFx3nCEecWl8Iz_0TyaL-hYaLZ87FIZqfX8pWPZtbQ4CWUWkxvv2Hq09QIMBmcMg',
        'Phú Quốc': 'https://lh3.googleusercontent.com/aida-public/AB6AXuBQD5lLRNpDviaZDOZpdPrd9iWC8TY62N1lkMcGVj3eVGMuxWjq4zkMiJS9ZIEYmiRRAtomgsHERVBAvA15NDaJ2J8yQ4FRMofTdh-6kOBAgOJFRl87lFZm73FbM3w__nLbASluDHOJ-eV4XU_6hJkmiErL7rSwVv0MLkoexkjY4fHohCy3C6k2-n7sCFNKR2BRo_pk0cipWGYnnEfSlz1DHrJ-xhoEpPDpVetjiu4G_h6Yzk6KbnnkCHF4gKSZVzQ0TZFAJA-REZk',
        'Đà Nẵng': 'https://lh3.googleusercontent.com/aida-public/AB6AXuC7N7VoGqXmCE_xTG-tHnfXCsT6TiHXEnb78cYiG6wIN7KRbEyx6sDwE9MQln91NolhXdovFlN3UQ_eckloJVYRGTfODpca0_x5zRkbhI6yzoWvPsykr6SZT9YW8Ei1sETchTtJqPNvegsb9qVia_qAqt_A_C_tcDJS8ZQx-_2EENaani9oNspkWc-QZBEXCQ00Mjc-fTU1vydTmh1Tus7lMQej6ba3oBEpFthiMHAYdn7TZTxv5-pd7Gh9an5JuVdUTayVnHuyIWo'
    };
    
    return images[destination] || 'https://lh3.googleusercontent.com/aida-public/AB6AXuBl4yfGCvMNncCqvEmgITcJeF7fh2BDC4gN06d2CnWngdCY1bkqXMsGRXfxWKYz1-aQErPpR9owyY4qXIfQVemgGDRKAFvziyWh7G6913ayP-zYXamHW3uNBmFCr_o_qT_jvGsDwpFjYnGopf-8-CwtI8N_IdDTuu4AwZ6A14h_zChPUwv47EK5N-7cIT3u3HPew7uiUex6BqTDvM6eps_E3oLo1YM79zuRQ_9VwPA4ok3UDw1v6MynDPZ5zKM2CKdxFC-BBAkPDjw';
}

function formatDateRange(createdAt, durationDays) {
    const start = new Date(createdAt);
    const end = new Date(start);
    end.setDate(end.getDate() + durationDays);
    
    const format = (date) => {
        return `${date.getDate().toString().padStart(2, '0')}/${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getFullYear()}`;
    };
    
    return `${format(start)} - ${format(end)}`;
}

function showNotification(type, title, message) {
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
    setTimeout(() => notif.remove(), 5000);
}
