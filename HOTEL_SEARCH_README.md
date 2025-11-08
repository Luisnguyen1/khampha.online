# HotelSearcher Class - Hướng dẫn sử dụng

Class `HotelSearcher` giúp tìm kiếm khách sạn thông qua Agoda API (RapidAPI) một cách dễ dàng và linh hoạt.

## 🎯 Tính năng chính

### ✅ Cải tiến mới:
1. **Lấy giá chính xác** từ API response structure mới:
   - Giá mỗi đêm (`price_per_night`)
   - Tổng giá toàn bộ booking (`price_total`)
   - Giá gốc trước giảm (`price_crossed_out`)
   - Phần trăm giảm giá (`discount_percent`)

2. **Tìm kiếm linh hoạt theo ngày**:
   - Theo ngày cụ thể (checkin_date + checkout_date)
   - Theo số ngày từ hôm nay (days_from_now)
   - Chỉ cần ngày check-in, tự tính check-out

3. **Thông tin chi tiết**:
   - Tên khách sạn (localeName/defaultName)
   - Đánh giá và số lượng review
   - Hạng sao
   - Địa chỉ và tọa độ GPS
   - Danh sách hình ảnh

## 📦 Cài đặt

```bash
pip install requests
```

## 🚀 Cách sử dụng

### 1. Khởi tạo

```python
from hotel_search import HotelSearcher

API_KEY = "your_rapidapi_key_here"
searcher = HotelSearcher(api_key=API_KEY)
```

### 2. Tìm kiếm theo ngày cụ thể

```python
# Sử dụng string format (YYYY-MM-DD)
hotels = searcher.search_and_display(
    city_name="Đà Lạt",
    checkin_date="2025-12-20",
    checkout_date="2025-12-23",
    rooms=1,
    adults=2,
    max_results=5
)
```

```python
# Hoặc sử dụng date object
from datetime import date, timedelta

hotels = searcher.search_and_display(
    city_name="Hồ Chí Minh",
    checkin_date=date(2025, 12, 25),
    checkout_date=date(2025, 12, 28),
    rooms=2,
    adults=4,
    max_results=10
)
```

### 3. Tìm kiếm theo số ngày từ hôm nay

```python
# Nhận phòng sau 30 ngày, ở 3 đêm
hotels = searcher.search_and_display(
    city_name="Đà Lạt",
    days_from_now=30,
    nights=3,
    rooms=1,
    adults=2
)
```

### 4. Chỉ cần ngày check-in

```python
# Tự động tính check-out dựa vào số đêm
from datetime import date, timedelta

hotels = searcher.search_and_display(
    city_name="Đà Nẵng",
    checkin_date=date.today() + timedelta(days=15),
    nights=2,  # Ở 2 đêm
    max_results=5
)
```

### 5. Lưu kết quả vào file JSON

```python
hotels = searcher.search_and_display(
    city_name="Đà Lạt",
    checkin_date="2025-12-20",
    checkout_date="2025-12-23",
    save_to_file="dalat_hotels.json"  # Lưu raw data
)
```

## 📊 Cấu trúc dữ liệu trả về

Mỗi khách sạn trong list trả về có cấu trúc:

```python
{
    'hotel_id': 52294627,
    'name': 'Villa đà lạt Trung Nghĩa 1',
    'rating': 8.5,
    'review_count': 120,
    'price_per_night': 233000.0,        # Giá mỗi đêm
    'price_total': 699000.0,             # Tổng giá
    'price_crossed_out': 2796000.0,      # Giá gốc
    'discount_percent': 75,              # % giảm giá
    'currency': 'VND',
    'is_available': True,
    'address': {...},
    'star_rating': 4,
    'latitude': 11.937788963317871,
    'longitude': 108.45995330810547,
    'images': ['url1', 'url2', ...]
}
```

## 🔧 API Methods

### `get_city_id(city_name, language="vi-vn")`
Lấy ID của thành phố từ tên.

```python
city_id = searcher.get_city_id("Đà Lạt")
# Returns: 15932
```

### `search_hotels(city_id, city_name, checkin_date, checkout_date, ...)`
Tìm kiếm khách sạn với các tham số chi tiết.

```python
from datetime import date, timedelta

data = searcher.search_hotels(
    city_id=15932,
    city_name="Đà Lạt",
    checkin_date=date.today() + timedelta(days=30),
    checkout_date=date.today() + timedelta(days=33),
    rooms=1,
    adults=2,
    currency="VND",
    save_to_file="result.json"
)
```

### `extract_hotels(search_data)`
Trích xuất danh sách khách sạn từ raw response.

```python
hotels = searcher.extract_hotels(search_data)
```

### `format_hotel_info(hotel, currency="VND")`
Định dạng thông tin khách sạn từ raw data.

```python
formatted = searcher.format_hotel_info(hotel_raw_data)
```

## 💡 Tips

### Tìm kiếm linh hoạt
```python
# Cách 1: Ngày cụ thể (ưu tiên cao nhất)
searcher.search_and_display(
    city_name="Đà Lạt",
    checkin_date="2025-12-20",
    checkout_date="2025-12-23"
)

# Cách 2: Chỉ check-in + nights
searcher.search_and_display(
    city_name="Đà Lạt",
    checkin_date="2025-12-20",
    nights=3  # Auto tính checkout = 2025-12-23
)

# Cách 3: days_from_now (backward compatible)
searcher.search_and_display(
    city_name="Đà Lạt",
    days_from_now=30,
    nights=3
)
```

### Lọc và sắp xếp kết quả
```python
hotels = searcher.search_and_display(city_name="Đà Lạt", ...)

# Lọc theo giá
cheap_hotels = [h for h in hotels if h['price_per_night'] and h['price_per_night'] < 500000]

# Sắp xếp theo rating
sorted_hotels = sorted(hotels, key=lambda x: x['rating'] or 0, reverse=True)

# Lọc theo discount
big_discount = [h for h in hotels if h['discount_percent'] and h['discount_percent'] > 50]
```

## 📝 Ví dụ hoàn chỉnh

```python
from hotel_search import HotelSearcher
from datetime import date, timedelta

# Init
searcher = HotelSearcher(api_key="YOUR_API_KEY")

# Tìm khách sạn cho kỳ nghỉ
hotels = searcher.search_and_display(
    city_name="Đà Lạt",
    checkin_date="2025-12-20",
    checkout_date="2025-12-25",
    rooms=1,
    adults=2,
    max_results=10,
    save_to_file="dalat_christmas.json"
)

# Phân tích kết quả
print(f"\nTìm thấy {len(hotels)} khách sạn")

# Khách sạn rẻ nhất
cheapest = min(hotels, key=lambda x: x['price_total'] or float('inf'))
print(f"Rẻ nhất: {cheapest['name']} - {cheapest['price_total']:,.0f} VND")

# Đánh giá cao nhất
best_rated = max(hotels, key=lambda x: x['rating'] or 0)
print(f"Rating cao nhất: {best_rated['name']} - {best_rated['rating']}/10")

# Giảm giá nhiều nhất
best_deal = max(hotels, key=lambda x: x['discount_percent'] or 0)
print(f"Giảm giá nhiều nhất: {best_deal['name']} - {best_deal['discount_percent']}%")
```

## 🌟 Response từ API

Cấu trúc giá trong API response:
```
pricing.offers[0].roomOffers[0].room.pricing[0].price
├── perRoomPerNight
│   ├── inclusive.display      -> price_per_night
│   └── inclusive.crossedOutPrice
├── perBook
│   ├── inclusive.display      -> price_total
│   └── inclusive.crossedOutPrice -> price_crossed_out
└── totalDiscount              -> discount_percent
```

## ⚠️ Lưu ý

1. **API Key**: Cần đăng ký RapidAPI và subscribe vào Agoda API
2. **Rate Limit**: Tuân thủ giới hạn của RapidAPI plan
3. **Ngày**: Nếu dùng cả `checkin_date` và `days_from_now`, `checkin_date` được ưu tiên
4. **Currency**: Mặc định VND, có thể đổi sang USD, EUR, etc.
5. **Language**: Mặc định "vi-vn", có thể đổi sang "en-us", etc.
