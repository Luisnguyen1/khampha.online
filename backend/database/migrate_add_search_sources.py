"""
Migration script to add search_sources field to travel_plans table
Stores the list of websites used to generate the plan
"""
import sqlite3
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Add search_sources column to travel_plans table"""
    db_path = Config.DATABASE_PATH
    logger.info(f"Connecting to database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(travel_plans)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'search_sources' in columns:
            logger.info("✅ Column 'search_sources' already exists. No migration needed.")
            return
        
        # Add search_sources column
        logger.info("📝 Adding 'search_sources' column to travel_plans table...")
        cursor.execute("""
            ALTER TABLE travel_plans 
            ADD COLUMN search_sources TEXT
        """)
        
        logger.info("✅ Successfully added 'search_sources' column")
        
        # Commit changes
        conn.commit()
        logger.info("✅ Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()
        logger.info("Database connection closed")


if __name__ == '__main__':
    logger.info("="*80)
    logger.info("MIGRATION: Add search_sources field to travel_plans")
    logger.info("="*80)
    migrate()
