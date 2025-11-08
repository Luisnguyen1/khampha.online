import requests
import json
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List, Any, Union


class HotelSearcher:
    """
    Class để tìm kiếm khách sạn sử dụng Agoda API (RapidAPI).
    
    Attributes:
        api_key (str): RapidAPI key
        host (str): RapidAPI host
        headers (dict): Headers cho API requests
    """
    
    def __init__(self, api_key: str, host: str = "agoda-com.p.rapidapi.com"):
        """
        Khởi tạo HotelSearcher.
        
        Args:
            api_key (str): RapidAPI key
            host (str): RapidAPI host (mặc định: "agoda-com.p.rapidapi.com")
        """
        self.api_key = api_key
        self.host = host
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host
        }
        self.base_url = f"https://{self.host}"
    
    def get_city_id(self, city_name: str, language: str = "vi-vn") -> Optional[int]:
        """
        Lấy city ID từ tên thành phố.
        
        Args:
            city_name (str): Tên thành phố cần tìm kiếm
            language (str): Ngôn ngữ (mặc định: "vi-vn")
            
        Returns:
            Optional[int]: City ID nếu tìm thấy, None nếu không tìm thấy
        """
        url = f"{self.base_url}/hotels/auto-complete"
        querystring = {
            "query": city_name,
            "language": language
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            data = response.json()
            
            if data and 'places' in data and data['places']:
                # Lọc ra đối tượng là 'Thành Phố' (City) và ở 'Việt Nam'
                city = next((p for p in data['places'] 
                           if p.get('typeName') in ('Thành Phố', 'City') 
                           and p.get('country', {}).get('name') == 'Việt Nam'), None)
                
                if city:
                    city_id = city.get('id')
                    print(f"✅ Tìm thấy ID của {city_name}: {city_id}")
                    return city_id
                else:
                    print(f"❌ Không tìm thấy ID cho thành phố '{city_name}'")
                    return None
            else:
                print("❌ Không nhận được dữ liệu hợp lệ từ API auto-complete")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Lỗi khi gọi API auto-complete: {e}")
            return None
    
    def search_hotels(
        self,
        city_id: int,
        city_name: str,
        checkin_date: date,
        checkout_date: date,
        rooms: int = 1,
        adults: int = 2,
        language: str = "vi-vn",
        currency: str = "VND",
        save_to_file: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Tìm kiếm khách sạn theo city ID.
        
        Args:
            city_id (int): ID của thành phố
            city_name (str): Tên thành phố
            checkin_date (date): Ngày nhận phòng
            checkout_date (date): Ngày trả phòng
            rooms (int): Số phòng (mặc định: 1)
            adults (int): Số người lớn (mặc định: 2)
            language (str): Ngôn ngữ (mặc định: "vi-vn")
            currency (str): Đơn vị tiền tệ (mặc định: "VND")
            save_to_file (Optional[str]): Đường dẫn file để lưu kết quả (JSON)
            
        Returns:
            Optional[Dict[str, Any]]: Dữ liệu kết quả tìm kiếm, None nếu có lỗi
        """
        url = f"{self.base_url}/hotels/search-overnight"
        querystring = {
            "id": f"1_{city_id}",
            "query": city_name,
            "checkinDate": checkin_date.strftime("%Y-%m-%d"),
            "checkoutDate": checkout_date.strftime("%Y-%m-%d"),
            "rooms": str(rooms),
            "adults": str(adults),
            "language": language,
            "currency": currency
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            data = response.json()
            
            # Lưu vào file nếu được yêu cầu
            if save_to_file:
                with open(save_to_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"💾 Đã lưu kết quả vào file: {save_to_file}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Lỗi khi gọi API tìm khách sạn: {e}")
            return None
    
    def extract_hotels(self, search_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Trích xuất danh sách khách sạn từ dữ liệu tìm kiếm.
        
        Args:
            search_data (Dict[str, Any]): Dữ liệu từ API search
            
        Returns:
            List[Dict[str, Any]]: Danh sách khách sạn
        """
        if search_data and search_data.get('data') and 'citySearch' in search_data['data']:
            properties = search_data['data']['citySearch'].get('properties', [])
            return properties
        return []
    
    def format_hotel_info(
        self, 
        hotel: Dict[str, Any], 
        currency: str = "VND"
    ) -> Dict[str, Any]:
        """
        Định dạng thông tin khách sạn thành dạng dễ đọc.
        
        Args:
            hotel (Dict[str, Any]): Dữ liệu khách sạn từ API
            currency (str): Đơn vị tiền tệ
            
        Returns:
            Dict[str, Any]: Thông tin khách sạn đã được định dạng
        """
        content = hotel.get('content', {})
        pricing = hotel.get('pricing', {})
        
        # Lấy giá chính xác từ cấu trúc mới
        price_per_night = None
        price_total = None
        price_crossed_out = None
        discount_percent = None
        
        if pricing.get('isAvailable'):
            offers = pricing.get('offers', [])
            if offers and len(offers) > 0:
                room_offers = offers[0].get('roomOffers', [])
                if room_offers and len(room_offers) > 0:
                    room = room_offers[0].get('room', {})
                    room_pricing = room.get('pricing', [])
                    
                    if room_pricing and len(room_pricing) > 0:
                        price_data = room_pricing[0].get('price', {})
                        
                        # Lấy giá per night (inclusive - đã bao gồm thuế)
                        per_night = price_data.get('perRoomPerNight', {}).get('inclusive', {})
                        price_per_night = per_night.get('display')
                        
                        # Lấy giá tổng cho toàn bộ booking
                        per_book = price_data.get('perBook', {}).get('inclusive', {})
                        price_total = per_book.get('display')
                        price_crossed_out = per_book.get('crossedOutPrice')
                        
                        # Lấy % giảm giá
                        discount_percent = price_data.get('totalDiscount')
        
        # Lấy đánh giá
        reviews = content.get('reviews', {})
        rating = reviews.get('score')
        review_count = reviews.get('numberOfReviews')
        
        # Lấy thông tin cơ bản
        info_summary = content.get('informationSummary', {})
        hotel_name = info_summary.get('localeName') or info_summary.get('defaultName') or info_summary.get('name', 'N/A')
        
        # Lấy hình ảnh
        images = content.get('images', {})
        image_urls = []
        if images:
            hotelImages = images.get('hotelImages', [])
            if hotelImages:
                for img in hotelImages[:5]:  # Lấy 5 ảnh đầu tiên
                    image_urls.append(img.get('urls', [{}])[0].get('value', ''))
        
        return {
            'hotel_id': hotel.get('propertyId'),
            'name': hotel_name,
            'rating': rating,
            'review_count': review_count,
            'price_per_night': price_per_night,
            'price_total': price_total,
            'price_crossed_out': price_crossed_out,
            'discount_percent': discount_percent,
            'currency': currency,
            'is_available': pricing.get('isAvailable', False),
            'address': info_summary.get('address', 'N/A'),
            'star_rating': info_summary.get('propertyRating'),
            'latitude': info_summary.get('geoInfo', {}).get('latitude'),
            'longitude': info_summary.get('geoInfo', {}).get('longitude'),
            'images': image_urls
        }
    
    def search_and_display(
        self,
        city_name: str,
        checkin_date: Optional[Union[date, str]] = None,
        checkout_date: Optional[Union[date, str]] = None,
        days_from_now: Optional[int] = None,
        nights: int = 3,
        rooms: int = 1,
        adults: int = 2,
        max_results: int = 5,
        language: str = "vi-vn",
        currency: str = "VND",
        save_to_file: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm và hiển thị khách sạn (phương thức tiện ích all-in-one).
        
        Args:
            city_name (str): Tên thành phố
            checkin_date (Optional[Union[date, str]]): Ngày nhận phòng (date object hoặc string 'YYYY-MM-DD')
            checkout_date (Optional[Union[date, str]]): Ngày trả phòng (date object hoặc string 'YYYY-MM-DD')
            days_from_now (Optional[int]): Số ngày từ hôm nay đến ngày nhận phòng (dùng nếu không có checkin_date)
            nights (int): Số đêm lưu trú (mặc định: 3, dùng khi chỉ có checkin_date hoặc days_from_now)
            rooms (int): Số phòng (mặc định: 1)
            adults (int): Số người lớn (mặc định: 2)
            max_results (int): Số kết quả hiển thị tối đa (mặc định: 5)
            language (str): Ngôn ngữ (mặc định: "vi-vn")
            currency (str): Đơn vị tiền tệ (mặc định: "VND")
            save_to_file (Optional[str]): Đường dẫn file để lưu kết quả
            
        Returns:
            List[Dict[str, Any]]: Danh sách khách sạn đã định dạng
        """
        print("=" * 60)
        print(f"🔍 BƯỚC 1: Đang tìm kiếm City ID cho '{city_name}'...")
        print("=" * 60)
        
        # Lấy city ID
        city_id = self.get_city_id(city_name, language)
        if not city_id:
            return []
        
        print(f"\n{'=' * 60}")
        print(f"🏨 BƯỚC 2: Đang tìm kiếm khách sạn tại {city_name}...")
        print("=" * 60)
        
        # Xử lý ngày tháng
        # Ưu tiên: checkin_date & checkout_date > days_from_now
        if checkin_date and checkout_date:
            # Nếu là string, convert sang date
            if isinstance(checkin_date, str):
                checkin = datetime.strptime(checkin_date, "%Y-%m-%d").date()
            else:
                checkin = checkin_date
                
            if isinstance(checkout_date, str):
                checkout = datetime.strptime(checkout_date, "%Y-%m-%d").date()
            else:
                checkout = checkout_date
        elif checkin_date:
            # Chỉ có checkin_date, tính checkout dựa vào nights
            if isinstance(checkin_date, str):
                checkin = datetime.strptime(checkin_date, "%Y-%m-%d").date()
            else:
                checkin = checkin_date
            checkout = checkin + timedelta(days=nights)
        else:
            # Không có checkin_date, dùng days_from_now
            if days_from_now is None:
                days_from_now = 30  # Mặc định 30 ngày
            checkin = date.today() + timedelta(days=days_from_now)
            checkout = checkin + timedelta(days=nights)
        
        print(f"📅 Ngày nhận phòng: {checkin.strftime('%d/%m/%Y')}")
        print(f"📅 Ngày trả phòng: {checkout.strftime('%d/%m/%Y')}")
        print(f"🛏️  Số phòng: {rooms}, Số người: {adults}")
        
        # Tìm kiếm khách sạn
        search_data = self.search_hotels(
            city_id=city_id,
            city_name=city_name,
            checkin_date=checkin,
            checkout_date=checkout,
            rooms=rooms,
            adults=adults,
            language=language,
            currency=currency,
            save_to_file=save_to_file
        )
        
        if not search_data:
            return []
        
        # Trích xuất và định dạng khách sạn
        hotels = self.extract_hotels(search_data)
        formatted_hotels = []
        
        print(f"\n✅ Tìm thấy {len(hotels)} khách sạn. Hiển thị {min(max_results, len(hotels))} kết quả đầu tiên:\n")
        
        for i, hotel in enumerate(hotels[:max_results]):
            formatted = self.format_hotel_info(hotel, currency)
            formatted_hotels.append(formatted)
            
            print(f"{'─' * 60}")
            print(f"🏨 KHÁCH SẠN {i+1} (ID: {formatted['hotel_id']})")
            print(f"{'─' * 60}")
            print(f"📍 Tên: {formatted['name']}")
            if formatted['star_rating']:
                print(f"⭐ Hạng: {formatted['star_rating']} sao")
            if formatted['rating']:
                print(f"💯 Đánh giá: {formatted['rating']}/10 ({formatted['review_count']} đánh giá)")
            
            # Hiển thị giá chi tiết
            if formatted['price_per_night']:
                print(f"💰 Giá mỗi đêm: {formatted['price_per_night']:,.0f} {formatted['currency']}")
            if formatted['price_total']:
                print(f"💰 Tổng giá: {formatted['price_total']:,.0f} {formatted['currency']}")
            if formatted['discount_percent']:
                print(f"🎁 Giảm giá: {formatted['discount_percent']}%")
                if formatted['price_crossed_out']:
                    print(f"   Giá gốc: {formatted['price_crossed_out']:,.0f} {formatted['currency']}")
            
            if not formatted['is_available']:
                print(f"⚠️  Không khả dụng")
            
            if formatted['address']:
                print(f"📍 Địa chỉ: {formatted['address']}")
            print()
        
        return formatted_hotels


# ===============================================
# USAGE EXAMPLE
# ===============================================
if __name__ == "__main__":
    # Khởi tạo searcher với API key
    API_KEY = "fe30b4f590msh6817e6a304fb995p1382dejsn50ae5d7c997d"
    searcher = HotelSearcher(api_key=API_KEY)
    
    print("=" * 60)
    print("VÍ DỤ 1: TÌM KIẾM THEO NGÀY CỤ THỂ")
    print("=" * 60)
    
    # Tìm kiếm theo ngày cụ thể (string format)
    hotels = searcher.search_and_display(
        city_name="Đà Lạt",
        checkin_date="2025-12-20",
        checkout_date="2025-12-23",
        rooms=1,
        adults=2,
        max_results=3,
        save_to_file="search_response.json"
    )
    
    print("\n" + "=" * 60)
    print("VÍ DỤ 2: TÌM KIẾM THEO SỐ NGÀY TỪ HÔM NAY")
    print("=" * 60)
    
    # Tìm kiếm theo days_from_now (cách cũ vẫn hoạt động)
    hotels2 = searcher.search_and_display(
        city_name="Đà Lạt",
        days_from_now=30,
        nights=3,
        rooms=1,
        adults=2,
        max_results=2
    )
    
    print("\n" + "=" * 60)
    print("VÍ DỤ 3: CHỈ CÓ NGÀY CHECK-IN, TỰ ĐỘNG TÍNH CHECK-OUT")
    print("=" * 60)
    
    # Chỉ cần ngày check-in, tự tính check-out theo nights
    from datetime import date, timedelta
    hotels3 = searcher.search_and_display(
        city_name="Đà Lạt",
        checkin_date=date.today() + timedelta(days=15),
        nights=2,  # Sẽ ở 2 đêm
        max_results=2
    )
