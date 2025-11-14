"""
Run all database migrations
This script automatically runs all migration files in the database folder
"""
import sys
import logging
from pathlib import Path
import importlib.util

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_migrations():
    """Run all migration files in order"""
    logger.info("🔄 Starting database migrations...")
    
    # Get database folder
    db_folder = Path(__file__).parent
    
    # List all migration files (excluding init_db.py and this script)
    migration_files = sorted([
        f for f in db_folder.glob('migrate_*.py')
        if f.is_file()
    ])
    
    if not migration_files:
        logger.info("ℹ️  No migration files found")
        return
    
    logger.info(f"📋 Found {len(migration_files)} migration file(s)")
    
    # Run each migration
    success_count = 0
    failed_count = 0
    
    for migration_file in migration_files:
        migration_name = migration_file.stem
        logger.info(f"\n{'='*60}")
        logger.info(f"🔧 Running migration: {migration_name}")
        logger.info(f"{'='*60}")
        
        try:
            # Load the migration module dynamically
            spec = importlib.util.spec_from_file_location(migration_name, migration_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Run the migrate function
            if hasattr(module, 'migrate'):
                module.migrate()
                logger.info(f"✅ Migration {migration_name} completed successfully")
                success_count += 1
            else:
                logger.warning(f"⚠️  Migration {migration_name} has no migrate() function")
                
        except Exception as e:
            logger.error(f"❌ Migration {migration_name} failed: {str(e)}")
            failed_count += 1
            # Continue with other migrations even if one fails
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 Migration Summary:")
    logger.info(f"   ✅ Successful: {success_count}")
    logger.info(f"   ❌ Failed: {failed_count}")
    logger.info(f"   📋 Total: {len(migration_files)}")
    logger.info(f"{'='*60}")
    
    if failed_count > 0:
        logger.warning(f"⚠️  {failed_count} migration(s) failed, but continuing...")
    else:
        logger.info("✅ All migrations completed successfully!")

def init_database():
    """Initialize database if needed"""
    from config import Config
    from database.db_manager import DatabaseManager
    
    logger.info("🗄️  Initializing database schema...")
    
    try:
        db = DatabaseManager(Config.DATABASE_PATH)
        stats = db.get_stats()
        
        logger.info("✅ Database schema initialized")
        logger.info(f"📊 Current stats:")
        logger.info(f"   - Users: {stats['total_users']}")
        logger.info(f"   - Conversations: {stats['total_conversations']}")
        logger.info(f"   - Plans: {stats['total_plans']}")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # First initialize database schema
        init_database()
        
        # Then run all migrations
        run_migrations()
        
        logger.info("\n🎉 Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {str(e)}")
        sys.exit(1)
