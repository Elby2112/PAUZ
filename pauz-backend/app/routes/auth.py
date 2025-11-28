from fastapi import APIRouter, Request, Depends, HTTPException, status # Re-added Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user
from app.models.user import User
from app.services import auth_service
from app.services.jwt_service import create_access_token

from pydantic import BaseModel

class TokenRequest(BaseModel):
    code: str
    state: str

class Token(BaseModel):
    access_token: str
    token_type: str


router = APIRouter()

@router.get("/login")
def login():
    authorization_url, state = auth_service.get_google_auth_url()
    return RedirectResponse(authorization_url)

@router.get("/callback")
def callback(request: Request, code: str, state: str, db: Session = Depends(get_session)):
    user = auth_service.get_user_info_and_upsert(code, state, db)
    
    access_token = create_access_token(data={"sub": user.email}) # Using user.email as sub for JWT
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user": {
            "email": user.email, 
            "name": user.name, 
            "picture": user.picture
        }
    }


@router.post("/token", response_model=Token)
def get_token(token_request: TokenRequest, db: Session = Depends(get_session)):
    user = auth_service.get_user_info_and_upsert(token_request.code, token_request.state, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
