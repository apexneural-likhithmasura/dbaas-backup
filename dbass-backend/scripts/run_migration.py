#!/usr/bin/env python3
"""
Database Migration Script

This script creates the users table for the authentication system.
Run this script to set up the database schema.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.database import db_manager
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_migration():
    """Run the database migration to create users table"""
    
    try:
        logger.info("Starting database migration...")
        logger.info(f"Database: {settings.db_host}:{settings.db_port}/{settings.db_name}")
        logger.info(f"Schema: {settings.db_schema}")
        
        # Read the SQL migration file
        migration_file = Path(__file__).parent / "create_users_table.sql"
        
        if not migration_file.exists():
            logger.error(f"Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r') as f:
            sql_script = f.read()
        
        logger.info("Executing SQL migration script...")
        
        # Execute the migration
        with db_manager.get_cursor() as cursor:
            cursor.execute(sql_script)
            logger.info("Migration script executed successfully")
        
        # Verify table creation
        logger.info("Verifying table creation...")
        with db_manager.get_cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = %s 
                    AND table_name = 'users'
                )
            """, (settings.db_schema,))
            result = cursor.fetchone()
            table_exists = result['exists'] if result else False
            
            if table_exists:
                logger.info("✅ Users table created successfully!")
                
                # Get table info
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_schema = %s 
                    AND table_name = 'users'
                    ORDER BY ordinal_position
                """, (settings.db_schema,))
                columns = cursor.fetchall()
                
                logger.info("Table structure:")
                for col in columns:
                    logger.info(f"  - {col['column_name']}: {col['data_type']} {'(nullable)' if col['is_nullable'] == 'YES' else '(not null)'}")
                
                return True
            else:
                logger.error("❌ Users table was not created")
                return False
                
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False


def check_connection():
    """Check database connection before migration"""
    
    try:
        logger.info("Checking database connection...")
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT 1")
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False


def main():
    """Main function"""
    
    print("=" * 60)
    print("  DATABASE MIGRATION - AUTHENTICATION SYSTEM")
    print("=" * 60)
    
    # Check connection first
    if not check_connection():
        print("\n❌ Cannot proceed with migration. Please check your database configuration.")
        sys.exit(1)
    
    # Run migration
    if run_migration():
        print("\n✅ Migration completed successfully!")
        print("\nYou can now use the authentication endpoints:")
        print("  - POST /dbas/api/auth/signup")
        print("  - POST /dbas/api/auth/login")
        print("  - GET /dbas/api/auth/user/{user_id}")
        print("  - GET /dbas/api/auth/health/check")
    else:
        print("\n❌ Migration failed. Please check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
