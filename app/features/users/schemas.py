from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.features.users.models import UserRole, ServiceType

# Schema for checking the data coming IN (e.g. from registration form)
class UserCreate(BaseModel):
    name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: UserRole
    address: str
    pincode: str
    phone_number: Optional[str] = None
    services: Optional[List[ServiceType]] = None

    # This is a custom validator to enforce our complex business rules!
    @field_validator('services')
    @classmethod
    def validate_services(cls, v, info):
        # We use info.data to see what role they selected
        role = info.data.get('role')
        if role == UserRole.PROVIDER and not v:
            raise ValueError('Providers must specify at least one service they provide')
        if role == UserRole.CUSTOMER and v is not None:
            raise ValueError('Customers cannot register with services')
        return v

# Schema for the data going OUT (e.g. responding after successful login)
# Notice how we DO NOT include the password here! 
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    address: str
    pincode: str
    phone_number: Optional[str] = None
    services: Optional[List[ServiceType]] = None

    class Config:
        from_attributes = True # This tells Pydantic it's okay to read data from a SQLAlchemy model
