# Discovery Feature - Tinder-style Destination Explorer

## 🎯 Tính năng

Khám phá các địa điểm du lịch nổi tiếng tại Việt Nam theo phong cách swipe (vuốt) giống Tinder:
- ❌ Swipe trái hoặc nhấn nút ❌ để bỏ qua
- 💚 Swipe phải hoặc nhấn nút 💚 để thêm vào yêu thích
- 🗺️ Nhấn nút 🗺️ để lên kế hoạch ngay cho địa điểm đó

## 📁 Files đã tạo

### Frontend
1. **`frontend/static/js/destinations-data.js`**
   - Chứa danh sách 20 địa điểm du lịch nổi tiếng Việt Nam
   - Mỗi địa điểm có: tên, region, description, tags, pexelsQuery

2. **`frontend/static/js/discover.js`**
   - PexelsClient: Gọi Pexels API trực tiếp từ frontend
   - DiscoveryApp: Quản lý state, swipe logic, localStorage tracking
   - Hammer.js integration cho touch gestures

3. **`frontend/templates/discover.html`**
   - UI với 3-card stack
   - Responsive design với Tailwind CSS
   - Touch-friendly controls

### Backend
4. **`backend/app.py`** (đã update)
   - Thêm route `/discover` với decorator `@require_login`

### Integration
5. **`frontend/templates/main_chat.html`** (đã update)
   - Link "Discover" trong sidebar đã được kích hoạt

6. **`frontend/static/js/main_chat.js`** (đã update)
   - Thêm function `checkAutoSendMessage()` để auto-send message từ URL parameter

## 🚀 Cách sử dụng

### 1. Truy cập trang Discovery
```
http://localhost:5000/discover
```

### 2. Swipe để khám phá
- **Swipe trái/phải** hoặc dùng nút ❌/💚
- **Nhấn 🗺️** để lên kế hoạch cho địa điểm đó

### 3. Auto-redirect to Chat
Khi nhấn "Lên Kế Hoạch":
- Tự động chuyển đến `/chat?message=Tôi muốn lên kế hoạch đi du lịch <tên địa điểm>`
- Message tự động được điền và gửi sau 0.5s

## 🔧 Cấu hình

### Pexels API Key
API key đã được hardcode trong `discover.js`:
```javascript
const PEXELS_API_KEY = 'MUPx8XZ2LA9uUVFMCEgjAxzoVLZ6gHCG5DrhjXCbZeFDL3uEJ9De8xX5';
```

**Rate Limit:** 200 requests/hour (Free tier)

### LocalStorage Keys
```javascript
'discover_liked_destinations'  // Array of liked destination IDs
'discover_seen_destinations'   // Array of seen destination IDs
'pexels_usage'                 // API usage tracking (timestamps)
```

## 📱 Mobile Support

- Touch gestures với Hammer.js
- Responsive design
- Optimized cho màn hình nhỏ

## 🎨 UI Features

### Card Stack
- 3 cards hiển thị cùng lúc
- Scale effect: 1.0, 0.95, 0.9
- Smooth transitions

### Animations
- Swipe rotation effect
- Card exit animations
- Loading spinner
- Empty state with reset button

### Photographer Attribution
Tất cả ảnh từ Pexels đều có credit photographer ở góc dưới card

## 🔄 Flow

```
1. User vào /discover
   ↓
2. App load 20 destinations từ destinations-data.js
   ↓
3. Chọn random từ unseen destinations (localStorage)
   ↓
4. Fetch ảnh từ Pexels API (portrait size)
   ↓
5. Render 3-card stack với Hammer.js gestures
   ↓
6. User swipe:
   - Trái: Add to seen
   - Phải: Add to liked + seen
   - Plan button: Redirect to /chat?message=...
   ↓
7. Load next destination (preload images)
   ↓
8. Repeat until hết destinations
   ↓
9. Empty state với nút "Khám phá lại"
```

## 🐛 Troubleshooting

### Pexels API không hoạt động
- Kiểm tra console log (F12)
- Check rate limit: localStorage.getItem('pexels_usage')
- Fallback images sẽ được dùng nếu API fail

### Swipe không hoạt động
- Kiểm tra Hammer.js CDN đã load: `typeof Hammer`
- Clear browser cache
- Thử trên mobile device thật

### LocalStorage bị đầy
```javascript
localStorage.clear(); // Xóa tất cả
// Hoặc
discoveryApp.resetProgress(); // Chỉ xóa discover data
```

## 📊 Statistics

### Bundle Size
- `destinations-data.js`: ~8KB
- `discover.js`: ~12KB
- `discover.html`: ~10KB
- Hammer.js CDN: ~21KB

### API Usage
- Average 1-2 API calls per destination
- Cache trong memory cho session
- Rate limit tracking trong localStorage

## 🎯 Future Enhancements

1. **Backend sync** cho liked destinations
2. **Recommendation algorithm** dựa trên user preferences
3. **Social sharing** cho destinations
4. **Filter by region/category**
5. **User-generated content** (photos, reviews)
6. **Offline mode** với cached images

## ✅ Testing Checklist

- [ ] Swipe gestures hoạt động (trái/phải)
- [ ] Buttons hoạt động (❌/💚/🗺️)
- [ ] Pexels API fetch ảnh thành công
- [ ] LocalStorage tracking đúng
- [ ] Empty state hiển thị khi hết cards
- [ ] Reset button hoạt động
- [ ] Redirect to chat với message đúng
- [ ] Auto-send message trong chat
- [ ] Responsive trên mobile
- [ ] Photographer attribution hiển thị

## 📝 Notes

- **MVP approach:** API key hardcoded (chấp nhận cho testing)
- **Production:** Di chuyển API calls sang backend proxy
- **Performance:** Preload 3 destinations để UX mượt
- **UX:** 0.5s delay trước auto-send để user thấy message
