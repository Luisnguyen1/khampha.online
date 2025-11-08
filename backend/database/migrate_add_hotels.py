"""
Database Migration: Add plan_hotels table and start_date/end_date to travel_plans
"""
import sqlite3
import os
import sys
from pathlib import Path

# Get database path
DB_PATH = Path(__file__).parent.parent / 'data' / 'travelmate.db'

def migrate():
    """Run migration to add hotel-related tables and fields"""
    conn = None
    try:
        print(f"🔧 Starting migration: Add hotels support")
        print(f"📁 Database: {DB_PATH}")
        
        # Create data directory if it doesn't exist
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        if not DB_PATH.exists():
            print(f"⚠️  Database file not found, it will be created: {DB_PATH}")
        
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Step 1: Add start_date and end_date to travel_plans
        print("\n📅 Step 1: Adding start_date and end_date columns to travel_plans...")
        try:
            cursor.execute("ALTER TABLE travel_plans ADD COLUMN start_date DATE")
            print("   ✅ Added start_date column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("   ⚠️  start_date column already exists")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE travel_plans ADD COLUMN end_date DATE")
            print("   ✅ Added end_date column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("   ⚠️  end_date column already exists")
            else:
                raise
        
        # Step 2: Create plan_hotels table
        print("\n🏨 Step 2: Creating plan_hotels table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plan_hotels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL UNIQUE,
                
                -- Hotel identification
                hotel_id TEXT NOT NULL,
                hotel_name TEXT NOT NULL,
                
                -- Location
                address TEXT,
                city TEXT,
                latitude REAL,
                longitude REAL,
                
                -- Ratings
                star_rating INTEGER,
                guest_rating REAL,
                review_count INTEGER,
                
                -- Booking dates
                checkin_date DATE NOT NULL,
                checkout_date DATE NOT NULL,
                nights INTEGER NOT NULL,
                
                -- Rooms
                rooms INTEGER DEFAULT 1,
                guests INTEGER DEFAULT 2,
                room_type TEXT,
                
                -- Pricing
                price_per_night REAL,
                total_price REAL NOT NULL,
                currency TEXT DEFAULT 'VND',
                discount_percent REAL,
                original_price REAL,
                
                -- Amenities & Features (JSON)
                amenities TEXT,
                images TEXT,
                
                -- Policies
                cancellation_policy TEXT,
                is_refundable INTEGER DEFAULT 0,
                
                -- Full hotel data from API (JSON)
                hotel_data TEXT,
                
                -- Metadata
                selected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (plan_id) REFERENCES travel_plans(id) ON DELETE CASCADE
            )
        """)
        print("   ✅ Created plan_hotels table")
        
        # Step 3: Create indexes
        print("\n📊 Step 3: Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_plan_hotels_plan_id 
            ON plan_hotels(plan_id)
        """)
        print("   ✅ Created index on plan_id")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_plan_hotels_checkin 
            ON plan_hotels(checkin_date)
        """)
        print("   ✅ Created index on checkin_date")
        
        # Step 4: Create trigger for updated_at
        print("\n⚙️  Step 4: Creating trigger for updated_at...")
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_plan_hotels_timestamp 
            AFTER UPDATE ON plan_hotels
            BEGIN
                UPDATE plan_hotels 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        """)
        print("   ✅ Created update trigger")
        
        # Commit changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Display table info
        print("\n📋 Table structure:")
        cursor.execute("PRAGMA table_info(plan_hotels)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n❌ Migration failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
