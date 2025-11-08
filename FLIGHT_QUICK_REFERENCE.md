# Flight Search - Quick Reference Guide

## ✅ Integration Complete!

The flight search feature has been successfully integrated into the system.

## Quick Test

Run the integration test to verify everything works:

```bash
python test_flight_integration.py
```

Expected output: All ✓ marks with no errors.

## API Endpoints Reference

### 1. Search Flights
```
POST /api/plans/<plan_id>/search-flights

Body:
{
    "origin": "Ho Chi Minh City",
    "destination": "Hanoi",
    "departure_date": "2025-03-15",
    "return_date": "2025-03-20",  // Optional
    "adults": 1,
    "children": 0,
    "infants": 0,
    "cabin_class": "Economy"
}
```

### 2. Save Flight
```
POST /api/plans/<plan_id>/flight

Body: Use any flight object from search results
```

### 3. Get Saved Flights
```
GET /api/plans/<plan_id>/flights
```

### 4. Delete Flight
```
DELETE /api/plans/<plan_id>/flight/<flight_id>
```

### 5. Get Airport Code
```
POST /api/flights/search-location

Body:
{
    "city_name": "Ho Chi Minh City"
}

Response:
{
    "success": true,
    "airport_code": "SGN"
}
```

## Python Usage Examples

### Search & Save
```python
from utils.flight_search import AgodaFlightSearchAPI
from database.db_manager import DatabaseManager
from config import Config

# Initialize
searcher = AgodaFlightSearchAPI(api_key=Config.RAPIDAPI_KEY)
db = DatabaseManager(Config.DATABASE_PATH)

# Search
flights = searcher.search_one_way_flight(
    origin="SGN",
    destination="HAN",
    departure_date="2025-03-15",
    adults=1
)

# Extract info
flight_list = searcher.extract_flight_info(flights)

# Save first flight
if flight_list:
    flight = flight_list[0]
    flight['currency'] = 'VND'
    flight['adults'] = 1
    flight['children'] = 0
    flight['infants'] = 0
    db.save_plan_flight(plan_id=1, flight_data=flight, flight_type="outbound")
```

### Get Airport Code
```python
code = searcher.get_airport_code("Ho Chi Minh City")
# Returns: "SGN"
```

### Filter & Sort
```python
# Filter flights
cheap_flights = searcher.filter_flights(
    flight_list,
    max_price=2000000,
    max_stops=0
)

# Sort by price
sorted_flights = searcher.sort_flights(flight_list, sort_by='price')

# Sort by duration
fast_flights = searcher.sort_flights(flight_list, sort_by='duration')
```

## JavaScript/Frontend Usage

```javascript
// Search flights
async function searchFlights(planId) {
    const response = await fetch(`/api/plans/${planId}/search-flights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            origin: "Ho Chi Minh City",
            destination: "Hanoi",
            departure_date: "2025-03-15",
            adults: 1
        })
    });
    const data = await response.json();
    return data.flights;
}

// Save flight
async function saveFlight(planId, flight) {
    await fetch(`/api/plans/${planId}/flight`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            ...flight,
            flight_type: 'outbound'
        })
    });
}

// Get saved flights
async function getSavedFlights(planId) {
    const response = await fetch(`/api/plans/${planId}/flights`);
    const data = await response.json();
    return data.flights;
}

// Delete flight
async function deleteFlight(planId, flightId) {
    await fetch(`/api/plans/${planId}/flight/${flightId}`, {
        method: 'DELETE'
    });
}
```

## Database Methods

```python
from database.db_manager import DatabaseManager
from config import Config

db = DatabaseManager(Config.DATABASE_PATH)

# Save flight
db.save_plan_flight(
    plan_id=1,
    flight_data={...},  # Flight data dict
    flight_type='outbound'  # or 'return'
)

# Get all flights for a plan
flights = db.get_plan_flights(plan_id=1)

# Delete specific flight
db.delete_plan_flight(plan_id=1, flight_id=1)
```

## Flight Data Structure

Returned by `extract_flight_info()`:

```python
{
    'departure_time': '2025-03-15T08:00:00',
    'arrival_time': '2025-03-15T10:15:00',
    'duration': 135,  # minutes
    'carrier_name': 'Vietnam Airlines',
    'carrier_code': 'VN',
    'carrier_logo': 'https://...',
    'flight_number': 'VN210',
    'origin_airport': 'Tan Son Nhat International Airport',
    'destination_airport': 'Noi Bai International Airport',
    'origin_city': 'Ho Chi Minh City',
    'destination_city': 'Hanoi',
    'origin_code': 'SGN',
    'destination_code': 'HAN',
    'stops': 0,
    'layover_info': [],  # If stops > 0
    'price_vnd': 1500000.0,
    'cabin_class': 'Economy',
    'overnight_flight': False,
    'bundle_key': '...',
    'segments': [...]
}
```

## Common Airport Codes

| City | Code |
|------|------|
| Ho Chi Minh City | SGN |
| Hanoi | HAN |
| Da Nang | DAD |
| Nha Trang | CXR |
| Phu Quoc | PQC |
| Hue | HUI |
| Can Tho | VCA |
| Dalat | DLI |

## Files Overview

| File | Purpose |
|------|---------|
| `backend/utils/flight_search.py` | Flight search API class |
| `backend/database/models.py` | PlanFlight data model |
| `backend/database/db_manager.py` | Database operations |
| `backend/app.py` | API endpoints |
| `backend/database/migrate_add_flights.py` | Database migration |
| `test_flight_integration.py` | Integration test |
| `docs/FLIGHT_FEATURE.md` | Full documentation |
| `docs/FLIGHT_INTEGRATION_SUMMARY.md` | Integration summary |

## Troubleshooting

### "No such table: plan_flights"
```bash
python backend/database/migrate_add_flights.py
```

### "Airport code not found"
```python
# Use exact city name or try variations:
searcher.get_airport_code("Ho Chi Minh City")  # ✓
searcher.get_airport_code("Saigon")            # May not work
searcher.get_airport_code("SGN")               # ✓ Direct code
```

### "No flights found"
- Check date format: "YYYY-MM-DD"
- Date should be in the future
- Verify origin/destination codes are valid
- Check API quota/rate limits

## Next Steps (Optional)

1. **Frontend UI**: Create flight search interface
2. **Price Tracking**: Monitor price changes
3. **Notifications**: Email alerts for flights
4. **Calendar**: Export flights to calendar
5. **Booking**: Direct booking integration

## Support

- Full documentation: `docs/FLIGHT_FEATURE.md`
- Integration summary: `docs/FLIGHT_INTEGRATION_SUMMARY.md`
- Test script: `test_flight_integration.py`

---

✅ **Status**: Backend integration 100% complete
⏳ **Pending**: Frontend UI (optional)
