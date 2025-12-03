#!/usr/bin/env python3
"""
Debug CORS issues and provide comprehensive fix
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_cors_endpoints():
    """Test CORS endpoints comprehensively"""
    
    print("🧪 CORS Debug Test")
    print("=" * 30)
    
    # Test different endpoints
    endpoints = [
        "/stats/overview",
        "/stats/journals/total", 
        "/stats/free_journals/total",
        "/stats/guided_journals/total",
        "/stats/garden/total"
    ]
    
    for endpoint in endpoints:
        print(f"\n📍 Testing {endpoint}")
        print("-" * 20)
        
        # Test OPTIONS preflight
        print("1. OPTIONS Preflight:")
        try:
            response = requests.options(
                f"{BASE_URL}{endpoint}",
                headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Content-Type, Authorization"
                }
            )
            
            print(f"   Status: {response.status_code}")
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
                'Access-Control-Max-Age': response.headers.get('Access-Control-Max-Age')
            }
            
            for header, value in cors_headers.items():
                if value:
                    print(f"   ✅ {header}: {value}")
                else:
                    print(f"   ❌ {header}: Missing")
                    
        except Exception as e:
            print(f"   ❌ OPTIONS Error: {e}")
        
        # Test GET with Origin header (simulates browser)
        print("\n2. GET with Origin:")
        try:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers={
                    "Origin": "http://localhost:5173",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"   Status: {response.status_code}")
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
                'Vary': response.headers.get('Vary')
            }
            
            for header, value in cors_headers.items():
                if value:
                    print(f"   ✅ {header}: {value}")
                else:
                    print(f"   ❌ {header}: Missing")
                    
            print(f"   Body: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"   ❌ GET Error: {e}")

def check_cors_config():
    """Check current CORS configuration"""
    
    print("\n🔧 CORS Configuration Check")
    print("=" * 35)
    
    try:
        with open('app/main.py', 'r') as f:
            content = f.read()
            
        print("1. CORS Middleware Import:")
        if 'from fastapi.middleware.cors import CORSMiddleware' in content:
            print("   ✅ CORSMiddleware imported")
        else:
            print("   ❌ CORSMiddleware import missing")
        
        print("\n2. CORS Middleware Setup:")
        if 'app.add_middleware(' in content and 'CORSMiddleware' in content:
            print("   ✅ Middleware added")
        else:
            print("   ❌ Middleware not configured")
        
        print("\n3. Allowed Origins:")
        import re
        origins_match = re.search(r'origins\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if origins_match:
            origins_text = origins_match.group(1)
            print(f"   Found origins: {origins_text}")
            if 'localhost:5173' in origins_text:
                print("   ✅ localhost:5173 allowed")
            else:
                print("   ❌ localhost:5173 not in allowed origins")
        else:
            print("   ❌ Origins configuration not found")
        
        print("\n4. CORS Settings:")
        if 'allow_credentials=True' in content:
            print("   ✅ Credentials allowed")
        else:
            print("   ❌ Credentials not allowed")
            
        if 'allow_methods=["*"]' in content:
            print("   ✅ All methods allowed")
        else:
            print("   ⚠️  Methods might be restricted")
            
        if 'allow_headers=["*"]' in content:
            print("   ✅ All headers allowed")
        else:
            print("   ⚠️  Headers might be restricted")
        
    except Exception as e:
        print(f"   ❌ Could not check CORS config: {e}")

def suggest_cors_fix():
    """Suggest CORS fixes"""
    
    print("\n🔨 CORS Fix Suggestion")
    print("=" * 25)
    
    fix_code = '''
# In app/main.py, update the CORS middleware section:

from fastapi.middleware.cors import CORSMiddleware

# More permissive CORS configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose all headers to browser
)
'''
    
    print("Add or replace the CORS middleware in app/main.py:")
    print(fix_code)
    
    print("\n🧪 After fixing CORS:")
    print("1. Restart the backend server")
    print("2. Clear browser cache (Ctrl+Shift+R)")
    print("3. Test the Profile page again")
    print("4. Check browser DevTools Network tab")

def check_browser_cache_issue():
    """Check if browser cache might be the issue"""
    
    print("\n🌐 Browser Cache Issues")
    print("=" * 25)
    
    print("Common causes of CORS errors with correct backend setup:")
    print()
    print("1. ❌ Browser caching old CORS headers")
    print("   Fix: Clear cache or use Incognito/Private mode")
    print()
    print("2. ❌ Extension interfering with requests")
    print("   Fix: Disable extensions temporarily")
    print()
    print("3. ❌ Service Worker caching old responses")
    print("   Fix: Clear service workers in DevTools")
    print()
    print("4. ❌ Frontend sending wrong Origin header")
    print("   Fix: Check API_BASE_URL in frontend")
    print()
    print("5. ❌ Backend not restarted after CORS changes")
    print("   Fix: Restart backend server")

if __name__ == "__main__":
    print("🚀 CORS Debug Tool")
    print("=" * 50)
    
    check_cors_config()
    test_cors_endpoints()
    suggest_cors_fix()
    check_browser_cache_issue()
    
    print("\n✅ Debug Complete!")
    print("If CORS is configured correctly but you still get errors,")
    print("the issue is likely browser cache or frontend configuration.")