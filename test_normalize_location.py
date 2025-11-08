"""
Test normalization of Vietnamese location names for flight search
"""
import sys
sys.path.insert(0, 'backend')

from utils.flight_search import AgodaFlightSearchAPI
from config import Config

# Initialize searcher
searcher = AgodaFlightSearchAPI(api_key=Config.RAPIDAPI_KEY)

# Test cases with Vietnamese names
test_locations = [
    "Hà Nội",
    "Đà Nẵng",
    "Sài Gòn",
    "Nha Trang",
    "Phú Quốc",
    "Đà Lạt",
    "Vũng Tàu",
    "Cần Thơ"
]

print("="*80)
print("TESTING LOCATION NORMALIZATION FOR FLIGHT SEARCH")
print("="*80)

for location in test_locations:
    print(f"\n{'='*80}")
    print(f"Testing: {location}")
    print(f"{'='*80}")
    
    # Test normalization
    normalized = searcher._normalize_location(location)
    print(f"Normalized: {normalized}")
    
    # Get airport code
    code = searcher.get_airport_code(location)
    print(f"Airport code: {code}")
    
    if code:
        print(f"✅ SUCCESS - Found code for '{location}'")
    else:
        print(f"❌ FAILED - No code found for '{location}'")

print(f"\n{'='*80}")
print("TEST COMPLETED")
print(f"{'='*80}")
