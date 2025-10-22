# 📋 CHECKLIST TÍNH NĂNG GIAO DIỆN - khappha.online

## 🎯 Tổng quan
Tài liệu này liệt kê **TẤT CẢ** các tính năng UI/UX hiện có trong giao diện đã thiết kế.

---

## 🏠 LANDING PAGE (`landingpage.html`)

### Header Navigation
- [ ] **Sticky header** với backdrop blur
- [ ] **Logo + Brand name** "TravelBot" với icon travel_explore
- [ ] **Desktop navigation menu**:
  - [ ] Link "Trang chủ"
  - [ ] Link "Tính năng" (scroll to #features)
  - [ ] Link "Liên hệ" (scroll to #contact)
- [ ] **Mobile hamburger menu** button
- [ ] **Dark/Light mode support**

### Hero Section
- [ ] **Background image** với gradient overlay
- [ ] **Hero heading**: "Trợ lý du lịch ảo của bạn"
- [ ] **Subheading**: "Lên kế hoạch cho chuyến đi trong mơ..."
- [ ] **CTA Button**: "Trải nghiệm ngay" → link to `/chat`
- [ ] **Responsive layout** (mobile/tablet/desktop)

### Features Section (#features)
- [ ] **Section heading**: "Tính năng nổi bật"
- [ ] **Feature 1: Lập kế hoạch thông minh**
  - [ ] Title + description
  - [ ] 3 checkmarks: Lịch trình tùy chỉnh, Gợi ý sở thích, Tối ưu chi phí
  - [ ] Feature image
- [ ] **Feature 2: Đặt vé và phòng dễ dàng**
  - [ ] Title + description
  - [ ] 3 checkmarks: So sánh giá, Thanh toán an toàn, Quản lý booking
  - [ ] Feature image (reverse layout)
- [ ] **Feature 3: Hỗ trợ 24/7**
  - [ ] Title + description
  - [ ] 3 checkmarks: Trợ giúp tức thì, Dịch đa ngôn ngữ, Thông tin khẩn cấp
  - [ ] Feature image

### How It Works Section
- [ ] **Section heading**: "Cách hoạt động"
- [ ] **3 steps grid**:
  - [ ] Step 1: Đặt câu hỏi (forum icon)
  - [ ] Step 2: Nhận gợi ý (checklist icon)
  - [ ] Step 3: Lên kế hoạch (flight_takeoff icon)
- [ ] **Icon + title + description** cho mỗi step

### Testimonials Section
- [ ] **Section heading**: "Đánh giá từ khách hàng"
- [ ] **2 testimonial cards**:
  - [ ] User avatar
  - [ ] Quote text
  - [ ] User name + role
  - [ ] Border với shadow
- [ ] **Grid layout** (2 columns desktop)

### Contact Section (#contact)
- [ ] **CTA Section** "Bắt đầu lên kế hoạch ngay hôm nay"
- [ ] **Description text**
- [ ] **Contact form** (hoặc button)
- [ ] **Social links** (optional)

### Footer
- [ ] **Copyright text**
- [ ] **Additional links** (optional)

---

## 💬 MAIN CHAT PAGE (`main_chat.html`)

### Sidebar Navigation
- [x] **App logo + name**: "TravelBot"
- [x] **Tagline**: "Your Personal Travel Planner"
- [x] **Navigation menu**:
  - [x] 🏠 Trang chủ → `/`
  - [x] 💬 Chat → `/chat` (active)
  - [x] 📋 Kế hoạch → `/plans`
  - [x] 🔍 Discover → `#`
  - [x] 👤 Profile → `#`
- [x] **"Lên kế hoạch ngay" button** (secondary color)
- [x] **Settings link** với icon
- [x] **Help link** với icon
- [x] **Active state highlighting** cho current page
- [x] **Hover effects** trên menu items

### Chat Interface (Left Panel)

#### Welcome Message
- [x] **Bot avatar** với background image
- [x] **Bot name label**: "TravelBot"
- [x] **Welcome text**: "Xin chào! Tôi là trợ lý du lịch ảo..."
- [x] **Gray background** cho bot messages

#### Message Display
- [x] **User messages**:
  - [x] Right-aligned layout
  - [x] User avatar
  - [x] "You" label
  - [x] Primary color background
  - [x] White text
- [x] **Bot messages**:
  - [x] Left-aligned layout
  - [x] Bot avatar
  - [x] "TravelBot" label
  - [x] Gray background
  - [x] Dark text
- [x] **Loading indicator**:
  - [x] 3 animated dots
  - [x] Gray color
  - [x] Staggered animation delay

#### Sample Prompts
- [x] **2 suggestion buttons**:
  - [x] "Gợi ý một chuyến đi đến Đà Lạt"
  - [x] "Lên kế hoạch 3 ngày ở biển"
- [x] **Border style** với hover effect
- [x] **Click to fill** input functionality

#### Chat Input (Composer)
- [x] **User avatar** ở bên trái
- [x] **Text input field**:
  - [x] Placeholder: "Nhập yêu cầu của bạn..."
  - [x] Gray background
  - [x] Focus state với primary ring
- [x] **Action buttons**:
  - [x] 📎 Attach file button
  - [x] 🎤 Voice input button
  - [x] 📤 Send button (primary color)
- [x] **Rounded corners** và proper spacing

### Travel Plan Display (Right Panel)

#### Header Controls
- [x] **Page title**: "Your Detailed Plan"
- [x] **Action buttons**:
  - [x] 💾 Save Plan (primary color) - FUNCTIONAL
  - [x] 🔗 Share (outline style)
  - [x] ✏️ Edit (outline style)
- [x] **Button icons** với Material Symbols

#### View Toggle
- [x] **Tab switcher**:
  - [x] Timeline view (active)
  - [x] Map view
- [x] **Active state** với background color
- [x] **Rounded toggle** container

#### Empty State
- [x] **Placeholder icon** (large)
- [x] **Empty message**: "Your plan will appear here"
- [x] **Call-to-action**: "Start by chatting with me!"
- [x] **Center-aligned** layout

#### Itinerary View - NEWLY IMPLEMENTED ✨
- [x] **Trip header**:
  - [x] 📍 Location icon
  - [x] Trip title: "Kế hoạch của bạn"
  - [x] Destination + duration
- [x] **Budget summary card**:
  - [x] Wallet icon
  - [x] Formatted currency display
  - [x] Blue background highlight
- [x] **Day sections**:
  - [x] Day heading với calendar icon
  - [x] **Left border** indicator (gray)
  - [x] **Activity cards**:
    - [x] Time stamp với clock icon
    - [x] Activity title (bold)
    - [x] Description text
    - [x] Cost display (if available)
    - [x] Border styling
- [x] **Save button** at bottom:
  - [x] Full width
  - [x] Bookmark icon
  - [x] Primary color
  - [x] Functional with API integration
  - [x] Loading state
  - [x] Success notification
  - [x] Redirect to /plans after save

---

## 📋 PLANS LIST PAGE (`danh_sach_ke_hoach.html`)

### Header
- [x] **Logo + Brand name** với icon
- [x] **Desktop navigation**:
  - [x] Trang chủ → `/`
  - [x] Chat → `/chat`
  - [x] Kế hoạch → `/plans` (active - bold)
- [x] **Notification button** với icon
- [x] **User avatar dropdown**
- [x] **Mobile hamburger menu**

### Page Header
- [x] **Page title**: "Kế hoạch của tôi"
- [x] **"Tạo kế hoạch mới" button**:
  - [x] ➕ Add icon
  - [x] Primary color
  - [x] Link to `/chat`

### Search & Filter Bar
- [x] **Search input**:
  - [x] 🔍 Search icon
  - [x] Placeholder: "Tìm theo tên, địa điểm, hoặc từ khóa"
  - [x] Full width với responsive
  - [x] **FUNCTIONAL** - searches name, destination, preferences
- [x] **Filter buttons**:
  - [x] "Sắp diễn ra" với dropdown icon - FUNCTIONAL
  - [x] "Đã hoàn thành" với dropdown icon - FUNCTIONAL
  - [x] "Tất cả" với dropdown icon - FUNCTIONAL
- [x] **Gray background** cho buttons
- [x] **Horizontal scroll** trên mobile

### Plans Grid
- [x] **Responsive grid**:
  - [x] 1 column trên mobile
  - [x] 2 columns trên tablet
  - [x] 3 columns trên desktop
- [x] **Plan cards**:
  - [x] **Destination image** (aspect-video)
  - [x] **Plan title**: dynamic từ database
  - [x] **Date range**: formatted với duration
  - [x] **Location**: "destination, Việt Nam"
  - [x] **"Xem chi tiết" button** (primary) - FUNCTIONAL
  - [x] **More options menu** (⋮ icon) - FUNCTIONAL
  - [x] **Context menu với 3 options**:
    - [x] 👁️ Xem chi tiết
    - [x] ✏️ Chỉnh sửa
    - [x] 🗑️ Xóa kế hoạch
  - [x] **Hover effects**: Shadow + translate
  - [x] **Rounded corners** và shadow

### Plan Actions - NEWLY IMPLEMENTED ✨
- [x] **View detail**: Navigate to /plans/:id
- [x] **Edit plan**: Navigate to /plans/:id/edit
- [x] **Delete plan**:
  - [x] Confirmation dialog
  - [x] API call to DELETE endpoint
  - [x] Success notification
  - [x] Auto reload list after delete

### Empty State
- [x] **Illustration image** (suitcase + map)
- [x] **Empty heading**: "Bạn chưa có kế hoạch nào"
- [x] **Description**: "Hãy bắt đầu hành trình..."
- [x] **"Tạo kế hoạch đầu tiên" button**:
  - [x] ➕ Icon
  - [x] Primary color
  - [x] Link to `/chat`
- [x] **Dashed border** container
- [x] **Toggle logic** based on data presence

---

## 📄 PLAN DETAIL PAGE (`chi_tiet_ke_hoach.html`) - NEWLY IMPLEMENTED ✨

### Sidebar Navigation
- [x] **Trip avatar** với destination image (dynamic)
- [x] **Trip title**: dynamic từ database
- [x] **Duration**: "X Ngày" format
- [x] **Day navigation** (DYNAMIC):
  - [x] 📅 Ngày 1, 2, 3... (generated from itinerary)
  - [x] Active state highlighting
  - [x] Click to switch days
  - [x] Update main content on click
- [x] **Divider line**
- [x] **📊 Tổng kết & Chi phí** link
- [x] **Bottom action buttons**:
  - [x] 💾 Tải xuống PDF (primary, full width)
  - [x] 💡 Lưu ý quan trọng
  - [x] 🔗 Chia sẻ kế hoạch
  - [x] ✏️ Chỉnh sửa (functional)

### Main Content Area
- [x] **Page heading**: "Ngày X: [Day Title]"
- [x] **Date subtitle**: Dynamic description
- [x] **Stats cards** (3 cards):
  - [x] ⏰ Thời gian (số hoạt động)
  - [x] 💰 Chi phí (tổng cost của ngày)
  - [x] 📍 Địa điểm (số locations)
- [x] **Timeline view** với activities
- [x] **Activity cards** (DYNAMIC):
  - [x] Icon based on activity type
  - [x] Activity title (bold)
  - [x] Time stamp with clock icon
  - [x] Description text
  - [x] Cost display (formatted currency)
  - [x] Location (if available)
  - [x] White background với shadow
  - [x] Hover effect
  - [x] Connected with vertical line
- [x] **Vertical timeline line** kết nối các activities
- [x] **Responsive layout** (sidebar + main)

### JavaScript Features (chi_tiet_ke_hoach.js)
- [x] Load plan from API by ID
- [x] Parse itinerary JSON
- [x] Generate day navigation dynamically
- [x] Display day details on click
- [x] Update stats cards per day
- [x] Render activity timeline
- [x] Smart activity icon detection
- [x] Currency formatting (VND)
- [x] Error handling with fallback UI
- [x] Edit button functionality
- [x] Empty state for no activities

### Budget Summary Section
- [ ] **Section heading**: "Chi Phí Dự Kiến"
- [ ] **Total budget** display
- [ ] **Expense categories**:
  - [ ] 🍽️ Ăn uống
  - [ ] 🏨 Lưu trú
  - [ ] 🚗 Di chuyển
  - [ ] 🎫 Giải trí
- [ ] **Progress bar** cho mỗi category
- [ ] **Amount labels** với VNĐ format

### Notes Section
- [ ] **Important notes** list
- [ ] **Weather information**
- [ ] **Tips & recommendations**
- [ ] **Emergency contacts**

---

## ✏️ EDIT PLAN PAGE (`edit_ke_hoach.html`)

### Sidebar Navigation
- [ ] **Trip avatar** với Eiffel Tower image
- [ ] **Trip title**: "Chuyến đi đến Paris"
- [ ] **Date range**: "12/12/2024 - 15/12/2024"
- [ ] **Section navigation**:
  - [ ] 📊 Tổng quan (active)
  - [ ] 💰 Chi phí
  - [ ] 📅 Lịch trình
  - [ ] 📝 Ghi chú
- [ ] **Timeline preview**:
  - [ ] Vertical timeline với dots
  - [ ] Ngày 1 (active - primary color)
  - [ ] Ngày 2 (gray)
  - [ ] Ngày 3 (gray)
- [ ] **"Chia sẻ" button** (primary, full width)

### Main Content Area

#### Tab Navigation
- [ ] **3 tabs**:
  - [ ] Chi phí (active)
  - [ ] Lịch trình
  - [ ] Ghi chú
- [ ] **Active indicator** (bottom border)

#### Budget Editor
- [ ] **Total budget section**:
  - [ ] Label: "Tổng ngân sách"
  - [ ] Amount: "15,000,000 VNĐ"
  - [ ] **Progress bar** với indicator
  - [ ] **Percentage display**: 32%
- [ ] **Expense categories cards**:
  - [ ] **Di chuyển** (✈️ icon):
    - [ ] Category name
    - [ ] Description: "Vé máy bay, taxi"
    - [ ] Amount: 5,000,000 VNĐ
  - [ ] **Lưu trú** (🏨 icon):
    - [ ] Description: "Khách sạn, Airbnb"
    - [ ] Amount: 4,000,000 VNĐ
  - [ ] **Ăn uống** (🍽️ icon):
    - [ ] Description: "Nhà hàng, quán ăn đường phố"
    - [ ] Amount: 3,500,000 VNĐ
  - [ ] **Tham quan** (🎡 icon):
    - [ ] Description: "Vé vào cửa, tour du lịch"
    - [ ] Amount: 2,500,000 VNĐ
- [ ] **Card layout**: Icon + title + description + amount
- [ ] **Border dividers** giữa các items

### Bottom Action Bar
- [ ] **Fixed bottom bar** với shadow
- [ ] **Button group** (right-aligned):
  - [ ] "Đặt lại" button (gray outline)
  - [ ] "Xuất PDF" button (gray outline, với 📄 icon)
  - [ ] "Lưu thay đổi" button (orange/coral color)
- [ ] **Sticky positioning**

### Itinerary Editor (Tab 2)
- [ ] **Day selector**
- [ ] **Add activity button**
- [ ] **Drag-and-drop reordering**
- [ ] **Time picker** cho activities
- [ ] **Location autocomplete**
- [ ] **Delete activity** button

### Notes Editor (Tab 3)
- [ ] **Rich text editor**
- [ ] **Bullet points**
- [ ] **Add note button**
- [ ] **Save notes** functionality

---

## 🚨 ERROR PAGES

### 404 Page (`404.html`)
- [ ] **Large "404" heading**
- [ ] **Error message**: "Không tìm thấy trang"
- [ ] **Description**: "Trang bạn đang tìm kiếm không tồn tại"
- [ ] **"Về trang chủ" button**:
  - [ ] Primary color
  - [ ] Link to `/`
- [ ] **Center-aligned layout**
- [ ] **Simple, clean design**

### 500 Page (`500.html`)
- [ ] **Large "500" heading**
- [ ] **Error message**: "Lỗi server"
- [ ] **Description**: "Đã có lỗi xảy ra. Vui lòng thử lại sau"
- [ ] **"Về trang chủ" button**:
  - [ ] Primary color
  - [ ] Link to `/`
- [ ] **Center-aligned layout**
- [ ] **Red color scheme** cho error

---

## 🎨 GLOBAL UI FEATURES

### Design System
- [ ] **Color palette**:
  - [ ] Primary: #13a4ec (blue)
  - [ ] Secondary: #F5A623 (orange)
  - [ ] Background Light: #f6f7f8
  - [ ] Background Dark: #101c22
- [ ] **Typography**:
  - [ ] Font family: Plus Jakarta Sans
  - [ ] Font weights: 400, 500, 600, 700, 800
- [ ] **Border radius**:
  - [ ] Default: 0.5rem
  - [ ] lg: 1rem
  - [ ] xl: 1.5rem
  - [ ] full: 9999px

### Dark Mode Support
- [ ] **Automatic dark mode** detection
- [ ] **Manual toggle** (optional)
- [ ] **Consistent colors** across all pages
- [ ] **Dark variants** cho:
  - [ ] Backgrounds
  - [ ] Text colors
  - [ ] Borders
  - [ ] Shadows

### Responsive Design
- [ ] **Mobile-first approach**
- [ ] **Breakpoints**:
  - [ ] sm: 640px
  - [ ] md: 768px
  - [ ] lg: 1024px
  - [ ] xl: 1280px
- [ ] **Responsive navigation** (hamburger menu)
- [ ] **Flexible grids** (1/2/3 columns)
- [ ] **Touch-friendly** buttons (min 44px height)

### Animations & Transitions
- [ ] **Hover effects**:
  - [ ] Scale up cards
  - [ ] Color transitions
  - [ ] Shadow increase
- [ ] **Loading states**:
  - [ ] Skeleton screens (optional)
  - [ ] Spinner animations
  - [ ] Pulse effects
- [ ] **Smooth scrolling**
- [ ] **Slide-in animations** (optional)

### Icons
- [ ] **Material Symbols Outlined** library
- [ ] **Consistent icon usage**:
  - [ ] travel_explore (brand)
  - [ ] home, chat, list_alt (navigation)
  - [ ] calendar_month (dates)
  - [ ] paid, pie_chart (budget)
  - [ ] download, share, edit (actions)
  - [ ] check_circle (checkmarks)
  - [ ] add, more_vert (utilities)

### Accessibility
- [ ] **Semantic HTML** tags
- [ ] **Alt text** cho images
- [ ] **ARIA labels** (cần bổ sung)
- [ ] **Keyboard navigation** support
- [ ] **Focus indicators**
- [ ] **Color contrast** compliance

---

## 📊 TỔNG KẾT

### Thống kê tính năng

| Loại | Số lượng | Trạng thái |
|------|----------|-----------|
| **Pages** | 6 | ✅ Hoàn thành UI |
| **Sections** | 15+ | ✅ Hoàn thành UI |
| **Navigation items** | 8 | ✅ Hoàn thành UI |
| **Action buttons** | 30+ | ✅ Hoàn thành UI |
| **Form inputs** | 5+ | ✅ Hoàn thành UI |
| **Cards/Components** | 20+ | ✅ Hoàn thành UI |
| **Icons** | 40+ | ✅ Hoàn thành UI |

### Độ phủ tính năng

#### ✅ Đã có UI hoàn chỉnh (100%)
- Landing page với hero + features + testimonials
- Chat interface 2-panel với sample prompts
- Plans list với search & filter
- Plan detail với sidebar navigation
- Edit plan với tabs và budget editor
- Error pages 404/500
- Dark mode support
- Responsive design
- Material icons

#### 🔧 Cần tích hợp Backend
- [ ] Chat API connection
- [ ] Real-time messaging
- [ ] AI response parsing
- [ ] Plan CRUD operations
- [ ] Search & filter functionality
- [ ] File upload (PDF export)
- [ ] User authentication (optional)
- [ ] Data persistence

#### 🎯 Next Actions
1. **Test UI** - Chạy server và kiểm tra tất cả pages
2. **Implement AI** - Tích hợp Gemini API vào chat
3. **Connect APIs** - Kết nối frontend ↔ backend
4. **Add validation** - Form validation và error handling
5. **Polish UX** - Animations, loading states, notifications

---

## 📝 Notes

### Template Files
```
frontend/templates/
├── landingpage.html      (Landing + marketing)
├── main_chat.html        (2-panel chat interface)
├── danh_sach_ke_hoach.html (Plans grid)
├── chi_tiet_ke_hoach.html  (Plan detail)
├── edit_ke_hoach.html    (Plan editor)
├── 404.html              (Not found)
├── 500.html              (Server error)
├── base.html             (Simple base - backup)
├── index.html            (Simple chat - backup)
└── plans.html            (Simple plans - backup)
```

### JavaScript Files
```
frontend/static/js/
├── main_chat.js             (Chat interface logic)
├── danh_sach_ke_hoach.js   (Plans list logic)
├── chat.js                  (Backup)
├── plans.js                 (Backup)
└── utils.js                 (Utilities)
```

### Priority của các tính năng cần implement
1. **🔥 Critical**: Chat functionality, AI integration
2. **⚡ High**: Save plan, View plans, Plan detail
3. **📌 Medium**: Edit plan, Search/filter, PDF export
4. **✨ Low**: Dark mode toggle, Settings, Profile page

---

**Version**: 1.0  
**Last Updated**: 2025-10-22  
**Author**: khappha.online team  
**Status**: ✅ UI Complete | ⏳ Backend Integration Pending
