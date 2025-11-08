# Flight Search Feature Documentation

## Overview
The flight search feature allows users to search for flights, save selected flights to travel plans, and manage flight bookings. This feature is fully integrated with the existing travel planning system.

## Architecture

### Components

1. **API Layer** (`backend/utils/flight_search.py`)
   - `AgodaFlightSearchAPI` class for Agoda flight API integration
   - Airport code lookup functionality
   - One-way and round-trip flight search
   - Flight information extraction and formatting

2. **Database Layer** (`backend/database/`)
   - `plan_flights` table for storing selected flights
   - `PlanFlight` model for data representation
   - Database methods: `save_plan_flight()`, `get_plan_flights()`, `delete_plan_flight()`

3. **API Endpoints** (`backend/app.py`)
   - `POST /api/plans/<plan_id>/search-flights` - Search for flights
   - `POST /api/plans/<plan_id>/flight` - Save selected flight
   - `GET /api/plans/<plan_id>/flights` - Get saved flights
   - `DELETE /api/plans/<plan_id>/flight/<flight_id>` - Delete flight
   - `POST /api/flights/search-location` - Get airport code

## Database Schema

### `plan_flights` Table

```sql
CREATE TABLE plan_flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    flight_type TEXT NOT NULL,          -- 'outbound' or 'return'
    bundle_key TEXT,
    carrier_name TEXT,
    carrier_code TEXT,
    carrier_logo TEXT,
    flight_number TEXT,
    origin_airport TEXT,
    origin_code TEXT,
    origin_city TEXT,
    destination_airport TEXT,
    destination_code TEXT,
    destination_city TEXT,
    departure_time TEXT,
    arrival_time TEXT,
    duration INTEGER,                   -- in minutes
    stops INTEGER,
    cabin_class TEXT,                   -- Economy, Business, First
    price REAL,
    currency TEXT,
    adults INTEGER,
    children INTEGER,
    infants INTEGER,
    is_overnight INTEGER,               -- 0 or 1
    layover_info TEXT,                  -- JSON array
    segments TEXT,                      -- JSON array
    flight_data TEXT,                   -- Full JSON response
    selected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES travel_plans(id) ON DELETE CASCADE
);
```

### Indexes
- `idx_plan_flights_plan_id` on `plan_id`
- `idx_plan_flights_type` on `flight_type`
- `idx_plan_flights_departure` on `departure_time`

## API Endpoints

### 1. Search Flights

**Endpoint:** `POST /api/plans/<plan_id>/search-flights`

**Request Body:**
```json
{
    "origin": "Ho Chi Minh City",
    "destination": "Hanoi",
    "departure_date": "2024-03-15",
    "return_date": "2024-03-20",      // Optional for one-way
    "adults": 1,
    "children": 0,
    "infants": 0,
    "cabin_class": "Economy"
}
```

**Response:**
```json
{
    "success": true,
    "flights": [
        {
            "bundle_key": "...",
            "carrier_name": "Vietnam Airlines",
            "carrier_code": "VN",
            "carrier_logo": "https://...",
            "flight_number": "VN210",
            "origin_airport": "Tan Son Nhat International Airport",
            "origin_code": "SGN",
            "destination_airport": "Noi Bai International Airport",
            "destination_code": "HAN",
            "departure_time": "2024-03-15T08:00:00",
            "arrival_time": "2024-03-15T10:15:00",
            "duration": 135,
            "stops": 0,
            "cabin_class": "Economy",
            "price_vnd": 1500000,
            "currency": "VND",
            "overnight_flight": false,
            "layover_info": [],
            "segments": [...]
        }
    ],
    "search_params": {
        "origin": "Ho Chi Minh City",
        "origin_code": "SGN",
        "destination": "Hanoi",
        "destination_code": "HAN",
        "departure_date": "2024-03-15",
        "return_date": "2024-03-20",
        "passengers": {
            "adults": 1,
            "children": 0,
            "infants": 0
        },
        "cabin_class": "Economy"
    }
}
```

### 2. Save Flight

**Endpoint:** `POST /api/plans/<plan_id>/flight`

**Request Body:**
```json
{
    "flight_type": "outbound",
    "bundle_key": "...",
    "carrier_name": "Vietnam Airlines",
    "carrier_code": "VN",
    "flight_number": "VN210",
    "origin_code": "SGN",
    "destination_code": "HAN",
    "departure_time": "2024-03-15T08:00:00",
    "arrival_time": "2024-03-15T10:15:00",
    "duration": 135,
    "stops": 0,
    "cabin_class": "Economy",
    "price_vnd": 1500000,
    "currency": "VND",
    "adults": 1,
    "children": 0,
    "infants": 0
}
```

**Response:**
```json
{
    "success": true,
    "message": "Flight saved successfully"
}
```

### 3. Get Flights

**Endpoint:** `GET /api/plans/<plan_id>/flights`

**Response:**
```json
{
    "success": true,
    "flights": [
        {
            "id": 1,
            "plan_id": 1,
            "flight_type": "outbound",
            "carrier_name": "Vietnam Airlines",
            "origin_code": "SGN",
            "destination_code": "HAN",
            "departure_time": "2024-03-15T08:00:00",
            "price": 1500000,
            "currency": "VND",
            "selected_at": "2024-01-15T10:30:00"
        }
    ]
}
```

### 4. Delete Flight

**Endpoint:** `DELETE /api/plans/<plan_id>/flight/<flight_id>`

**Response:**
```json
{
    "success": true,
    "message": "Flight deleted successfully"
}
```

### 5. Search Airport Code

**Endpoint:** `POST /api/flights/search-location`

**Request Body:**
```json
{
    "city_name": "Ho Chi Minh City"
}
```

**Response:**
```json
{
    "success": true,
    "city_name": "Ho Chi Minh City",
    "airport_code": "SGN"
}
```

## Usage Examples

### Python API Usage

```python
from utils.flight_search import AgodaFlightSearchAPI
from config import Config

# Initialize searcher
searcher = AgodaFlightSearchAPI(api_key=Config.RAPIDAPI_KEY)

# Get airport code
airport_code = searcher.get_airport_code("Ho Chi Minh City")
# Returns: "SGN"

# Search one-way flight
flights = searcher.search_one_way_flight(
    origin_code="SGN",
    destination_code="HAN",
    departure_date="2024-03-15",
    adults=1
)

# Search round-trip flight
flights = searcher.search_round_trip_flight(
    origin_code="SGN",
    destination_code="HAN",
    departure_date="2024-03-15",
    return_date="2024-03-20",
    adults=2,
    children=1
)

# Extract flight information
flight_info = searcher.extract_flight_info(flights, max_results=10)

# Filter flights
cheap_flights = searcher.filter_flights(
    flight_info,
    max_price=2000000,
    max_stops=0
)

# Sort flights
sorted_flights = searcher.sort_flights(flight_info, sort_by='price')
```

### Database Operations

```python
from database.db_manager import DatabaseManager

db = DatabaseManager()

# Save flight
flight_data = {
    'carrier_name': 'Vietnam Airlines',
    'origin_code': 'SGN',
    'destination_code': 'HAN',
    # ... other fields
}
db.save_plan_flight(plan_id=1, flight_data=flight_data, flight_type='outbound')

# Get flights
flights = db.get_plan_flights(plan_id=1)

# Delete flight
db.delete_plan_flight(plan_id=1, flight_id=1)
```

### Frontend JavaScript Usage

```javascript
// Search flights
async function searchFlights(planId, searchParams) {
    const response = await fetch(`/api/plans/${planId}/search-flights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchParams)
    });
    return await response.json();
}

// Save flight
async function saveFlight(planId, flightData) {
    const response = await fetch(`/api/plans/${planId}/flight`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(flightData)
    });
    return await response.json();
}

// Get flights
async function getFlights(planId) {
    const response = await fetch(`/api/plans/${planId}/flights`);
    return await response.json();
}

// Delete flight
async function deleteFlight(planId, flightId) {
    const response = await fetch(`/api/plans/${planId}/flight/${flightId}`, {
        method: 'DELETE'
    });
    return await response.json();
}
```

## Flight Data Structure

### Flight Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Unique identifier (auto-generated) |
| `plan_id` | Integer | Travel plan ID (foreign key) |
| `flight_type` | String | 'outbound' or 'return' |
| `bundle_key` | String | Unique flight bundle identifier |
| `carrier_name` | String | Airline name |
| `carrier_code` | String | IATA airline code |
| `carrier_logo` | String | URL to airline logo |
| `flight_number` | String | Flight number |
| `origin_airport` | String | Departure airport name |
| `origin_code` | String | IATA origin airport code |
| `origin_city` | String | Departure city |
| `destination_airport` | String | Arrival airport name |
| `destination_code` | String | IATA destination airport code |
| `destination_city` | String | Arrival city |
| `departure_time` | String | ISO 8601 format |
| `arrival_time` | String | ISO 8601 format |
| `duration` | Integer | Flight duration in minutes |
| `stops` | Integer | Number of stops (0 = direct) |
| `cabin_class` | String | Economy/Business/First |
| `price` | Float | Price in specified currency |
| `currency` | String | Currency code (e.g., VND) |
| `adults` | Integer | Number of adult passengers |
| `children` | Integer | Number of child passengers |
| `infants` | Integer | Number of infant passengers |
| `is_overnight` | Boolean | Whether flight crosses midnight |
| `layover_info` | JSON | Array of layover details |
| `segments` | JSON | Array of flight segments |
| `flight_data` | JSON | Full API response data |
| `selected_at` | Timestamp | When flight was saved |
| `updated_at` | Timestamp | Last update time |

## Testing

Run the integration test:

```bash
python test_flight_integration.py
```

This test will:
1. Look up airport codes
2. Search for flights
3. Save a flight to database
4. Retrieve saved flights
5. Delete the flight
6. Verify deletion

## Configuration

Required environment variables (in `config.py`):

```python
RAPIDAPI_KEY = "your-rapidapi-key"
```

## Error Handling

All endpoints return standardized error responses:

```json
{
    "success": false,
    "error": "Error message describing what went wrong"
}
```

Common error scenarios:
- Invalid plan ID → 404 Not Found
- Missing required fields → 400 Bad Request
- Airport code not found → 404 Not Found
- API errors → 500 Internal Server Error

## Performance Considerations

1. **API Rate Limits**: Agoda API has rate limits. Consider caching airport codes.
2. **Database Indexes**: Indexes on `plan_id`, `flight_type`, and `departure_time` optimize queries.
3. **JSON Storage**: Large flight data stored as JSON for flexibility.

## Future Enhancements

1. **Flight Price Tracking**: Monitor price changes for saved flights
2. **Multi-city Flights**: Support for complex itineraries
3. **Seat Selection**: Integration with seat map APIs
4. **Booking Integration**: Direct booking through Agoda
5. **Email Notifications**: Flight reminders and updates
6. **Calendar Integration**: Export flights to calendar apps

## Support

For issues or questions:
- Check the test script: `test_flight_integration.py`
- Review API logs in Flask console
- Check database with SQLite browser

## Related Documentation

- `DISCOVERY_FEATURE.md` - Discovery page implementation
- Hotel search implementation (similar pattern)
- Database migration scripts in `backend/database/`
