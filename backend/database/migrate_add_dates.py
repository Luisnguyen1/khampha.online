"""
Migration: Add start_date and end_date columns to travel_plans table
"""
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """Add start_date and end_date columns to travel_plans"""
    db_path = Path(__file__).parent.parent / 'data' / 'travelmate.db'
    
    logger.info(f"Database path: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(travel_plans)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'start_date' not in columns:
            logger.info("Adding start_date column to travel_plans...")
            cursor.execute("""
                ALTER TABLE travel_plans 
                ADD COLUMN start_date TEXT
            """)
            logger.info("✅ Added start_date column")
        else:
            logger.info("start_date column already exists")
        
        if 'end_date' not in columns:
            logger.info("Adding end_date column to travel_plans...")
            cursor.execute("""
                ALTER TABLE travel_plans 
                ADD COLUMN end_date TEXT
            """)
            logger.info("✅ Added end_date column")
        else:
            logger.info("end_date column already exists")
        
        conn.commit()
        logger.info("✅ Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
