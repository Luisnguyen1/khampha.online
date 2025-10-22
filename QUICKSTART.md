# 🎯 QUICKSTART GUIDE - khappha.online

## ⚡ Chạy nhanh trong 5 phút

### 1. Cài đặt dependencies
```powershell
cd d:\SGU_Hackathon\backend
pip install -r requirements.txt
```

### 2. Khởi tạo database
```powershell
python -m database.init_db
```

### 3. Chạy server
```powershell
python app.py
```

### 4. Mở browser
- Landing page: http://localhost:5000
- Chat interface: http://localhost:5000/chat
- Plans list: http://localhost:5000/plans

---

## ✅ Tính năng đã hoàn thiện

### Backend Core ✅
- [x] Database với SQLite (models, CRUD operations)
- [x] Flask API với 11 endpoints
- [x] Session management
- [x] Error handling 404/500

### AI Agent ✅
- [x] Search tool (DuckDuckGo)
- [x] Prompts templates (Vietnamese-optimized)
- [x] AI Agent với Gemini Flash 2.0
- [x] Requirements extraction
- [x] Itinerary generation
- [x] Tích hợp vào `/api/chat`

### Frontend ✅
- [x] Landing page (marketing)
- [x] Main chat (2-panel interface)
- [x] Plans list (grid với search)
- [x] Plan detail page
- [x] Edit plan page
- [x] Error pages
- [x] JavaScript logic cho chat & plans
- [x] Search & filter functionality
- [x] Responsive design
- [x] Dark mode support

---

## 🔧 Đang hoàn thiện

### Priority 1 - Critical 🔥
- [ ] Test AI chat end-to-end
- [ ] Parse AI response thành plan structure
- [ ] Update plan view khi có response
- [ ] Save plan từ chat
- [ ] Load real plans từ database

### Priority 2 - High ⚡
- [ ] Plan detail page với real data
- [ ] Edit plan functionality
- [ ] Delete plan confirmation
- [ ] PDF export

### Priority 3 - Medium 📌
- [ ] Filter buttons logic hoàn chỉnh
- [ ] Upload images
- [ ] Share plan (copy link)
- [ ] Favorite/unfavorite

### Priority 4 - Low ✨
- [ ] Settings page
- [ ] Profile page
- [ ] Dark mode toggle button
- [ ] Animations polish

---

## 📝 Test Checklist

### Test Backend
```powershell
# Test database
python -m database.init_db

# Test AI agent standalone
python -m agents.ai_agent

# Test search tool
python -m agents.search_tool
```

### Test API
```powershell
# Health check
curl http://localhost:5000/api/health

# Chat (khi server đang chạy)
curl -X POST http://localhost:5000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Tôi muốn đi Đà Lạt 3 ngày\"}"

# Get plans
curl http://localhost:5000/api/plans
```

### Test Frontend
1. Mở http://localhost:5000
2. Click "Trải nghiệm ngay"
3. Chat: "Tôi muốn đi Đà Lạt 3 ngày 2 đêm, ngân sách 5 triệu"
4. Kiểm tra response có plan không
5. Click "Lưu kế hoạch"
6. Vào http://localhost:5000/plans kiểm tra

---

## 🐛 Troubleshooting

### Lỗi: "GEMINI_API_KEY not found"
```powershell
# Kiểm tra file .env có API key chưa
cat .env

# Nếu chưa có, thêm vào:
echo GEMINI_API_KEY=your-api-key-here >> .env
```

### Lỗi: "No module named 'google.generativeai'"
```powershell
pip install google-generativeai==0.3.0
```

### Lỗi: Database locked
```powershell
# Xóa database cũ và tạo lại
rm data/travelmate.db
python -m database.init_db
```

### AI không hoạt động
- Kiểm tra API key đúng chưa
- Kiểm tra internet connection
- Xem logs trong terminal
- Thử với mock mode (agent sẽ tự động fallback)

---

## 📊 Progress Overview

```
✅ Phase 0: Setup (100%)
✅ Phase 1: Backend Core (100%)  
✅ Phase 2: AI Agent (100%)
🔄 Phase 3: Frontend Integration (80%)
⏳ Phase 4: Polish & Test (0%)
```

**Tổng tiến độ: ~70%**

---

## 🎯 Next Steps

1. **Test chat flow** - Đảm bảo AI trả lời đúng
2. **Fix plan display** - Hiển thị itinerary trong chat
3. **Save plan** - Lưu vào database thành công
4. **Load plans** - Hiển thị danh sách từ DB
5. **Polish UX** - Loading states, animations

---

## 💡 Tips

- Dùng Chrome DevTools để debug JavaScript
- Check Console cho errors
- Check Network tab cho API calls
- Xem logs trong terminal cho backend errors
- Dùng mock data nếu API không hoạt động

---

**Cần trợ giúp?** Check logs hoặc hỏi AI assistant! 🤖
