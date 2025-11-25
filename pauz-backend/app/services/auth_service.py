import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlmodel import Session, select
from app.models.user import User
from app.database import get_session
from fastapi import Depends

load_dotenv()

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid']

def get_google_auth_url():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=os.getenv("REDIRECT_URI")
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return authorization_url, state

def get_user_info_and_upsert(code: str, state: str, db: Session = Depends(get_session)):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=os.getenv("REDIRECT_URI")
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials

    user_info_service = build('oauth2', 'v2', credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()

    user_id = user_info['id']
    email = user_info['email']
    name = user_info.get('name', '')
    picture = user_info.get('picture')

    # Check if user exists in our database
    db_user = db.exec(select(User).where(User.id == user_id)).first()

    if not db_user:
        # Create new user
        db_user = User(
            id=user_id,
            email=email,
            name=name,
            picture=picture
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    else:
        # Update existing user's details if necessary
        db_user.email = email
        db_user.name = name
        db_user.picture = picture
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return db_user