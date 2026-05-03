from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import PyJWTError

from app.db.session import get_db
from app.config import settings
from app.features.users.models import User

# This tool automatically looks for the "Authorization: Bearer <token>" header in incoming requests.
# The 'tokenUrl' is just for the Swagger UI so it knows where to send the login request.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """
    A FastAPI Dependency that protects routes.
    It decodes the JWT token, extracts the email, and returns the User object.
    Throws 401 Unauthorized if the token is invalid, expired, or missing.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode the token using our SECRET_KEY
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # 2. Extract the "subject" (which we set to the user's email during login)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except PyJWTError:
        # If the token is expired or forged by a hacker, PyJWT automatically throws an error
        raise credentials_exception
        
    # 3. Look up the user in the database to make sure they still exist
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user
