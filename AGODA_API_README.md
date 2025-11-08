# Agoda Flight Search API - Class Documentation

## Giới thiệu

`AgodaFlightSearchAPI` là một class Python hoàn chỉnh để tìm kiếm chuyến bay qua Agoda API trên RapidAPI. Class được thiết kế để dễ sử dụng, tái sử dụng và mở rộng.

## Cài đặt

```bash
pip install requests
```

## Khởi tạo

```python
from test import AgodaFlightSearchAPI

API_KEY = "your-rapidapi-key-here"
api = AgodaFlightSearchAPI(API_KEY)
```

## Các phương thức chính

### 1. Tìm kiếm địa điểm (Auto-complete)

```python
result = api.search_location("Hanoi")
```

**Tham số:**
- `query` (str): Tên địa điểm cần tìm

**Trả về:**
- Dict chứa danh sách gợi ý địa điểm hoặc None

### 2. Tìm kiếm chuyến bay một chiều

```python
result = api.search_one_way_flight(
    origin="SGN",
    destination="HAN", 
    departure_date="2025-11-15",
    currency="VND",
    adults=1,
    children=0,
    infants=0
)
```

**Tham số:**
- `origin` (str): Mã sân bay đi (ví dụ: "SGN")
- `destination` (str): Mã sân bay đến (ví dụ: "HAN")
- `departure_date` (str): Ngày khởi hành (format: "YYYY-MM-DD")
- `currency` (str, optional): Loại tiền tệ (mặc định: "VND")
- `adults` (int, optional): Số người lớn (mặc định: 1)
- `children` (int, optional): Số trẻ em (mặc định: 0)
- `infants` (int, optional): Số em bé (mặc định: 0)

**Trả về:**
- Dict chứa dữ liệu JSON từ API hoặc None

### 3. Tìm kiếm chuyến bay khứ hồi

```python
result = api.search_round_trip_flight(
    origin="SGN",
    destination="HAN",
    departure_date="2025-11-15",
    return_date="2025-11-20",
    currency="VND",
    adults=1
)
```

**Tham số:** Tương tự `search_one_way_flight` nhưng có thêm:
- `return_date` (str): Ngày về (format: "YYYY-MM-DD")

### 4. Trích xuất thông tin chuyến bay

```python
flights = api.extract_flight_info(flight_data)
```

**Tham số:**
- `flight_data` (dict): Dữ liệu JSON trả về từ API

**Trả về:**
- List các dict chứa thông tin chi tiết:
  - `departure_time`: Thời gian khởi hành
  - `arrival_time`: Thời gian đến
  - `duration`: Thời gian bay (phút)
  - `carrier_name`: Tên hãng bay
  - `carrier_code`: Mã hãng bay
  - `flight_number`: Số hiệu chuyến bay
  - `origin_airport`: Tên sân bay đi
  - `destination_airport`: Tên sân bay đến
  - `origin_code`: Mã sân bay đi
  - `destination_code`: Mã sân bay đến
  - `stops`: Số điểm dừng
  - `price_vnd`: Giá trọn gói (VND)
  - `cabin_class`: Hạng ghế
  - `overnight_flight`: Bay đêm hay không
  - Và nhiều thông tin khác...

### 5. Lọc chuyến bay

```python
filtered_flights = api.filter_flights(
    flights,
    max_price=2000000,
    direct_only=True,
    carriers=["VN", "VJ"],
    max_duration=150
)
```

**Tham số:**
- `flights` (list): Danh sách chuyến bay cần lọc
- `max_price` (float, optional): Giá tối đa (VND)
- `direct_only` (bool, optional): Chỉ lấy chuyến bay thẳng
- `carriers` (list, optional): Danh sách mã hãng bay
- `max_duration` (int, optional): Thời gian bay tối đa (phút)

**Trả về:**
- List chuyến bay đã lọc

### 6. Sắp xếp chuyến bay

```python
sorted_flights = api.sort_flights(flights, sort_by='price')
```

**Tham số:**
- `flights` (list): Danh sách chuyến bay cần sắp xếp
- `sort_by` (str): Tiêu chí sắp xếp
  - `'price'`: Theo giá
  - `'duration'`: Theo thời gian bay
  - `'departure_time'`: Theo giờ khởi hành

**Trả về:**
- List chuyến bay đã sắp xếp

### 7. Lấy mã sân bay từ tên địa điểm

```python
airport_code = api.get_airport_code("Hanoi")
# Trả về: "HAN"
```

### 8. Lưu dữ liệu vào file JSON

```python
api.save_to_json(data, 'flights.json')
```

### 9. Hiển thị thông tin chuyến bay

```python
api.print_flight_summary(flight, index=1)
```

## Ví dụ sử dụng

### Ví dụ 1: Tìm kiếm chuyến bay cơ bản

```python
from test import AgodaFlightSearchAPI

api = AgodaFlightSearchAPI("your-api-key")

# Tìm kiếm chuyến bay
result = api.search_one_way_flight("SGN", "HAN", "2025-11-15")

# Trích xuất thông tin
flights = api.extract_flight_info(result)

# Hiển thị chuyến bay đầu tiên
if flights:
    api.print_flight_summary(flights[0])
```

### Ví dụ 2: Tìm chuyến bay rẻ nhất

```python
# Tìm kiếm
result = api.search_one_way_flight("SGN", "HAN", "2025-11-15")
flights = api.extract_flight_info(result)

# Sắp xếp theo giá
sorted_flights = api.sort_flights(flights, sort_by='price')

# Lấy chuyến rẻ nhất
cheapest = sorted_flights[0]
print(f"Giá: {cheapest['price_vnd']:,.0f} VND")
```

### Ví dụ 3: Lọc chuyến bay theo điều kiện

```python
# Tìm kiếm
result = api.search_one_way_flight("SGN", "HAN", "2025-11-15")
flights = api.extract_flight_info(result)

# Lọc: bay thẳng, giá dưới 2 triệu VND
filtered = api.filter_flights(
    flights,
    max_price=2000000,
    direct_only=True
)

# Sắp xếp theo giá
sorted_flights = api.sort_flights(filtered, sort_by='price')

# Hiển thị top 5
for i, flight in enumerate(sorted_flights[:5], 1):
    api.print_flight_summary(flight, i)
```

### Ví dụ 4: Tìm kiếm tự động với tên địa điểm

```python
# Tự động lấy mã sân bay
origin_code = api.get_airport_code("Ho Chi Minh")  # SGN
dest_code = api.get_airport_code("Hanoi")          # HAN

# Tìm kiếm với mã vừa lấy
result = api.search_one_way_flight(origin_code, dest_code, "2025-11-15")
flights = api.extract_flight_info(result)
```

### Ví dụ 5: Lọc theo hãng bay

```python
# Tìm kiếm
result = api.search_one_way_flight("SGN", "HAN", "2025-11-15")
flights = api.extract_flight_info(result)

# Chỉ lấy chuyến bay Vietnam Airlines
vn_flights = api.filter_flights(flights, carriers=['VN'])

# Hiển thị
for flight in vn_flights:
    print(f"{flight['flight_number']}: {flight['price_vnd']:,.0f} VND")
```

### Ví dụ 6: Tìm chuyến bay nhanh nhất

```python
# Tìm kiếm
result = api.search_one_way_flight("SGN", "HAN", "2025-11-15")
flights = api.extract_flight_info(result)

# Sắp xếp theo thời gian bay
fastest_flights = api.sort_flights(flights, sort_by='duration')

# Lấy chuyến nhanh nhất
fastest = fastest_flights[0]
print(f"Thời gian: {fastest['duration']} phút")
```

### Ví dụ 7: Tìm kiếm nhiều người

```python
# Tìm kiếm cho 2 người lớn và 1 trẻ em
result = api.search_one_way_flight(
    "SGN", 
    "HAN", 
    "2025-11-15",
    adults=2,
    children=1
)

flights = api.extract_flight_info(result)
print(f"Giá cho 2 người lớn + 1 trẻ em: {flights[0]['price_vnd']:,.0f} VND")
```

### Ví dụ 8: Lưu kết quả

```python
# Tìm kiếm
result = api.search_one_way_flight("SGN", "HAN", "2025-11-15")

# Lưu dữ liệu raw
api.save_to_json(result, 'raw_data.json')

# Trích xuất và lưu dữ liệu đã xử lý
flights = api.extract_flight_info(result)
api.save_to_json(flights, 'processed_data.json')
```

## Cấu trúc dữ liệu chuyến bay

Mỗi chuyến bay trong list trả về có cấu trúc:

```python
{
    'departure_time': '2025-11-15T23:20:00',
    'arrival_time': '2025-11-16T01:30:00',
    'duration': 130,  # phút
    'carrier_name': 'VietJet Air',
    'carrier_code': 'VJ',
    'carrier_logo': 'https://...',
    'flight_number': '182',
    'origin_airport': 'Tan Son Nhat International Airport',
    'destination_airport': 'Noi Bai International Airport',
    'origin_city': 'Ho Chi Minh City',
    'destination_city': 'Hanoi',
    'origin_code': 'SGN',
    'destination_code': 'HAN',
    'stops': 0,  # 0 = bay thẳng
    'layover_info': [],  # Thông tin điểm dừng nếu có
    'price_vnd': 1128623.0,
    'cabin_class': 'Economy Class',
    'overnight_flight': False,
    'bundle_key': '1617193676',
    'segments': [...]  # Chi tiết các segment
}
```

## Mã hãng bay phổ biến

- `VN`: Vietnam Airlines
- `VJ`: VietJet Air
- `QH`: Bamboo Airways
- `VU`: Vietravel Airlines

## Mã sân bay Việt Nam

- `SGN`: Sân bay Tân Sơn Nhất (TP. HCM)
- `HAN`: Sân bay Nội Bài (Hà Nội)
- `DAD`: Sân bay Đà Nẵng
- `CXR`: Sân bay Cam Ranh (Nha Trang)
- `HPH`: Sân bay Cát Bi (Hải Phòng)
- `PQC`: Sân bay Phú Quốc
- `VCA`: Sân bay Cần Thơ

## Xử lý lỗi

Class tự động xử lý lỗi và trả về None hoặc list rỗng khi có lỗi. Bạn nên kiểm tra kết quả:

```python
result = api.search_one_way_flight("SGN", "HAN", "2025-11-15")

if result:
    flights = api.extract_flight_info(result)
    if flights:
        # Xử lý dữ liệu
        pass
    else:
        print("Không tìm thấy chuyến bay")
else:
    print("Lỗi khi gọi API")
```

## Best Practices

1. **Cache kết quả**: Lưu kết quả API vào file để tránh gọi API nhiều lần
2. **Xử lý lỗi**: Luôn kiểm tra kết quả trả về
3. **Sử dụng filter**: Lọc dữ liệu sau khi nhận để giảm số lần gọi API
4. **Rate limiting**: Chú ý giới hạn số lần gọi API của RapidAPI

## Tích hợp vào dự án

### Cách 1: Import trực tiếp

```python
from test import AgodaFlightSearchAPI

api = AgodaFlightSearchAPI("your-api-key")
```

### Cách 2: Tạo wrapper class

```python
from test import AgodaFlightSearchAPI

class MyFlightService:
    def __init__(self, api_key):
        self.api = AgodaFlightSearchAPI(api_key)
    
    def find_cheapest_flight(self, origin, destination, date):
        result = self.api.search_one_way_flight(origin, destination, date)
        flights = self.api.extract_flight_info(result)
        sorted_flights = self.api.sort_flights(flights, sort_by='price')
        return sorted_flights[0] if sorted_flights else None
```

## License

MIT License

## Support

Để được hỗ trợ, vui lòng tạo issue trên GitHub hoặc liên hệ qua email.
