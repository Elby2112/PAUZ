import os
import httpx
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import json

from fastapi import HTTPException
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlmodel import Session, select
from starlette import status

from app.models import User
from mcp import put_object, get_object, delete_object

load_dotenv()

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email',
          'openid']


def get_google_auth_url():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=os.getenv("REDIRECT_URI")
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # Add this to force fresh consent
    )
    return authorization_url, state


def get_user_info_and_upsert(code: str, state: str, db: Session):
    try:
        print(f"🔐 Starting Google OAuth - Code length: {len(code)}")

        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=os.getenv("REDIRECT_URI")
        )

        print("🔄 Fetching token from Google...")
        flow.fetch_token(code=code)
        credentials = flow.credentials
        print("✅ Token received from Google")

        # Get user info
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()
        print(f"👤 User info: {user_info.get('email')}")

        user_id = user_info['id']
        email = user_info['email']
        name = user_info.get('name', 'User')
        picture = user_info.get('picture')

        print("💾 Step 5: Checking if user exists...")

        # FIX: First try to find user by ID (Google ID)
        db_user = db.exec(select(User).where(User.id == user_id)).first()

        if not db_user:
            # If not found by ID, try by email
            db_user = db.exec(select(User).where(User.email == email)).first()

            if db_user:
                print(f"🔄 User found by email, updating Google ID: {email}")
                # Update existing user with Google ID
                db_user.id = user_id
                db_user.name = name
                db_user.picture = picture
            else:
                print(f"🆕 Creating new user: {email}")
                db_user = User(
                    id=user_id,
                    email=email,
                    name=name,
                    picture=picture
                )
                db.add(db_user)
        else:
            print(f"🔄 Updating existing user: {email}")
            # Update existing user details
            db_user.email = email
            db_user.name = name
            db_user.picture = picture

        db.commit()
        db.refresh(db_user)
        print(f"✅ Step 6: User saved successfully: {db_user.email}")

        return db_user

    except Exception as e:
        print(f"❌ OAuth Error: {str(e)}")
        db.rollback()  # Important: rollback on error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )