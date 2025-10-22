"""
Database migration script - Add conversation_id and plan_id columns
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "backend" / "data" / "travelmate.db"

def migrate():
    """Add conversation_id and plan_id columns to link conversations and plans"""
    print("🔄 Starting database migration...")
    print(f"📂 Database: {DB_PATH}")
    
    if not DB_PATH.exists():
        print("⚠️  Database file not found. Will be created on first run.")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check conversations table columns
        cursor.execute("PRAGMA table_info(conversations)")
        conv_columns = [row[1] for row in cursor.fetchall()]
        
        if 'plan_id' not in conv_columns:
            print("➕ Adding 'plan_id' column to conversations table...")
            cursor.execute("ALTER TABLE conversations ADD COLUMN plan_id INTEGER")
            print("✅ Column 'plan_id' added to conversations")
        else:
            print("✅ Column 'plan_id' already exists in conversations table")
        
        # Check travel_plans table columns
        cursor.execute("PRAGMA table_info(travel_plans)")
        plan_columns = [row[1] for row in cursor.fetchall()]
        
        missing_plan_cols = []
        if 'user_id' not in plan_columns:
            missing_plan_cols.append('user_id')
        if 'conversation_id' not in plan_columns:
            missing_plan_cols.append('conversation_id')
        
        if missing_plan_cols:
            print(f"➕ Adding columns to travel_plans table: {', '.join(missing_plan_cols)}")
            
            if 'user_id' in missing_plan_cols:
                cursor.execute("ALTER TABLE travel_plans ADD COLUMN user_id INTEGER")
            if 'conversation_id' in missing_plan_cols:
                cursor.execute("ALTER TABLE travel_plans ADD COLUMN conversation_id INTEGER")
            
            print("✅ Columns added to travel_plans")
        else:
            print("✅ All required columns exist in travel_plans table")
        
        # Check if email/username/password columns exist in users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        
        missing_user_cols = []
        if 'email' not in user_columns:
            missing_user_cols.append('email')
        if 'username' not in user_columns:
            missing_user_cols.append('username')
        if 'password_hash' not in user_columns:
            missing_user_cols.append('password_hash')
        if 'full_name' not in user_columns:
            missing_user_cols.append('full_name')
        if 'is_authenticated' not in user_columns:
            missing_user_cols.append('is_authenticated')
        
        if missing_user_cols:
            print(f"➕ Adding authentication columns to users table: {', '.join(missing_user_cols)}")
            
            if 'email' in missing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
            if 'username' in missing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
            if 'password_hash' in missing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
            if 'full_name' in missing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
            if 'is_authenticated' in missing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN is_authenticated INTEGER DEFAULT 0")
            
            print("✅ Authentication columns added to users table")
        else:
            print("✅ All authentication columns exist in users table")
        
        # Create indexes if not exist
        print("➕ Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_plan ON conversations(plan_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_plan_user ON travel_plans(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_plan_conv ON travel_plans(conversation_id)")
        print("✅ Indexes created")
        
        conn.commit()
        print("\n✨ Migration completed successfully!\n")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
