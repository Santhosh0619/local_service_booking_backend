from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.features.users.models import User
from app.features.users.schemas import UserCreate
from app.core.security import get_password_hash, verify_password

def create_user_service(db: Session, user_data: UserCreate):
    """Business logic to register a new user."""
    
    # 1. Check if email already exists in the database
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        # We throw a proper 400 Bad Request error if it exists!
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2. Hash the password before saving it
    hashed_password = get_password_hash(user_data.password)
    
    # 3. Create the SQLAlchemy Database object
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password, # Notice we are saving the HASH, not the raw password!
        role=user_data.role,
        services=user_data.services,
        address=user_data.address,
        pincode=user_data.pincode,
        phone_number=user_data.phone_number
    )
    
    # 4. Save it to MySQL
    db.add(new_user)
    db.commit()        # Actually execute the save
    db.refresh(new_user) # Pull the fresh data back from MySQL (so we get the new auto-increment ID)
    
    return new_user

def authenticate_user(db: Session, email: str, password: str):
    """Business logic to verify login credentials."""
    
    # 1. Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None # User doesn't exist
    
    # 2. Verify the password hash using passlib
    if not verify_password(password, user.password):
        return None # Wrong password
        
    return user # Success!
