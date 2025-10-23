"""
SIMPLIFIED Prompts - Less detailed but faster and more reliable
Use this for better Gemini performance
"""

# Simplified itinerary prompt - much shorter, focused on essentials
ITINERARY_PROMPT_SIMPLE = """Tạo kế hoạch du lịch {destination} {duration_days} ngày, ngân sách {budget} VNĐ.

SỞ THÍCH: {preferences}

THÔNG TIN TÌM KIẾM:
{search_results}

YÊU CẦU TRẢ VỀ JSON:
{{
  "plan_name": "Tên kế hoạch hấp dẫn",
  "destination": "{destination}",
  "duration_days": {duration_days},
  "budget": {budget_number},
  "itinerary": [
    {{
      "day": 1,
      "title": "Ngày 1: Mô tả ngắn gọn",
      "activities": [
        {{
          "time": "08:00",
          "title": "Tên hoạt động",
          "description": "Mô tả chi tiết, địa chỉ, giá cả",
          "cost": 100000,
          "type": "breakfast/lunch/dinner/sightseeing/shopping/cafe/hotel"
        }}
      ]
    }}
  ],
  "cost_breakdown": {{
    "food": {{"amount": 1500000, "description": "Ăn uống 3 ngày"}},
    "accommodation": {{"amount": 1000000, "description": "Khách sạn 2 đêm"}},
    "transportation": {{"amount": 800000, "description": "Di chuyển"}},
    "activities": {{"amount": 500000, "description": "Tham quan"}},
    "other": {{"amount": 200000, "description": "Khác"}}
  }},
  "total_cost": {budget_number},
  "notes": ["Lưu ý 1", "Lưu ý 2"]
}}

CHỈ TRẢ VỀ JSON, KHÔNG TEXT KHÁC!
"""
