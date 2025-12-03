#!/usr/bin/env python3
"""
Debug Google OAuth flow
"""

import os
import requests
import json
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv

load_dotenv()

def test_oauth_config():
    """Test OAuth configuration"""
    
    print("🔐 OAuth Configuration Debug")
    print("=" * 35)
    
    # Check environment variables
    print("1. Environment Variables:")
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("REDIRECT_URI")
    
    print(f"   Client ID: {'✅ Set' if client_id else '❌ Missing'}")
    print(f"   Client Secret: {'✅ Set' if client_secret else '❌ Missing'}")
    print(f"   Redirect URI: {'✅ Set' if redirect_uri else '❌ Missing'}")
    print(f"   Redirect URI Value: {redirect_uri}")
    
    # Check client_secret.json
    print("\n2. client_secret.json:")
    try:
        with open('client_secret.json', 'r') as f:
            client_data = json.load(f)
            
        web_config = client_data.get('web', {})
        file_client_id = web_config.get('client_id')
        file_redirect_uri = web_config.get('redirect_uris', [])
        
        print(f"   File Client ID: {'✅ Matches' if file_client_id == client_id else '❌ Mismatch'}")
        print(f"   File Redirect URIs: {file_redirect_uri}")
        
        if redirect_uri in file_redirect_uri:
            print(f"   ✅ Redirect URI matches file")
        else:
            print(f"   ❌ Redirect URI not in file")
            
    except FileNotFoundError:
        print("   ❌ client_secret.json not found")
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")

def test_oauth_flow_start():
    """Test starting OAuth flow"""
    
    print("\n🚀 Testing OAuth Flow Start")
    print("=" * 35)
    
    try:
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid'],
            redirect_uri=os.getenv("REDIRECT_URI")
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        print("   ✅ OAuth flow initialized successfully")
        print(f"   Auth URL: {authorization_url[:100]}...")
        print(f"   State: {state}")
        
        return authorization_url, state
        
    except Exception as e:
        print(f"   ❌ OAuth flow initialization failed: {e}")
        return None, None

def test_callback_handling(code, state):
    """Test handling OAuth callback"""
    
    print(f"\n🔄 Testing Callback Handling")
    print("=" * 35)
    print(f"   Code length: {len(code) if code else 0}")
    print(f"   State: {state}")
    
    if not code or not state:
        print("   ❌ Missing code or state")
        return
    
    try:
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid'],
            redirect_uri=os.getenv("REDIRECT_URI")
        )
        
        print("   🔄 Fetching token...")
        flow.fetch_token(code=code)
        print("   ✅ Token received successfully")
        
        # Get user info
        from googleapiclient.discovery import build
        user_info_service = build('oauth2', 'v2', credentials=flow.credentials)
        user_info = user_info_service.userinfo().get().execute()
        
        print(f"   👤 User: {user_info.get('email')}")
        print("   ✅ OAuth callback handling successful")
        
        return user_info
        
    except Exception as e:
        print(f"   ❌ OAuth callback failed: {e}")
        return None

def check_google_console_settings():
    """Check what needs to be set in Google Console"""
    
    print("\n🌐 Google OAuth Console Requirements")
    print("=" * 40)
    
    print("In Google Cloud Console → APIs & Services → OAuth 2.0 Client IDs:")
    print()
    print("1. ✅ Authorized JavaScript origins:")
    print("   - http://localhost:5173")
    print("   - http://localhost:3000")
    print()
    print("2. ✅ Authorized redirect URIs:")
    print("   - http://localhost:5173/auth/callback")
    print("   - http://localhost:3000/auth/callback")
    print()
    print("3. ✅ Application type: Web application")
    print()
    print("4. ✅ Consent screen configured:")
    print("   - App name, logo, support email")
    print("   - Scopes: email, profile, openid")
    print()
    print("❌ Common Issues:")
    print("   - Redirect URI doesn't match exactly")
    print("   - Missing http:// or https://")
    print("   - Trailing slashes")
    print("   - Wrong port number")

def suggest_fix():
    """Suggest fixes for OAuth issues"""
    
    print("\n🔨 OAuth Fix Suggestions")
    print("=" * 28)
    
    print("Step 1: Check Google Console Settings")
    print("1. Go to Google Cloud Console")
    print("2. APIs & Services → OAuth 2.0 Client IDs")
    print("3. Edit your OAuth 2.0 Client ID")
    print("4. Add 'http://localhost:5173/auth/callback' to redirect URIs")
    print("5. Add 'http://localhost:5173' to JavaScript origins")
    
    print("\nStep 2: Clear Browser Data")
    print("1. Clear browser cache and cookies")
    print("2. Use incognito mode to test")
    print("3. Make sure no old OAuth state remains")
    
    print("\nStep 3: Test Fresh OAuth Flow")
    print("1. Start fresh login attempt")
    print("2. Complete Google consent quickly (code expires in 10 min)")
    print("3. Don't reuse authorization codes")
    
    print("\nStep 4: Check for Common Issues")
    print("1. Time synchronization between browser and Google")
    print("2. Network connectivity issues")
    print("3. Firewall blocking OAuth requests")

if __name__ == "__main__":
    print("🚀 Google OAuth Debug Tool")
    print("=" * 50)
    
    test_oauth_config()
    auth_url, state = test_oauth_flow_start()
    check_google_console_settings()
    suggest_fix()
    
    print("\n✅ OAuth Debug Complete!")
    print("Most likely issue: Redirect URI mismatch in Google Console")