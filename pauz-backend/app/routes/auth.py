from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from app.services import auth_service
from app.services.jwt_service import create_access_token
from app.database import get_session
from app.models.user import User

router = APIRouter()

@router.get("/login")
def login():
    authorization_url, state = auth_service.get_google_auth_url()
    return RedirectResponse(authorization_url)

@router.get("/callback")
def callback(request: Request, code: str, state: str, db: Session = Depends(get_session)):
    user = auth_service.get_user_info_and_upsert(code, state, db)
    
    access_token = create_access_token(data={"sub": user.email}) # Using user.email as sub for JWT
    return {"access_token": access_token, "token_type": "bearer"}
