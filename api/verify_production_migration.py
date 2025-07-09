#!/usr/bin/env python3
"""
Script to verify that the production migration worked correctly.
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def verify_production_migration():
    """Verify that all tables were created correctly in production database."""
    
    # Set up environment variables for production
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:root@localhost:5432/xhub")
    os.environ.setdefault("SECRET_KEY", "test-secret")
    os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
    
    try:
        # Import configuration after setting env vars
        from core.config import get_settings
        
        settings = get_settings()
        database_url = settings.get_database_url()
        
        print("🔧 Verifying production database migration...")
        print(f"Connecting to database: {database_url}")
        
        engine = create_async_engine(database_url)
        
        # Check tables
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = result.fetchall()
            
            print(f"\n✅ Found {len(tables)} tables in production database:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Check alembic version
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            print(f"\n✅ Alembic version: {version}")
            
            # Check all expected tables exist
            expected_tables = [
                # Core tables
                'users', 'posts', 'categories', 'tags', 'comments', 'media',
                # Social interaction tables
                'likes', 'follows', 'bookmarks', 'views', 'user_likes', 
                'user_bookmarks', 'comment_likes', 'user_follows', 'user_topics',
                'user_preferences', 'user_reads',
                # Junction tables
                'post_tags',
                # Admin audit tables
                'user_management_logs', 'content_approvals', 'system_operations',
                'access_audit_log', 'settings'
            ]
            
            table_names = [table[0] for table in tables]
            missing_tables = [table for table in expected_tables if table not in table_names]
            
            if missing_tables:
                print(f"\n❌ Missing expected tables: {missing_tables}")
                return False
            else:
                print(f"\n✅ All {len(expected_tables)} expected tables are present!")
                
                # Check some table structures
                print("\n🔍 Checking table structures:")
                
                # Check users table
                result = await conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    ORDER BY ordinal_position
                """))
                user_columns = result.fetchall()
                print(f"  - users table has {len(user_columns)} columns")
                
                # Check posts table
                result = await conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'posts' 
                    ORDER BY ordinal_position
                """))
                post_columns = result.fetchall()
                print(f"  - posts table has {len(post_columns)} columns")
                
                # Check admin audit tables
                result = await conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'user_management_logs' 
                    ORDER BY ordinal_position
                """))
                audit_columns = result.fetchall()
                print(f"  - user_management_logs table has {len(audit_columns)} columns")
                
                return True
                
    except Exception as e:
        print(f"❌ Production migration verification failed: {e}")
        return False

async def main():
    """Main function."""
    success = await verify_production_migration()
    
    if success:
        print("\n🎉 Production migration verification completed successfully!")
        print("✅ Your CraftyXhub database is ready for use!")
    else:
        print("\n❌ Production migration verification failed!")
        
    return success

if __name__ == "__main__":
    asyncio.run(main()) 