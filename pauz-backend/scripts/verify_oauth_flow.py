#!/usr/bin/env python3
"""
Complete OAuth flow verification tool
"""

import requests
import json
import time
import webbrowser
from urllib.parse import urlparse, parse_qs
import threading

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def manual_oauth_flow_test():
    """Guide user through manual OAuth flow testing"""
    
    print("🔄 Manual OAuth Flow Test")
    print("=" * 35)
    
    print("This test will help you identify where token retrieval fails.")
    print("Follow these steps carefully:")
    print()
    
    # Step 1: Get OAuth URL
    print("📋 Step 1: Getting OAuth URL...")
    try:
        response = requests.get(f"{BASE_URL}/auth/login", allow_redirects=False)
        if response.status_code == 307:
            auth_url = response.headers.get('Location')
            print(f"✅ OAuth URL obtained")
            print(f"   {auth_url}")
            print()
            return auth_url
        else:
            print(f"❌ Failed to get OAuth URL: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_callback_with_sample_code():
    """Test callback endpoint behavior"""
    
    print("📋 Step 2: Testing Callback Behavior...")
    print("The callback endpoint should:")
    print("1. Receive authorization code from Google")
    print("2. Exchange it for access token")
    print("3. Get user info from Google")
    print("4. Create JWT token")
    print("5. Redirect to frontend with token")
    print()
    
    # Test with invalid code to see error handling
    print("Testing callback with invalid code...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/callback",
            params={"code": "invalid_test_code", "state": "test_state"},
            allow_redirects=False
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code in [302, 307]:
            redirect = response.headers.get('Location', '')
            if 'error=' in redirect:
                error = parse_qs(urlparse(redirect).query).get('error', [''])[0]
                print(f"✅ Correctly handles error: {error}")
            else:
                print(f"Redirect: {redirect[:100]}...")
        else:
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error testing callback: {e}")

def check_google_oauth_settings():
    """Provide guidance on Google OAuth settings"""
    
    print("\n🌐 Google OAuth Settings Verification")
    print("=" * 45)
    
    print("Go to Google Cloud Console: https://console.cloud.google.com/")
    print()
    print("Navigate to: APIs & Services → OAuth 2.0 Client IDs")
    print()
    print("Check these settings:")
    print()
    print("1. 📱 Application Type:")
    print("   ✅ Web application")
    print()
    print("2. 🔗 Authorized JavaScript origins:")
    print("   ✅ http://localhost:5173")
    print("   ✅ http://localhost:3000 (if needed)")
    print()
    print("3. 🎯 Authorized redirect URIs:")
    print("   ✅ http://localhost:5173/auth/callback")
    print("   ✅ http://localhost:3000/auth/callback (if needed)")
    print()
    print("4. 📄 Consent Screen:")
    print("   ✅ App name configured")
    print("   ✅ User support email set")
    print("   ✅ Scopes: email, profile, openid")
    print()
    print("⚠️  Common Issues:")
    print("   • Missing http:// prefix")
    print("   • Wrong port number")
    print("   • Trailing slashes")
    print("   • HTTP vs HTTPS mismatch")

def analyze_common_failures():
    """Analyze common OAuth failure points"""
    
    print("\n🔍 Common Token Retrieval Failures")
    print("=" * 40)
    
    print("Based on our tests, here are the most likely issues:")
    print()
    
    print("1. ⏰ TIMING ISSUES:")
    print("   • Authorization codes expire in 10 minutes")
    print("   • User takes too long to complete consent")
    print("   • Network delays during OAuth flow")
    print()
    
    print("2. 🔄 REDIRECT URI ISSUES:")
    print("   • Google Console doesn't match backend exactly")
    print("   • Check for trailing slashes")
    print("   • HTTP vs HTTPS mismatch")
    print()
    
    print("3. 🍎 BROWSER ISSUES:")
    print("   • Safari blocking third-party cookies")
    print("   • Pop-up blockers interfering")
    print("   • Cached OAuth state")
    print()
    
    print("4. 🔐 GOOGLE ACCOUNT ISSUES:")
    print("   • Account disabled or restricted")
    print("   • 2FA requirements")
    print("   • API quota exceeded")
    print()
    
    print("5. 🌐 NETWORK ISSUES:")
    print("   • Firewall blocking Google requests")
    print("   • DNS resolution problems")
    print("   • SSL/TLS certificate issues")

def provide_troubleshooting_steps():
    """Provide step-by-step troubleshooting"""
    
    print("\n🔧 Troubleshooting Steps")
    print("=" * 30)
    
    print("Step 1: Clear Browser Data")
    print("   • Clear cache and cookies for localhost:5173")
    print("   • Try incognito/private mode")
    print("   • Disable extensions temporarily")
    print()
    
    print("Step 2: Verify Google Console Settings")
    print("   • Double-check redirect URIs")
    print("   • Ensure JavaScript origins match")
    print("   • Test with both HTTP and HTTPS if needed")
    print()
    
    print("Step 3: Check Server Logs")
    print("   • Watch terminal where uvicorn is running")
    print("   • Look for OAuth-related errors")
    print("   • Check for token creation logs")
    print()
    
    print("Step 4: Test Fresh OAuth Flow")
    print("   • Start completely fresh login")
    print("   • Complete Google consent quickly")
    print("   • Don't reuse old authorization codes")
    print()
    
    print("Step 5: Check Browser Console")
    print("   • Open DevTools (F12)")
    print("   • Check Console tab for errors")
    print("   • Monitor Network tab for requests")
    print()
    
    print("Step 6: Verify Token Storage")
    print("   • After successful login, check localStorage")
    print("   • Look for 'pauz_token' key")
    print("   • Verify token value looks like JWT (xxxx.yyyy.zzzz)")

def create_debug_script():
    """Create a script to debug live OAuth flow"""
    
    debug_script = '''
// Browser Console Debug Script
// Copy and paste this into browser console during OAuth flow

console.log("🔍 OAuth Debug Mode Activated");

// Monitor localStorage changes
const originalSetItem = localStorage.setItem;
localStorage.setItem = function(key, value) {
    if (key === 'pauz_token') {
        console.log("✅ Token stored:", value.substring(0, 20) + "...");
        console.log("📅 Token length:", value.length);
        console.log("🕐 Time:", new Date().toISOString());
    }
    if (key === 'pauz_user') {
        console.log("✅ User data stored:", JSON.parse(value));
    }
    return originalSetItem.apply(this, arguments);
};

// Monitor network requests
const originalFetch = window.fetch;
window.fetch = function(url, options) {
    if (url.includes('/auth/') || url.includes('/stats/')) {
        console.log("🌐 Request:", url, options?.method);
        return originalFetch.apply(this, arguments).then(response => {
            console.log("📬 Response:", response.status, response.statusText);
            return response;
        });
    }
    return originalFetch.apply(this, arguments);
};

console.log("📊 Monitoring OAuth flow... Check for token storage messages.");
'''
    
    print("\n📝 Browser Debug Script")
    print("=" * 28)
    print("Copy this script into browser console during OAuth flow:")
    print()
    print(debug_script)

if __name__ == "__main__":
    print("🚀 Complete OAuth Flow Verification")
    print("=" * 50)
    
    # Run tests
    auth_url = manual_oauth_flow_test()
    test_callback_with_sample_code()
    
    # Provide guidance
    check_google_oauth_settings()
    analyze_common_failures()
    provide_troubleshooting_steps()
    create_debug_script()
    
    print("\n✅ Verification Complete!")
    print()
    print("🎯 Most Likely Issue: Authorization code timing or redirect URI mismatch")
    print("📋 Next Steps: Follow the troubleshooting steps above")
    
    if auth_url:
        print()
        print("🔄 To test manually:")
        print(f"1. Visit: {auth_url}")
        print("2. Complete Google consent quickly (within 5 minutes)")
        print("3. Check if you're redirected back with token")
        print("4. Check browser localStorage for 'pauz_token'")