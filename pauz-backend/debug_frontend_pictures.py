#!/usr/bin/env python3
"""
Test if the /auth/me endpoint returns picture data correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_me_endpoint():
    """Test the /auth/me endpoint to see if it returns picture data"""
    
    print("🔍 Testing /auth/me Endpoint")
    print("=" * 35)
    
    print("📋 To test the /auth/me endpoint:")
    print("1. Sign in through your app")
    print("2. Open browser DevTools (F12)")
    print("3. Go to Application > Local Storage")
    print("4. Copy the value of 'pauz_token'")
    print("5. Run: curl -X GET 'http://localhost:8000/auth/me' -H 'Authorization: Bearer YOUR_TOKEN'")
    print()
    
    # Check what the endpoint should return
    print("📋 Expected response from /auth/me should include:")
    print('```json')
    print('{')
    print('  "id": "google_user_id",')
    print('  "email": "user@gmail.com",')
    print('  "name": "User Name",')
    print('  "picture": "https://lh3.googleusercontent.com/..."')
    print('}')
    print('```')

def check_database_vs_api():
    """Compare database data with what API returns"""
    
    print("\n💾 Database vs API Comparison")
    print("=" * 38)
    
    try:
        import sqlite3
        from pathlib import Path
        
        # Check database for picture data
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT email, name, picture 
            FROM users 
            WHERE picture IS NOT NULL 
            LIMIT 1
        """)
        
        user = cursor.fetchone()
        
        if user:
            email, name, picture = user
            print("📊 Database User Data:")
            print(f"   Email: {email}")
            print(f"   Name: {name}")
            print(f"   Picture: {picture[:50] if picture else 'NULL'}...")
            
            if picture:
                print(f"   ✅ Picture stored in database")
            else:
                print(f"   ❌ No picture in database")
        else:
            print("❌ No users with pictures found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

def suggest_frontend_debug():
    """Suggest frontend debugging steps"""
    
    print("\n🎨 Frontend Debugging Steps")
    print("=" * 32)
    
    print("📋 Check your localStorage:")
    print("1. Open browser DevTools (F12)")
    print("2. Go to Application > Local Storage")
    print("3. Check 'pauz_user' item")
    print("4. Verify it contains 'picture' field")
    print()
    
    print("🔍 Browser Console Debug:")
    print("```javascript")
    print("// Check user data in localStorage")
    print("const userData = JSON.parse(localStorage.getItem('pauz_user'));")
    print("console.log('User data:', userData);")
    print("console.log('Picture URL:', userData?.picture);")
    print()
    print("// Test picture URL")
    print("if (userData?.picture) {")
    print("  const img = new Image();")
    print("  img.onload = () => console.log('✅ Picture loads');")
    print("  img.onerror = () => console.log('❌ Picture failed');")
    print("  img.src = userData.picture;")
    print("}")
    print("```")
    print()
    
    print("🌐 Network Tab Debug:")
    print("1. Open DevTools Network tab")
    print("2. Filter by 'auth' requests")
    print("3. Check /auth/me response")
    print("4. Verify picture field is present")
    print()
    
    print("🖼️  Image Loading Debug:")
    print("1. Right-click on profile picture")
    print("2. Select 'Inspect Element'")
    print("3. Check img src attribute")
    print("4. Look for CORS errors in console")

def check_common_issues():
    """Check for common profile picture issues"""
    
    print("\n🔧 Common Profile Picture Issues")
    print("=" * 38)
    
    print("❌ Issue 1: CORS Policy")
    print("   • Google images might block cross-origin requests")
    print("   • Solution: You're already using crossOrigin='anonymous'")
    print("   • Alternative: Use a proxy or different image service")
    print()
    
    print("❌ Issue 2: Browser Caching")
    print("   • Old/invalid picture URL might be cached")
    print("   • Solution: Clear browser cache")
    print("   • Alternative: Add timestamp to URL")
    print()
    
    print("❌ Issue 3: Privacy Settings")
    print("   • Some Google accounts restrict profile picture access")
    print("   • Solution: Check Google account privacy settings")
    print("   • Alternative: Use a default picture for restricted accounts")
    print()
    
    print("❌ Issue 4: Network Issues")
    print("   • Firewall or ad-blocker might block Google CDN")
    print("   • Solution: Disable ad-blocker temporarily")
    print("   • Alternative: Use VPN or different network")

def analyze_your_code():
    """Analyze the frontend code you provided"""
    
    print("\n📝 Your Code Analysis")
    print("=" * 28)
    
    print("✅ What's Good:")
    print("• Both components read user.picture from localStorage")
    print("• Fallback to profileIcon when picture fails")
    print("• Error handling with onError handlers")
    print("• crossOrigin='anonymous' attribute set")
    print("• Image preloading logic in Navbar")
    print()
    
    print("🔍 Potential Issues:")
    print()
    
    print("1. 🔄 Data Flow Issue:")
    print("   • localStorage.getItem('pauz_user') must contain picture field")
    print("   • Check if GoogleCallback.js saves picture to localStorage")
    print("   • Verify timing of when pauz_user is set vs when components load")
    print()
    
    print("2. 🖼️  Image Loading Timing:")
    print("   • Multiple image loading states might conflict")
    print("   • setImageLoaded used in multiple places")
    print("   • Preloading logic might override error handling")
    print()
    
    print("3. 💾 localStorage Consistency:")
    print("   • Multiple storage listeners and intervals")
    print("   • Potential race conditions in data loading")
    print("   • Storage updates might not trigger re-renders")
    print()
    
    print("🎯 Quick Debug Steps:")
    print("1. Add console.log to see what's in pauz_user")
    print("2. Check if picture URL is valid when loaded")
    print("3. Test with a hardcoded Google picture URL")
    print("4. Check browser console for CORS errors")

if __name__ == "__main__":
    print("🖼️  Profile Picture Frontend Debug Tool")
    print("=" * 50)
    
    test_auth_me_endpoint()
    check_database_vs_api()
    suggest_frontend_debug()
    check_common_issues()
    analyze_your_code()
    
    print("\n✅ Frontend Debug Complete!")
    print("🎯 Next Steps:")
    print("1. Check localStorage for 'pauz_user' data")
    print("2. Test picture URL manually in browser")
    print("3. Check browser console for CORS errors")
    print("4. Verify GoogleCallback saves picture to localStorage")