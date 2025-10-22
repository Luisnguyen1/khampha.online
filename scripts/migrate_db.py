"""
Database migration script - Add user_id column to travel_plans
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "backend" / "data" / "khappha.db"

def migrate():
    """Add user_id column to travel_plans table"""
    print("🔄 Starting database migration...")
    print(f"📂 Database: {DB_PATH}")
    
    if not DB_PATH.exists():
        print("⚠️  Database file not found. Will be created on first run.")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check if user_id column already exists
        cursor.execute("PRAGMA table_info(travel_plans)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'user_id' in columns:
            print("✅ Column 'user_id' already exists in travel_plans table")
        else:
            print("➕ Adding 'user_id' column to travel_plans table...")
            cursor.execute("ALTER TABLE travel_plans ADD COLUMN user_id INTEGER")
            print("✅ Column 'user_id' added successfully")
        
        # Check if email/username/password columns exist in users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        
        missing_columns = []
        if 'email' not in user_columns:
            missing_columns.append('email')
        if 'username' not in user_columns:
            missing_columns.append('username')
        if 'password_hash' not in user_columns:
            missing_columns.append('password_hash')
        if 'full_name' not in user_columns:
            missing_columns.append('full_name')
        if 'is_authenticated' not in user_columns:
            missing_columns.append('is_authenticated')
        
        if missing_columns:
            print(f"➕ Adding authentication columns to users table: {', '.join(missing_columns)}")
            
            if 'email' in missing_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN email TEXT UNIQUE")
            if 'username' in missing_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN username TEXT UNIQUE")
            if 'password_hash' in missing_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
            if 'full_name' in missing_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
            if 'is_authenticated' in missing_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN is_authenticated INTEGER DEFAULT 0")
            
            print("✅ Authentication columns added successfully")
        else:
            print("✅ All authentication columns already exist in users table")
        
        # Create index for user_id if not exists
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_plan_user ON travel_plans(user_id)
        """)
        print("✅ Index created for user_id")
        
        conn.commit()
        print("\n✨ Migration completed successfully!\n")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
