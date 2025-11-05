"""
Migration script to add profile fields to users table
Run this to update existing database with new profile columns
"""
import sqlite3
from pathlib import Path

# Path to database
DB_PATH = Path(__file__).parent.parent / 'data' / 'travelmate.db'

def migrate_database():
    """Add new profile columns to users table"""
    print(f"🔄 Migrating database: {DB_PATH}")
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    print(f"📋 Existing columns: {existing_columns}")
    
    # List of new columns to add
    new_columns = [
        ('bio', 'TEXT'),
        ('phone', 'TEXT'),
        ('address', 'TEXT'),
        ('avatar_url', 'TEXT'),
        ('date_of_birth', 'TEXT'),
        ('travel_preferences', 'TEXT')
    ]
    
    # Add missing columns
    for column_name, column_type in new_columns:
        if column_name not in existing_columns:
            try:
                sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                print(f"  ➕ Adding column: {column_name} {column_type}")
                cursor.execute(sql)
                conn.commit()
                print(f"  ✅ Added: {column_name}")
            except sqlite3.OperationalError as e:
                print(f"  ⚠️  Error adding {column_name}: {e}")
        else:
            print(f"  ℹ️  Column {column_name} already exists")
    
    # Verify final schema
    cursor.execute("PRAGMA table_info(users)")
    final_columns = [row[1] for row in cursor.fetchall()]
    print(f"\n✅ Final columns: {final_columns}")
    
    conn.close()
    print("\n🎉 Migration completed!")

if __name__ == '__main__':
    migrate_database()
