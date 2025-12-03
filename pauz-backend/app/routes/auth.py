from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session
import time
import logging

from app.database import get_session
from app.dependencies import get_current_user
from app.models import User
from app.services import auth_service
from app.services.jwt_service import create_access_token

from pydantic import BaseModel

# Configure auth route logging
auth_logger = logging.getLogger('auth_routes')


class TokenRequest(BaseModel):
    code: str
    state: str


class Token(BaseModel):
    access_token: str
    token_type: str


router = APIRouter()


@router.get("/login")
def login():
    """Initiate OAuth login with timing and logging"""
    start_time = time.time()
    
    try:
        auth_logger.info("🚀 Login endpoint accessed")
        
        authorization_url, state = auth_service.get_google_auth_url()
        
        timing = time.time() - start_time
        auth_logger.info(f"✅ Login redirect prepared in {timing:.2f}s")
        auth_logger.info(f"🔀 Redirecting to Google OAuth with state: {state}")
        
        return RedirectResponse(authorization_url)
        
    except Exception as e:
        timing = time.time() - start_time
        auth_logger.error(f"❌ Login endpoint failed after {timing:.2f}s: {str(e)}")
        
        # For login failures, we can't redirect to frontend with error
        # because we don't have a valid OAuth state yet
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth login: {str(e)}"
        )


@router.get("/callback")
def callback(request: Request, code: str, state: str, db: Session = Depends(get_session)):
    """Handle OAuth callback with comprehensive logging"""
    start_time = time.time()
    
    auth_logger.info("=" * 50)
    auth_logger.info("🔄 OAUTH CALLBACK RECEIVED")
    auth_logger.info(f"📅 Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    auth_logger.info(f"🌐 Client IP: {request.client.host if request.client else 'unknown'}")
    auth_logger.info(f"🔑 State: {state}")
    auth_logger.info(f"📝 Code received: {'✅' if code else '❌'}")
    auth_logger.info(f"📝 Code length: {len(code) if code else 0}")
    
    # Validate required parameters
    if not code:
        auth_logger.error("❌ No authorization code received")
        return redirect_with_error("No authorization code received")
    
    if not state:
        auth_logger.error("❌ No state parameter received")
        return redirect_with_error("Invalid OAuth state")
    
    try:
        auth_logger.info("🔄 Processing OAuth callback...")
        
        user = auth_service.get_user_info_and_upsert(code, state, db)
        
        if not user:
            auth_logger.error("❌ No user returned from OAuth processing")
            return redirect_with_error("Failed to authenticate user")

        # Step 3: Create JWT token
        auth_logger.info("🔑 Creating JWT token...")
        token_start = time.time()
        
        try:
            access_token = create_access_token(data={"sub": user.email})
            token_time = time.time() - token_start
            
            auth_logger.info(f"✅ JWT token created in {token_time:.2f}s")
            auth_logger.info(f"🔑 Token length: {len(access_token)}")
            auth_logger.info(f"👤 Token for user: {user.email}")
            
        except Exception as token_error:
            token_time = time.time() - token_start
            auth_logger.error(f"❌ JWT token creation failed after {token_time:.2f}s: {str(token_error)}")
            return redirect_with_error(f"Token creation failed: {str(token_error)}")

        # Step 4: Redirect to frontend with token
        auth_logger.info("🔀 Preparing frontend redirect...")
        frontend_url = "http://localhost:5173/auth/callback"
        redirect_url = f"{frontend_url}?token={access_token}&email={user.email}&name={user.name}"
        
        total_time = time.time() - start_time
        auth_logger.info(f"✅ OAuth callback completed in {total_time:.2f}s")
        auth_logger.info(f"🔀 Redirecting to frontend: {frontend_url}")
        auth_logger.info(f"👤 User authenticated: {user.email}")
        auth_logger.info("=" * 50)
        
        return RedirectResponse(redirect_url)
        
    except HTTPException as http_error:
        total_time = time.time() - start_time
        auth_logger.error(f"❌ HTTP exception in callback after {total_time:.2f}s: {http_error.detail}")
        return redirect_with_error(http_error.detail)
        
    except Exception as e:
        total_time = time.time() - start_time
        auth_logger.error(f"❌ Unexpected error in callback after {total_time:.2f}s: {str(e)}")
        return redirect_with_error(f"Authentication failed: {str(e)}")

def redirect_with_error(error_message: str):
    """Helper function to redirect to frontend with error message"""
    auth_logger.info(f"🔀 Redirecting to frontend with error: {error_message}")
    frontend_url = "http://localhost:5173/auth/callback"
    redirect_url = f"{frontend_url}?error={error_message}"
    return RedirectResponse(redirect_url)


@router.post("/token", response_model=Token)
def get_token(token_request: TokenRequest, db: Session = Depends(get_session)):
    """Token endpoint for programmatic token exchange"""
    start_time = time.time()
    
    auth_logger.info("=" * 40)
    auth_logger.info("🔄 TOKEN ENDPOINT ACCESSED")
    auth_logger.info(f"📅 Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    auth_logger.info(f"📝 Code provided: {'✅' if token_request.code else '❌'}")
    auth_logger.info(f"📝 Code length: {len(token_request.code) if token_request.code else 0}")
    auth_logger.info(f"🔑 State: {token_request.state}")
    
    if not token_request.code or not token_request.state:
        auth_logger.error("❌ Missing code or state in token request")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both code and state are required"
        )
    
    try:
        auth_logger.info("🔄 Processing token request...")
        
        user = auth_service.get_user_info_and_upsert(token_request.code, token_request.state, db)

        if not user:
            auth_logger.error("❌ No user returned from OAuth processing")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        auth_logger.info("🔑 Creating access token...")
        token_start = time.time()
        
        try:
            access_token = create_access_token(data={"sub": user.email})
            token_time = time.time() - token_start
            
            auth_logger.info(f"✅ Access token created in {token_time:.2f}s")
            
        except Exception as token_error:
            token_time = time.time() - token_start
            auth_logger.error(f"❌ Access token creation failed after {token_time:.2f}s: {str(token_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token creation failed: {str(token_error)}"
            )

        total_time = time.time() - start_time
        auth_logger.info(f"✅ Token request completed in {total_time:.2f}s")
        auth_logger.info(f"👤 Token issued for: {user.email}")
        auth_logger.info("=" * 40)
        
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        total_time = time.time() - start_time
        auth_logger.error(f"❌ Unexpected error in /token endpoint after {total_time:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

