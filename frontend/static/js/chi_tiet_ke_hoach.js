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
    const navContainer = document.getElementById('day-navigation');
    if (!navContainer) return;
    
    // Get itinerary
    const itinerary = typeof plan.itinerary === 'string' ? JSON.parse(plan.itinerary) : plan.itinerary;
    if (!Array.isArray(itinerary) || itinerary.length === 0) {
        navContainer.innerHTML = '<p class="text-sm text-gray-500 px-3">Không có lịch trình</p>';
        return;
    }
    
    // Clear container
    navContainer.innerHTML = '';
    
    // Generate day links
    itinerary.forEach((day, index) => {
        const dayNum = day.day || index + 1;
        const link = document.createElement('a');
        link.className = `flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors day-link`;
        link.dataset.day = dayNum;
        link.innerHTML = `
            <span class="material-symbols-outlined">calendar_month</span>
            <p class="font-medium leading-normal">Ngày ${dayNum}</p>
        `;
        
        // Add click handler
        link.onclick = (e) => {
            e.preventDefault();
            currentDay = dayNum;
            displayDay(dayNum, plan);
            updateActiveNavigation(dayNum);
        };
        
        // Set first day as active
        if (dayNum === 1) {
            link.classList.add('bg-primary/20', 'text-primary');
        } else {
            link.classList.add('hover:bg-gray-100', 'dark:hover:bg-gray-800', 'text-[#111618]', 'dark:text-gray-300');
        }
        
        navContainer.appendChild(link);
    });
    
    // Add divider and summary link
    const divider = document.createElement('div');
    divider.className = 'my-2 border-t border-gray-200 dark:border-gray-700';
    navContainer.appendChild(divider);
    
    const summaryLink = document.createElement('a');
    summaryLink.className = 'flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-[#111618] dark:text-gray-300 cursor-pointer';
    summaryLink.innerHTML = `
        <span class="material-symbols-outlined">pie_chart</span>
        <p class="font-medium leading-normal">Tổng kết & Chi phí</p>
    `;
    summaryLink.onclick = (e) => {
        e.preventDefault();
        showSummary(plan);
    };
    navContainer.appendChild(summaryLink);
}

// Update active navigation
function updateActiveNavigation(dayNum) {
    const navLinks = document.querySelectorAll('.day-link');
    navLinks.forEach((link) => {
        const linkDay = parseInt(link.dataset.day);
        if (linkDay === dayNum) {
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
    if (!dayData) {
        showError(`Không tìm thấy dữ liệu cho ngày ${dayNum}`);
        return;
    }
    
    // Update page heading
    const heading = document.getElementById('page-heading');
    const subheading = document.getElementById('page-subheading');
    
    if (heading) {
        heading.textContent = `Ngày ${dayNum}: ${dayData.title || 'Chi tiết lịch trình'}`;
    }
    
    if (subheading) {
        subheading.textContent = dayData.description || `Chi tiết lịch trình ngày ${dayNum} của bạn`;
    }
    
    // Update stats
    updateDayStats(dayData, plan);
    
    // Render timeline
    renderTimeline(dayData);
    
    // Update map
    updateMapImage(plan.destination);
    
    // Update notes (pass both dayData and plan)
    updateNotes(dayData, plan);
}

// Update day stats
function updateDayStats(dayData, plan) {
    const statsContainer = document.getElementById('day-stats');
    if (!statsContainer) return;
    
    const activities = dayData.activities || [];
    const totalCost = activities.reduce((sum, act) => sum + (act.cost || 0), 0);
    
    statsContainer.innerHTML = `
        <div class="flex flex-col gap-2 rounded-xl p-6 border border-[#dbe2e6] dark:border-gray-700 bg-white dark:bg-gray-800">
            <p class="text-[#111618] dark:text-gray-300 text-base font-medium leading-normal">Chi phí ngày này</p>
            <p class="text-[#111618] dark:text-white tracking-light text-2xl font-bold leading-tight">${formatCurrency(totalCost)}</p>
        </div>
        <div class="flex flex-col gap-2 rounded-xl p-6 border border-[#dbe2e6] dark:border-gray-700 bg-white dark:bg-gray-800">
            <p class="text-[#111618] dark:text-gray-300 text-base font-medium leading-normal">Số hoạt động</p>
            <p class="text-[#111618] dark:text-white tracking-light text-2xl font-bold leading-tight">${activities.length}</p>
        </div>
        <div class="flex flex-col gap-2 rounded-xl p-6 border border-[#dbe2e6] dark:border-gray-700 bg-white dark:bg-gray-800">
            <p class="text-[#111618] dark:text-gray-300 text-base font-medium leading-normal">Tổng ngân sách</p>
            <p class="text-[#111618] dark:text-white tracking-light text-2xl font-bold leading-tight">${formatCurrency(plan.budget || 0)}</p>
        </div>
    `;
}

// Render timeline
function renderTimeline(dayData) {
    const timelineContainer = document.getElementById('timeline-container');
    if (!timelineContainer) return;
    
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
    
    // Use grid layout like original template
    let html = '<div class="grid grid-cols-[auto_1fr] gap-x-4">';
    
    activities.forEach((activity, index) => {
        const isLast = index === activities.length - 1;
        const icon = getActivityIcon(activity);
        const time = activity.time || 'Cả ngày';
        const title = activity.title || activity.name || 'Hoạt động';
        const description = activity.description || '';
        const cost = activity.cost;
        const location = activity.location || '';
        
        // Icon column
        html += `
            <div class="flex flex-col items-center gap-1.5 ${index === 0 ? 'pt-3' : ''}">
                ${index > 0 ? '<div class="w-[2px] bg-[#dbe2e6] dark:bg-gray-700 h-6"></div>' : ''}
                <span class="material-symbols-outlined text-primary">${icon}</span>
                ${!isLast ? '<div class="w-[2px] bg-[#dbe2e6] dark:bg-gray-700 h-full"></div>' : ''}
            </div>
        `;
        
        // Content column
        html += `
            <div class="flex-1 pb-8">
                <p class="text-sm font-medium text-[#617c89] dark:text-gray-400">${time}</p>
                <p class="text-lg font-semibold text-[#111618] dark:text-white">${title}</p>
                ${description ? `<p class="text-base text-[#617c89] dark:text-gray-400 mt-1">${description}</p>` : ''}
                ${cost ? `<p class="text-sm font-medium text-green-600 mt-2">Chi phí: ${formatCurrency(cost)}</p>` : ''}
                ${location ? `<p class="text-sm text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-1"><span class="material-symbols-outlined text-sm">location_on</span>${location}</p>` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    timelineContainer.innerHTML = html;
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

// Update map image
function updateMapImage(destination) {
    const mapImage = document.getElementById('map-image');
    if (mapImage) {
        mapImage.style.backgroundImage = `url("${getDestinationImage(destination)}")`;
    }
}

// Update notes
function updateNotes(dayData, plan) {
    const notesContent = document.getElementById('notes-content');
    const notesContainer = document.getElementById('day-notes');
    if (!notesContent) return;
    
    // Check if viewing a specific day or summary
    const notes = dayData ? dayData.notes : null;
    
    // Update title
    const titleElement = notesContainer.querySelector('h3');
    
    if (notes && notes.length > 0) {
        // Show notes for specific day
        if (titleElement) {
            titleElement.textContent = `Lưu ý ngày ${dayData.day || ''}`;
        }
        const html = '<ul class="list-disc list-inside space-y-1 text-sm">' + 
            notes.map(note => `<li>${note}</li>`).join('') + 
            '</ul>';
        notesContent.innerHTML = html;
    } else {
        // Show general notes for the whole trip
        if (titleElement) {
            titleElement.textContent = 'Lưu ý tổng quan';
        }
        const generalNotes = plan.general_notes || plan.notes || [];
        if (generalNotes.length > 0) {
            const html = '<ul class="list-disc list-inside space-y-1 text-sm">' + 
                generalNotes.map(note => `<li>${note}</li>`).join('') + 
                '</ul>';
            notesContent.innerHTML = html;
        } else {
            notesContent.innerHTML = '<p class="text-sm">Không có ghi chú đặc biệt.</p>';
        }
    }
}

// Show summary
function showSummary(plan) {
    const heading = document.getElementById('page-heading');
    const subheading = document.getElementById('page-subheading');
    
    if (heading) {
        heading.textContent = 'Tổng kết chuyến đi';
    }
    
    if (subheading) {
        subheading.textContent = 'Tổng quan chi phí và thông tin chuyến đi';
    }
    
    // Calculate total cost from all days
    const itinerary = typeof plan.itinerary === 'string' ? JSON.parse(plan.itinerary) : plan.itinerary;
    let totalCost = 0;
    let totalActivities = 0;
    
    if (Array.isArray(itinerary)) {
        itinerary.forEach(day => {
            const activities = day.activities || [];
            totalActivities += activities.length;
            activities.forEach(act => {
                totalCost += (act.cost || 0);
            });
        });
    }
    
    // Update stats for summary
    const statsContainer = document.getElementById('day-stats');
    if (statsContainer) {
        statsContainer.innerHTML = `
            <div class="flex flex-col gap-2 rounded-xl p-6 border border-[#dbe2e6] dark:border-gray-700 bg-white dark:bg-gray-800">
                <p class="text-[#111618] dark:text-gray-300 text-base font-medium leading-normal">Tổng chi phí thực tế</p>
                <p class="text-[#111618] dark:text-white tracking-light text-2xl font-bold leading-tight">${formatCurrency(totalCost)}</p>
            </div>
            <div class="flex flex-col gap-2 rounded-xl p-6 border border-[#dbe2e6] dark:border-gray-700 bg-white dark:bg-gray-800">
                <p class="text-[#111618] dark:text-gray-300 text-base font-medium leading-normal">Ngân sách dự kiến</p>
                <p class="text-[#111618] dark:text-white tracking-light text-2xl font-bold leading-tight">${formatCurrency(plan.budget || 0)}</p>
            </div>
            <div class="flex flex-col gap-2 rounded-xl p-6 border border-[#dbe2e6] dark:border-gray-700 bg-white dark:bg-gray-800">
                <p class="text-[#111618] dark:text-gray-300 text-base font-medium leading-normal">${totalCost > (plan.budget || 0) ? 'Vượt ngân sách' : 'Tiết kiệm'}</p>
                <p class="text-[#111618] dark:text-white tracking-light text-2xl font-bold leading-tight">${formatCurrency(Math.abs(totalCost - (plan.budget || 0)))}</p>
            </div>
        `;
    }
    
    // Show summary timeline
    const timelineContainer = document.getElementById('timeline-container');
    if (timelineContainer) {
        let summaryHtml = '<div class="space-y-4">';
        
        if (Array.isArray(itinerary)) {
            itinerary.forEach((day, index) => {
                const dayNum = day.day || index + 1;
                const activities = day.activities || [];
                const dayCost = activities.reduce((sum, act) => sum + (act.cost || 0), 0);
                
                summaryHtml += `
                    <div class="bg-white dark:bg-gray-800 rounded-xl p-6 border border-[#dbe2e6] dark:border-gray-700">
                        <div class="flex justify-between items-center mb-3">
                            <h3 class="text-lg font-bold text-[#111618] dark:text-white">Ngày ${dayNum}: ${day.title || 'Chi tiết lịch trình'}</h3>
                            <p class="text-lg font-bold text-primary">${formatCurrency(dayCost)}</p>
                        </div>
                        <p class="text-sm text-gray-600 dark:text-gray-400">${activities.length} hoạt động</p>
                    </div>
                `;
            });
        }
        
        summaryHtml += '</div>';
        timelineContainer.innerHTML = summaryHtml;
    }
    
    // Update navigation to remove active state
    document.querySelectorAll('.day-link').forEach(link => {
        link.classList.remove('bg-primary/20', 'text-primary');
        link.classList.add('hover:bg-gray-100', 'dark:hover:bg-gray-800', 'text-[#111618]', 'dark:text-gray-300');
    });
    
    // Update notes for summary view (show general notes)
    updateNotes(null, plan);
}

// Edit plan button
const editButton = document.getElementById('edit-button');
if (editButton) {
    editButton.addEventListener('click', () => {
        const planId = getPlanIdFromUrl();
        if (planId) {
            window.location.href = `/plans/${planId}/edit`;
        }
    });
}

// Download PDF button
const downloadButton = document.getElementById('download-button');
if (downloadButton) {
    downloadButton.addEventListener('click', () => {
        alert('Tính năng tải PDF sẽ được cập nhật sớm!');
    });
}
