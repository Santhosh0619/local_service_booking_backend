import enum
from sqlalchemy import Column, Integer, String, Enum, JSON
from app.db.base import Base

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    PROVIDER = "provider"

class ServiceType(str, enum.Enum):
    PLUMBER = "plumber"
    ELECTRICIAN = "electrician"
    CARPENTER = "carpenter"
    MAID = "maid"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False) # Will store the hashed string
    role = Column(Enum(UserRole), nullable=False)
    
    # Store the list of services as a JSON array (e.g., ["plumber", "maid"])
    # This will be NULL for customers, but populated for providers
    services = Column(JSON, nullable=True) 
    
    address = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    pincode = Column(String(20), nullable=False)
