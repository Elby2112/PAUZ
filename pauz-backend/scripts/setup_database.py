#!/usr/bin/env python3
"""
Setup script for PAUZ Journaling App Database
Initializes database with migrations and sample data
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from scripts.migrate import DatabaseMigrator
from app.database_enhanced import create_db_and_tables
from app.models import User

load_dotenv()

def setup_database():
    """Complete database setup process"""
    print("🚀 Starting PAUZ Journaling Database Setup")
    print("=" * 50)
    
    # Step 1: Check environment
    print("\n📋 Step 1: Checking Environment")
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print(f"✅ DATABASE_URL found: {db_url.split('@')[-1] if '@' in db_url else 'SQLite'}")
    else:
        print("⚠️ No DATABASE_URL found, using SQLite")
    
    # Step 2: Run migrations
    print("\n📋 Step 2: Running Database Migrations")
    try:
        migrator = DatabaseMigrator()
        if migrator.migrate():
            print("✅ Migrations completed successfully")
        else:
            print("❌ Migrations failed")
            return False
    except Exception as e:
        print(f"❌ Migration error: {e}")
        print("💡 Make sure your database server is running")
        return False
    
    # Step 3: Create tables (fallback)
    print("\n📋 Step 3: Ensuring Tables Exist")
    try:
        engine = create_db_and_tables()
        print("✅ Database tables verified")
    except Exception as e:
        print(f"❌ Table creation error: {e}")
        return False
    
    # Step 4: Create admin user (if needed)
    print("\n📋 Step 4: Setting Up Default Data")
    try:
        from app.database import get_session
        
        # Check if admin user exists
        for session in get_session():
            existing_user = session.exec(
                "SELECT id FROM users WHERE email = 'admin@pauz.app'"
            ).first()
            
            if not existing_user:
                admin_user = User(
                    id="admin-system",
                    email="admin@pauz.app", 
                    name="PAUZ System",
                    picture=None
                )
                session.add(admin_user)
                session.commit()
                print("✅ Admin user created")
            else:
                print("✅ Admin user already exists")
            break  # Only need first session
    
    except Exception as e:
        print(f"⚠️ Admin user setup failed (non-critical): {e}")
    
    # Step 5: Show status
    print("\n📋 Step 5: Database Status")
    migrator.status()
    
    print("\n🎉 Database Setup Complete!")
    print("=" * 50)
    print("✅ Your PAUZ database is ready for use!")
    print("💡 You can now start the application with:")
    print("   uvicorn app.main:app --reload")
    
    return True

def reset_database():
    """Reset database (development only)"""
    if os.getenv("ENVIRONMENT") == "production":
        print("❌ Cannot reset database in production!")
        return False
    
    print("🔄 Resetting development database...")
    
    try:
        # For SQLite, just delete the file
        db_url = os.getenv("DATABASE_URL", "sqlite:///./database.db")
        if db_url.startswith("sqlite"):
            db_file = db_url.replace("sqlite:///", "")
            if os.path.exists(db_file):
                os.remove(db_file)
                print("✅ SQLite database deleted")
        
        # Reset migrations table
        migrator = DatabaseMigrator()
        if migrator.connection:
            with migrator.connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS schema_migrations")
                migrator.connection.commit()
                print("✅ Migration history reset")
        
        # Run setup again
        return setup_database()
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PAUZ Database Setup")
    parser.add_argument("--reset", action="store_true", help="Reset database (development only)")
    
    args = parser.parse_args()
    
    try:
        if args.reset:
            success = reset_database()
        else:
            success = setup_database()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)