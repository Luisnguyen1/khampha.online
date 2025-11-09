/**
 * Mobile optimizations for chi_tiet_ke_hoach page
 * Enhanced with better touch interactions and animations
 */

// Mobile viewport height fix
function setMobileViewportHeight() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
}

// Call on load and resize
window.addEventListener('load', setMobileViewportHeight);
window.addEventListener('resize', setMobileViewportHeight);

// Prevent body scroll when drawer is open
function toggleBodyScroll(lock) {
    if (lock) {
        document.body.style.overflow = 'hidden';
        document.body.style.position = 'fixed';
        document.body.style.width = '100%';
    } else {
        document.body.style.overflow = '';
        document.body.style.position = '';
        document.body.style.width = '';
    }
}

// Sync mobile sidebar with desktop sidebar
function syncMobileSidebar(plan) {
    const mobileAvatar = document.getElementById('mobile-plan-avatar');
    const mobileTitle = document.getElementById('mobile-plan-title');
    const mobileSubtitle = document.getElementById('mobile-plan-subtitle');
    
    if (mobileTitle && plan) {
        mobileTitle.textContent = plan.plan_name || `Khám phá ${plan.destination}`;
    }
    
    if (mobileSubtitle && plan) {
        mobileSubtitle.textContent = `${plan.duration_days} Ngày`;
    }
    
    if (mobileAvatar && plan) {
        mobileAvatar.style.backgroundImage = `url("${getDestinationImage(plan.destination)}")`;
    }
}

// Sync mobile day navigation
function syncMobileDayNavigation(plan) {
    const mobileNavContainer = document.getElementById('mobile-day-navigation');
    if (!mobileNavContainer || !plan) return;
    
    const itinerary = typeof plan.itinerary === 'string' ? JSON.parse(plan.itinerary) : plan.itinerary;
    if (!Array.isArray(itinerary) || itinerary.length === 0) {
        mobileNavContainer.innerHTML = '<p class="text-sm text-gray-500 px-3">Không có lịch trình</p>';
        return;
    }
    
    mobileNavContainer.innerHTML = '';
    
    // Add day links
    itinerary.forEach((day, index) => {
        const dayNum = day.day || index + 1;
        const link = document.createElement('a');
        link.className = 'day-link flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300 cursor-pointer';
        link.dataset.day = dayNum;
        
        const activities = day.activities || [];
        const totalCost = activities.reduce((sum, act) => sum + (act.cost || 0), 0);
        
        link.innerHTML = `
            <span class="material-symbols-outlined">${getActivityIcon(activities[0] || {})}</span>
            <div class="flex-1">
                <p class="font-medium">Ngày ${dayNum}</p>
                <p class="text-xs text-gray-500">${activities.length} hoạt động • ${formatCurrency(totalCost)}</p>
            </div>
        `;
        
        link.onclick = (e) => {
            e.preventDefault();
            currentDay = dayNum;
            displayDay(dayNum, plan);
            updateActiveNavigation(dayNum);
            closeSidebarDrawer();
        };
        
        mobileNavContainer.appendChild(link);
    });
    
    // Add summary link
    const divider = document.createElement('div');
    divider.className = 'my-2 border-t border-gray-200 dark:border-gray-700';
    mobileNavContainer.appendChild(divider);
    
    const summaryLink = document.createElement('a');
    summaryLink.className = 'flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300 cursor-pointer';
    summaryLink.innerHTML = `
        <span class="material-symbols-outlined">pie_chart</span>
        <p class="font-medium">Tổng kết & Chi phí</p>
    `;
    summaryLink.onclick = (e) => {
        e.preventDefault();
        switchTab('summary');
        closeSidebarDrawer();
    };
    mobileNavContainer.appendChild(summaryLink);
}

// Close sidebar drawer helper
function closeSidebarDrawer() {
    const drawer = document.getElementById('mobileSidebarDrawer');
    const overlay = document.getElementById('drawerOverlay');
    
    if (drawer) drawer.classList.remove('drawer-open');
    if (overlay) overlay.classList.remove('overlay-visible');
    toggleBodyScroll(false);
}

// Open sidebar drawer helper
function openSidebarDrawer() {
    const drawer = document.getElementById('mobileSidebarDrawer');
    const overlay = document.getElementById('drawerOverlay');
    
    if (drawer) drawer.classList.add('drawer-open');
    if (overlay) overlay.classList.add('overlay-visible');
    toggleBodyScroll(true);
}

// Swipe gesture support for closing drawer
let touchStartX = 0;
let touchEndX = 0;

function handleDrawerSwipe() {
    const drawer = document.getElementById('mobileSidebarDrawer');
    if (!drawer) return;
    
    drawer.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    
    drawer.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipeGesture();
    }, { passive: true });
}

function handleSwipeGesture() {
    const swipeThreshold = 50;
    const swipeDistance = touchEndX - touchStartX;
    
    // Swipe left to close
    if (swipeDistance < -swipeThreshold) {
        closeSidebarDrawer();
    }
}

// Hook into existing renderPlanDetail function
const originalRenderPlanDetail = window.renderPlanDetail;
if (originalRenderPlanDetail) {
    window.renderPlanDetail = function(plan) {
        originalRenderPlanDetail(plan);
        syncMobileSidebar(plan);
        syncMobileDayNavigation(plan);
    };
}

// Mobile initialization
document.addEventListener('DOMContentLoaded', function() {
    // Sync with current plan if available
    if (window.currentPlan) {
        syncMobileSidebar(window.currentPlan);
        syncMobileDayNavigation(window.currentPlan);
    }
    
    // Initialize swipe gestures
    handleDrawerSwipe();
    
    // Setup FAB sidebar button
    const fabSidebarBtn = document.getElementById('fabSidebarBtn');
    if (fabSidebarBtn) {
        fabSidebarBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openSidebarDrawer();
        });
    }
    
    // Setup FAB main button
    const fabMainBtn = document.getElementById('fabMainBtn');
    const fabMenu = document.getElementById('fabMenu');
    
    if (fabMainBtn && fabMenu) {
        fabMainBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fabMenu.classList.toggle('active');
            fabMainBtn.classList.toggle('active');
        });
        
        // Close FAB menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!fabMenu.contains(e.target) && e.target !== fabMainBtn) {
                fabMenu.classList.remove('active');
                fabMainBtn.classList.remove('active');
            }
        });
    }
    
    // Setup overlay click to close drawers
    const overlay = document.getElementById('drawerOverlay');
    if (overlay) {
        overlay.addEventListener('click', () => {
            closeSidebarDrawer();
        });
    }
    
    // Smooth scroll to active day on mobile
    const activeDayLink = document.querySelector('.day-link.active');
    if (activeDayLink && window.innerWidth <= 768) {
        setTimeout(() => {
            activeDayLink.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 300);
    }
    
    // Touch-friendly tab scrolling
    const tabNav = document.querySelector('nav.flex.gap-6');
    if (tabNav && window.innerWidth <= 768) {
        const activeTab = tabNav.querySelector('.border-primary');
        if (activeTab) {
            activeTab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }
    }
    
    // Prevent zoom on double tap for specific elements
    let lastTouchEnd = 0;
    document.addEventListener('touchend', (e) => {
        const now = Date.now();
        if (now - lastTouchEnd <= 300) {
            if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                e.preventDefault();
            }
        }
        lastTouchEnd = now;
    }, false);
});
