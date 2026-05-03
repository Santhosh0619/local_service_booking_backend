from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from app.config import settings

# 1. Setup the BCrypt hashing context
# This tells PassLib to use the 'bcrypt' algorithm to securely hash passwords.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Takes the plain text password from the login form and compares it 
    safely to the hashed password in the database.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Takes a plain text password and runs it through bcrypt to generate 
    a secure, irreversible hash string.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """
    Takes user data (like their email), adds an expiration time, 
    and signs it securely using our SECRET_KEY to create a JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # We use PyJWT to actually create the token string
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
