"""
Initialize database for khappha.online
Run this script to create the database
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from database.db_manager import DatabaseManager


def init_database():
    """Initialize database with schema"""
    print("🗄️  Initializing database...")
    print(f"📂 Database path: {Config.DATABASE_PATH}")
    
    # Create database manager
    db = DatabaseManager(Config.DATABASE_PATH)
    
    # Get stats
    stats = db.get_stats()
    
    print("\n✅ Database initialized successfully!")
    print(f"📊 Stats:")
    print(f"   - Users: {stats['total_users']}")
    print(f"   - Conversations: {stats['total_conversations']}")
    print(f"   - Plans: {stats['total_plans']}")
    print(f"   - Cache entries: {stats['cache_entries']}")
    print(f"\n💡 Database ready at: {Config.DATABASE_PATH}")


if __name__ == "__main__":
    init_database()
