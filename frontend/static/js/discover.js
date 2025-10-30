// Discovery Feature - Tinder-style destination explorer
// Pexels API Integration with Swipe Gestures

const PEXELS_API_KEY = 'MUPx8XZ2LA9uUVFMCEgjAxzoVLZ6gHCG5DrhjXCbZeFDL3uEJ9De8xX5';
const PEXELS_BASE_URL = 'https://api.pexels.com/v1';
const SWIPE_THRESHOLD = 100; // pixels
const CARD_STACK_SIZE = 3;

class PexelsClient {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.cache = new Map();
    }

    async search(query, perPage = 5) {
        const cacheKey = `${query}_${perPage}`;
        
        // Check cache first
        if (this.cache.has(cacheKey)) {
            console.log('Using cached images for:', query);
            return this.cache.get(cacheKey);
        }

        // Check rate limit
        if (!this.checkRateLimit()) {
            console.warn('Rate limit approaching, using cache');
            return this.getFallbackImages(query);
        }

        try {
            const url = `${PEXELS_BASE_URL}/search?query=${encodeURIComponent(query)}&per_page=${perPage}&orientation=portrait`;
            console.log(`Fetching from Pexels: ${query}`);
            
            const response = await fetch(url, {
                headers: {
                    'Authorization': this.apiKey
                }
            });

            if (!response.ok) {
                console.error(`Pexels API error: ${response.status} ${response.statusText}`);
                throw new Error(`Pexels API error: ${response.status}`);
            }

            const data = await response.json();
            console.log(`Pexels returned ${data.photos.length} photos for "${query}"`);
            
            // Track API usage
            this.trackApiUsage();
            
            // Cache results
            this.cache.set(cacheKey, data.photos);
            
            return data.photos;
        } catch (error) {
            console.error('Pexels fetch error:', error);
            console.log('Using fallback images');
            return this.getFallbackImages(query);
        }
    }

    checkRateLimit() {
        const usage = JSON.parse(localStorage.getItem('pexels_usage') || '[]');
        const oneHourAgo = Date.now() - (60 * 60 * 1000);
        const recentRequests = usage.filter(timestamp => timestamp > oneHourAgo);
        
        return recentRequests.length < 180; // Stay under 200/hour limit
    }

    trackApiUsage() {
        const usage = JSON.parse(localStorage.getItem('pexels_usage') || '[]');
        const oneHourAgo = Date.now() - (60 * 60 * 1000);
        const recentRequests = usage.filter(timestamp => timestamp > oneHourAgo);
        
        recentRequests.push(Date.now());
        localStorage.setItem('pexels_usage', JSON.stringify(recentRequests));
    }

    getFallbackImages(query) {
        // Return placeholder image if API fails
        return [{
            id: 0,
            src: {
                portrait: `https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&h=1200&fit=crop`,
                large: `https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=940&h=650&fit=crop`
            },
            photographer: 'Pexels',
            photographer_url: 'https://www.pexels.com',
            alt: query
        }];
    }
}

class DiscoveryApp {
    constructor() {
        console.log('DiscoveryApp constructor started');
        this.pexelsClient = new PexelsClient(PEXELS_API_KEY);
        this.currentDestinations = [];
        this.currentIndex = 0;
        this.loadedImages = new Map();
        this.isAnimating = false;
        
        console.log('Initializing storage...');
        this.initializeStorage();
        
        console.log('Loading destinations...');
        this.loadDestinations();
        
        console.log('DiscoveryApp initialized successfully');
    }

    initializeStorage() {
        if (!localStorage.getItem('discover_liked_destinations')) {
            localStorage.setItem('discover_liked_destinations', JSON.stringify([]));
        }
        if (!localStorage.getItem('discover_seen_destinations')) {
            localStorage.setItem('discover_seen_destinations', JSON.stringify([]));
        }
    }

    getLikedDestinations() {
        return JSON.parse(localStorage.getItem('discover_liked_destinations') || '[]');
    }

    getSeenDestinations() {
        return JSON.parse(localStorage.getItem('discover_seen_destinations') || '[]');
    }

    addLikedDestination(destinationId) {
        const liked = this.getLikedDestinations();
        if (!liked.includes(destinationId)) {
            liked.push(destinationId);
            localStorage.setItem('discover_liked_destinations', JSON.stringify(liked));
        }
    }

    addSeenDestination(destinationId) {
        const seen = this.getSeenDestinations();
        if (!seen.includes(destinationId)) {
            seen.push(destinationId);
            localStorage.setItem('discover_seen_destinations', JSON.stringify(seen));
        }
    }

    resetProgress() {
        localStorage.setItem('discover_liked_destinations', JSON.stringify([]));
        localStorage.setItem('discover_seen_destinations', JSON.stringify([]));
        this.loadDestinations();
    }

    getUnseenDestinations() {
        const seen = this.getSeenDestinations();
        if (typeof VIETNAMESE_DESTINATIONS === 'undefined') {
            console.error('VIETNAMESE_DESTINATIONS is not defined! Make sure destinations-data.js is loaded first.');
            return [];
        }
        return VIETNAMESE_DESTINATIONS.filter(dest => !seen.includes(dest.id));
    }

    loadDestinations() {
        const unseen = this.getUnseenDestinations();
        console.log(`Unseen destinations: ${unseen.length}`);
        
        if (unseen.length === 0) {
            console.log('No unseen destinations, showing empty state');
            this.showEmptyState();
            return;
        }

        // Shuffle unseen destinations
        this.currentDestinations = this.shuffleArray([...unseen]);
        this.currentIndex = 0;
        
        console.log(`Shuffled ${this.currentDestinations.length} destinations, starting preload...`);
        
        // Preload first 3 destinations
        this.preloadDestinations();
    }

    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    async preloadDestinations() {
        console.log('preloadDestinations started');
        const promises = [];
        const count = Math.min(CARD_STACK_SIZE, this.currentDestinations.length);
        console.log(`Preloading ${count} destinations`);
        
        for (let i = 0; i < count; i++) {
            promises.push(this.loadDestinationImages(i));
        }
        
        try {
            await Promise.all(promises);
            console.log('All images preloaded successfully');
            this.renderCards();
        } catch (error) {
            console.error('Error preloading destinations:', error);
            // Still try to render with fallback images
            this.renderCards();
        }
    }

    async loadDestinationImages(index) {
        if (index >= this.currentDestinations.length) return;
        
        const destination = this.currentDestinations[index];
        
        if (this.loadedImages.has(destination.id)) {
            return this.loadedImages.get(destination.id);
        }

        const images = await this.pexelsClient.search(destination.pexelsQuery, 3);
        this.loadedImages.set(destination.id, images);
        return images;
    }

    async renderCards() {
        console.log('renderCards called');
        const container = document.getElementById('cards-container');
        if (!container) {
            console.error('cards-container element not found!');
            return;
        }
        
        console.log('Container found:', container);

        // Clear existing cards
        container.innerHTML = '';

        // Hide loading
        this.hideLoading();

        // Render up to 3 cards
        const cardsToRender = Math.min(CARD_STACK_SIZE, this.currentDestinations.length - this.currentIndex);
        console.log(`Rendering ${cardsToRender} cards`);
        
        for (let i = 0; i < cardsToRender; i++) {
            const cardIndex = this.currentIndex + i;
            const destination = this.currentDestinations[cardIndex];
            console.log(`Creating card ${i} for destination:`, destination.name);
            
            const images = this.loadedImages.get(destination.id) || [];
            const image = images[0] || this.pexelsClient.getFallbackImages(destination.name)[0];

            const card = this.createCard(destination, image, i);
            container.appendChild(card);
        }

        console.log('All cards rendered, setting up gestures...');
        
        // Setup gestures on top card
        this.setupGestures();

        // Check if we're running out of destinations
        if (this.currentDestinations.length - this.currentIndex <= CARD_STACK_SIZE) {
            this.preloadNextDestination(this.currentIndex + CARD_STACK_SIZE);
        }
        
        console.log('renderCards completed');
    }

    createCard(destination, image, stackPosition) {
        const card = document.createElement('div');
        card.className = 'discover-card';
        card.setAttribute('data-destination-id', destination.id);
        card.setAttribute('data-stack-position', stackPosition);
        
        // Apply stacking styles
        const scale = 1 - (stackPosition * 0.05);
        const translateY = stackPosition * 10;
        card.style.transform = `scale(${scale}) translateY(${translateY}px)`;
        card.style.zIndex = CARD_STACK_SIZE - stackPosition;

        card.innerHTML = `
            <div class="card-image-container">
                <img src="${image.src.portrait}" alt="${image.alt || destination.name}" class="card-image">
                <div class="card-overlay"></div>
                <div class="swipe-indicator swipe-left">
                    <span class="text-6xl">❌</span>
                </div>
                <div class="swipe-indicator swipe-right">
                    <span class="text-6xl">💚</span>
                </div>
            </div>
            <div class="card-content">
                <h2 class="card-title">${destination.name}</h2>
                <p class="card-subtitle">${destination.region}</p>
                <p class="card-description">${destination.description}</p>
                <div class="card-tags">
                    ${destination.tags.slice(0, 4).map(tag => `<span class="tag">#${tag}</span>`).join('')}
                </div>
                <div class="card-photographer">
                    <span class="material-symbols-outlined">photo_camera</span>
                    <a href="${image.photographer_url}" target="_blank">${image.photographer}</a>
                </div>
            </div>
        `;

        return card;
    }

    setupGestures() {
        const topCard = document.querySelector('.discover-card[data-stack-position="0"]');
        if (!topCard) return;

        // Only apply gestures to the image container, not the entire card
        const imageContainer = topCard.querySelector('.card-image-container');
        if (!imageContainer) return;

        const hammer = new Hammer(imageContainer);
        
        hammer.on('pan', (event) => {
            if (this.isAnimating) return;
            
            const card = topCard; // Use the top card directly
            const rotation = event.deltaX / 20;
            
            card.style.transform = `translateX(${event.deltaX}px) translateY(${event.deltaY}px) rotate(${rotation}deg)`;
            
            // Show swipe indicators
            this.updateSwipeIndicators(card, event.deltaX);
        });

        hammer.on('panend', (event) => {
            if (this.isAnimating) return;
            
            const card = topCard; // Use the top card directly
            
            if (Math.abs(event.deltaX) > SWIPE_THRESHOLD) {
                // Trigger swipe
                if (event.deltaX > 0) {
                    this.handleSwipeRight(card);
                } else {
                    this.handleSwipeLeft(card);
                }
            } else {
                // Reset card position
                card.style.transition = 'transform 0.3s ease';
                card.style.transform = 'translateX(0) translateY(0) rotate(0)';
                this.hideSwipeIndicators(card);
                setTimeout(() => {
                    card.style.transition = '';
                }, 300);
            }
        });

        // Click handlers for buttons
        const swipeLeftBtn = document.getElementById('swipe-left-btn');
        const swipeRightBtn = document.getElementById('swipe-right-btn');
        const planTripBtn = document.getElementById('plan-trip-btn');

        if (swipeLeftBtn) {
            swipeLeftBtn.onclick = () => this.handleSwipeLeft(topCard);
        }
        if (swipeRightBtn) {
            swipeRightBtn.onclick = () => this.handleSwipeRight(topCard);
        }
        if (planTripBtn) {
            planTripBtn.onclick = () => this.handlePlanTrip(topCard);
        }
    }

    updateSwipeIndicators(card, deltaX) {
        const leftIndicator = card.querySelector('.swipe-left');
        const rightIndicator = card.querySelector('.swipe-right');
        
        if (deltaX < -20) {
            leftIndicator.style.opacity = Math.min(Math.abs(deltaX) / SWIPE_THRESHOLD, 1);
            rightIndicator.style.opacity = 0;
        } else if (deltaX > 20) {
            rightIndicator.style.opacity = Math.min(deltaX / SWIPE_THRESHOLD, 1);
            leftIndicator.style.opacity = 0;
        } else {
            leftIndicator.style.opacity = 0;
            rightIndicator.style.opacity = 0;
        }
    }

    hideSwipeIndicators(card) {
        const leftIndicator = card.querySelector('.swipe-left');
        const rightIndicator = card.querySelector('.swipe-right');
        leftIndicator.style.opacity = 0;
        rightIndicator.style.opacity = 0;
    }

    handleSwipeLeft(card) {
        if (this.isAnimating) return;
        
        this.isAnimating = true;
        const destinationId = parseInt(card.getAttribute('data-destination-id'));
        
        // Add to seen
        this.addSeenDestination(destinationId);
        
        // Animate out
        card.style.transition = 'transform 0.4s ease';
        card.style.transform = 'translateX(-150%) rotate(-30deg)';
        
        setTimeout(() => {
            this.nextCard();
        }, 400);
    }

    handleSwipeRight(card) {
        if (this.isAnimating) return;
        
        this.isAnimating = true;
        const destinationId = parseInt(card.getAttribute('data-destination-id'));
        
        // Add to liked and seen
        this.addLikedDestination(destinationId);
        this.addSeenDestination(destinationId);
        
        // Show notification
        if (typeof showNotification === 'function') {
            showNotification('Đã thêm vào danh sách yêu thích! 💚', 'success');
        }
        
        // Animate out
        card.style.transition = 'transform 0.4s ease';
        card.style.transform = 'translateX(150%) rotate(30deg)';
        
        setTimeout(() => {
            this.nextCard();
        }, 400);
    }

    handlePlanTrip(card) {
        const destinationId = parseInt(card.getAttribute('data-destination-id'));
        const destination = this.currentDestinations.find(d => d.id === destinationId);
        
        if (!destination) return;
        
        // Add to liked and seen
        this.addLikedDestination(destinationId);
        this.addSeenDestination(destinationId);
        
        // Redirect to chat with pre-filled message
        const message = encodeURIComponent(`Tôi muốn lên kế hoạch đi du lịch ${destination.name}`);
        window.location.href = `/chat?message=${message}`;
    }

    nextCard() {
        this.currentIndex++;
        this.isAnimating = false;
        
        if (this.currentIndex >= this.currentDestinations.length) {
            this.showEmptyState();
            return;
        }
        
        // Preload next destination
        this.preloadNextDestination(this.currentIndex + CARD_STACK_SIZE - 1);
        
        // Re-render cards
        this.renderCards();
    }

    async preloadNextDestination(index) {
        if (index < this.currentDestinations.length) {
            await this.loadDestinationImages(index);
        }
    }

    showEmptyState() {
        const container = document.getElementById('cards-container');
        if (!container) return;

        container.innerHTML = `
            <div class="empty-state">
                <span class="material-symbols-outlined" style="font-size: 80px; color: #13a4ec;">explore_off</span>
                <h2 class="text-2xl font-bold mt-4 mb-2">Bạn đã xem hết!</h2>
                <p class="text-gray-600 mb-6">Đã duyệt qua tất cả các địa điểm</p>
                <button onclick="discoveryApp.resetProgress()" class="btn-primary">
                    <span class="material-symbols-outlined">refresh</span>
                    Khám phá lại
                </button>
                <a href="/chat" class="btn-secondary mt-4">
                    <span class="material-symbols-outlined">chat</span>
                    Lên kế hoạch ngay
                </a>
            </div>
        `;

        this.hideLoading();
    }

    showLoading() {
        const loading = document.getElementById('loading-overlay');
        if (loading) loading.classList.remove('hidden');
    }

    hideLoading() {
        const loading = document.getElementById('loading-overlay');
        if (loading) loading.classList.add('hidden');
    }
}

// Initialize app when DOM is ready
let discoveryApp;

document.addEventListener('DOMContentLoaded', () => {
    // Check if required dependencies are loaded
    if (typeof Hammer === 'undefined') {
        console.error('Hammer.js is not loaded! Please check the CDN link.');
        alert('Lỗi: Thư viện Hammer.js chưa được tải. Vui lòng kiểm tra kết nối internet.');
        return;
    }
    
    if (typeof VIETNAMESE_DESTINATIONS === 'undefined') {
        console.error('VIETNAMESE_DESTINATIONS is not defined! Please check if destinations-data.js is loaded.');
        alert('Lỗi: Dữ liệu địa điểm chưa được tải. Vui lòng tải lại trang.');
        return;
    }
    
    console.log('Initializing Discovery App...');
    console.log(`Found ${VIETNAMESE_DESTINATIONS.length} destinations`);
    discoveryApp = new DiscoveryApp();
});
