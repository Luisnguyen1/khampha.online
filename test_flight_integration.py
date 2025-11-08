"""
Test script for flight search integration
Tests the complete flow: API search → Database save → Retrieve → Delete
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.db_manager import DatabaseManager
from utils.flight_search import AgodaFlightSearchAPI
from config import Config
from datetime import datetime, timedelta

def test_flight_integration():
    """Test complete flight integration"""
    print("=" * 60)
    print("TESTING FLIGHT SEARCH INTEGRATION")
    print("=" * 60)
    
    # Initialize components
    db = DatabaseManager(Config.DATABASE_PATH)
    searcher = AgodaFlightSearchAPI(api_key=Config.RAPIDAPI_KEY)
    
    # Step 1: Get airport codes
    print("\n1. TESTING AIRPORT CODE LOOKUP")
    print("-" * 60)
    origin_code = searcher.get_airport_code("Ho Chi Minh City")
    dest_code = searcher.get_airport_code("Hanoi")
    print(f"✓ Ho Chi Minh City → {origin_code}")
    print(f"✓ Hanoi → {dest_code}")
    
    # Step 2: Search flights
    print("\n2. TESTING FLIGHT SEARCH")
    print("-" * 60)
    departure_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"Searching one-way flights: {origin_code} → {dest_code} on {departure_date}")
    flights = searcher.search_one_way_flight(
        origin=origin_code,
        destination=dest_code,
        departure_date=departure_date,
        adults=1
    )
    
    if flights:
        print(f"✓ Found {len(flights)} flight options")
        
        # Extract flight info
        flight_info = searcher.extract_flight_info(flights)
        print(f"✓ Extracted info for {len(flight_info)} flights")
        
        # Limit to 3 for testing
        flight_info = flight_info[:3]
        
        if flight_info:
            # Display first flight
            first_flight = flight_info[0]
            print("\nFirst flight details:")
            print(f"  Carrier: {first_flight['carrier_name']} ({first_flight['flight_number']})")
            print(f"  Route: {first_flight['origin_code']} → {first_flight['destination_code']}")
            print(f"  Departure: {first_flight['departure_time']}")
            print(f"  Arrival: {first_flight['arrival_time']}")
            print(f"  Duration: {first_flight['duration']} minutes")
            print(f"  Stops: {first_flight['stops']}")
            print(f"  Price: {first_flight['price_vnd']:,.0f} VND")
            
            # Step 3: Test database operations
            print("\n3. TESTING DATABASE OPERATIONS")
            print("-" * 60)
            
            # Create a test plan (using existing or creating new one)
            test_plan_id = 1  # Assuming plan ID 1 exists
            
            # Save flight
            print("Saving flight to database...")
            # Add currency field for database
            first_flight['currency'] = 'VND'
            first_flight['adults'] = 1
            first_flight['children'] = 0
            first_flight['infants'] = 0
            
            success = db.save_plan_flight(test_plan_id, first_flight, "outbound")
            if success:
                print("✓ Flight saved successfully")
            else:
                print("✗ Failed to save flight")
                return
            
            # Retrieve flights
            print("Retrieving saved flights...")
            saved_flights = db.get_plan_flights(test_plan_id)
            if saved_flights:
                print(f"✓ Retrieved {len(saved_flights)} flight(s)")
                
                # Display saved flight
                saved = saved_flights[0]
                print("\nSaved flight details:")
                print(f"  ID: {saved['id']}")
                print(f"  Carrier: {saved['carrier_name']}")
                print(f"  Route: {saved['origin_code']} → {saved['destination_code']}")
                print(f"  Price: {saved['price']:,} {saved['currency']}")
                
                # Delete flight
                print("\nDeleting flight...")
                flight_id = saved['id']
                delete_success = db.delete_plan_flight(test_plan_id, flight_id)
                if delete_success:
                    print("✓ Flight deleted successfully")
                else:
                    print("✗ Failed to delete flight")
                
                # Verify deletion
                remaining = db.get_plan_flights(test_plan_id)
                if not remaining:
                    print("✓ Deletion verified - no flights remain")
                else:
                    print(f"⚠ {len(remaining)} flight(s) still in database")
            else:
                print("✗ No flights retrieved")
        else:
            print("✗ No flight info extracted")
    else:
        print("✗ No flights found")
    
    print("\n" + "=" * 60)
    print("INTEGRATION TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_flight_integration()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
