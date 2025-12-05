#!/usr/bin/env python3
"""
Debug profile picture handling in Google OAuth
"""

import os
import requests
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json

load_dotenv()

def test_google_user_info():
    """Test what user info we get from Google OAuth"""
    
    print("🔍 Testing Google OAuth User Info")
    print("=" * 40)
    
    # Check OAuth configuration
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("REDIRECT_URI")
    
    print(f"Client ID: {'✅ Set' if client_id else '❌ Missing'}")
    print(f"Client Secret: {'✅ Set' if client_secret else '❌ Missing'}")
    print(f"Redirect URI: {'✅ Set' if redirect_uri else '❌ Missing'}")
    print(f"Redirect URI Value: {redirect_uri}")
    
    if not all([client_id, client_secret, redirect_uri]):
        print("❌ Missing OAuth configuration")
        return
    
    print("\n🚀 To test with real Google OAuth:")
    print("1. Run this test with a real authorization code")
    print("2. Complete the OAuth flow manually")
    print("3. Check what user info we receive")
    
    # Show what we expect from Google
    print("\n📋 Expected Google User Info Fields:")
    print("✅ id: Google user ID")
    print("✅ email: User's email address")
    print("✅ name: User's full name")
    print("✅ picture: Profile picture URL")
    print("✅ given_name: First name")
    print("✅ family_name: Last name")
    print("✅ verified_email: Boolean")

def check_database_user_data():
    """Check what user data is stored in database"""
    
    print("\n💾 Checking Database User Data")
    print("=" * 35)
    
    try:
        import sqlite3
        from pathlib import Path
        
        # Find database file
        db_files = [Path('database.db')]  # Use main database first
        if not db_files:
            print("❌ No database file found")
            return
        
        db_file = db_files[0]
        print(f"📄 Using database: {db_file}")
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        """)
        
        if not cursor.fetchone():
            print("❌ Users table not found")
            conn.close()
            return
        
        # Get sample user data
        cursor.execute("""
            SELECT id, email, name, picture 
            FROM users 
            LIMIT 5
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("❌ No users found in database")
            conn.close()
            return
        
        print(f"📊 Found {len(users)} user(s) in database:")
        
        for user in users:
            user_id, email, name, picture = user
            print(f"\n👤 User: {email}")
            print(f"   Name: {name}")
            print(f"   ID: {user_id}")
            if picture:
                print(f"   Picture: ✅ {picture[:50]}...")
                # Test if picture URL is accessible
                try:
                    response = requests.head(picture, timeout=5)
                    if response.status_code == 200:
                        print(f"   Picture URL: ✅ Accessible")
                    else:
                        print(f"   Picture URL: ❌ Not accessible (HTTP {response.status_code})")
                except Exception as e:
                    print(f"   Picture URL: ❌ Error checking: {e}")
            else:
                print(f"   Picture: ❌ NULL/Empty")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

def test_profile_picture_url():
    """Test a typical Google profile picture URL"""
    
    print("\n🖼️  Testing Profile Picture URL Format")
    print("=" * 42)
    
    # Example Google profile picture URL format
    example_url = "https://lh3.googleusercontent.com/a-/AOh14Gjexample123456789=s96-c"
    
    print("📋 Google Profile Picture URL Format:")
    print("• Base: https://lh3.googleusercontent.com/a-/")
    print("• Followed by user-specific identifier")
    print("• Ends with size parameter (=s96-c for 96px)")
    print()
    
    print("🔍 Checking your database picture URLs...")
    
    # Check database for picture URLs
    try:
        import sqlite3
        from pathlib import Path
        
        db_files = [Path('database.db')]  # Use main database first
        if not db_files:
            return
        
        conn = sqlite3.connect(db_files[0])
        cursor = conn.cursor()
        
        cursor.execute("SELECT picture FROM users WHERE picture IS NOT NULL LIMIT 3")
        pictures = cursor.fetchall()
        
        for picture_tuple in pictures:
            picture_url = picture_tuple[0]
            print(f"\n🔗 URL: {picture_url}")
            
            # Check URL format
            if 'googleusercontent.com' in picture_url:
                print("   ✅ Valid Google URL format")
            else:
                print("   ⚠️  Unexpected URL format")
            
            # Check size parameter
            if '=s' in picture_url:
                size_part = picture_url.split('=s')[-1]
                print(f"   📏 Size parameter: s{size_part}")
            else:
                print("   ⚠️  No size parameter found")
            
            # Test accessibility
            try:
                response = requests.head(picture_url, timeout=5)
                print(f"   🌐 HTTP Status: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        print(f"   📷 Content Type: {content_type} ✅")
                    else:
                        print(f"   📷 Content Type: {content_type} ❌")
                        
                    # Check content length
                    content_length = response.headers.get('content-length')
                    if content_length:
                        print(f"   📦 Size: {content_length} bytes")
                else:
                    print(f"   ❌ URL not accessible")
                    
            except Exception as e:
                print(f"   ❌ Error testing URL: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing picture URLs: {e}")

def check_auth_endpoints():
    """Check what auth endpoints return"""
    
    print("\n🔗 Testing Auth Endpoints")
    print("=" * 32)
    
    base_url = "http://localhost:8000"
    
    # Test /auth/me endpoint (requires valid token)
    print("📋 To test /auth/me endpoint:")
    print("1. Get a valid JWT token from successful login")
    print("2. Make request with Authorization header")
    print("3. Check if picture field is included in response")
    
    example_curl = f'''curl -X GET "{base_url}/auth/me" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json"'''
    
    print(f"\n💻 Example command:")
    print(example_curl)
    
    print("\n📋 Expected response should include:")
    print('```json')
    print('{')
    print('  "id": "google_user_id",')
    print('  "email": "user@gmail.com",')
    print('  "name": "User Name",')
    print('  "picture": "https://lh3.googleusercontent.com/..."')
    print('}')
    print('```')

def suggest_fixes():
    """Suggest fixes for profile picture issues"""
    
    print("\n🔨 Profile Picture Fix Suggestions")
    print("=" * 38)
    
    print("🎯 Common Issues & Solutions:")
    print()
    
    print("1. ❌ Picture URL not stored in database:")
    print("   • Check if Google returns picture field")
    print("   • Verify auth_service.py saves picture field")
    print("   • Check User model has picture field")
    print()
    
    print("2. ❌ Picture URL stored but not accessible:")
    print("   • URL might be expired or invalid")
    print("   • Google might require authentication for access")
    print("   • URL might be blocked by CORS")
    print()
    
    print("3. ❌ Frontend not displaying picture:")
    print("   • Check if frontend reads picture field")
    print("   • Verify img src attribute is set correctly")
    print("   • Check browser console for errors")
    print()
    
    print("4. ❌ Picture URL format issues:")
    print("   • URL might be missing size parameter")
    print("   • URL might be truncated in database")
    print("   • Special characters might be encoded")
    print()
    
    print("🔧 Debug Steps:")
    print("1. Run this script to check database")
    print("2. Test picture URLs manually")
    print("3. Check browser network tab")
    print("4. Verify frontend code uses picture field")

if __name__ == "__main__":
    print("🖼️  Profile Picture Debug Tool")
    print("=" * 50)
    
    test_google_user_info()
    check_database_user_data()
    test_profile_picture_url()
    check_auth_endpoints()
    suggest_fixes()
    
    print("\n✅ Profile Picture Debug Complete!")
    print("Next: Check database results and test picture URLs")