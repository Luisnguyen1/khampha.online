"""
Migration: Add location fields to users table
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config

def migrate():
    """Add latitude, longitude, and location_updated_at columns to users table"""
    db_path = Config.DATABASE_PATH
    
    print(f"📍 Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        needs_migration = False
        
        # Add latitude column if not exists
        if 'latitude' not in columns:
            print("  ➕ Adding 'latitude' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN latitude REAL")
            needs_migration = True
        else:
            print("  ✓ 'latitude' column already exists")
        
        # Add longitude column if not exists
        if 'longitude' not in columns:
            print("  ➕ Adding 'longitude' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN longitude REAL")
            needs_migration = True
        else:
            print("  ✓ 'longitude' column already exists")
        
        # Add location_updated_at column if not exists
        if 'location_updated_at' not in columns:
            print("  ➕ Adding 'location_updated_at' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN location_updated_at TIMESTAMP")
            needs_migration = True
        else:
            print("  ✓ 'location_updated_at' column already exists")
        
        if needs_migration:
            conn.commit()
            print("✅ Migration completed successfully!")
        else:
            print("✅ Database already up to date!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
