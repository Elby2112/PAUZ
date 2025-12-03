import os
import httpx
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import json
import time
import logging
from datetime import datetime

from fastapi import HTTPException
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlmodel import Session, select
from starlette import status

from app.models import User
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../scripts'))

try:
    from mcp import put_object, get_object, delete_object
    print("✅ Using local MCP storage (mcp.py)")
except ImportError:
    # Fallback if mcp is not available
    put_object = None
    get_object = None  
    delete_object = None

load_dotenv()

# Configure detailed logging for OAuth
logging.basicConfig(level=logging.INFO)
oauth_logger = logging.getLogger('oauth_flow')

# OAuth configuration from environment variables
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email',
          'openid']

# Get Google OAuth credentials from environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

def create_client_secrets_dict():
    """Create client secrets dictionary from environment variables"""
    return {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [os.getenv("REDIRECT_URI", "http://localhost:5173/auth/callback")]
        }
    }


def get_google_auth_url():
    """Generate Google OAuth URL using environment variables"""
    start_time = time.time()
    
    oauth_logger.info("=" * 60)
    oauth_logger.info("🚀 OAUTH FLOW STARTED")
    oauth_logger.info(f"📅 Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Check environment variables
        redirect_uri = os.getenv("REDIRECT_URI")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        oauth_logger.info(f"🔗 Redirect URI: {redirect_uri}")
        oauth_logger.info(f"🔑 Client ID: {client_id[:20] if client_id else 'NOT SET'}...")
        oauth_logger.info(f"🔑 Client Secret: {'SET' if client_secret else 'NOT SET'}")
        
        if not redirect_uri:
            oauth_logger.error("❌ REDIRECT_URI not set in environment")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error: Missing redirect URI"
            )
        
        if not client_id or not client_secret:
            oauth_logger.error("❌ Google OAuth credentials not set in environment")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error: Missing Google OAuth credentials"
            )
        
        # Create flow from client secrets dictionary
        client_secrets = create_client_secrets_dict()
        flow = Flow.from_client_config(
            client_secrets,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Add this to force fresh consent
        )
        
        # Store state with timestamp for timing analysis
        oauth_state_data = {
            'state': state,
            'created_at': datetime.now().isoformat(),
            'redirect_uri': redirect_uri
        }
        
        oauth_logger.info(f"🔑 State generated: {state}")
        oauth_logger.info(f"🌐 Authorization URL: {authorization_url[:100]}...")
        oauth_logger.info(f"⏱️  OAuth URL generation took: {time.time() - start_time:.2f}s")
        
        return authorization_url, state
        
    except Exception as e:
        oauth_logger.error(f"❌ Failed to generate OAuth URL: {str(e)}")
        oauth_logger.error(f"⏱️  Failed after: {time.time() - start_time:.2f}s")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start OAuth flow: {str(e)}"
        )


def get_user_info_and_upsert(code: str, state: str, db: Session):
    """Complete OAuth flow with comprehensive logging and timing analysis"""
    start_time = time.time()
    
    oauth_logger.info("=" * 60)
    oauth_logger.info("🔄 OAUTH CALLBACK PROCESSING")
    oauth_logger.info(f"📅 Timestamp: {datetime.now().isoformat()}")
    oauth_logger.info(f"🔑 State: {state}")
    oauth_logger.info(f"📝 Code length: {len(code)} characters")
    oauth_logger.info(f"📝 Code prefix: {code[:20]}...")
    
    # Analyze code characteristics
    if len(code) < 20:
        oauth_logger.warning("⚠️  Authorization code seems too short")
    if len(code) > 200:
        oauth_logger.warning("⚠️  Authorization code seems unusually long")
    
    # Validate input parameters
    if not code or not state:
        oauth_logger.error("❌ Missing code or state parameter")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required OAuth parameters"
        )
    
    try:
        # Step 1: Initialize OAuth flow
        oauth_logger.info("📋 Step 1: Initializing OAuth flow...")
        step_start = time.time()
        
        redirect_uri = os.getenv("REDIRECT_URI")
        oauth_logger.info(f"🔗 Using redirect URI: {redirect_uri}")
        
        if not redirect_uri:
            oauth_logger.error("❌ REDIRECT_URI not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error: Missing redirect URI"
            )
        
        try:
            # Create flow from client secrets dictionary
            client_secrets = create_client_secrets_dict()
            flow = Flow.from_client_config(
                client_secrets,
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )
            oauth_logger.info(f"✅ OAuth flow initialized in {time.time() - step_start:.2f}s")
        except Exception as flow_init_error:
            oauth_logger.error(f"❌ Failed to initialize OAuth flow: {str(flow_init_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize OAuth: {str(flow_init_error)}"
            )

        # Step 2: Exchange code for token
        oauth_logger.info("📋 Step 2: Exchanging authorization code for access token...")
        step_start = time.time()
        
        try:
            # Add timeout and retry logic for token exchange
            flow.fetch_token(code=code, client_config={'timeout': 30})
            credentials = flow.credentials
            token_time = time.time() - step_start
            
            oauth_logger.info(f"✅ Token received from Google in {token_time:.2f}s")
            oauth_logger.info(f"🔑 Access token present: {'✅' if credentials.token else '❌'}")
            oauth_logger.info(f"🔄 Refresh token present: {'✅' if credentials.refresh_token else '❌'}")
            
            # Safely access token_expiry attribute
            token_expiry = getattr(credentials, 'token_expiry', None)
            if token_expiry:
                oauth_logger.info(f"⏰ Token expires in: {token_expiry}")
            else:
                oauth_logger.info("⏰ Token expiry information not available")
                
            # Validate credentials
            if not credentials or not credentials.token:
                oauth_logger.error("❌ Invalid credentials received from Google")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid credentials received from Google"
                )
            
        except Exception as token_error:
            error_time = time.time() - step_start
            error_detail = str(token_error)
            
            oauth_logger.error(f"❌ Token fetch failed after {error_time:.2f}s: {error_detail}")
            
            # Analyze specific error types
            if "invalid_grant" in error_detail:
                oauth_logger.error("🔍 DIAGNOSIS: Authorization code expired or already used")
                oauth_logger.error("💡 SOLUTION: User needs to start fresh login attempt")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Authorization code expired or already used. Please try logging in again."
                )
            elif "redirect_uri_mismatch" in error_detail:
                oauth_logger.error("🔍 DIAGNOSIS: Redirect URI mismatch between Google Console and backend")
                oauth_logger.error("💡 SOLUTION: Check Google OAuth Console settings")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Redirect URI mismatch. Check Google OAuth configuration."
                )
            elif "invalid_client" in error_detail:
                oauth_logger.error("🔍 DIAGNOSIS: Invalid client credentials")
                oauth_logger.error("💡 SOLUTION: Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Invalid OAuth client configuration."
                )
            elif "token_expiry" in error_detail:
                oauth_logger.error("🔍 DIAGNOSIS: Credentials object missing token_expiry attribute")
                oauth_logger.error("💡 SOLUTION: This is a known issue, continuing without expiry info")
                # Don't raise an exception for this specific issue, just log it
                pass
            else:
                oauth_logger.error(f"🔍 DIAGNOSIS: Unknown token exchange error")
                oauth_logger.error(f"💡 SOLUTION: Check network connectivity and Google API status")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Token exchange failed: {error_detail}"
                )

        # Step 3: Get user info from Google
        oauth_logger.info("📋 Step 3: Fetching user information from Google...")
        step_start = time.time()
        
        try:
            user_info_service = build('oauth2', 'v2', credentials=credentials)
            user_info = user_info_service.userinfo().get().execute()
            user_info_time = time.time() - step_start
            
            oauth_logger.info(f"✅ User info received in {user_info_time:.2f}s")
            oauth_logger.info(f"👤 User email: {user_info.get('email', 'NOT_FOUND')}")
            oauth_logger.info(f"👤 User name: {user_info.get('name', 'NOT_FOUND')}")
            oauth_logger.info(f"👤 User ID: {user_info.get('id', 'NOT_FOUND')}")
            oauth_logger.info(f"📷 Has picture: {'✅' if user_info.get('picture') else '❌'}")
            
        except Exception as user_info_error:
            user_info_time = time.time() - step_start
            oauth_logger.error(f"❌ Failed to get user info after {user_info_time:.2f}s: {str(user_info_error)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to retrieve user information: {str(user_info_error)}"
            )

        # Step 4: Extract user data
        user_id = user_info['id']
        email = user_info['email']
        name = user_info.get('name', 'User')
        picture = user_info.get('picture')
        
        # Modify picture URL to use a smaller size to avoid rate limiting
        if picture and '=s96-c' in picture:
            picture = picture.replace('=s96-c', '=s64-c')
            oauth_logger.info(f"🖼️ Modified picture URL to avoid rate limiting: s64-c size")
        
        oauth_logger.info("📋 Step 4: Processing user data in database...")
        step_start = time.time()

        # Step 5: Check if user exists
        oauth_logger.info(f"💾 Checking for existing user: {email}")
        
        db_user = db.exec(select(User).where(User.id == user_id)).first()

        if not db_user:
            # If not found by ID, try by email
            db_user = db.exec(select(User).where(User.email == email)).first()

            if db_user:
                oauth_logger.info(f"🔄 User found by email, updating Google ID: {email}")
                # Update existing user with Google ID
                db_user.id = user_id
                db_user.name = name
                db_user.picture = picture
            else:
                oauth_logger.info(f"🆕 Creating new user: {email}")
                db_user = User(
                    id=user_id,
                    email=email,
                    name=name,
                    picture=picture
                )
                db.add(db_user)
        else:
            oauth_logger.info(f"🔄 Updating existing user: {email}")
            # Update existing user details
            db_user.email = email
            db_user.name = name
            db_user.picture = picture

        # Step 6: Save user
        try:
            db.commit()
            db.refresh(db_user)
            db_time = time.time() - step_start
            
            oauth_logger.info(f"✅ User saved successfully in {db_time:.2f}s: {db_user.email}")
            
        except Exception as db_error:
            db_time = time.time() - step_start
            oauth_logger.error(f"❌ Database operation failed after {db_time:.2f}s: {str(db_error)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save user data: {str(db_error)}"
            )

        # Final timing summary
        total_time = time.time() - start_time
        oauth_logger.info("=" * 60)
        oauth_logger.info("🎉 OAUTH FLOW COMPLETED SUCCESSFULLY")
        oauth_logger.info(f"⏱️  Total time: {total_time:.2f}s")
        oauth_logger.info(f"👤 User: {db_user.email}")
        oauth_logger.info(f"🆔 User ID: {db_user.id}")
        
        # Performance warnings
        if total_time > 30:
            oauth_logger.warning("⚠️  OAuth flow took longer than 30 seconds - user may have experienced delays")
        elif total_time > 10:
            oauth_logger.warning("⚠️  OAuth flow took longer than 10 seconds - check network performance")
        
        oauth_logger.info("=" * 60)

        return db_user

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        total_time = time.time() - start_time
        oauth_logger.error(f"❌ OAuth Error after {total_time:.2f}s: {str(e)}")
        oauth_logger.error("🔍 DIAGNOSIS: Unexpected error in OAuth flow")
        oauth_logger.error("💡 SOLUTION: Check server logs and Google API status")
        
        try:
            db.rollback()
            oauth_logger.info("🔄 Database transaction rolled back")
        except:
            oauth_logger.warning("⚠️  Could not rollback database transaction")
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )