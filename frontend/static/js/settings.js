/**
 * Settings Management for khampha.online
 * Handles language, theme, and other app settings
 * This file works globally across all pages
 */

// Initialize settings when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Load and apply saved settings
    loadAndApplySettings();
    
    // Add data-setting attributes to checkboxes programmatically
    addDataSettingAttributes();
});

/**
 * Add data-setting attributes to checkboxes
 */
function addDataSettingAttributes() {
    // Map of checkbox identifiers to setting names
    const checkboxMap = {
        'email': 'email_notifications',
        'push': 'push_notifications',
        'history': 'save_history',
        'voice': 'voice_input',
        'suggestions': 'smart_suggestions',
        'analytics': 'analytics'
    };
    
    // Find checkboxes and add attributes
    document.querySelectorAll('.settings-checkbox').forEach((checkbox, index) => {
        const settingName = Object.values(checkboxMap)[index];
        if (settingName) {
            checkbox.setAttribute('data-setting', settingName);
        }
    });
}

/**
 * Load settings from localStorage and apply them globally
 */
function loadAndApplySettings() {
    // Load language
    const savedLang = localStorage.getItem('app_language') || 'vi';
    if (typeof changeLanguage === 'function') {
        changeLanguage(savedLang);
    }
    
    // Load and apply theme
    const savedTheme = localStorage.getItem('app_theme') || 'dark';
    applyTheme(savedTheme);
    
    // Load other settings
    const settings = JSON.parse(localStorage.getItem('app_settings') || '{}');
    console.log('📋 Loaded settings globally:', settings);
}

/**
 * Load current settings into the Settings modal
 */
function loadCurrentSettings() {
    // Load language
    const currentLang = localStorage.getItem('app_language') || 'vi';
    const langRadio = document.querySelector(`input[name="language"][value="${currentLang}"]`);
    if (langRadio) langRadio.checked = true;
    
    // Load theme
    const currentTheme = localStorage.getItem('app_theme') || 'dark';
    const themeRadio = document.querySelector(`input[name="theme"][value="${currentTheme}"]`);
    if (themeRadio) {
        themeRadio.checked = true;
        // Update visual feedback
        document.querySelectorAll('input[name="theme"]').forEach(r => {
            r.closest('label').classList.remove('border-primary');
            r.closest('label').classList.add('border-gray-200', 'dark:border-gray-700');
        });
        themeRadio.closest('label').classList.remove('border-gray-200', 'dark:border-gray-700');
        themeRadio.closest('label').classList.add('border-primary');
    }
    
    // Load other settings from localStorage
    const settings = JSON.parse(localStorage.getItem('app_settings') || '{}');
    
    // Set checkboxes
    const checkboxSettings = {
        'email_notifications': true,
        'push_notifications': false,
        'save_history': true,
        'voice_input': true,
        'smart_suggestions': true,
        'analytics': true
    };
    
    Object.keys(checkboxSettings).forEach(key => {
        const checkbox = document.querySelector(`input[type="checkbox"][data-setting="${key}"]`);
        if (checkbox) {
            checkbox.checked = settings[key] !== undefined ? settings[key] : checkboxSettings[key];
        }
    });
}

/**
 * Save all settings and broadcast to other tabs
 */
function saveSettings() {
    // Get all settings
    const settings = {};
    
    // Get language
    const selectedLang = document.querySelector('input[name="language"]:checked');
    if (selectedLang) {
        const newLang = selectedLang.value;
        if (typeof changeLanguage === 'function') {
            changeLanguage(newLang);
        }
        localStorage.setItem('app_language', newLang);
        
        // Broadcast to other tabs
        broadcastSettingChange('app_language', newLang);
    }
    
    // Get theme
    const selectedTheme = document.querySelector('input[name="theme"]:checked');
    if (selectedTheme) {
        const newTheme = selectedTheme.value;
        localStorage.setItem('app_theme', newTheme);
        applyTheme(newTheme);
        settings.theme = newTheme;
        
        // Broadcast to other tabs
        broadcastSettingChange('app_theme', newTheme);
    }
    
    // Get checkboxes
    document.querySelectorAll('input[type="checkbox"][data-setting]').forEach(checkbox => {
        const settingName = checkbox.getAttribute('data-setting');
        settings[settingName] = checkbox.checked;
    });
    
    // Save to localStorage
    localStorage.setItem('app_settings', JSON.stringify(settings));
    
    // Broadcast to other tabs
    broadcastSettingChange('app_settings', JSON.stringify(settings));
    
    // Close modal
    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) {
        settingsModal.classList.add('hidden');
        settingsModal.classList.remove('flex');
        document.body.style.overflow = '';
    }
    
    // Show notification
    if (typeof showNotification === 'function') {
        showNotification('success', '✅ Đã lưu', 'Cài đặt đã được lưu thành công!');
    }
    
    console.log('💾 Settings saved globally:', settings);
}

/**
 * Broadcast setting changes to other tabs/windows
 */
function broadcastSettingChange(key, value) {
    // Trigger storage event for other tabs
    window.dispatchEvent(new StorageEvent('storage', {
        key: key,
        newValue: value,
        oldValue: localStorage.getItem(key),
        storageArea: localStorage
    }));
}

/**
 * Reset all settings to default
 */
function resetSettings() {
    const confirmMsg = typeof t === 'function' ? t('notif.confirm_delete') : 'Bạn có chắc muốn đặt lại tất cả cài đặt về mặc định?';
    
    if (!confirm(confirmMsg)) {
        return;
    }
    
    // Clear all settings
    localStorage.removeItem('app_settings');
    localStorage.setItem('app_language', 'vi');
    localStorage.setItem('app_theme', 'dark');
    
    // Reset language
    if (typeof changeLanguage === 'function') {
        changeLanguage('vi');
    }
    
    // Reset theme
    applyTheme('dark');
    
    // Reload settings UI
    loadCurrentSettings();
    
    // Broadcast to other tabs
    broadcastSettingChange('app_language', 'vi');
    broadcastSettingChange('app_theme', 'dark');
    broadcastSettingChange('app_settings', '{}');
    
    // Show notification
    if (typeof showNotification === 'function') {
        showNotification('info', '🔄 Đã đặt lại', 'Cài đặt đã được đặt lại về mặc định!');
    }
    
    console.log('🔄 Settings reset to default globally');
}

/**
 * Apply theme to the application
 * @param {string} theme - 'light', 'dark', or 'auto'
 */
function applyTheme(theme) {
    const html = document.documentElement;
    
    if (theme === 'auto') {
        // Use system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        html.classList.toggle('dark', prefersDark);
        html.classList.toggle('light', !prefersDark);
        
        // Listen for system theme changes (only add once)
        if (!window._themeListenerAdded) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (localStorage.getItem('app_theme') === 'auto') {
                    html.classList.toggle('dark', e.matches);
                    html.classList.toggle('light', !e.matches);
                }
            });
            window._themeListenerAdded = true;
        }
    } else {
        html.classList.toggle('dark', theme === 'dark');
        html.classList.toggle('light', theme === 'light');
    }
    
    // Update meta theme-color for mobile browsers
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (!metaThemeColor) {
        metaThemeColor = document.createElement('meta');
        metaThemeColor.setAttribute('name', 'theme-color');
        document.head.appendChild(metaThemeColor);
    }
    
    const isDark = theme === 'dark' || (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    metaThemeColor.setAttribute('content', isDark ? '#101c22' : '#f6f7f8');
    
    console.log(`🎨 Theme applied globally: ${theme}`);
}

// Listen for storage changes from other tabs/windows
window.addEventListener('storage', function(e) {
    if (e.key === 'app_theme' && e.newValue) {
        applyTheme(e.newValue);
        console.log(`🎨 Theme updated from another tab: ${e.newValue}`);
    }
    
    if (e.key === 'app_settings' && e.newValue) {
        console.log('📋 Settings updated from another tab');
    }
});

// Export functions to global scope
window.loadCurrentSettings = loadCurrentSettings;
window.saveSettings = saveSettings;
window.resetSettings = resetSettings;
window.applyTheme = applyTheme;
