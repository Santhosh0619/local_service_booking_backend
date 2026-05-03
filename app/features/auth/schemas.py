from pydantic import BaseModel, EmailStr

# We use this schema to format the JWT token response when a user logs in successfully.
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# We use this custom JSON schema for login so modern frontends 
# (like React/Flutter) can easily send login data without dealing with Form Data.
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
