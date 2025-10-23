"""
Migration script to add conversation_session_id column to conversations table
"""
import sqlite3
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from config import Config

def migrate():
    """Add conversation_session_id column"""
    db_path = Config.DATABASE_PATH
    
    print(f"📊 Migrating database: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'conversation_session_id' not in columns:
            print("➕ Adding conversation_session_id column...")
            cursor.execute("""
                ALTER TABLE conversations 
                ADD COLUMN conversation_session_id TEXT
            """)
            
            print("📑 Creating index on conversation_session_id...")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_session_id 
                ON conversations(conversation_session_id)
            """)
            
            conn.commit()
            print("✅ Migration completed successfully!")
        else:
            print("ℹ️  Column conversation_session_id already exists, skipping...")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
