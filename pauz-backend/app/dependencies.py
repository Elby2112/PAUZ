from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.services import jwt_service
from app.database import get_session
from app.models import User

bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                     db: Session = Depends(get_session)):

    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = jwt_service.verify_token(token, credentials_exception)

    user = db.exec(select(User).where(User.email == token_data.email)).first()

    if user is None:
        raise credentials_exception

    return user
