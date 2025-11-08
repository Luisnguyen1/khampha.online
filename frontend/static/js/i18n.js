/**
 * Internationalization (i18n) for khampha.online
 * Handles multi-language support for Vietnamese, English, and Japanese
 */

// Translation data
const translations = {
    vi: {
        // Navigation
        'nav.home': 'Trang chủ',
        'nav.chat': 'Chat',
        'nav.plans': 'Kế hoạch',
        'nav.discover': 'Discover',
        'nav.profile': 'Profile',
        'nav.settings': 'Settings',
        'nav.help': 'Help',
        'nav.about': 'Về tôi',
        'nav.chat_history': 'Lịch sử Chat',
        'nav.new_chat': 'Chat mới',
        
        // Chat Interface
        'chat.welcome': 'Xin chào! Tôi là trợ lý du lịch ảo của bạn. Bạn muốn đi đâu hôm nay? 😊',
        'chat.input_placeholder': 'Nhập yêu cầu của bạn...',
        'chat.thinking': 'Đang suy nghĩ...',
        'chat.you': 'You',
        'chat.bot_name': 'khampha.online',
        'chat.tagline': 'Your Personal Travel Planner',
        
        // Suggestions
        'suggestion.dalat': 'Gợi ý một chuyến đi đến Đà Lạt',
        'suggestion.beach': 'Lên kế hoạch 3 ngày ở biển',
        
        // Modes
        'mode.plan': 'Lên kế hoạch',
        'mode.plan_desc': 'Tạo kế hoạch du lịch chi tiết',
        'mode.ask': 'Hỏi đáp',
        'mode.ask_desc': 'Trả lời câu hỏi về du lịch',
        'mode.edit': 'Chỉnh sửa',
        'mode.edit_desc': 'Chỉnh sửa kế hoạch hiện tại',
        
        // Plan Display
        'plan.your_plan': 'Kế hoạch của bạn',
        'plan.detailed_plan': 'Your Detailed Plan',
        'plan.save': 'Save',
        'plan.share': 'Share',
        'plan.edit': 'Edit',
        'plan.budget': 'Ngân sách',
        'plan.day': 'Ngày',
        'plan.empty_state': 'Kế hoạch của bạn sẽ xuất hiện ở đây',
        'plan.empty_desc': 'Bắt đầu chat để tạo kế hoạch du lịch!',
        'plan.will_appear': 'Your plan will appear here.',
        'plan.start_chatting': 'Start by chatting with me!',
        
        // Settings Modal
        'settings.title': 'Cài đặt',
        'settings.language': 'Ngôn ngữ',
        'settings.theme': 'Giao diện',
        'settings.theme_light': 'Sáng',
        'settings.theme_dark': 'Tối',
        'settings.theme_auto': 'Tự động',
        'settings.notifications': 'Thông báo',
        'settings.email_notif': 'Thông báo Email',
        'settings.email_desc': 'Nhận thông báo qua email',
        'settings.push_notif': 'Thông báo đẩy',
        'settings.push_desc': 'Nhận thông báo trên trình duyệt',
        'settings.chat': 'Trò chuyện',
        'settings.save_history': 'Lưu lịch sử chat',
        'settings.save_history_desc': 'Lưu các cuộc trò chuyện của bạn',
        'settings.voice_input': 'Nhập bằng giọng nói',
        'settings.voice_desc': 'Sử dụng mic để nhập tin nhắn',
        'settings.smart_suggestions': 'Gợi ý thông minh',
        'settings.suggestions_desc': 'Hiển thị gợi ý câu hỏi',
        'settings.privacy': 'Quyền riêng tư',
        'settings.analytics': 'Phân tích sử dụng',
        'settings.analytics_desc': 'Giúp cải thiện trải nghiệm',
        'settings.delete_data': 'Xóa dữ liệu',
        'settings.delete_desc': 'Xóa tất cả lịch sử và dữ liệu',
        'settings.reset_default': 'Đặt lại mặc định',
        'settings.save_changes': 'Lưu thay đổi',
        
        // Status Messages
        'status.analyzing': '🤔 Đang phân tích yêu cầu...',
        'status.processing': '⚙️ Đang xử lý...',
        'status.searching': '🔍 Đang tìm kiếm thông tin...',
        'status.extracting': '📝 Đang xác định yêu cầu...',
        'status.creating_plan': '🗺️ Đang tạo kế hoạch...',
        'status.generating': '✨ Đang tạo câu trả lời...',
        'status.analyzing_plan': '📋 Đang phân tích kế hoạch...',
        
        // Notifications
        'notif.plan_saved': 'Kế hoạch đã được lưu!',
        'notif.link_copied': 'Link chia sẻ đã được sao chép vào clipboard!',
        'notif.no_plan': 'Chưa có kế hoạch để',
        'notif.edit_tip': 'Bạn có thể sử dụng @edit_plan trong chat để chỉnh sửa kế hoạch!',
        'notif.new_chat_created': 'Đã tạo cuộc hội thoại mới',
        'notif.chat_deleted': 'Cuộc hội thoại đã được xóa',
        'notif.confirm_delete': 'Bạn có chắc muốn xóa cuộc hội thoại này?',
        'notif.no_conversations': 'Chưa có cuộc hội thoại nào',
        'notif.settings_saved': 'Cài đặt đã được lưu',
        'notif.settings_reset': 'Đã đặt lại cài đặt mặc định',
        
        // Errors
        'error.connection': 'Lỗi kết nối. Vui lòng thử lại.',
        'error.load_history': 'Không thể tải lịch sử chat',
        'error.create_chat': 'Không thể tạo chat mới',
        'error.delete_chat': 'Không thể xóa chat',
        'error.save_plan': 'Không thể lưu kế hoạch',
        'error.invalid_plan': 'Dữ liệu kế hoạch không hợp lệ',
        
        // Time
        'time.just_now': 'Vừa xong',
        'time.mins_ago': 'phút trước',
        'time.hours_ago': 'giờ trước',
        'time.days_ago': 'ngày trước',
        
        // References Modal
        'ref.title': 'Kiến thức tham khảo',
        'ref.sources_used': 'Các nguồn tham khảo được sử dụng để tạo kế hoạch của bạn',
        'ref.no_data': 'Không có dữ liệu tham khảo',
        'ref.found': 'Tìm thấy',
        'ref.sources': 'nguồn tham khảo',
        'ref.no_sources': 'Không có nguồn tham khảo cho kế hoạch này',
        'ref.manual_plan': 'Kế hoạch có thể được tạo thủ công hoặc từ dữ liệu mẫu',
    },
    
    en: {
        // Navigation
        'nav.home': 'Home',
        'nav.chat': 'Chat',
        'nav.plans': 'Plans',
        'nav.discover': 'Discover',
        'nav.profile': 'Profile',
        'nav.settings': 'Settings',
        'nav.help': 'Help',
        'nav.about': 'About Me',
        'nav.chat_history': 'Chat History',
        'nav.new_chat': 'New Chat',
        
        // Chat Interface
        'chat.welcome': 'Hello! I\'m your virtual travel assistant. Where would you like to go today? 😊',
        'chat.input_placeholder': 'Enter your request...',
        'chat.thinking': 'Thinking...',
        'chat.you': 'You',
        'chat.bot_name': 'khampha.online',
        'chat.tagline': 'Your Personal Travel Planner',
        
        // Suggestions
        'suggestion.dalat': 'Suggest a trip to Da Lat',
        'suggestion.beach': 'Plan a 3-day beach vacation',
        
        // Modes
        'mode.plan': 'Plan',
        'mode.plan_desc': 'Create detailed travel plan',
        'mode.ask': 'Ask',
        'mode.ask_desc': 'Answer travel questions',
        'mode.edit': 'Edit',
        'mode.edit_desc': 'Edit current plan',
        
        // Plan Display
        'plan.your_plan': 'Your Plan',
        'plan.detailed_plan': 'Your Detailed Plan',
        'plan.save': 'Save',
        'plan.share': 'Share',
        'plan.edit': 'Edit',
        'plan.budget': 'Budget',
        'plan.day': 'Day',
        'plan.empty_state': 'Your plan will appear here',
        'plan.empty_desc': 'Start chatting to create a travel plan!',
        'plan.will_appear': 'Your plan will appear here.',
        'plan.start_chatting': 'Start by chatting with me!',
        
        // Settings Modal
        'settings.title': 'Settings',
        'settings.language': 'Language',
        'settings.theme': 'Theme',
        'settings.theme_light': 'Light',
        'settings.theme_dark': 'Dark',
        'settings.theme_auto': 'Auto',
        'settings.notifications': 'Notifications',
        'settings.email_notif': 'Email Notifications',
        'settings.email_desc': 'Receive notifications via email',
        'settings.push_notif': 'Push Notifications',
        'settings.push_desc': 'Receive browser notifications',
        'settings.chat': 'Chat',
        'settings.save_history': 'Save chat history',
        'settings.save_history_desc': 'Save your conversations',
        'settings.voice_input': 'Voice Input',
        'settings.voice_desc': 'Use microphone to enter messages',
        'settings.smart_suggestions': 'Smart Suggestions',
        'settings.suggestions_desc': 'Show question suggestions',
        'settings.privacy': 'Privacy',
        'settings.analytics': 'Usage Analytics',
        'settings.analytics_desc': 'Help improve experience',
        'settings.delete_data': 'Delete Data',
        'settings.delete_desc': 'Delete all history and data',
        'settings.reset_default': 'Reset to Default',
        'settings.save_changes': 'Save Changes',
        
        // Status Messages
        'status.analyzing': '🤔 Analyzing request...',
        'status.processing': '⚙️ Processing...',
        'status.searching': '🔍 Searching for information...',
        'status.extracting': '📝 Extracting requirements...',
        'status.creating_plan': '🗺️ Creating plan...',
        'status.generating': '✨ Generating response...',
        'status.analyzing_plan': '📋 Analyzing plan...',
        
        // Notifications
        'notif.plan_saved': 'Plan has been saved!',
        'notif.link_copied': 'Share link copied to clipboard!',
        'notif.no_plan': 'No plan to',
        'notif.edit_tip': 'You can use @edit_plan in chat to edit your plan!',
        'notif.new_chat_created': 'New conversation created',
        'notif.chat_deleted': 'Conversation deleted',
        'notif.confirm_delete': 'Are you sure you want to delete this conversation?',
        'notif.no_conversations': 'No conversations yet',
        'notif.settings_saved': 'Settings saved',
        'notif.settings_reset': 'Settings reset to default',
        
        // Errors
        'error.connection': 'Connection error. Please try again.',
        'error.load_history': 'Cannot load chat history',
        'error.create_chat': 'Cannot create new chat',
        'error.delete_chat': 'Cannot delete chat',
        'error.save_plan': 'Cannot save plan',
        'error.invalid_plan': 'Invalid plan data',
        
        // Time
        'time.just_now': 'Just now',
        'time.mins_ago': 'mins ago',
        'time.hours_ago': 'hours ago',
        'time.days_ago': 'days ago',
        
        // References Modal
        'ref.title': 'Knowledge References',
        'ref.sources_used': 'Sources used to create your plan',
        'ref.no_data': 'No reference data',
        'ref.found': 'Found',
        'ref.sources': 'references',
        'ref.no_sources': 'No references for this plan',
        'ref.manual_plan': 'Plan may have been created manually or from sample data',
    },
    
    ja: {
        // Navigation
        'nav.home': 'ホーム',
        'nav.chat': 'チャット',
        'nav.plans': 'プラン',
        'nav.discover': '発見',
        'nav.profile': 'プロフィール',
        'nav.settings': '設定',
        'nav.help': 'ヘルプ',
        'nav.about': '私について',
        'nav.chat_history': 'チャット履歴',
        'nav.new_chat': '新しいチャット',
        
        // Chat Interface
        'chat.welcome': 'こんにちは！私はあなたのバーチャル旅行アシスタントです。今日はどこに行きたいですか？ 😊',
        'chat.input_placeholder': 'リクエストを入力してください...',
        'chat.thinking': '考え中...',
        'chat.you': 'あなた',
        'chat.bot_name': 'トラベルボット',
        'chat.tagline': 'あなたの個人旅行プランナー',
        
        // Suggestions
        'suggestion.dalat': 'ダラットへの旅行を提案',
        'suggestion.beach': '3日間のビーチバケーションを計画',
        
        // Modes
        'mode.plan': '計画',
        'mode.plan_desc': '詳細な旅行計画を作成',
        'mode.ask': '質問',
        'mode.ask_desc': '旅行に関する質問に答える',
        'mode.edit': '編集',
        'mode.edit_desc': '現在のプランを編集',
        
        // Plan Display
        'plan.your_plan': 'あなたのプラン',
        'plan.detailed_plan': '詳細プラン',
        'plan.save': '保存',
        'plan.share': '共有',
        'plan.edit': '編集',
        'plan.budget': '予算',
        'plan.day': '日',
        'plan.empty_state': 'プランはここに表示されます',
        'plan.empty_desc': 'チャットを開始して旅行計画を作成しましょう！',
        'plan.will_appear': 'プランはここに表示されます。',
        'plan.start_chatting': 'チャットを始めてください！',
        
        // Settings Modal
        'settings.title': '設定',
        'settings.language': '言語',
        'settings.theme': 'テーマ',
        'settings.theme_light': 'ライト',
        'settings.theme_dark': 'ダーク',
        'settings.theme_auto': '自動',
        'settings.notifications': '通知',
        'settings.email_notif': 'メール通知',
        'settings.email_desc': 'メールで通知を受け取る',
        'settings.push_notif': 'プッシュ通知',
        'settings.push_desc': 'ブラウザ通知を受け取る',
        'settings.chat': 'チャット',
        'settings.save_history': 'チャット履歴を保存',
        'settings.save_history_desc': '会話を保存する',
        'settings.voice_input': '音声入力',
        'settings.voice_desc': 'マイクを使用してメッセージを入力',
        'settings.smart_suggestions': 'スマート提案',
        'settings.suggestions_desc': '質問の提案を表示',
        'settings.privacy': 'プライバシー',
        'settings.analytics': '使用状況分析',
        'settings.analytics_desc': '体験の改善に役立つ',
        'settings.delete_data': 'データを削除',
        'settings.delete_desc': 'すべての履歴とデータを削除',
        'settings.reset_default': 'デフォルトにリセット',
        'settings.save_changes': '変更を保存',
        
        // Status Messages
        'status.analyzing': '🤔 リクエストを分析中...',
        'status.processing': '⚙️ 処理中...',
        'status.searching': '🔍 情報を検索中...',
        'status.extracting': '📝 要件を抽出中...',
        'status.creating_plan': '🗺️ プランを作成中...',
        'status.generating': '✨ 回答を生成中...',
        'status.analyzing_plan': '📋 プランを分析中...',
        
        // Notifications
        'notif.plan_saved': 'プランが保存されました！',
        'notif.link_copied': '共有リンクがクリップボードにコピーされました！',
        'notif.no_plan': 'プランがありません',
        'notif.edit_tip': 'チャットで@edit_planを使用してプランを編集できます！',
        'notif.new_chat_created': '新しい会話が作成されました',
        'notif.chat_deleted': '会話が削除されました',
        'notif.confirm_delete': 'この会話を削除してもよろしいですか？',
        'notif.no_conversations': 'まだ会話がありません',
        'notif.settings_saved': '設定が保存されました',
        'notif.settings_reset': '設定がデフォルトにリセットされました',
        
        // Errors
        'error.connection': '接続エラー。もう一度お試しください。',
        'error.load_history': 'チャット履歴を読み込めません',
        'error.create_chat': '新しいチャットを作成できません',
        'error.delete_chat': 'チャットを削除できません',
        'error.save_plan': 'プランを保存できません',
        'error.invalid_plan': '無効なプランデータ',
        
        // Time
        'time.just_now': 'たった今',
        'time.mins_ago': '分前',
        'time.hours_ago': '時間前',
        'time.days_ago': '日前',
        
        // References Modal
        'ref.title': '参考資料',
        'ref.sources_used': 'プラン作成に使用されたソース',
        'ref.no_data': '参考データなし',
        'ref.found': '見つかりました',
        'ref.sources': '参考資料',
        'ref.no_sources': 'このプランの参考資料はありません',
        'ref.manual_plan': '手動またはサンプルデータから作成された可能性があります',
    }
};

// Current language (default: Vietnamese)
let currentLanguage = localStorage.getItem('app_language') || 'vi';

/**
 * Get translation for a key
 * @param {string} key - Translation key (e.g., 'nav.home')
 * @param {string} lang - Language code (optional, uses current language if not provided)
 * @returns {string} Translated text
 */
function t(key, lang = null) {
    const language = lang || currentLanguage;
    
    if (translations[language] && translations[language][key]) {
        return translations[language][key];
    }
    
    // Fallback to Vietnamese
    if (translations['vi'][key]) {
        return translations['vi'][key];
    }
    
    // Return key if not found
    console.warn(`Translation not found: ${key}`);
    return key;
}

/**
 * Change application language
 * @param {string} lang - Language code ('vi', 'en', 'ja')
 */
function changeLanguage(lang) {
    if (!translations[lang]) {
        console.error(`Language not supported: ${lang}`);
        return;
    }
    
    currentLanguage = lang;
    localStorage.setItem('app_language', lang);
    
    // Update all translatable elements
    updateTranslations();
    
    console.log(`✅ Language changed to: ${lang}`);
}

/**
 * Update all elements with data-i18n attribute
 */
function updateTranslations() {
    // Update elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key);
        
        // Update text content
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            element.placeholder = translation;
        } else {
            element.textContent = translation;
        }
    });
    
    // Update elements with data-i18n-html attribute (for HTML content)
    document.querySelectorAll('[data-i18n-html]').forEach(element => {
        const key = element.getAttribute('data-i18n-html');
        element.innerHTML = t(key);
    });
    
    // Update page title if exists
    const titleKey = document.documentElement.getAttribute('data-i18n-title');
    if (titleKey) {
        document.title = t(titleKey);
    }
}

/**
 * Initialize i18n system
 */
function initI18n() {
    // Apply saved language or default
    const savedLang = localStorage.getItem('app_language') || 'vi';
    currentLanguage = savedLang;
    
    // Update document language attribute
    document.documentElement.setAttribute('lang', savedLang);
    
    // Update all translations
    updateTranslations();
    
    // Set language radio button in settings if exists
    const langRadio = document.querySelector(`input[name="language"][value="${savedLang}"]`);
    if (langRadio) {
        langRadio.checked = true;
    }
    
    console.log(`🌐 i18n initialized with language: ${currentLanguage}`);
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initI18n);
} else {
    initI18n();
}

// Also listen for storage changes (when settings changed in another tab)
window.addEventListener('storage', function(e) {
    if (e.key === 'app_language' && e.newValue !== currentLanguage) {
        currentLanguage = e.newValue;
        updateTranslations();
        console.log(`🌐 Language updated from another tab: ${e.newValue}`);
    }
});

// Export for use in other scripts
window.t = t;
window.changeLanguage = changeLanguage;
window.getCurrentLanguage = () => currentLanguage;
