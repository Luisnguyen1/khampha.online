/**
 * Plan detail page logic for khappha.online
 * Handles loading and displaying detailed travel plan information
 */

let currentPlan = null;
let currentDay = 1;

// Get plan ID from URL
function getPlanIdFromUrl() {
    const path = window.location.pathname;
    const match = path.match(/\/plans\/(\d+)/);
    return match ? parseInt(match[1]) : null;
}

// Load plan on page load
window.addEventListener('DOMContentLoaded', () => {
    const planId = getPlanIdFromUrl();
    if (planId) {
        loadPlanDetail(planId);
    } else {
        showError('Không tìm thấy ID kế hoạch');
    }
});

// Load plan detail from API
async function loadPlanDetail(planId) {
    try {
        const response = await fetch(`/api/plans/${planId}`);
        const data = await response.json();
        
        if (data.success && data.plan) {
            currentPlan = data.plan;
            renderPlanDetail(currentPlan);
        } else {
            showError(data.error || 'Không tìm thấy kế hoạch');
        }
    } catch (error) {
        console.error('Error loading plan:', error);
        showError('Không thể tải dữ liệu kế hoạch');
    }
}

// Render plan detail
function renderPlanDetail(plan) {
    // Update sidebar header
    updateSidebarHeader(plan);
    
    // Generate day navigation
    generateDayNavigation(plan);
    
    // Display current day
    displayDay(currentDay, plan);
    
    // Update budget section
    updateBudgetSection(plan);
}

// Update sidebar header
function updateSidebarHeader(plan) {
    const avatar = document.querySelector('aside .bg-cover');
    const title = document.querySelector('aside h1');
    const subtitle = document.querySelector('aside p');
    
    if (title) {
        title.textContent = plan.plan_name || `Khám phá ${plan.destination}`;
    }
    
    if (subtitle) {
        subtitle.textContent = `${plan.duration_days} Ngày`;
    }
    
    if (avatar) {
        avatar.style.backgroundImage = `url("${getDestinationImage(plan.destination)}")`;
    }
}

// Generate day navigation
function generateDayNavigation(plan) {
    const navContainer = document.querySelector('aside .flex.flex-col.gap-2');
    if (!navContainer) return;
    
    // Clear existing navigation
    const existingDays = navContainer.querySelectorAll('a[href="#"]');
    existingDays.forEach(el => el.remove());
    
    // Get itinerary
    const itinerary = typeof plan.itinerary === 'string' ? JSON.parse(plan.itinerary) : plan.itinerary;
    if (!Array.isArray(itinerary)) return;
    
    // Generate day links
    const firstLink = navContainer.querySelector('a');
    itinerary.forEach((day, index) => {
        const dayNum = day.day || index + 1;
        const link = document.createElement('a');
        link.className = `flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-[#111618] dark:text-gray-300 cursor-pointer`;
        link.innerHTML = `
            <span class="material-symbols-outlined">calendar_month</span>
            <p class="font-medium leading-normal">Ngày ${dayNum}</p>
        `;
        link.onclick = (e) => {
            e.preventDefault();
            currentDay = dayNum;
            displayDay(dayNum, plan);
            updateActiveNavigation(dayNum);
        };
        
        if (firstLink) {
            navContainer.insertBefore(link, firstLink);
        } else {
            navContainer.appendChild(link);
        }
        
        // Set first day as active
        if (dayNum === 1) {
            link.classList.add('bg-primary/20', 'text-primary');
            link.classList.remove('hover:bg-gray-100', 'dark:hover:bg-gray-800', 'text-[#111618]', 'dark:text-gray-300');
        }
    });
}

// Update active navigation
function updateActiveNavigation(dayNum) {
    const navLinks = document.querySelectorAll('aside a[class*="calendar_month"]');
    navLinks.forEach((link, index) => {
        if (index + 1 === dayNum) {
            link.classList.add('bg-primary/20', 'text-primary');
            link.classList.remove('hover:bg-gray-100', 'dark:hover:bg-gray-800', 'text-[#111618]', 'dark:text-gray-300');
        } else {
            link.classList.remove('bg-primary/20', 'text-primary');
            link.classList.add('hover:bg-gray-100', 'dark:hover:bg-gray-800', 'text-[#111618]', 'dark:text-gray-300');
        }
    });
}

// Display specific day
function displayDay(dayNum, plan) {
    const itinerary = typeof plan.itinerary === 'string' ? JSON.parse(plan.itinerary) : plan.itinerary;
    if (!Array.isArray(itinerary)) return;
    
    const dayData = itinerary.find(d => (d.day || itinerary.indexOf(d) + 1) === dayNum);
    if (!dayData) return;
    
    // Update page heading
    const heading = document.querySelector('main .text-3xl.font-black');
    const subheading = document.querySelector('main .text-base.font-normal.leading-normal');
    
    if (heading) {
        heading.textContent = `Ngày ${dayNum}: ${dayData.title || 'Chi tiết lịch trình'}`;
    }
    
    if (subheading) {
        subheading.textContent = dayData.description || `Chi tiết lịch trình ngày ${dayNum} của bạn`;
    }
    
    // Update stats
    updateDayStats(dayData);
    
    // Render timeline
    renderTimeline(dayData);
}

// Update day stats
function updateDayStats(dayData) {
    const statsContainer = document.querySelector('.grid.grid-cols-1.md\\:grid-cols-3');
    if (!statsContainer) return;
    
    const activities = dayData.activities || [];
    const totalCost = activities.reduce((sum, act) => sum + (act.cost || 0), 0);
    const duration = activities.length;
    
    statsContainer.innerHTML = `
        <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <div class="flex items-center gap-3 mb-2">
                <span class="material-symbols-outlined text-primary">schedule</span>
                <p class="text-sm text-gray-500 dark:text-gray-400">Thời gian</p>
            </div>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">${duration} hoạt động</p>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <div class="flex items-center gap-3 mb-2">
                <span class="material-symbols-outlined text-green-600">attach_money</span>
                <p class="text-sm text-gray-500 dark:text-gray-400">Chi phí</p>
            </div>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">${formatCurrency(totalCost)}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <div class="flex items-center gap-3 mb-2">
                <span class="material-symbols-outlined text-blue-600">location_on</span>
                <p class="text-sm text-gray-500 dark:text-gray-400">Địa điểm</p>
            </div>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">${activities.length}</p>
        </div>
    `;
}

// Render timeline
function renderTimeline(dayData) {
    const timelineContainer = document.querySelector('main .flex.flex-col.gap-6');
    if (!timelineContainer) {
        // Create timeline container if not exists
        const mainContent = document.querySelector('main .layout-content-container');
        const timeline = document.createElement('div');
        timeline.className = 'flex flex-col gap-6 mt-8';
        mainContent.appendChild(timeline);
        renderTimeline(dayData);
        return;
    }
    
    timelineContainer.innerHTML = '';
    
    const activities = dayData.activities || [];
    
    if (activities.length === 0) {
        timelineContainer.innerHTML = `
            <div class="bg-gray-100 dark:bg-gray-800 rounded-xl p-8 text-center">
                <span class="material-symbols-outlined text-6xl text-gray-400">event_busy</span>
                <p class="text-gray-500 dark:text-gray-400 mt-4">Chưa có hoạt động nào cho ngày này</p>
            </div>
        `;
        return;
    }
    
    activities.forEach((activity, index) => {
        const activityCard = document.createElement('div');
        activityCard.className = 'bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow';
        
        activityCard.innerHTML = `
            <div class="flex items-start gap-4">
                <div class="flex flex-col items-center gap-2">
                    <div class="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                        <span class="material-symbols-outlined text-primary">${getActivityIcon(activity)}</span>
                    </div>
                    ${index < activities.length - 1 ? '<div class="w-0.5 h-full bg-gray-200 dark:bg-gray-700"></div>' : ''}
                </div>
                <div class="flex-1">
                    <div class="flex items-start justify-between mb-2">
                        <div>
                            <p class="text-lg font-bold text-gray-900 dark:text-white">${activity.title || activity.name}</p>
                            <p class="text-sm text-gray-500 dark:text-gray-400">${activity.time || 'Cả ngày'}</p>
                        </div>
                        ${activity.cost ? `<p class="text-lg font-bold text-primary">${formatCurrency(activity.cost)}</p>` : ''}
                    </div>
                    ${activity.description ? `<p class="text-gray-600 dark:text-gray-300 mb-3">${activity.description}</p>` : ''}
                    ${activity.location ? `
                        <div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                            <span class="material-symbols-outlined text-sm">location_on</span>
                            <span>${activity.location}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        timelineContainer.appendChild(activityCard);
    });
}

// Update budget section
function updateBudgetSection(plan) {
    // This would update the budget summary in the sidebar or footer
    const totalCost = plan.total_cost || plan.budget || 0;
    
    // You can add a budget widget here if needed
    console.log('Total budget:', formatCurrency(totalCost));
}

// Get activity icon based on type
function getActivityIcon(activity) {
    const title = (activity.title || activity.name || '').toLowerCase();
    
    if (title.includes('ăn') || title.includes('nhà hàng') || title.includes('quán')) return 'restaurant';
    if (title.includes('khách sạn') || title.includes('check')) return 'hotel';
    if (title.includes('bãi biển') || title.includes('biển')) return 'beach_access';
    if (title.includes('chùa') || title.includes('đền') || title.includes('đình')) return 'temple_buddhist';
    if (title.includes('bảo tàng') || title.includes('museum')) return 'museum';
    if (title.includes('mua sắm') || title.includes('shopping')) return 'shopping_bag';
    if (title.includes('cà phê') || title.includes('cafe')) return 'local_cafe';
    
    return 'place';
}

// Utility functions
function formatCurrency(amount) {
    if (!amount) return '0 ₫';
    return new Intl.NumberFormat('vi-VN', { 
        style: 'currency', 
        currency: 'VND',
        minimumFractionDigits: 0
    }).format(amount);
}

function getDestinationImage(destination) {
    const images = {
        'Đà Lạt': 'https://lh3.googleusercontent.com/aida-public/AB6AXuC7N7VoGqXmCE_xTG-tHnfXCsT6TiHXEnb78cYiG6wIN7KRbEyx6sDwE9MQln91NolhXdovFlN3UQ_eckloJVYRGTfODpca0_x5zRkbhI6yzoWvPsykr6SZT9YW8Ei1sETchTtJqPNvegsb9qVia_qAqt_A_C_tcDJS8ZQx-_2EENaani9oNspkWc-QZBEXCQ00Mjc-fTU1vydTmh1Tus7lMQej6ba3oBEpFthiMHAYdn7TZTxv5-pd7Gh9an5JuVdUTayVnHuyIWo',
        'Hà Nội': 'https://lh3.googleusercontent.com/aida-public/AB6AXuCpyhLTCSZTVWPC0nU5bgn9fdDQbWQPrGSI_k_uh4F_juLXuvOq8duySIAZmoYZeLRWPoJ-7CffdsDdz-uTQBcwnYYWJjWsbOLXYCOUWSt0Kvyq-eSfAEtbg9y5AzUZ2n9mIgaHgal0k_e4bybNu8HnSoPs16_2Q9XHqwJRuRH137AQ0ZAs14vOAoitfN9QWQTg5jk1ZzxRso4xFx3nCEecWl8Iz_0TyaL-hYaLZ87FIZqfX8pWPZtbQ4CWUWkxvv2Hq09QIMBmcMg',
        'Phú Quốc': 'https://lh3.googleusercontent.com/aida-public/AB6AXuBQD5lLRNpDviaZDOZpdPrd9iWC8TY62N1lkMcGVj3eVGMuxWjq4zkMiJS9ZIEYmiRRAtomgsHERVBAvA15NDaJ2J8yQ4FRMofTdh-6kOBAgOJFRl87lFZm73FbM3w__nLbASluDHOJ-eV4XU_6hJkmiErL7rSwVv0MLkoexkjY4fHohCy3C6k2-n7sCFNKR2BRo_pk0cipWGYnnEfSlz1DHrJ-xhoEpPDpVetjiu4G_h6Yzk6KbnnkCHF4gKSZVzQ0TZFAJA-REZk',
        'Đà Nẵng': 'https://lh3.googleusercontent.com/aida-public/AB6AXuAMJD6UsCS0L3QbSKsgNM6jDhcAoa7UNtuJBN24E7WZ89gTo-Iil0HRHJN5jVzkgFYCSsvMH7IRwORU_9iEIat_bbd1dNiNj-kImgI9ybdZBaqZBXlG2ujVbnANL5s9j-bJUwOa_4qWlnlwg0kzTxQ8UM3XlIrz9fyiPNtGAqeVWPCCsyjuKrBwrUMamEpQcfkOM9pecdp77OzlIDUgjsH6G9VVVKA9JAvtGTWt--X4EOTA4mSj4O_URbEzEkJlY_r3xWzAs95Lemo'
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

// Edit plan button
const editButton = document.querySelector('button:has(.material-symbols-outlined:contains("edit"))');
if (editButton) {
    editButton.addEventListener('click', () => {
        const planId = getPlanIdFromUrl();
        if (planId) {
            window.location.href = `/plans/${planId}/edit`;
        }
    });
}

// Download PDF button
const downloadButton = document.querySelector('button:has(.material-symbols-outlined:contains("download"))');
if (downloadButton) {
    downloadButton.addEventListener('click', () => {
        alert('Tính năng tải PDF sẽ được cập nhật sớm!');
    });
}
