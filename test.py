import requests
import json
from datetime import date, timedelta

# --- 1. CẤU HÌNH CHUNG ---
RAPIDAPI_HOST = "agoda-com.p.rapidapi.com"
RAPIDAPI_KEY = "fe30b4f590msh6817e6a304fb995p1382dejsn50ae5d7c997d" 

# Headers sử dụng chung cho cả hai API call
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST
}

# --- 2. HÀM CHÍNH THỰC HIỆN LƯU LƯỢNG ---
def get_dalat_id_and_search_hotels():
    # Tham số tìm kiếm chung
    DESTINATION_NAME = "Đà Lạt"
    
    # URL cho Bước 1: Lấy ID
    URL_AUTO_COMPLETE = f"https://{RAPIDAPI_HOST}/hotels/auto-complete"
    
    # URL cho Bước 2: Tìm khách sạn
    URL_SEARCH_HOTELS = f"https://{RAPIDAPI_HOST}/hotels/search-overnight"
    
    # Biến để lưu trữ ID
    dalat_id = None

    # ===============================================
    # BƯỚC 1: LẤY CITY ID CỦA ĐÀ LẠT (hotels/auto-complete)
    # ===============================================
    print("=============================================")
    print(f"BƯỚC 1: Đang tìm kiếm City ID cho '{DESTINATION_NAME}'...")
    print("=============================================")
    
    querystring_id = {
        "query": DESTINATION_NAME,
        "language": "vi-vn"
    }

    try:
        response = requests.get(URL_AUTO_COMPLETE, headers=HEADERS, params=querystring_id)
        response.raise_for_status()
        data_id = response.json()
        
        if data_id and 'places' in data_id and data_id['places']:
            # Lọc ra đối tượng là 'Thành Phố' (City) và ở 'Việt Nam'
            dalat_city = next((p for p in data_id['places'] 
                               if p.get('typeName') in ('Thành Phố', 'City') 
                               and p.get('country', {}).get('name') == 'Việt Nam'), None)
            
            if dalat_city:
                dalat_id = dalat_city.get('id')
                print(f"✅ ID chính xác của {DESTINATION_NAME} là: **{dalat_id}**")
            else:
                print(f"❌ Lỗi: Không tìm thấy ID cho thành phố '{DESTINATION_NAME}'.")
                return # Dừng nếu không tìm thấy ID
        else:
            print("❌ Lỗi: Không nhận được dữ liệu hợp lệ từ API auto-complete.")
            return

    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi khi gọi API auto-complete: {e}")
        return

    # ===============================================
    # BƯỚC 2: TÌM KIẾM KHÁCH SẠN (hotels/search-overnight)
    # ===============================================
    
    if dalat_id:
        print("\n=============================================")
        print(f"BƯỚC 2: Đang tìm kiếm khách sạn bằng ID {dalat_id}...")
        print("=============================================")
        
        # Định nghĩa ngày tháng (nhận phòng sau 30 ngày, ở 3 đêm)
        ngay_nhan_phong = date.today() + timedelta(days=30)
        ngay_tra_phong = ngay_nhan_phong + timedelta(days=3)

        querystring_search = {
            # Sử dụng ID đã tìm thấy
            "id": "1_" + str(dalat_id), 
            "query": DESTINATION_NAME,            
            
            # Khắc phục lỗi thiếu 'checkinDate' và 'checkoutDate'
            "checkinDate": ngay_nhan_phong.strftime("%Y-%m-%d"), 
            "checkoutDate": ngay_tra_phong.strftime("%Y-%m-%d"),  
            
            "rooms": "1",                 
            "adults": "2",                
            "language": "vi-vn",          
            "currency": "VND"             
        }

        try:
            response = requests.get(URL_SEARCH_HOTELS, headers=HEADERS, params=querystring_search)
            response.raise_for_status() 
            data_search = response.json()
            print(data_search)
            with open('search_response.json', 'w', encoding='utf-8') as f:
                json.dump(data_search, f, ensure_ascii=False, indent=2)
            
            # Khắc phục lỗi TypeError: argument of type 'NoneType' is not iterable
            # Kiểm tra an toàn: data phải tồn tại, có key 'data' VÀ 'hotels' trong 'data'
            if data_search and data_search.get('data') and 'hotels' in data_search['data']:
                hotels = data_search['data']['hotels']
                print(f"\n✅ Tìm kiếm thành công! Tìm thấy **{len(hotels)}** kết quả. Hiển thị 3 kết quả đầu tiên:")
                
                for i, hotel in enumerate(hotels[:3]): 
                    print(f"\n--- KHÁCH SẠN {i+1} ({hotel.get('hotelId', 'N/A')}) ---")
                    print(f"Tên: {hotel.get('name', 'N/A')}")
                    print(f"Giá từ: {hotel.get('price', {}).get('currentPrice', 'N/A')} {querystring_search['currency']}")
                    print(f"Đánh giá (Khách): {hotel.get('guestRating', 'N/A')}")
            else:
                print("\n⚠️ Không tìm thấy khách sạn nào hoặc có lỗi trong cấu trúc phản hồi.")
                # In lỗi chi tiết nếu có
                if 'errors' in data_search:
                     print("Chi tiết lỗi API:", json.dumps(data_search['errors'], indent=2, ensure_ascii=False))

        except requests.exceptions.RequestException as e:
            print(f"❌ Lỗi khi gọi API tìm khách sạn (Network/HTTP): {e}")

# Chạy luồng code
get_dalat_id_and_search_hotels()