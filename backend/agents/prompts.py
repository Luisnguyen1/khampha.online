"""
AI Agent Prompts and Templates for khappha.online
Vietnamese-optimized prompts for travel planning
"""

# System prompt for the travel planning agent
SYSTEM_PROMPT = """Bạn là một trợ lý du lịch AI chuyên nghiệp, thân thiện và hiểu biết sâu về du lịch Việt Nam.

NHIỆM VỤ CỦA BẠN:
1. Lắng nghe nhu cầu du lịch của khách hàng
2. Đặt câu hỏi để hiểu rõ: điểm đến, số ngày, ngân sách, sở thích
3. Tìm kiếm thông tin thực tế về địa điểm
4. Đề xuất lịch trình chi tiết, thực tế và hấp dẫn
5. Tính toán chi phí ước tính hợp lý

PHONG CÁCH GIAO TIẾP:
- Thân thiện, nhiệt tình, chuyên nghiệp
- Sử dụng emoji phù hợp (🏖️ 🏔️ 🍜 💰)
- Câu văn ngắn gọn, dễ hiểu
- Đưa ra lời khuyên thực tế

THÔNG TIN QUAN TRỌNG:
- Luôn hỏi rõ: Điểm đến, Số ngày, Ngân sách, Sở thích (ẩm thực, thiên nhiên, văn hóa...)
- Đề xuất chi phí theo VNĐ
- Đề xuất giờ giấc hợp lý cho mỗi hoạt động
- Cảnh báo nếu ngân sách không khả thi

KHI TẠO KẾ HOẠCH:
- Chia rõ theo ngày (Day 1, Day 2...)
- Mỗi hoạt động có: Thời gian, Địa điểm, Mô tả, Chi phí ước tính
- Tổng hợp chi phí cuối cùng
- Lưu ý thời tiết, giao thông, điều kiện đặc biệt

CÔNG CỤ CỦA BẠN:
- search_web: Tìm kiếm thông tin thực tế về địa điểm, giá cả, review
"""

# Prompt for gathering user requirements
REQUIREMENTS_PROMPT = """Dựa trên tin nhắn của người dùng, hãy xác định:

TIN NHẮN: {user_message}

LỊCH SỬ HỘI THOẠI:
{conversation_history}

HÃY PHÂN TÍCH:
1. Điểm đến: [tên địa điểm hoặc "chưa rõ"]
2. Số ngày: [số ngày hoặc "chưa rõ"]
3. Ngân sách: [số tiền hoặc "chưa rõ"]
4. Sở thích: [danh sách hoặc "chưa rõ"]
5. Thông tin đã đủ để tạo kế hoạch: [có/không]

Nếu thông tin chưa đủ, hãy đặt câu hỏi tiếp theo một cách tự nhiên.
Nếu đã đủ, hãy xác nhận và bắt đầu tạo kế hoạch.
"""

# Prompt for creating detailed itinerary
ITINERARY_PROMPT = """Hãy tạo một kế hoạch du lịch CỰC KỲ CHI TIẾT dựa trên thông tin sau:

THÔNG TIN CHUYẾN ĐI:
- Điểm đến: {destination}
- Số ngày: {duration_days} ngày
- Ngân sách: {budget} VNĐ
- Sở thích: {preferences}

THÔNG TIN TÌM KIẾM:
{search_results}

YÊU CẦU TẠO KẾ HOẠCH CỰC KỲ CHI TIẾT:

1. TỔNG QUAN:
   - Tiêu đề hấp dẫn cho chuyến đi
   - Mô tả ngắn gọn (2-3 câu)

2. LỊCH TRÌNH SIÊU CHI TIẾT:
   Cho mỗi ngày, tạo cấu trúc với THÔNG TIN CỤ THỂ:
   
   🔥 QUAN TRỌNG - MỖI HOẠT ĐỘNG PHẢI CÓ:
   
   A. ĐI ĂN (Breakfast/Lunch/Dinner):
      - Tên quán ăn CỤ THỂ (VD: Quán Phở Hòa Pasteur, Bánh Mì Phượng)
      - Địa chỉ CHÍNH XÁC (VD: 123 Nguyễn Huệ, Quận 1, TP.HCM)
      - Món ăn ĐỀ XUẤT (VD: Phở bò tái, Bánh mì thịt nướng đặc biệt, Bún bò Huế)
      - Giá tiền TỪNG MÓN (VD: Phở: 50.000đ, Nước ngọt: 15.000đ)
      - Thời gian ăn ước tính
      - Lưu ý: Đặt chỗ trước, món ngon, giờ đông
   
   B. THAM QUAN/DU LỊCH:
      - Tên địa điểm ĐẦY ĐỦ (VD: Hồ Xuân Hương, Chùa Linh Phước, Đỉnh Langbiang)
      - Địa chỉ CỤ THỂ (VD: Phường 10, TP. Đà Lạt, Lâm Đồng)
      - Hoạt động CỤ THỂ (VD: Chụp ảnh hồ, Đi thuyền kayak, Leo đỉnh núi)
      - Giá vé chi tiết (VD: Vé vào cổng: 30.000đ, Thuê thuyền: 50.000đ/người)
      - Thời gian tham quan (VD: 1.5 - 2 giờ)
      - Cách di chuyển (VD: Đi bộ 10 phút, Taxi 15 phút 50.000đ)
   
   C. NGHỈ NGƠI/CAFE:
      - Tên quán cafe CỤ THỂ (VD: The Married Beans Coffee, Mê Linh Coffee Garden)
      - Địa chỉ CHÍNH XÁC
      - Đồ uống ĐỀ XUẤT với giá (VD: Cà phê sữa đá: 25.000đ, Bánh ngọt: 35.000đ)
      - View/Không gian đặc biệt
   
   D. MUA SẮM:
      - Tên chợ/shop CỤ THỂ (VD: Chợ Đà Lạt, Cửa hàng đặc sản ABC)
      - Địa chỉ CHÍNH XÁC
      - Món đồ NÊN MUA (VD: Mứt dâu tây: 50.000đ/hộp, Rượu sim: 100.000đ/chai)
      - Giá tham khảo
      - Tips mặc cả
   
   E. KHÁCH SẠN/NHÀ NGHỈ:
      - Tên khách sạn ĐỀ XUẤT (VD: Terracotta Hotel & Resort, Sammy Hotel)
      - Địa chỉ CHÍNH XÁC
      - Loại phòng (VD: Deluxe Double, Standard Twin)
      - Giá phòng/đêm (VD: 500.000đ - 800.000đ/đêm)
      - Tiện ích (VD: Có bữa sáng, Wifi, Bồn tắm)

   Cấu trúc JSON cho mỗi ngày:
   {{
     "day": 1,
     "title": "Ngày 1: Khám phá trung tâm [Địa điểm]",
     "activities": [
       {{
         "time": "07:00",
         "type": "breakfast",
         "title": "Ăn sáng tại [Tên quán cụ thể]",
         "restaurant_name": "Tên quán đầy đủ",
         "address": "Số nhà, đường, phường/quận, thành phố",
         "dishes": ["Món 1: giá", "Món 2: giá"],
         "description": "Mô tả chi tiết về quán, không gian, món ăn đặc sắc",
         "cost": 80000,
         "duration": "45 phút",
         "notes": "Tips: Nên đến trước 8h để tránh đông, món phở đặc biệt rất ngon"
       }},
       {{
         "time": "08:30",
         "type": "sightseeing",
         "title": "Tham quan [Tên địa điểm cụ thể]",
         "place_name": "Tên đầy đủ địa điểm",
         "address": "Địa chỉ chi tiết",
         "activities": ["Hoạt động 1", "Hoạt động 2", "Chụp ảnh tại góc X"],
         "description": "Mô tả chi tiết địa điểm, lịch sử, điểm nhấn",
         "entrance_fee": 50000,
         "other_costs": "Thuê thuyền: 30.000đ, Gửi xe: 10.000đ",
         "cost": 90000,
         "duration": "2 giờ",
         "transportation": "Taxi từ khách sạn, 15 phút, ~40.000đ",
         "notes": "Mở cửa 6h-18h, nên đến sáng sớm để tránh nắng"
       }},
       {{
         "time": "12:00",
         "type": "lunch",
         "title": "Ăn trưa tại [Tên nhà hàng cụ thể]",
         "restaurant_name": "Tên nhà hàng đầy đủ",
         "address": "Địa chỉ chi tiết",
         "dishes": ["Món chính: giá", "Món phụ: giá", "Đồ uống: giá"],
         "description": "Mô tả nhà hàng, đặc sản, không gian",
         "cost": 150000,
         "duration": "1 giờ",
         "notes": "Đặc sản là [món gì], nên gọi trước nếu đi nhóm đông"
       }}
     ]
   }}

3. CHI PHÍ CHI TIẾT TỪNG NGÀY:
   {{
     "day_1": {{
       "breakfast": {{amount, "Tại quán X"}},
       "lunch": {{amount, "Tại nhà hàng Y"}},
       "dinner": {{amount, "Tại Z"}},
       "transportation": {{amount, "Taxi, xe máy"}},
       "entrance_fees": {{amount, "Vé tham quan A, B, C"}},
       "other": {{amount, "Cafe, mua sắm"}},
       "total": day_total
     }},
     ...
   }}

4. TỔNG HỢP CHI PHÍ:
   {{
     "accommodation": {{amount, "Khách sạn X, Y phòng x Z đêm"}},
     "food": {{amount, "Ăn uống {duration_days} ngày"}},
     "transportation": {{amount, "Vé máy bay + di chuyển"}},
     "activities": {{amount, "Vé tham quan + hoạt động"}},
     "shopping": {{amount, "Mua quà, đặc sản"}},
     "reserve": {{amount, "Dự phòng 10%"}},
     "total": total_amount
   }}

5. DANH SÁCH NHÀ HÀNG/QUÁN ĂN ĐỀ XUẤT:
   - Tên, địa chỉ, món ngon, giá tham khảo cho TỪNG BỮA ĂN

6. DANH SÁCH KHÁCH SẠN ĐỀ XUẤT:
   - Tên, địa chỉ, loại phòng, giá phòng, tiện ích, đánh giá

7. LƯU Ý QUAN TRỌNG:
   - Thời tiết theo mùa
   - Phương tiện di chuyển cụ thể (bus, taxi, xe máy)
   - Nên mang theo gì
   - Số điện thoại khẩn cấp
   - Tips tiết kiệm

🔥 LƯU Ý QUAN TRỌNG NHẤT:
- KHÔNG được viết chung chung "ăn tại nhà hàng địa phương" - PHẢI ghi TÊN CỤ THỂ
- KHÔNG được viết "tham quan khu vực" - PHẢI ghi TÊN ĐỊA ĐIỂM CHÍNH XÁC
- MỖI địa điểm, nhà hàng, quán ăn PHẢI có ĐỊA CHỈ CỤ THỂ
- MỖI món ăn, vé tham quan PHẢI có GIÁ CỤ THỂ
- PHẢI có lộ trình di chuyển giữa các điểm (đi bộ, taxi, xe máy + thời gian)

HÃY TẠO KẾ HOẠCH CỰC KỲ CHI TIẾT, THỰC TẾ VÀ CỤ THỂ!
"""

# Prompt for search query generation
SEARCH_QUERY_PROMPT = """Dựa trên yêu cầu du lịch, hãy tạo các câu query tìm kiếm:

YÊU CẦU: {user_request}

Tạo 3-5 câu query tiếng Việt để tìm:
1. Thông tin địa điểm du lịch
2. Giá cả, chi phí
3. Lịch trình mẫu
4. Review, đánh giá
5. Tips, lưu ý

Trả về dạng JSON array: ["query 1", "query 2", ...]
"""

# Response templates
RESPONSE_TEMPLATES = {
    'greeting': """Xin chào! 👋 Tôi là trợ lý du lịch AI của khappha.online.

Tôi sẽ giúp bạn lên kế hoạch cho chuyến đi hoàn hảo! 

Để bắt đầu, hãy cho tôi biết:
🗺️ Bạn muốn đi đâu?
📅 Bao nhiêu ngày?
💰 Ngân sách dự kiến?
❤️ Bạn thích gì? (ẩm thực, thiên nhiên, văn hóa...)""",

    'missing_info': """Cảm ơn bạn! Để tạo kế hoạch tốt nhất, tôi cần thêm thông tin:

{missing_fields}

Bạn có thể cung cấp thêm được không? 😊""",

    'confirm_details': """Tuyệt vời! Để xác nhận lại:

📍 Điểm đến: {destination}
📅 Thời gian: {duration_days} ngày
💰 Ngân sách: {budget} VNĐ
❤️ Sở thích: {preferences}

Tôi sẽ tạo kế hoạch ngay! ⏱️ (Có thể mất 10-20 giây)""",

    'plan_ready': """✅ Kế hoạch của bạn đã sẵn sàng!

Tôi đã tạo một lịch trình chi tiết {duration_days} ngày với tổng chi phí ước tính khoảng {total_cost} VNĐ.

Bạn có thể:
💾 Lưu kế hoạch này
✏️ Chỉnh sửa theo ý muốn
📄 Xuất ra PDF

Hoặc hỏi tôi thêm về bất kỳ điều gì nhé! 😊""",

    'error': """Xin lỗi, đã có lỗi xảy ra: {error}

Hãy thử lại hoặc mô tả yêu cầu khác nhé! 🙏""",

    'no_search_results': """Hmm... Tôi không tìm thấy đủ thông tin về "{destination}". 

Bạn có thể:
- Thử tên địa điểm khác
- Cung cấp thêm chi tiết
- Hoặc để tôi gợi ý địa điểm khác? 🤔"""
}

def get_response_template(template_name, **kwargs):
    """Get formatted response template"""
    template = RESPONSE_TEMPLATES.get(template_name, "")
    return template.format(**kwargs)

def format_missing_fields(missing):
    """Format missing fields message"""
    field_names = {
        'destination': '📍 Điểm đến',
        'duration_days': '📅 Số ngày',
        'budget': '💰 Ngân sách',
        'preferences': '❤️ Sở thích'
    }
    
    return '\n'.join([f"- {field_names.get(field, field)}" for field in missing])

def create_search_queries(destination, preferences=None):
    """Create detailed search queries for a destination"""
    queries = [
        f"nhà hàng quán ăn ngon {destination} địa chỉ giá cả",
        f"địa điểm tham quan {destination} địa chỉ giá vé",
        f"khách sạn {destination} giá rẻ đẹp địa chỉ",
        f"{destination} lịch trình chi tiết địa điểm cụ thể",
        f"ăn gì ở {destination} món ngon quán nổi tiếng",
        f"chi phí du lịch {destination} ăn ở đi lại",
        f"chợ đêm mua sắm {destination} địa chỉ"
    ]
    
    if preferences:
        if isinstance(preferences, str):
            preferences = [p.strip() for p in preferences.split(',')]
        
        for pref in preferences[:2]:  # Top 2 preferences
            queries.append(f"{destination} {pref} địa chỉ giá cả")
            queries.append(f"quán {pref} ngon {destination}")
    
    return queries[:8]  # Maximum 8 detailed queries
