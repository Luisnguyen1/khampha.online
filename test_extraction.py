"""
Test script for requirements extraction
"""
import re
from datetime import datetime

def simple_extract_requirements(text: str):
    """Test extraction logic"""
    text_lower = text.lower()
    
    # Common Vietnamese destinations
    destinations = ['đà lạt', 'nha trang', 'phú quốc', 'đà nẵng', 'hội an', 
                   'sapa', 'hạ long', 'vũng tàu', 'hà nội', 'sài gòn', 'huế']
    
    destination = None
    for dest in destinations:
        if dest in text_lower:
            destination = dest.title()
            break
    
    # Extract days - improved to handle "3 ngày 2 đêm"
    duration_days = None
    
    # Pattern 1: "X ngày" or "X ngay"
    day_patterns = [
        r'(\d+)\s*ngày',  # "3 ngày"
        r'(\d+)\s*ngay',  # "3 ngay" (typo)
        r'(\d+)\s*days?',  # "3 day" or "3 days"
    ]
    
    for pattern in day_patterns:
        match = re.search(pattern, text_lower)
        if match:
            days = int(match.group(1))
            if days <= 30:
                duration_days = days
                break
    
    # Fallback: simple number extraction if no pattern matched
    if duration_days is None:
        for word in text.split():
            if word.isdigit() and int(word) <= 30:
                duration_days = int(word)
                break
    
    # Extract budget (millions) - improved patterns
    budget = None
    
    # Pattern 1: "X triệu" or "X tr" or "X trieu"
    budget_patterns = [
        r'(\d+(?:[.,]\d+)?)\s*triệu',  # "5 triệu" or "5.5 triệu"
        r'(\d+(?:[.,]\d+)?)\s*trieu',  # "5 trieu"
        r'(\d+(?:[.,]\d+)?)\s*tr\b',   # "5 tr"
        r'(\d+(?:[.,]\d+)?)\s*million', # "5 million"
    ]
    
    for pattern in budget_patterns:
        match = re.search(pattern, text_lower)
        if match:
            amount = float(match.group(1).replace(',', '.'))
            budget = amount * 1000000  # Convert to VND
            break
    
    # Pattern 2: "X nghìn" or "X nghin" or "X k"
    if budget is None:
        thousand_patterns = [
            r'(\d+(?:[.,]\d+)?)\s*nghìn',  # "500 nghìn"
            r'(\d+(?:[.,]\d+)?)\s*nghin',  # "500 nghin"
            r'(\d+(?:[.,]\d+)?)\s*k\b',    # "500k"
        ]
        
        for pattern in thousand_patterns:
            match = re.search(pattern, text_lower)
            if match:
                amount = float(match.group(1).replace(',', '.'))
                budget = amount * 1000  # Convert to VND
                break
    
    # Extract start_date - parse various formats
    start_date = None
    
    # Try to find date patterns: 20/12/2025, 20-12-2025, "ngày 20 tháng 12"
    date_patterns = [
        r'(\d{1,2})/(\d{1,2})/(\d{4})',  # 20/12/2025
        r'(\d{1,2})-(\d{1,2})-(\d{4})',  # 20-12-2025
        r'ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})',  # ngày 20 tháng 12
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                if len(match.groups()) == 3:
                    day, month, year = match.groups()
                    start_date = f"{year}-{int(month):02d}-{int(day):02d}"
                    # Validate date
                    datetime.strptime(start_date, '%Y-%m-%d')
                elif len(match.groups()) == 2:  # No year provided
                    day, month = match.groups()
                    # Use current year or next year if month has passed
                    now = datetime.now()
                    year = now.year
                    if int(month) < now.month or (int(month) == now.month and int(day) < now.day):
                        year += 1
                    start_date = f"{year}-{int(month):02d}-{int(day):02d}"
                    datetime.strptime(start_date, '%Y-%m-%d')
                break
            except (ValueError, IndexError):
                continue
    
    # Extract preferences
    preferences = []
    pref_keywords = {
        'biển': 'tắm biển', 'ẩm thực': 'ẩm thực', 'núi': 'leo núi',
        'văn hóa': 'văn hóa', 'lịch sử': 'lịch sử', 'thiên nhiên': 'thiên nhiên'
    }
    for keyword, pref in pref_keywords.items():
        if keyword in text_lower:
            preferences.append(pref)
    
    # Check if ready - NOW requires destination, duration_days, budget AND start_date
    ready = destination is not None and duration_days is not None and budget is not None and start_date is not None
    
    missing = []
    if not destination:
        missing.append('destination')
    if not duration_days:
        missing.append('duration_days')
    if not budget:
        missing.append('budget')
    if not start_date:
        missing.append('start_date')
    if not preferences:
        missing.append('preferences')
    
    return {
        'destination': destination,
        'duration_days': duration_days,
        'budget': budget,
        'start_date': start_date,
        'preferences': ', '.join(preferences) if preferences else None,
        'ready_to_plan': ready,
        'missing_fields': missing
    }


# Test cases
test_messages = [
    "tôi muốn đi 3 ngày 2 đêm, tôi muốn đi vào ngày 11/11/2025, ngân sách khoảng 5 triệu",
    "tôi muốn đi Đà Lạt 3 ngày 2 đêm, tôi muốn đi vào ngày 11/11/2025, ngân sách khoảng 5 triệu",
    "tôi muốn đi Đà Lạt 3 ngày, ngân sách 5 tr, ngày 11/11/2025",
    "đi Nha Trang 4 ngày, 8 triệu, 15-12-2025",
]

print("=" * 80)
print("TESTING REQUIREMENTS EXTRACTION")
print("=" * 80)

for i, msg in enumerate(test_messages, 1):
    print(f"\n📝 Test {i}: {msg}")
    print("-" * 80)
    
    result = simple_extract_requirements(msg)
    
    print(f"✅ Destination: {result['destination']}")
    print(f"✅ Duration: {result['duration_days']} ngày")
    print(f"✅ Budget: {result['budget']:,.0f} VND" if result['budget'] else "❌ Budget: None")
    print(f"✅ Start date: {result['start_date']}")
    print(f"✅ Preferences: {result['preferences']}")
    print(f"\n{'✅ READY TO PLAN' if result['ready_to_plan'] else '❌ NOT READY'}")
    if result['missing_fields']:
        print(f"Missing: {', '.join(result['missing_fields'])}")
    print()
