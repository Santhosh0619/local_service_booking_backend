from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db

# We import schemas and models from the Users domain because Auth relies on them
from app.features.users.schemas import UserCreate, UserResponse

from app.features.auth.schemas import LoginRequest, Token
from app.features.auth.service import create_user_service, authenticate_user
from app.core.security import create_access_token

# Define the router so we can attach these endpoints to the main app
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user in the system.
    Returns 201 Created on success.
    Returns 400 Bad Request if the email is already in use.
    """
    # We pass the heavy lifting to the service layer.
    new_user = create_user_service(db=db, user_data=user_in)
    
    # FastAPI automatically filters the response using the UserResponse schema,
    # ensuring the hashed password is stripped out before sending to the browser.
    return new_user

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a JWT token.
    Accepts a standard JSON body payload.
    """
    # Check credentials
    user = authenticate_user(db, email=login_data.email, password=login_data.password)
    
    if not user:
        # Proper 401 Unauthorized error handling for bad credentials
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Generate the JWT token containing the user's email inside the payload ('sub' = subject)
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}
