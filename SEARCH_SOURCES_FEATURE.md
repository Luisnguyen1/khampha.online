# Tính năng Kiến thức Tham khảo (Search Sources)

## Tổng quan
Tính năng này cho phép lưu trữ và hiển thị các trang web đã được sử dụng để tạo kế hoạch du lịch, giúp người dùng có thể tham khảo lại nguồn thông tin.

## Các thay đổi đã thực hiện

### 1. Backend - Search Tool (`backend/agents/search_tool.py`)

**Thêm method mới:**
```python
def extract_sources_for_storage(self, results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Extract source information for storage in database
    
    Returns:
        List of dicts with title, url, snippet for each source
    """
```

Trích xuất thông tin nguồn từ kết quả tìm kiếm để lưu vào database (title, url, snippet).

### 2. Backend - AI Agent (`backend/agents/ai_agent.py`)

**Cập nhật methods:**

1. **`_search_for_destination()`**: Trả về tuple (formatted_string, sources_list) thay vì chỉ string
2. **`_handle_plan_mode()`**: Capture search_sources và thêm vào plan_data
3. **`_handle_plan_mode_stream()`**: Tương tự cho streaming mode
4. **`_handle_ask_mode()`**: Trích xuất search sources cho chế độ hỏi đáp

### 3. Database - Schema (`backend/database/`)

**Migration script:** `migrate_add_search_sources.py`
- Thêm cột `search_sources` (TEXT) vào bảng `travel_plans`

**Models (`models.py`):**
```python
class TravelPlan:
    ...
    search_sources: Optional[str] = None  # JSON array of search sources
    
    def to_dict(self):
        ...
        'search_sources': json.loads(self.search_sources) if self.search_sources else [],
```

**Database Manager (`db_manager.py`):**
- Thêm parameter `search_sources` vào `save_plan()`
- Cập nhật `_row_to_travel_plan()` để parse search_sources

### 4. Backend - API (`backend/app.py`)

**Cập nhật endpoints:**
- `/api/chat`: Thêm `search_sources` khi save plan
- `/api/chat-stream`: Thêm `search_sources` khi save plan

### 5. Frontend - UI (`frontend/templates/chi_tiet_ke_hoach.html`)

**Thêm button:**
```html
<button id="references-button" onclick="openReferencesModal()">
    <span class="material-symbols-outlined">menu_book</span>
    <span>Kiến thức tham khảo</span>
</button>
```

**Thêm modal:**
```html
<div id="referencesModal">
    <!-- Modal header -->
    <!-- References list -->
    <!-- Modal footer -->
</div>
```

### 6. Frontend - JavaScript (`frontend/static/js/chi_tiet_ke_hoach.js`)

**Thêm functions:**
```javascript
function openReferencesModal()     // Mở modal
function closeReferencesModal()    // Đóng modal
function populateReferences()      // Populate danh sách từ plan data
```

## Cấu trúc dữ liệu

### Search Source Object
```json
{
    "title": "Tiêu đề trang web",
    "url": "https://example.com",
    "snippet": "Đoạn mô tả ngắn (max 200 ký tự)"
}
```

### Trong Database
```sql
-- Lưu dạng JSON array string
search_sources TEXT  -- '[{"title": "...", "url": "...", "snippet": "..."}]'
```

### Trong Plan Data
```python
{
    'plan_name': '...',
    'destination': '...',
    'search_sources': [
        {'title': '...', 'url': '...', 'snippet': '...'},
        {'title': '...', 'url': '...', 'snippet': '...'}
    ]
}
```

## Luồng hoạt động

1. **User tạo plan** → Chat "Tôi muốn đi Đà Lạt 3 ngày"

2. **AI Agent search** → `_search_for_destination()` tìm kiếm trên web
   - Trả về: (formatted_string, sources_list)

3. **AI Agent tạo plan** → Include search_sources vào plan_data

4. **Backend save plan** → Lưu search_sources vào database (JSON)

5. **User xem plan** → Load plan từ `/api/plans/{id}`
   - plan_data.search_sources được parse từ JSON

6. **User click "Kiến thức tham khảo"** → Modal hiển thị danh sách:
   - Số thứ tự
   - Tiêu đề
   - Snippet
   - Link (mở tab mới)

## Testing

### Test script: `test_search_sources.py`
```bash
cd d:\SGU_Hackathon
python test_search_sources.py
```

### Kết quả test:
✅ SearchTool.search() hoạt động
✅ extract_sources_for_storage() trích xuất đúng cấu trúc
✅ Tất cả sources có đủ keys: title, url, snippet

## UI/UX

### Vị trí button
- Sidebar bên phải (dưới nút "Tải xuống PDF")
- Icon: 📚 menu_book
- Text: "Kiến thức tham khảo"
- Màu: Xanh dương nhạt (bg-blue-100)

### Modal
- Full screen overlay với backdrop
- Max width: 3xl (48rem)
- Max height: 80vh
- Scrollable body
- Header: Icon + Title + Close button
- Footer: Info text về nguồn tham khảo

### References Display
- Card-based layout
- Số thứ tự trong circle
- Title (bold, 2 lines max)
- Snippet (gray, 2 lines max)
- Link với icon mở tab mới
- Hover effect

## Xử lý edge cases

1. **Không có search sources**: Hiển thị placeholder "Không có nguồn tham khảo"
2. **Plan cũ (trước migration)**: search_sources = null → Hiển thị message phù hợp
3. **Search fail**: sources = [] → Vẫn lưu plan, chỉ không có references
4. **XSS prevention**: Sử dụng escapeHtml() cho tất cả user content

## Dependencies

- **Python**: duckduckgo-search (đã có sẵn)
- **JavaScript**: Vanilla JS, không cần thêm library
- **CSS**: Tailwind CSS (đã có sẵn)

## Migration

```bash
cd backend
python database/migrate_add_search_sources.py
```

Output:
```
✅ Successfully added 'search_sources' column
✅ Migration completed successfully!
```

## Files Modified

### Backend
1. `backend/agents/search_tool.py` - Thêm extract_sources_for_storage()
2. `backend/agents/ai_agent.py` - Capture & return search sources
3. `backend/database/models.py` - Thêm search_sources field
4. `backend/database/db_manager.py` - Save & load search_sources
5. `backend/app.py` - Pass search_sources to db.save_plan()

### Database
6. `backend/database/migrate_add_search_sources.py` - Migration script

### Frontend
7. `frontend/templates/chi_tiet_ke_hoach.html` - Button + Modal HTML
8. `frontend/static/js/chi_tiet_ke_hoach.js` - Modal logic + populate

### Tests
9. `test_search_sources.py` - Verification script

## Tổng kết

Tính năng đã được triển khai đầy đủ:
✅ Backend: Search, extract, save sources
✅ Database: Schema migration, models update
✅ API: Endpoints support search_sources
✅ Frontend: Button, modal, display logic
✅ Testing: Verified working correctly

User có thể:
- Xem danh sách trang web đã tham khảo khi tạo plan
- Click vào link để mở trang web gốc
- Hiểu nguồn gốc thông tin của kế hoạch
