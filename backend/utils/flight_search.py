import requests
import json
from datetime import date, timedelta
from typing import Dict, List, Optional, Any

# --- CLASS QUẢN LÝ TÌM KIẾM CHUYẾN BAY AGODA ---
class AgodaFlightSearchAPI:
    """
    Class quản lý tìm kiếm chuyến bay qua Agoda API
    
    Attributes:
        api_key: RapidAPI key để xác thực
        api_host: Host của Agoda API trên RapidAPI
        headers: Headers cho các request
    """
    
    def __init__(self, api_key: str):
        """
        Khởi tạo API client
        
        Args:
            api_key: RapidAPI key
        """
        self.api_key = api_key
        self.api_host = "agoda-com.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host
        }
        self.base_url = f"https://{self.api_host}"
    
    def search_location(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Tìm kiếm địa điểm theo tên (auto-complete)
        
        Args:
            query: Tên địa điểm cần tìm (ví dụ: "Hanoi", "Ho Chi Minh")
            
        Returns:
            Dict chứa danh sách gợi ý địa điểm hoặc None nếu có lỗi
        """
        url = f"{self.base_url}/flights/auto-complete"
        querystring = {"query": query}
        
        try:
            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tìm kiếm địa điểm '{query}': {e}")
            return None
    
    def search_one_way_flight(
        self, 
        origin: str, 
        destination: str, 
        departure_date: str,
        currency: str = "VND",
        adults: int = 1,
        children: int = 0,
        infants: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Tìm kiếm chuyến bay một chiều
        
        Args:
            origin: Mã sân bay đi (ví dụ: "SGN")
            destination: Mã sân bay đến (ví dụ: "HAN")
            departure_date: Ngày khởi hành (format: "YYYY-MM-DD")
            currency: Loại tiền tệ (mặc định: "VND")
            adults: Số người lớn (mặc định: 1)
            children: Số trẻ em (mặc định: 0)
            infants: Số em bé (mặc định: 0)
            
        Returns:
            Dict chứa danh sách chuyến bay hoặc None nếu có lỗi
        """
        url = f"{self.base_url}/flights/search-one-way"
        querystring = {
            "origin": origin,
            "destination": destination,
            "departureDate": departure_date,
            "currency": currency,
            "adults": str(adults)
        }
        
        if children > 0:
            querystring["children"] = str(children)
        if infants > 0:
            querystring["infants"] = str(infants)
        
        try:
            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tìm kiếm chuyến bay: {e}")
            return None
    
    def search_round_trip_flight(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str,
        currency: str = "VND",
        adults: int = 1,
        children: int = 0,
        infants: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Tìm kiếm chuyến bay khứ hồi
        
        Args:
            origin: Mã sân bay đi
            destination: Mã sân bay đến
            departure_date: Ngày khởi hành (format: "YYYY-MM-DD")
            return_date: Ngày về (format: "YYYY-MM-DD")
            currency: Loại tiền tệ (mặc định: "VND")
            adults: Số người lớn
            children: Số trẻ em
            infants: Số em bé
            
        Returns:
            Dict chứa danh sách chuyến bay hoặc None nếu có lỗi
        """
        url = f"{self.base_url}/flights/search-round-trip"
        querystring = {
            "origin": origin,
            "destination": destination,
            "departureDate": departure_date,
            "returnDate": return_date,
            "currency": currency,
            "adults": str(adults)
        }
        
        if children > 0:
            querystring["children"] = str(children)
        if infants > 0:
            querystring["infants"] = str(infants)
        
        try:
            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tìm kiếm chuyến bay khứ hồi: {e}")
            return None
    
    def extract_flight_info(self, flight_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Trích xuất thông tin quan trọng từ kết quả tìm kiếm
        
        Args:
            flight_data: Dữ liệu JSON trả về từ API
            
        Returns:
            List các dict chứa thông tin chuyến bay đã được xử lý
        """
        if not flight_data or 'trips' not in flight_data:
            print("Không có dữ liệu chuyến bay")
            return []
        
        flights = []
        for trip in flight_data.get('trips', []):
            for bundle in trip.get('bundles', []):
                flight_info = self._extract_bundle_info(bundle)
                if flight_info:
                    flights.append(flight_info)
        
        return flights
    
    def _extract_bundle_info(self, bundle: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Trích xuất thông tin từ một bundle (private method)
        
        Args:
            bundle: Dict chứa thông tin một gói chuyến bay
            
        Returns:
            Dict chứa thông tin đã trích xuất hoặc None
        """
        outbound = bundle.get('outboundSlice', {})
        segments = outbound.get('segments', [])
        
        if not segments:
            return None
        
        first_segment = segments[0]
        last_segment = segments[-1]
        
        # Lấy thời gian bay
        departure_time = first_segment.get('departDateTime', '')
        arrival_time = last_segment.get('arrivalDateTime', '')
        
        # Lấy thông tin hãng bay
        carrier_content = first_segment.get('carrierContent', {})
        carrier_name = carrier_content.get('carrierName', 'N/A')
        carrier_code = carrier_content.get('carrierCode', 'N/A')
        
        # Lấy giá VND
        price_vnd = self._extract_price(bundle)
        
        # Lấy thông tin sân bay
        airport_content = first_segment.get('airportContent', {})
        origin_airport = airport_content.get('departureAirportName', 'N/A')
        destination_airport = airport_content.get('arrivalAirportName', 'N/A')
        origin_city = airport_content.get('departureCityName', 'N/A')
        destination_city = airport_content.get('arrivalCityName', 'N/A')
        
        # Kiểm tra điểm dừng
        stops = len(segments) - 1
        layover_info = self._extract_layover_info(segments) if stops > 0 else []
        
        return {
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'duration': outbound.get('duration', 0),
            'carrier_name': carrier_name,
            'carrier_code': carrier_code,
            'carrier_logo': carrier_content.get('carrierIcon', ''),
            'flight_number': first_segment.get('flightNumber', 'N/A'),
            'origin_airport': origin_airport,
            'destination_airport': destination_airport,
            'origin_city': origin_city,
            'destination_city': destination_city,
            'origin_code': first_segment.get('originAirport', 'N/A'),
            'destination_code': last_segment.get('destinationAirport', 'N/A'),
            'stops': stops,
            'layover_info': layover_info,
            'price_vnd': price_vnd,
            'cabin_class': first_segment.get('cabinClassContent', {}).get('cabinName', 'N/A'),
            'overnight_flight': outbound.get('overnightFlight', False),
            'bundle_key': bundle.get('key', ''),
            'segments': segments
        }
    
    def _extract_price(self, bundle: Dict[str, Any]) -> float:
        """
        Trích xuất giá từ bundle (private method)
        
        Args:
            bundle: Dict chứa thông tin gói chuyến bay
            
        Returns:
            Giá trọn gói (VND)
        """
        bundle_prices = bundle.get('bundlePrice', [])
        if not bundle_prices:
            return 0.0
        
        price_data = bundle_prices[0].get('price', {})
        vnd_data = price_data.get('vnd', {})
        display_data = vnd_data.get('display', {})
        avg_per_pax = display_data.get('averagePerPax', {})
        return avg_per_pax.get('allInclusive', 0.0)
    
    def _extract_layover_info(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Trích xuất thông tin điểm dừng (private method)
        
        Args:
            segments: List các segment của chuyến bay
            
        Returns:
            List thông tin điểm dừng
        """
        layovers = []
        for i in range(len(segments) - 1):
            layover = segments[i].get('layoverAfter')
            if layover:
                layovers.append({
                    'airport': segments[i].get('destinationAirport', 'N/A'),
                    'duration': layover.get('duration', 0)
                })
        return layovers
    
    def get_airport_code(self, location_name: str) -> Optional[str]:
        """
        Lấy mã sân bay từ tên địa điểm
        
        Args:
            location_name: Tên địa điểm (ví dụ: "Hà Nội" hoặc "Hanoi")
            
        Returns:
            Mã sân bay (ví dụ: "HAN") hoặc None
        """
        # Chuẩn hóa tên địa điểm: loại bỏ dấu, viết liền
        normalized_name = self._normalize_location(location_name)
        print(f"🔍 Normalizing location: '{location_name}' → '{normalized_name}'")
        
        result = self.search_location(normalized_name)
        if result and 'suggestions' in result and len(result['suggestions']) > 0:
            first_suggestion = result['suggestions'][0]
            airports = first_suggestion.get('airports', [])
            if airports:
                code = airports[0].get('code')
                print(f"✅ Found airport code: {code}")
                return code
        
        print(f"❌ No airport code found for '{location_name}'")
        return None
    
    def _normalize_location(self, location: str) -> str:
        """
        Chuẩn hóa tên địa điểm: loại bỏ dấu và khoảng trắng
        
        Args:
            location: Tên địa điểm có dấu (ví dụ: "Hà Nội", "Đà Nẵng")
            
        Returns:
            Tên địa điểm không dấu, viết liền (ví dụ: "HaNoi", "DaNang")
        """
        import unicodedata
        
        # Bảng mapping đặc biệt cho tiếng Việt
        replacements = {
            'Đ': 'D', 'đ': 'd',
            'Ð': 'D', 'ð': 'd'
        }
        
        # Thay thế các ký tự đặc biệt
        result = location
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        # Loại bỏ dấu bằng NFD (Normalization Form Decomposed)
        nfd = unicodedata.normalize('NFD', result)
        result = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
        
        # Loại bỏ khoảng trắng
        result = result.replace(' ', '')
        
        return result
    
    def save_to_json(self, data: Any, filename: str) -> bool:
        """
        Lưu dữ liệu vào file JSON
        
        Args:
            data: Dữ liệu cần lưu
            filename: Tên file
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu file {filename}: {e}")
            return False
    
    def filter_flights(
        self,
        flights: List[Dict[str, Any]],
        max_price: Optional[float] = None,
        direct_only: bool = False,
        carriers: Optional[List[str]] = None,
        max_duration: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Lọc danh sách chuyến bay theo điều kiện
        
        Args:
            flights: List chuyến bay cần lọc
            max_price: Giá tối đa (VND)
            direct_only: Chỉ lấy chuyến bay thẳng
            carriers: List mã hãng bay cần lọc
            max_duration: Thời gian bay tối đa (phút)
            
        Returns:
            List chuyến bay đã lọc
        """
        filtered = flights
        
        if max_price:
            filtered = [f for f in filtered if f['price_vnd'] <= max_price]
        
        if direct_only:
            filtered = [f for f in filtered if f['stops'] == 0]
        
        if carriers:
            filtered = [f for f in filtered if f['carrier_code'] in carriers]
        
        if max_duration:
            filtered = [f for f in filtered if f['duration'] <= max_duration]
        
        return filtered
    
    def sort_flights(
        self,
        flights: List[Dict[str, Any]],
        sort_by: str = 'price'
    ) -> List[Dict[str, Any]]:
        """
        Sắp xếp danh sách chuyến bay
        
        Args:
            flights: List chuyến bay cần sắp xếp
            sort_by: Tiêu chí sắp xếp ('price', 'duration', 'departure_time')
            
        Returns:
            List chuyến bay đã sắp xếp
        """
        if sort_by == 'price':
            return sorted(flights, key=lambda x: x['price_vnd'])
        elif sort_by == 'duration':
            return sorted(flights, key=lambda x: x['duration'])
        elif sort_by == 'departure_time':
            return sorted(flights, key=lambda x: x['departure_time'])
        else:
            return flights
    
    def print_flight_summary(self, flight: Dict[str, Any], index: int = 0):
        """
        In thông tin tóm tắt của một chuyến bay
        
        Args:
            flight: Dict chứa thông tin chuyến bay
            index: Số thứ tự
        """
        print(f"\n{'='*70}")
        if index > 0:
            print(f"CHUYẾN BAY #{index}")
        else:
            print("THÔNG TIN CHUYẾN BAY")
        print(f"{'='*70}")
        print(f"Hãng bay:        {flight['carrier_name']} ({flight['carrier_code']} {flight['flight_number']})")
        print(f"Hạng ghế:        {flight['cabin_class']}")
        print(f"Khởi hành:       {flight['departure_time']}")
        print(f"Đến nơi:         {flight['arrival_time']}")
        print(f"Thời gian bay:   {flight['duration']} phút ({flight['duration']//60}h {flight['duration']%60}m)")
        print(f"Điểm đi:         {flight['origin_airport']} ({flight['origin_code']})")
        print(f"Điểm đến:        {flight['destination_airport']} ({flight['destination_code']})")
        
        stops_text = 'Bay thẳng' if flight['stops'] == 0 else f"{flight['stops']} điểm dừng"
        print(f"Điểm dừng:       {stops_text}")
        
        if flight['layover_info']:
            print(f"Chi tiết dừng:")
            for layover in flight['layover_info']:
                print(f"  - {layover['airport']}: {layover['duration']} phút")
        
        print(f"Bay đêm:         {'Có' if flight['overnight_flight'] else 'Không'}")
        print(f"Giá trọn gói:    {flight['price_vnd']:,.0f} VND")


# # --- HÀM MAIN ĐỂ TEST ---
# def main():
#     """Hàm main để test class AgodaFlightSearchAPI"""
#     print("=" * 80)
#     print("TEST API TÌM KIẾM CHUYẾN BAY AGODA - OOP VERSION")
#     print("=" * 80)
    
#     # Khởi tạo API client
#     API_KEY = "fe30b4f590msh6817e6a304fb995p1382dejsn50ae5d7c997d"
#     api_client = AgodaFlightSearchAPI(API_KEY)
    
#     # Bước 1: Tìm kiếm địa điểm "Hanoi"
#     print("\n--- BƯỚC 1: Tìm kiếm địa điểm 'Hanoi' ---")
#     location_result = api_client.search_location("Hanoi")
    
#     if location_result and 'suggestions' in location_result:
#         print(f"Tìm thấy {len(location_result['suggestions'])} gợi ý:")
#         for i, suggestion in enumerate(location_result['suggestions'][:3], 1):
#             print(f"{i}. {suggestion['name']} - {suggestion['country']['name']}")
#             if suggestion.get('airports'):
#                 for airport in suggestion['airports']:
#                     print(f"   Sân bay: {airport['name']} ({airport['code']})")
    
#     # Bước 2: Tìm kiếm chuyến bay SGN -> HAN
#     print("\n--- BƯỚC 2: Tìm kiếm chuyến bay SGN -> HAN (15/11/2025) ---")
#     flight_result = api_client.search_one_way_flight("SGN", "HAN", "2025-11-15")
    
#     if flight_result:
#         # Lưu kết quả đầy đủ
#         if api_client.save_to_json(flight_result, 'flight_response.json'):
#             print("✓ Đã lưu kết quả đầy đủ vào file 'flight_response.json'")
        
#         # Trích xuất thông tin chuyến bay
#         flights = api_client.extract_flight_info(flight_result)
#         print(f"\n✓ Tìm thấy {len(flights)} chuyến bay")
        
#         # Lọc chỉ lấy chuyến bay thẳng
#         direct_flights = api_client.filter_flights(flights, direct_only=True)
#         print(f"✓ Có {len(direct_flights)} chuyến bay thẳng")
        
#         # Sắp xếp theo giá
#         sorted_flights = api_client.sort_flights(direct_flights, sort_by='price')
        
#         # Hiển thị 5 chuyến bay rẻ nhất
#         print("\n--- TOP 5 CHUYẾN BAY RẺ NHẤT ---")
#         for i, flight in enumerate(sorted_flights[:5], 1):
#             api_client.print_flight_summary(flight, i)
    
#     print("\n" + "=" * 80)
#     print("HOÀN THÀNH TEST")
#     print("=" * 80)


# if __name__ == "__main__":
#     main()