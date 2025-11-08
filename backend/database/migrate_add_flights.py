"""
Migration script to add plan_flights table
"""
import sqlite3
import os
from pathlib import Path

# Get database path - should match config.py
DB_PATH = Path(__file__).parent.parent / 'data' / 'travelmate.db'

def migrate():
    """Add plan_flights table to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create plan_flights table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plan_flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                flight_type TEXT DEFAULT 'outbound',
                bundle_key TEXT,
                carrier_name TEXT NOT NULL,
                carrier_code TEXT NOT NULL,
                carrier_logo TEXT,
                flight_number TEXT NOT NULL,
                origin_airport TEXT NOT NULL,
                origin_code TEXT NOT NULL,
                origin_city TEXT,
                destination_airport TEXT NOT NULL,
                destination_code TEXT NOT NULL,
                destination_city TEXT,
                departure_time TEXT NOT NULL,
                arrival_time TEXT NOT NULL,
                duration INTEGER DEFAULT 0,
                stops INTEGER DEFAULT 0,
                cabin_class TEXT DEFAULT 'Economy',
                price REAL DEFAULT 0,
                currency TEXT DEFAULT 'VND',
                adults INTEGER DEFAULT 1,
                children INTEGER DEFAULT 0,
                infants INTEGER DEFAULT 0,
                is_overnight INTEGER DEFAULT 0,
                layover_info TEXT,
                segments TEXT,
                flight_data TEXT,
                selected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES travel_plans(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flight_plan ON plan_flights(plan_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flight_type ON plan_flights(flight_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flight_departure ON plan_flights(departure_time)
        """)
        
        # Create trigger for auto-update timestamp
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_flight_timestamp 
            AFTER UPDATE ON plan_flights
            BEGIN
                UPDATE plan_flights SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("✅ Added plan_flights table")
        print("✅ Added indexes")
        print("✅ Added update trigger")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
