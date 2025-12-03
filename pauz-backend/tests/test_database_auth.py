#!/usr/bin/env python3
"""
Test database authentication components
"""

import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    """Test if database is accessible"""
    print("🗄️  Testing database connection...")
    
    try:
        # Check if database file exists
        db_files = ['database.db', 'test.db', 'your_database.db']
        db_path = None
        
        for db_file in db_files:
            if os.path.exists(db_file):
                db_path = db_file
                break
        
        if db_path:
            print(f"   ✅ Database file found: {db_path}")
            
            # Test connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("   ✅ Users table exists")
                
                # Check table structure
                cursor.execute("PRAGMA table_info(users)")
                columns = cursor.fetchall()
                print("   📋 User table columns:")
                for col in columns:
                    print(f"     - {col[1]} ({col[2]})")
                
                # Count users
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                print(f"   👥 Total users: {user_count}")
                
                # Get recent users
                cursor.execute("SELECT id, email, name FROM users LIMIT 5")
                users = cursor.fetchall()
                if users:
                    print("   📝 Recent users:")
                    for user in users:
                        print(f"     - {user[1]} ({user[2]})")
                
                conn.close()
                return True
            else:
                print("   ❌ Users table not found")
                conn.close()
                return False
                
        else:
            print("   ⚠️  No database file found (will be created on first run)")
            return False
            
    except Exception as e:
        print(f"   ❌ Database connection error: {e}")
        return False

def test_jwt_configuration():
    """Test JWT configuration"""
    print("\n🔑 Testing JWT configuration...")
    
    try:
        from app.services.jwt_service import create_access_token, verify_token, TokenData
        from fastapi import HTTPException
        
        # Test token creation
        test_data = {"sub": "test@example.com"}
        token = create_access_token(test_data)
        print(f"   ✅ Token creation works")
        print(f"   🔑 Token length: {len(token)}")
        
        # Test token verification
        credentials_exception = HTTPException(status_code=401, detail="Invalid token")
        token_data = verify_token(token, credentials_exception)
        print(f"   ✅ Token verification works")
        print(f"   👤 Email extracted: {token_data.email}")
        
        # Test invalid token
        try:
            verify_token("invalid.token", credentials_exception)
            print("   ❌ Should reject invalid token")
            return False
        except HTTPException:
            print("   ✅ Correctly rejects invalid token")
        
        return True
        
    except Exception as e:
        print(f"   ❌ JWT configuration error: {e}")
        return False

def test_user_model():
    """Test User model"""
    print("\n👤 Testing User model...")
    
    try:
        from app.models import User
        
        # Test model creation
        test_user = User(
            id="test123",
            email="test@example.com", 
            name="Test User",
            picture="http://example.com/pic.jpg"
        )
        print("   ✅ User model creation works")
        
        # Test model attributes
        attrs = ['id', 'email', 'name', 'picture']
        for attr in attrs:
            if hasattr(test_user, attr):
                print(f"   ✅ Attribute '{attr}' exists")
            else:
                print(f"   ❌ Attribute '{attr}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ User model error: {e}")
        return False

def test_oauth_dependencies():
    """Test OAuth dependencies"""
    print("\n🔗 Testing OAuth dependencies...")
    
    dependencies = ['google_auth_oauthlib', 'googleapiclient', 'jose']
    all_good = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"   ✅ {dep} available")
        except ImportError:
            print(f"   ❌ {dep} missing")
            all_good = False
    
    return all_good

def main():
    """Run database authentication tests"""
    print("🗄️  Database Authentication Test")
    print("=" * 35)
    
    results = []
    results.append(("Database Connection", test_database_connection()))
    results.append(("JWT Configuration", test_jwt_configuration()))
    results.append(("User Model", test_user_model()))
    results.append(("OAuth Dependencies", test_oauth_dependencies()))
    
    # Summary
    print("\n📊 DATABASE AUTH SUMMARY")
    print("=" * 28)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nScore: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)