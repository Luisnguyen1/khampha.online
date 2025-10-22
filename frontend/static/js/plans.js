/**
 * Plans management logic for khappha.online
 */

const plansContainer = document.getElementById('plansContainer');
const emptyState = document.getElementById('emptyState');
const loadingPlans = document.getElementById('loadingPlans');

// Load plans on page load
window.addEventListener('DOMContentLoaded', loadPlans);

// Load plans from API
async function loadPlans() {
    try {
        const response = await fetch('/api/plans?limit=20');
        const data = await response.json();
        
        loadingPlans.classList.add('hidden');
        
        if (data.success && data.plans.length > 0) {
            renderPlans(data.plans);
        } else {
            showEmptyState();
        }
    } catch (error) {
        console.error('Error loading plans:', error);
        loadingPlans.classList.add('hidden');
        showEmptyState();
    }
}

// Render plans
function renderPlans(plans) {
    plansContainer.innerHTML = '';
    emptyState.classList.add('hidden');
    
    plans.forEach(plan => {
        const planCard = createPlanCard(plan);
        plansContainer.appendChild(planCard);
    });
}

// Create plan card
function createPlanCard(plan) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow hover:shadow-lg transition p-6';
    
    const favoriteIcon = plan.is_favorite ? '⭐' : '☆';
    const createdDate = new Date(plan.created_at).toLocaleDateString('vi-VN');
    
    card.innerHTML = `
        <div class="flex justify-between items-start mb-4">
            <div class="flex-1">
                <h3 class="text-xl font-bold text-gray-800 mb-1">
                    ${plan.plan_name || plan.destination}
                </h3>
                <p class="text-gray-600 text-sm">
                    📍 ${plan.destination} • ${plan.duration_days} ngày
                </p>
            </div>
            <button onclick="toggleFavorite(${plan.id})" class="text-2xl hover:scale-110 transition">
                ${favoriteIcon}
            </button>
        </div>
        
        <div class="mb-4">
            <div class="flex items-center justify-between text-sm text-gray-600 mb-2">
                <span>💰 Ngân sách:</span>
                <span class="font-semibold">${formatCurrency(plan.budget || plan.total_cost)}</span>
            </div>
            <div class="flex items-center justify-between text-sm text-gray-600">
                <span>📅 Ngày tạo:</span>
                <span>${createdDate}</span>
            </div>
        </div>
        
        ${plan.preferences ? `
        <div class="mb-4">
            <div class="flex flex-wrap gap-2">
                ${JSON.parse(plan.preferences).map(pref => 
                    `<span class="px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs">${pref}</span>`
                ).join('')}
            </div>
        </div>
        ` : ''}
        
        <div class="flex gap-2">
            <button onclick="viewPlan(${plan.id})" 
                    class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition">
                👁️ Xem chi tiết
            </button>
            <button onclick="deletePlan(${plan.id})" 
                    class="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-600 rounded-lg text-sm transition">
                🗑️
            </button>
        </div>
    `;
    
    return card;
}

// Show empty state
function showEmptyState() {
    plansContainer.innerHTML = '';
    emptyState.classList.remove('hidden');
}

// View plan details
async function viewPlan(planId) {
    try {
        const response = await fetch(`/api/plans/${planId}`);
        const data = await response.json();
        
        if (data.success) {
            // Show plan details in modal (implement later)
            alert('Chi tiết kế hoạch:\n' + JSON.stringify(data.plan.itinerary, null, 2));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Không thể tải chi tiết kế hoạch');
    }
}

// Toggle favorite
async function toggleFavorite(planId) {
    try {
        const response = await fetch(`/api/plans/${planId}/favorite`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Reload plans
            loadPlans();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Delete plan
async function deletePlan(planId) {
    if (!confirm('Bạn có chắc muốn xóa kế hoạch này?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/plans/${planId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Reload plans
            loadPlans();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Không thể xóa kế hoạch');
    }
}

// Format currency
function formatCurrency(amount) {
    if (!amount) return 'Chưa xác định';
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}
