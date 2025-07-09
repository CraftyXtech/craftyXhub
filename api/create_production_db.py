#!/usr/bin/env python3
"""
Script to create the production xhub database.
"""
import asyncio
import asyncpg

async def create_production_database():
    """Create the xhub database for production."""
    
    # Connect to the default postgres database first
    try:
        conn = await asyncpg.connect(
            host='localhost',
            user='postgres',
            password='root',
            database='postgres'
        )
        
        # Check if database exists
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'xhub'"
        )
        
        if result:
            print("✅ Database 'xhub' already exists")
        else:
            # Create the database
            await conn.execute("CREATE DATABASE xhub")
            print("✅ Database 'xhub' created successfully")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

async def main():
    """Main function."""
    print("🔧 Setting up production xhub database...")
    
    success = await create_production_database()
    
    if success:
        print("\n✅ Production database setup completed!")
    else:
        print("\n❌ Production database setup failed!")
        
    return success

if __name__ == "__main__":
    asyncio.run(main()) 