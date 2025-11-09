/**
 * Plan detail page logic for khappha.online
 * Handles loading and displaying detailed travel plan information
 */

let currentPlan = null;
let currentDay = 1;
let currentTab = 'itinerary'; // Track active tab
let googleMapsApiKey = ''; // Store API key

// Get plan ID from URL
function getPlanIdFromUrl() {
    const path = window.location.pathname;
    const match = path.match(/\/plans\/(\d+)/);
    return match ? parseInt(match[1]) : null;
}

// Load Google Maps API key from backend
async function loadGoogleMapsApiKey() {
    try {
        const response = await fetch('/api/config/google-maps-key');
        const data = await response.json();
        
        if (data.success && data.api_key) {
            googleMapsApiKey = data.api_key;
            console.log('Google Maps API key loaded successfully');
        } else {
            console.warn('Failed to load Google Maps API key');
        }
    } catch (error) {
        console.error('Error loading Google Maps API key:', error);
    }
}

// Load plan on page load
window.addEventListener('DOMContentLoaded', () => {
    // Load Google Maps API key first
    loadGoogleMapsApiKey();
    
    const planId = getPlanIdFromUrl();
    if (planId) {
        loadPlanDetail(planId);
        // Initialize hotel dates if plan has start/end dates
        initializeHotelDates();
    } else {
        showError('Không tìm thấy ID kế hoạch');
    }
});

// Switch tab function
function switchTab(tabName) {
    // Update tab state
    currentTab = tabName;
    
    // Update tab buttons
    const tabs = ['itinerary', 'hotel', 'flight', 'summary'];
    tabs.forEach(tab => {
        const btn = document.getElementById(`tab-${tab}`);
        const content = document.getElementById(`content-${tab}`);
        
        if (tab === tabName) {
            // Active tab
            btn?.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
            btn?.classList.add('border-primary', 'text-primary');
            content?.classList.remove('hidden');
        } else {
            // Inactive tab
            btn?.classList.remove('border-primary', 'text-primary');
            btn?.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
            content?.classList.add('hidden');
        }
    });
    
    // Load tab-specific content
    if (tabName === 'summary' && currentPlan) {
        renderSummaryTab(currentPlan);
    } else if (tabName === 'hotel' && currentPlan) {
        initializeHotelTab();
    } else if (tabName === 'flight' && currentPlan) {
        initializeFlightTab();
    }
}

// Initialize hotel tab with auto-search
async function initializeHotelTab() {
    console.log('=== initializeHotelTab called ===');
    console.log('currentPlan:', currentPlan);
    
    // Load selected hotel first
    await loadSelectedHotel();
    
    // Fill in dates from plan
    if (currentPlan) {
        const checkinInput = document.getElementById('hotel-checkin');
        const checkoutInput = document.getElementById('hotel-checkout');
        
        console.log('Plan dates:', {
            start_date: currentPlan.start_date,
            end_date: currentPlan.end_date
        });
        
        let checkinDate = '';
        let checkoutDate = '';
        
        // If plan has explicit start/end dates, use them
        if (currentPlan.start_date && currentPlan.end_date) {
            if (checkinInput) {
                checkinDate = formatDateForInput(currentPlan.start_date);
                checkinInput.value = checkinDate;
                console.log('Set checkin input value:', checkinDate);
            }
            
            if (checkoutInput) {
                checkoutDate = formatDateForInput(currentPlan.end_date);
                checkoutInput.value = checkoutDate;
                console.log('Set checkout input value:', checkoutDate);
            }
        } 
        // Otherwise, calculate from created_at and duration_days
        else if (currentPlan.created_at && currentPlan.duration_days) {
            console.log('Calculating dates from created_at and duration_days');
            
            // Use today as check-in date (or a few days from now)
            const today = new Date();
            const checkinDateObj = new Date(today.getTime() + (2 * 24 * 60 * 60 * 1000)); // 2 days from now
            
            // Calculate checkout date based on duration
            const checkoutDateObj = new Date(checkinDateObj.getTime() + (currentPlan.duration_days * 24 * 60 * 60 * 1000));
            
            checkinDate = checkinDateObj.toISOString().split('T')[0]; // YYYY-MM-DD
            checkoutDate = checkoutDateObj.toISOString().split('T')[0];
            
            if (checkinInput) {
                checkinInput.value = checkinDate;
                console.log('Set calculated checkin input value:', checkinDate);
            }
            
            if (checkoutInput) {
                checkoutInput.value = checkoutDate;
                console.log('Set calculated checkout input value:', checkoutDate);
            }
        }
        
        // Auto-search if dates are available and valid
        if (checkinDate && checkoutDate) {
            console.log('Auto-searching hotels with dates:', checkinDate, checkoutDate);
            // Use setTimeout to ensure DOM is updated
            setTimeout(() => {
                searchHotels();
            }, 100);
        } else {
            console.log('Missing dates for hotel search:', { checkinDate, checkoutDate });
        }
    } else {
        console.log('No currentPlan available');
    }
}

// Initialize hotel dates from plan
function initializeHotelDates() {
    if (!currentPlan) return;
    
    const checkinInput = document.getElementById('hotel-checkin');
    const checkoutInput = document.getElementById('hotel-checkout');
    
    if (currentPlan.start_date && checkinInput) {
        checkinInput.value = formatDateForInput(currentPlan.start_date);
    }
    
    if (currentPlan.end_date && checkoutInput) {
        checkoutInput.value = formatDateForInput(currentPlan.end_date);
    }
}

// Format date string to YYYY-MM-DD for input[type="date"]
function formatDateForInput(dateStr) {
    if (!dateStr) {
        console.log('formatDateForInput: empty dateStr');
        return '';
    }
    
    console.log('formatDateForInput input:', dateStr, 'type:', typeof dateStr);
    
    // Convert to string if not already
    const dateString = String(dateStr).trim();
    
    // If already in YYYY-MM-DD format
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
        console.log('formatDateForInput output (YYYY-MM-DD):', dateString);
        return dateString;
    }
    
    // If in DD/MM/YYYY format
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateString)) {
        const [day, month, year] = dateString.split('/');
        const formatted = `${year}-${month}-${day}`;
        console.log('formatDateForInput output (from DD/MM/YYYY):', formatted);
        return formatted;
    }
    
    // Try to parse as Date object
    try {
        const date = new Date(dateString);
        if (!isNaN(date.getTime())) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const formatted = `${year}-${month}-${day}`;
            console.log('formatDateForInput output (from Date parsing):', formatted);
            return formatted;
        }
    } catch (e) {
        console.error('formatDateForInput: Failed to parse date:', e);
    }
    
    console.log('formatDateForInput: Could not format date:', dateString);
    return '';
}

// Search hotels
async function searchHotels() {
    const planId = getPlanIdFromUrl();
    if (!planId) {
        showError('Không tìm thấy ID kế hoạch');
        return;
    }
    
    const checkin = document.getElementById('hotel-checkin')?.value;
    const checkout = document.getElementById('hotel-checkout')?.value;
    
    if (!checkin || !checkout) {
        showError('Vui lòng chọn ngày nhận phòng và trả phòng');
        return;
    }
    
    // Show loading
    const resultsContainer = document.getElementById('hotel-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="text-center py-12">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                <p class="text-gray-500 dark:text-gray-400 mt-4">Đang tìm kiếm khách sạn...</p>
            </div>
        `;
    }
    
    try {
        const response = await fetch(`/api/plans/${planId}/search-hotels`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                checkin_date: checkin,
                checkout_date: checkout
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.hotels) {
            renderHotelResults(data.hotels);
        } else {
            showError(data.error || 'Không tìm thấy khách sạn');
        }
    } catch (error) {
        console.error('Error searching hotels:', error);
        showError('Không thể tìm kiếm khách sạn');
    }
}

// Render hotel search results
function renderHotelResults(hotels) {
    const resultsContainer = document.getElementById('hotel-results');
    if (!resultsContainer) return;
    
    if (!hotels || hotels.length === 0) {
        resultsContainer.innerHTML = `
            <div class="text-center py-12">
                <span class="material-symbols-outlined text-6xl text-gray-400">hotel</span>
                <p class="text-gray-500 dark:text-gray-400 mt-4">Không tìm thấy khách sạn phù hợp</p>
            </div>
        `;
        return;
    }
    
    resultsContainer.innerHTML = hotels.map(hotel => `
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow">
            <div class="md:flex">
                <div class="md:w-48 h-48 md:h-auto">
                    <img src="${hotel.image_url || '/static/images/hotel-placeholder.jpg'}" 
                         alt="${hotel.name}" 
                         class="w-full h-full object-cover" />
                </div>
                <div class="p-6 flex-1">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <h3 class="text-lg font-bold text-gray-900 dark:text-white">${hotel.name}</h3>
                            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                <span class="material-symbols-outlined text-sm align-middle">location_on</span>
                                ${hotel.address || 'Địa chỉ không có'}
                            </p>
                            <div class="flex items-center gap-2 mt-2">
                                <div class="flex text-yellow-400">
                                    ${renderStars(hotel.star_rating || 0)}
                                </div>
                                <span class="text-sm text-gray-600 dark:text-gray-400">
                                    ${hotel.review_score ? `${hotel.review_score}/10` : 'Chưa có đánh giá'}
                                </span>
                            </div>
                        </div>
                        <div class="text-right ml-4">
                            <p class="text-2xl font-bold text-primary">${formatPrice(hotel.price)}</p>
                            <p class="text-sm text-gray-500 dark:text-gray-400">/đêm</p>
                        </div>
                    </div>
                    <div class="mt-4 flex justify-end">
                        <button onclick='selectHotel(${JSON.stringify(hotel)})' 
                                class="px-6 py-2 bg-primary hover:bg-primary/90 text-white font-semibold rounded-lg transition-colors">
                            Chọn khách sạn này
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Render star rating
function renderStars(rating) {
    const fullStars = Math.floor(rating);
    const stars = [];
    for (let i = 0; i < 5; i++) {
        if (i < fullStars) {
            stars.push('<span class="material-symbols-outlined text-sm">star</span>');
        } else {
            stars.push('<span class="material-symbols-outlined text-sm text-gray-300">star</span>');
        }
    }
    return stars.join('');
}

// Format price to VND
function formatPrice(price) {
    if (!price) return '0 ₫';
    return parseInt(price).toLocaleString('vi-VN') + ' ₫';
}

// Calculate number of nights between two dates
function calculateNights(checkin, checkout) {
    if (!checkin || !checkout) return 0;
    const start = new Date(checkin);
    const end = new Date(checkout);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

// Select hotel
async function selectHotel(hotel) {
    const planId = getPlanIdFromUrl();
    if (!planId) {
        showError('Không tìm thấy ID kế hoạch');
        return;
    }
    
    const checkin = document.getElementById('hotel-checkin')?.value;
    const checkout = document.getElementById('hotel-checkout')?.value;
    
    try {
        const response = await fetch(`/api/plans/${planId}/hotel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ...hotel,
                checkin_date: checkin,
                checkout_date: checkout
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Reload hotel data from database to get calculated total_price
            const hotelResponse = await fetch(`/api/plans/${planId}/hotel`);
            const hotelData = await hotelResponse.json();
            
            if (hotelData.success && hotelData.hotel) {
                showSelectedHotel(hotelData.hotel);
            } else {
                // Fallback: calculate and show with original hotel data
                const nights = calculateNights(checkin, checkout);
                showSelectedHotel({
                    ...hotel,
                    checkin_date: checkin,
                    checkout_date: checkout,
                    number_of_nights: nights,
                    total_price: (hotel.price || 0) * nights
                });
            }
            
            showSuccess('Đã chọn khách sạn thành công!');
            // Summary tab will auto-update when user switches to it
        } else {
            showError(data.error || 'Không thể chọn khách sạn');
        }
    } catch (error) {
        console.error('Error selecting hotel:', error);
        showError('Không thể chọn khách sạn');
    }
}

// Show selected hotel card - render full hotel card at top of hotel tab
function showSelectedHotel(hotel) {
    const selectedContainer = document.getElementById('selected-hotel-container');
    
    if (!selectedContainer) return;
    
    // Build full hotel card HTML (similar to search results)
    selectedContainer.innerHTML = `
        <div class="bg-green-50 dark:bg-green-900/20 border-2 border-green-500 rounded-xl overflow-hidden shadow-lg mb-6">
            <div class="bg-green-500 text-white px-4 py-2 flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined">check_circle</span>
                    <span class="font-bold">Khách sạn đã chọn</span>
                </div>
                <button onclick="clearSelectedHotel()" 
                        class="text-white hover:text-green-100 transition-colors">
                    <span class="material-symbols-outlined">close</span>
                </button>
            </div>
            <div class="bg-white dark:bg-gray-800">
                <div class="md:flex">
                    <div class="md:w-48 h-48 md:h-auto">
                        <img src="${hotel.image_url || hotel.images?.[0] || '/static/images/hotel-placeholder.jpg'}" 
                             alt="${hotel.name}" 
                             class="w-full h-full object-cover" />
                    </div>
                    <div class="p-6 flex-1">
                        <div class="flex justify-between items-start">
                            <div class="flex-1">
                                <h3 class="text-lg font-bold text-gray-900 dark:text-white">${hotel.name}</h3>
                                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                    <span class="material-symbols-outlined text-sm align-middle">location_on</span>
                                    ${hotel.address || 'Địa chỉ không có'}
                                </p>
                                <div class="flex items-center gap-2 mt-2">
                                    <div class="flex text-yellow-400">
                                        ${renderStars(hotel.star_rating || 0)}
                                    </div>
                                    <span class="text-sm text-gray-600 dark:text-gray-400">
                                        ${hotel.review_score ? `${hotel.review_score}/10` : 'Chưa có đánh giá'}
                                    </span>
                                </div>
                                <div class="mt-3 flex items-center gap-4 text-sm">
                                    <span class="text-gray-600 dark:text-gray-400">
                                        <span class="material-symbols-outlined text-sm align-middle">calendar_today</span>
                                        ${hotel.checkin_date || ''} → ${hotel.checkout_date || ''}
                                    </span>
                                    <span class="text-gray-600 dark:text-gray-400">
                                        <span class="material-symbols-outlined text-sm align-middle">hotel</span>
                                        ${hotel.number_of_nights || 0} đêm
                                    </span>
                                </div>
                            </div>
                            <div class="text-right ml-4">
                                <p class="text-2xl font-bold text-green-600">${formatPrice(hotel.total_price)}</p>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Tổng cộng</p>
                                ${hotel.price_per_night ? `<p class="text-sm text-gray-600 dark:text-gray-400 mt-1">${formatPrice(hotel.price_per_night)}/đêm</p>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    selectedContainer.classList.remove('hidden');
}

// Load selected hotel on page load
async function loadSelectedHotel() {
    const planId = getPlanIdFromUrl();
    if (!planId) return;
    
    try {
        const response = await fetch(`/api/plans/${planId}/hotel`);
        const data = await response.json();
        
        if (data.success && data.hotel) {
            showSelectedHotel(data.hotel);
        }
    } catch (error) {
        console.error('Error loading selected hotel:', error);
    }
}

// Clear selected hotel
async function clearSelectedHotel() {
    const planId = getPlanIdFromUrl();
    if (!planId) return;
    
    try {
        const response = await fetch(`/api/plans/${planId}/hotel`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            const selectedContainer = document.getElementById('selected-hotel-container');
            if (selectedContainer) {
                selectedContainer.innerHTML = '';
                selectedContainer.classList.add('hidden');
            }
            showSuccess('Đã xóa khách sạn đã chọn');
        }
    } catch (error) {
        console.error('Error clearing hotel:', error);
        showError('Không thể xóa khách sạn');
    }
}

// ===== FLIGHT FUNCTIONS =====

// Initialize flight tab
async function initializeFlightTab() {
    console.log('=== initializeFlightTab called ===');
    console.log('currentPlan:', currentPlan);
    
    // Load selected flights first
    await loadSelectedFlights();
    
    // Fill in data from plan and auto-search
    if (currentPlan) {
        const originInput = document.getElementById('flight-origin');
        const destinationInput = document.getElementById('flight-destination');
        const departureInput = document.getElementById('flight-departure');
        const returnInput = document.getElementById('flight-return');
        
        // Get user's location from localStorage (set during chat permission)
        const userLocation = localStorage.getItem('userLocation') || 'SGN';
        
        // Set origin from user location
        if (originInput) {
            originInput.value = userLocation;
        }
        
        // Set destination from plan
        if (destinationInput && currentPlan.destination) {
            destinationInput.value = currentPlan.destination;
        }
        
        // Calculate dates: departure is 1 day before start_date, return is 1 day after end_date
        let departureDate = '';
        let returnDate = '';
        
        if (currentPlan.start_date) {
            const startDate = new Date(currentPlan.start_date);
            const departureDateObj = new Date(startDate.getTime() - (1 * 24 * 60 * 60 * 1000)); // 1 day before
            departureDate = departureDateObj.toISOString().split('T')[0];
            
            if (departureInput) {
                departureInput.value = departureDate;
            }
        }
        
        if (currentPlan.end_date) {
            const endDate = new Date(currentPlan.end_date);
            const returnDateObj = new Date(endDate.getTime() + (1 * 24 * 60 * 60 * 1000)); // 1 day after
            returnDate = returnDateObj.toISOString().split('T')[0];
            
            if (returnInput) {
                returnInput.value = returnDate;
            }
        }
        
        // Auto-search flights if we have all required data
        if (userLocation && currentPlan.destination && departureDate && returnDate) {
            console.log('Auto-searching flights:', {
                origin: userLocation,
                destination: currentPlan.destination,
                departure: departureDate,
                return: returnDate
            });
            
            // Use setTimeout to ensure DOM is updated
            setTimeout(() => {
                autoSearchFlights(userLocation, currentPlan.destination, departureDate, returnDate);
            }, 100);
        }
    }
}

// Auto-search flights on tab initialization
async function autoSearchFlights(origin, destination, departureDate, returnDate) {
    const planId = getPlanIdFromUrl();
    if (!planId) return;
    
    // Show loading
    const resultsContainer = document.getElementById('flight-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="text-center py-12">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                <p class="text-gray-500 dark:text-gray-400 mt-4">Đang tự động tìm kiếm chuyến bay phù hợp...</p>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">Tìm chuyến bay đi và về cho bạn</p>
            </div>
        `;
    }
    
    try {
        // Search outbound flight (origin -> destination)
        const outboundResponse = await fetch(`/api/plans/${planId}/search-flights`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                origin: origin,
                destination: destination,
                departure_date: departureDate,
                return_date: null, // One-way for outbound
                adults: 1,
                children: 0,
                infants: 0
            })
        });
        
        const outboundData = await outboundResponse.json();
        
        // Search return flight (destination -> origin)
        const returnResponse = await fetch(`/api/plans/${planId}/search-flights`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                origin: destination,
                destination: origin,
                departure_date: returnDate,
                return_date: null, // One-way for return
                adults: 1,
                children: 0,
                infants: 0
            })
        });
        
        const returnData = await returnResponse.json();
        
        // Combine results
        let allFlights = [];
        
        if (outboundData.success && outboundData.flights) {
            // Mark outbound flights
            outboundData.flights.forEach(flight => {
                flight.flight_direction = 'outbound';
                flight.flight_label = 'Chuyến đi';
            });
            allFlights = allFlights.concat(outboundData.flights);
        }
        
        if (returnData.success && returnData.flights) {
            // Mark return flights
            returnData.flights.forEach(flight => {
                flight.flight_direction = 'return';
                flight.flight_label = 'Chuyến về';
            });
            allFlights = allFlights.concat(returnData.flights);
        }
        
        if (allFlights.length > 0) {
            renderCombinedFlightResults(allFlights);
        } else {
            if (resultsContainer) {
                resultsContainer.innerHTML = `
                    <div class="text-center py-12">
                        <span class="material-symbols-outlined text-6xl text-gray-400">flight</span>
                        <p class="text-gray-500 dark:text-gray-400 mt-4">Không tìm thấy chuyến bay phù hợp</p>
                        <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">Vui lòng thử tìm kiếm với thông tin khác</p>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error auto-searching flights:', error);
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="text-center py-12">
                    <span class="material-symbols-outlined text-6xl text-red-400">error</span>
                    <p class="text-gray-500 dark:text-gray-400 mt-4">Không thể tìm kiếm chuyến bay</p>
                    <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">${error.message}</p>
                    <button onclick="searchFlights()" class="mt-4 px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90">
                        Thử lại
                    </button>
                </div>
            `;
        }
    }
}

// Render combined flight results (outbound + return)
function renderCombinedFlightResults(flights) {
    const resultsContainer = document.getElementById('flight-results');
    if (!resultsContainer) return;
    
    // Separate outbound and return flights
    const outboundFlights = flights.filter(f => f.flight_direction === 'outbound');
    const returnFlights = flights.filter(f => f.flight_direction === 'return');
    
    let html = '';
    
    // Outbound flights section
    if (outboundFlights.length > 0) {
        html += `
            <div class="mb-8">
                <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <span class="material-symbols-outlined text-primary">flight_takeoff</span>
                    Chuyến bay đi (${outboundFlights.length} chuyến)
                </h3>
                <div class="space-y-4">
                    ${outboundFlights.map(flight => renderSingleFlight(flight, 'outbound')).join('')}
                </div>
            </div>
        `;
    }
    
    // Return flights section
    if (returnFlights.length > 0) {
        html += `
            <div class="mb-8">
                <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <span class="material-symbols-outlined text-primary">flight_land</span>
                    Chuyến bay về (${returnFlights.length} chuyến)
                </h3>
                <div class="space-y-4">
                    ${returnFlights.map(flight => renderSingleFlight(flight, 'return')).join('')}
                </div>
            </div>
        `;
    }
    
    resultsContainer.innerHTML = html;
}

// Render a single flight card
function renderSingleFlight(flight, flightType) {
    return `
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <!-- Flight Info -->
                <div class="flex-1">
                    <div class="flex items-center gap-4 mb-3">
                        ${flight.carrier_logo ? `<img src="${flight.carrier_logo}" alt="${flight.carrier_name}" class="h-8 w-8 object-contain" />` : ''}
                        <div>
                            <h3 class="font-bold text-gray-900 dark:text-white">${flight.carrier_name}</h3>
                            <p class="text-sm text-gray-500">${flight.flight_number}</p>
                        </div>
                    </div>
                    
                    <div class="flex items-center gap-4">
                        <div class="text-center">
                            <p class="text-2xl font-bold text-gray-900 dark:text-white">${formatTime(flight.departure_time)}</p>
                            <p class="text-sm text-gray-600 dark:text-gray-400">${flight.origin_code}</p>
                        </div>
                        
                        <div class="flex-1 text-center">
                            <p class="text-sm text-gray-500">${formatDuration(flight.duration)}</p>
                            <div class="relative h-0.5 bg-gray-300 my-2">
                                <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white px-2">
                                    ${flight.stops === 0 ? '✈️ Bay thẳng' : `${flight.stops} điểm dừng`}
                                </div>
                            </div>
                        </div>
                        
                        <div class="text-center">
                            <p class="text-2xl font-bold text-gray-900 dark:text-white">${formatTime(flight.arrival_time)}</p>
                            <p class="text-sm text-gray-600 dark:text-gray-400">${flight.destination_code}</p>
                        </div>
                    </div>
                    
                    ${flight.overnight_flight ? '<p class="text-xs text-orange-600 mt-2">⚠️ Bay qua đêm</p>' : ''}
                </div>
                
                <!-- Price and Action -->
                <div class="text-right md:ml-6">
                    <p class="text-3xl font-bold text-primary mb-2">${formatPrice(flight.price_vnd)}</p>
                    <p class="text-sm text-gray-500 mb-4">${flight.cabin_class}</p>
                    <button onclick='selectFlight(${JSON.stringify(flight).replace(/'/g, "&apos;")}, "${flightType}")' 
                            class="px-6 py-2 bg-primary hover:bg-primary/90 text-white font-semibold rounded-lg transition-colors whitespace-nowrap">
                        Chọn chuyến ${flightType === 'outbound' ? 'đi' : 'về'}
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Search flights
async function searchFlights() {
    const planId = getPlanIdFromUrl();
    if (!planId) {
        showError('Không tìm thấy ID kế hoạch');
        return;
    }
    
    const origin = document.getElementById('flight-origin')?.value;
    const destination = document.getElementById('flight-destination')?.value;
    const departure = document.getElementById('flight-departure')?.value;
    const returnDate = document.getElementById('flight-return')?.value;
    const adults = document.getElementById('flight-adults')?.value || 1;
    
    if (!origin || !destination || !departure) {
        showError('Vui lòng điền đầy đủ thông tin điểm đi, điểm đến và ngày đi');
        return;
    }
    
    // Show loading
    const resultsContainer = document.getElementById('flight-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="text-center py-12">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                <p class="text-gray-500 dark:text-gray-400 mt-4">Đang tìm kiếm chuyến bay...</p>
            </div>
        `;
    }
    
    try {
        const response = await fetch(`/api/plans/${planId}/search-flights`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                origin: origin,
                destination: destination,
                departure_date: departure,
                return_date: returnDate || null,
                adults: parseInt(adults),
                children: 0,
                infants: 0
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.flights) {
            renderFlightResults(data.flights, returnDate ? 'round-trip' : 'one-way');
        } else {
            showError(data.error || 'Không tìm thấy chuyến bay');
        }
    } catch (error) {
        console.error('Error searching flights:', error);
        showError('Không thể tìm kiếm chuyến bay');
    }
}

// Render flight search results
function renderFlightResults(flights, tripType) {
    const resultsContainer = document.getElementById('flight-results');
    if (!resultsContainer) return;
    
    if (!flights || flights.length === 0) {
        resultsContainer.innerHTML = `
            <div class="text-center py-12">
                <span class="material-symbols-outlined text-6xl text-gray-400">flight</span>
                <p class="text-gray-500 dark:text-gray-400 mt-4">Không tìm thấy chuyến bay phù hợp</p>
            </div>
        `;
        return;
    }
    
    resultsContainer.innerHTML = flights.map(flight => `
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 mb-4 hover:shadow-lg transition-shadow">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <!-- Flight Info -->
                <div class="flex-1">
                    <div class="flex items-center gap-4 mb-3">
                        ${flight.carrier_logo ? `<img src="${flight.carrier_logo}" alt="${flight.carrier_name}" class="h-8 w-8 object-contain" />` : ''}
                        <div>
                            <h3 class="font-bold text-gray-900 dark:text-white">${flight.carrier_name}</h3>
                            <p class="text-sm text-gray-500">${flight.flight_number}</p>
                        </div>
                    </div>
                    
                    <div class="flex items-center gap-4">
                        <div class="text-center">
                            <p class="text-2xl font-bold text-gray-900 dark:text-white">${formatTime(flight.departure_time)}</p>
                            <p class="text-sm text-gray-600 dark:text-gray-400">${flight.origin_code}</p>
                        </div>
                        
                        <div class="flex-1 text-center">
                            <p class="text-sm text-gray-500">${formatDuration(flight.duration)}</p>
                            <div class="relative h-0.5 bg-gray-300 my-2">
                                <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white px-2">
                                    ${flight.stops === 0 ? '✈️ Bay thẳng' : `${flight.stops} điểm dừng`}
                                </div>
                            </div>
                        </div>
                        
                        <div class="text-center">
                            <p class="text-2xl font-bold text-gray-900 dark:text-white">${formatTime(flight.arrival_time)}</p>
                            <p class="text-sm text-gray-600 dark:text-gray-400">${flight.destination_code}</p>
                        </div>
                    </div>
                    
                    ${flight.overnight_flight ? '<p class="text-xs text-orange-600 mt-2">⚠️ Bay qua đêm</p>' : ''}
                </div>
                
                <!-- Price and Action -->
                <div class="text-right md:ml-6">
                    <p class="text-3xl font-bold text-primary mb-2">${formatPrice(flight.price_vnd)}</p>
                    <p class="text-sm text-gray-500 mb-4">${flight.cabin_class}</p>
                    <button onclick='selectFlight(${JSON.stringify(flight).replace(/'/g, "&apos;")}, "outbound")' 
                            class="px-6 py-2 bg-primary hover:bg-primary/90 text-white font-semibold rounded-lg transition-colors whitespace-nowrap">
                        Chọn chuyến bay
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Format time from ISO string
function formatTime(isoString) {
    if (!isoString) return '--:--';
    const date = new Date(isoString);
    return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
}

// Format duration in minutes to hours and minutes
function formatDuration(minutes) {
    if (!minutes) return '--';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}g ${mins}p`;
}

// Select flight
async function selectFlight(flight, flightType) {
    const planId = getPlanIdFromUrl();
    if (!planId) {
        showError('Không tìm thấy ID kế hoạch');
        return;
    }
    
    try {
        const response = await fetch(`/api/plans/${planId}/flight`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ...flight,
                flight_type: flightType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Đã chọn chuyến bay thành công!');
            await loadSelectedFlights();
        } else {
            showError(data.error || 'Không thể chọn chuyến bay');
        }
    } catch (error) {
        console.error('Error selecting flight:', error);
        showError('Không thể chọn chuyến bay');
    }
}

// Load selected flights
async function loadSelectedFlights() {
    const planId = getPlanIdFromUrl();
    if (!planId) return;
    
    try {
        const response = await fetch(`/api/plans/${planId}/flights`);
        const data = await response.json();
        
        if (data.success && data.flights && data.flights.length > 0) {
            showSelectedFlights(data.flights);
        }
    } catch (error) {
        console.error('Error loading selected flights:', error);
    }
}

// Show selected flights
function showSelectedFlights(flights) {
    const selectedContainer = document.getElementById('selected-flights-container');
    if (!selectedContainer) return;
    
    const outbound = flights.find(f => f.flight_type === 'outbound');
    const returnFlight = flights.find(f => f.flight_type === 'return');
    
    let html = '<div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-xl p-6 mb-6">';
    html += '<h3 class="text-lg font-bold text-green-800 dark:text-green-300 mb-4 flex items-center gap-2">';
    html += '<span class="material-symbols-outlined">check_circle</span> Chuyến bay đã chọn';
    html += '</h3>';
    
    if (outbound) {
        html += `
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 mb-3">
                <p class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Chuyến đi</p>
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        ${outbound.carrier_logo ? `<img src="${outbound.carrier_logo}" alt="${outbound.carrier_name}" class="h-6 w-6" />` : ''}
                        <div>
                            <p class="font-bold text-gray-900 dark:text-white">${outbound.carrier_name} ${outbound.flight_number}</p>
                            <p class="text-sm text-gray-600">${outbound.origin_code} → ${outbound.destination_code}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="font-bold text-gray-900 dark:text-white">${formatTime(outbound.departure_time)} - ${formatTime(outbound.arrival_time)}</p>
                        <p class="text-sm text-primary font-semibold">${formatPrice(outbound.price)}</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    if (returnFlight) {
        html += `
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 mb-3">
                <p class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Chuyến về</p>
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        ${returnFlight.carrier_logo ? `<img src="${returnFlight.carrier_logo}" alt="${returnFlight.carrier_name}" class="h-6 w-6" />` : ''}
                        <div>
                            <p class="font-bold text-gray-900 dark:text-white">${returnFlight.carrier_name} ${returnFlight.flight_number}</p>
                            <p class="text-sm text-gray-600">${returnFlight.origin_code} → ${returnFlight.destination_code}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="font-bold text-gray-900 dark:text-white">${formatTime(returnFlight.departure_time)} - ${formatTime(returnFlight.arrival_time)}</p>
                        <p class="text-sm text-primary font-semibold">${formatPrice(returnFlight.price)}</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    html += `
        <button onclick="clearSelectedFlights()" class="mt-3 px-4 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors text-sm font-semibold">
            Xóa chuyến bay đã chọn
        </button>
    </div>`;
    
    selectedContainer.innerHTML = html;
    selectedContainer.classList.remove('hidden');
}

// Clear selected flights
async function clearSelectedFlights() {
    const planId = getPlanIdFromUrl();
    if (!planId) return;
    
    try {
        const response = await fetch(`/api/plans/${planId}/flights`);
        const data = await response.json();
        
        if (data.success && data.flights) {
            // Delete each flight
            for (const flight of data.flights) {
                await fetch(`/api/plans/${planId}/flight/${flight.id}`, {
                    method: 'DELETE'
                });
            }
            
            const selectedContainer = document.getElementById('selected-flights-container');
            if (selectedContainer) {
                selectedContainer.innerHTML = '';
                selectedContainer.classList.add('hidden');
            }
            showSuccess('Đã xóa chuyến bay đã chọn');
        }
    } catch (error) {
        console.error('Error clearing flights:', error);
        showError('Không thể xóa chuyến bay');
    }
}

// Render summary tab
function renderSummaryTab(plan) {
    // Update destination and duration
    const destEl = document.getElementById('summary-destination');
    const durationEl = document.getElementById('summary-duration');
    const startDateEl = document.getElementById('summary-start-date');
    const groupEl = document.getElementById('summary-group');
    
    if (destEl) destEl.textContent = plan.destination || '-';
    if (durationEl) durationEl.textContent = `${plan.duration_days || 0} ngày`;
    if (startDateEl) startDateEl.textContent = plan.start_date || '-';
    if (groupEl) groupEl.textContent = plan.group_type || '-';
    
    // Calculate ACTUAL cost from itinerary activities
    const itinerary = Array.isArray(plan.itinerary) ? plan.itinerary : [];
    let actualCost = 0;
    
    itinerary.forEach(day => {
        const activities = day.activities || [];
        activities.forEach(activity => {
            actualCost += (activity.cost || 0);
        });
    });
    
    console.log('Calculated actual cost from itinerary:', actualCost);
    console.log('Plan budget:', plan.budget);
    console.log('Plan total_cost (from DB):', plan.total_cost);
    
    // Load hotel and flight costs, then update total
    loadAllCosts(actualCost, plan.budget);
}

// Load all costs (hotel + flights) and update total
async function loadAllCosts(activitiesCost, budget) {
    const planId = getPlanIdFromUrl();
    if (!planId) return;
    
    try {
        // Load hotel cost
        const hotelResponse = await fetch(`/api/plans/${planId}/hotel`);
        const hotelData = await hotelResponse.json();
        
        let hotelCost = 0;
        if (hotelData.success && hotelData.hotel && hotelData.hotel.total_price) {
            hotelCost = hotelData.hotel.total_price;
        }
        
        // Load flight costs
        const flightResponse = await fetch(`/api/plans/${planId}/flights`);
        const flightData = await flightResponse.json();
        
        let flightCost = 0;
        if (flightData.success && flightData.flights) {
            flightData.flights.forEach(flight => {
                flightCost += (flight.price || 0);
            });
        }
        
        // Calculate total actual cost (activities + hotel + flights)
        const totalActualCost = activitiesCost + hotelCost + flightCost;
        
        // Update UI - Cost breakdown table
        const activitiesEl = document.getElementById('cost-activities');
        const hotelEl = document.getElementById('cost-hotel');
        const flightsEl = document.getElementById('cost-flights');
        const totalEl = document.getElementById('cost-total');
        
        if (activitiesEl) activitiesEl.textContent = formatPrice(activitiesCost);
        if (hotelEl) hotelEl.textContent = formatPrice(hotelCost);
        if (flightsEl) flightsEl.textContent = formatPrice(flightCost);
        if (totalEl) totalEl.textContent = formatPrice(totalActualCost);
        
        // Update stats at top of Summary tab
        const statsContainer = document.getElementById('day-stats');
        if (statsContainer && budget !== undefined) {
            const savings = budget - totalActualCost;
            const isOverBudget = savings < 0;
            
            statsContainer.innerHTML = `
                <div class="flex flex-col gap-2 rounded-xl p-6 border border-[#dbe2e6] dark:border-gray-700 bg-white dark:bg-gray-800">
                    <p class="text-[#111618] dark:text-gray-300 text-base font-medium leading-normal">Tổng chi phí thực tế</p>
                    <p class="text-[#111618] dark:text-white tracking-light text-2xl font-bold leading-tight">${formatCurrency(totalActualCost)}</p>
                </div>
                <div class="flex flex-col gap-2 rounded-xl p-6 border border-[#dbe2e6] dark:border-gray-700 bg-white dark:bg-gray-800">
                    <p class="text-[#111618] dark:text-gray-300 text-base font-medium leading-normal">Ngân sách dự kiến</p>
                    <p class="text-[#111618] dark:text-white tracking-light text-2xl font-bold leading-tight">${formatCurrency(budget)}</p>
                </div>
                <div class="flex flex-col gap-2 rounded-xl p-6 border border-[#dbe2e6] dark:border-gray-700 bg-white dark:bg-gray-800">
                    <p class="text-[#111618] dark:text-gray-300 text-base font-medium leading-normal">${isOverBudget ? 'Vượt ngân sách' : 'Tiết kiệm'}</p>
                    <p class="text-[#111618] dark:text-white tracking-light text-2xl font-bold leading-tight ${isOverBudget ? 'text-red-600' : 'text-green-600'}">${formatCurrency(Math.abs(savings))}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading costs:', error);
    }
}

// Legacy function for backward compatibility - now calls loadAllCosts
async function loadHotelCost(activitiesCost, budget) {
    await loadAllCosts(activitiesCost, budget);
}

// Confirm plan
async function confirmPlan() {
    const planId = getPlanIdFromUrl();
    if (!planId) return;
    
    try {
        const response = await fetch(`/api/plans/${planId}/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Đã xác nhận kế hoạch thành công!');
            // Reload page to update status
            setTimeout(() => location.reload(), 1500);
        } else {
            showError(data.error || 'Không thể xác nhận kế hoạch');
        }
    } catch (error) {
        console.error('Error confirming plan:', error);
        showError('Không thể xác nhận kế hoạch');
    }
}

// Show success notification
function showSuccess(message) {
    // Reuse the notification function from main_chat.js pattern
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 px-4 py-3 rounded-lg shadow-lg z-50 transition-opacity duration-300 bg-green-500 text-white';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

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
    
    // Initialize hotel dates
    initializeHotelDates();
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
        let title = dayData.title || 'Chi tiết lịch trình';
        // Remove duplicate "Ngày X: " prefix if it exists
        title = title.replace(/^Ngày\s+\d+:\s*/i, '');
        heading.textContent = `Ngày ${dayNum}: ${title}`;
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
                <div class="flex items-center gap-2">
                    <p class="text-lg font-semibold text-[#111618] dark:text-white">${title}</p>
                    ${location ? `<a href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(location)}" target="_blank" rel="noopener noreferrer" class="text-primary hover:text-primary/80 transition-colors" title="Xem trên Google Maps"><span class="material-symbols-outlined text-xl">map</span></a>` : ''}
                </div>
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

// Update map with Google Maps Embed showing route
function updateMapImage(destination) {
    const mapImage = document.getElementById('map-image');
    if (!mapImage) return;
    
    // Get current day data to extract locations
    const itinerary = typeof currentPlan.itinerary === 'string' ? JSON.parse(currentPlan.itinerary) : currentPlan.itinerary;
    if (!Array.isArray(itinerary)) return;
    
    const dayData = itinerary.find(d => (d.day || itinerary.indexOf(d) + 1) === currentDay);
    if (!dayData) return;
    
    const activities = dayData.activities || [];
    const locations = activities
        .filter(act => act.location)
        .map(act => act.location);
    
    if (locations.length === 0) {
        // No locations, show static image
        mapImage.style.backgroundImage = `url("${getDestinationImage(destination)}")`;
        mapImage.innerHTML = '';
        return;
    }
    
    // Build Google Maps Embed URL with directions
    let embedUrl = `https://www.google.com/maps/embed/v1/directions?key=${googleMapsApiKey}`;
    
    if (locations.length === 1) {
        // Single location - show place mode
        embedUrl = `https://www.google.com/maps/embed/v1/place?key=${googleMapsApiKey}&q=${encodeURIComponent(locations[0])}`;
    } else {
        // Multiple locations - show directions
        embedUrl += `&origin=${encodeURIComponent(locations[0])}`;
        embedUrl += `&destination=${encodeURIComponent(locations[locations.length - 1])}`;
        
        // Add waypoints for intermediate locations
        if (locations.length > 2) {
            const waypoints = locations.slice(1, -1).join('|');
            embedUrl += `&waypoints=${encodeURIComponent(waypoints)}`;
        }
        
        embedUrl += '&mode=driving'; // or walking, transit
    }
    
    // Clear background image and set iframe
    mapImage.style.backgroundImage = '';
    mapImage.innerHTML = `
        <iframe
            width="100%"
            height="100%"
            style="border:0; border-radius: 0.75rem;"
            loading="lazy"
            allowfullscreen
            referrerpolicy="no-referrer-when-downgrade"
            src="${embedUrl}">
        </iframe>
    `;
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
            // Redirect to edit plan page
            window.location.href = `/plans/${planId}/edit`;
        }
    });
}

// Download PDF button
const downloadButton = document.getElementById('download-button');
if (downloadButton) {
    downloadButton.addEventListener('click', async () => {
        const planId = getPlanIdFromUrl();
        if (!planId) {
            alert('Không tìm thấy ID kế hoạch!');
            return;
        }
        
        try {
            // Show loading state
            downloadButton.disabled = true;
            const originalHTML = downloadButton.innerHTML;
            downloadButton.innerHTML = '<span class="material-symbols-outlined animate-spin">progress_activity</span><span class="truncate">Đang tạo PDF...</span>';
            
            // Call API to download PDF
            const response = await fetch(`/api/plans/${planId}/download-pdf`);
            
            if (!response.ok) {
                throw new Error('Không thể tải PDF');
            }
            
            // Get PDF blob
            const blob = await response.blob();
            
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentPlan?.plan_name || 'ke-hoach-du-lich'}.pdf`;
            document.body.appendChild(a);
            a.click();
            
            // Cleanup
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Reset button
            downloadButton.innerHTML = originalHTML;
            downloadButton.disabled = false;
            
        } catch (error) {
            console.error('Error downloading PDF:', error);
            alert('Có lỗi khi tải PDF. Vui lòng thử lại!');
            
            // Reset button
            downloadButton.innerHTML = '<span class="material-symbols-outlined">download</span><span class="truncate">Tải xuống PDF</span>';
            downloadButton.disabled = false;
        }
    });
}

// ===== REFERENCES MODAL FUNCTIONS =====

/**
 * Open the references modal and populate it with search sources
 */
function openReferencesModal() {
    const modal = document.getElementById('referencesModal');
    if (!modal) return;
    
    // Populate references
    populateReferences();
    
    // Show modal
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

/**
 * Close the references modal
 */
function closeReferencesModal() {
    const modal = document.getElementById('referencesModal');
    if (!modal) return;
    
    modal.classList.add('hidden');
    document.body.style.overflow = '';
}

/**
 * Populate the references list from plan data
 */
function populateReferences() {
    const referencesList = document.getElementById('referencesList');
    if (!referencesList) return;
    
    // Check if plan has search sources
    if (!currentPlan || !currentPlan.search_sources || currentPlan.search_sources.length === 0) {
        referencesList.innerHTML = `
            <div class="text-center py-12">
                <span class="material-symbols-outlined text-6xl text-gray-400">search_off</span>
                <p class="text-gray-500 dark:text-gray-400 mt-4">Không có nguồn tham khảo cho kế hoạch này</p>
                <p class="text-sm text-gray-400 dark:text-gray-500 mt-2">Kế hoạch có thể được tạo thủ công hoặc từ dữ liệu mẫu</p>
            </div>
        `;
        return;
    }
    
    // Build references HTML
    let referencesHtml = `
        <div class="mb-4">
            <p class="text-sm text-gray-600 dark:text-gray-400">
                Tìm thấy <strong>${currentPlan.search_sources.length}</strong> nguồn tham khảo
            </p>
        </div>
    `;
    
    currentPlan.search_sources.forEach((source, index) => {
        const title = source.title || 'Không có tiêu đề';
        const url = source.url || '#';
        const snippet = source.snippet || '';
        
        referencesHtml += `
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors overflow-hidden">
                <div class="flex items-start gap-3">
                    <div class="flex-shrink-0 w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                        <span class="text-primary font-bold text-sm">${index + 1}</span>
                    </div>
                    <div class="flex-1 min-w-0 overflow-hidden">
                        <h3 class="font-semibold text-gray-900 dark:text-white mb-1 line-clamp-2">
                            ${escapeHtml(title)}
                        </h3>
                        ${snippet ? `
                            <p class="text-sm text-gray-600 dark:text-gray-300 mb-2 line-clamp-2">
                                ${escapeHtml(snippet)}
                            </p>
                        ` : ''}
                        <a href="${escapeHtml(url)}" 
                           target="_blank" 
                           rel="noopener noreferrer"
                           class="flex items-start gap-1 text-sm text-primary hover:text-primary/80 transition-colors group">
                            <span class="material-symbols-outlined text-sm flex-shrink-0">link</span>
                            <span class="break-words flex-1 overflow-hidden">${escapeHtml(url)}</span>
                            <span class="material-symbols-outlined text-sm flex-shrink-0">open_in_new</span>
                        </a>
                    </div>
                </div>
            </div>
        `;
    });
    
    referencesList.innerHTML = referencesHtml;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal on outside click
document.addEventListener('click', (e) => {
    const modal = document.getElementById('referencesModal');
    if (e.target === modal) {
        closeReferencesModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeReferencesModal();
    }
});
