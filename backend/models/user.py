from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class User(BaseModel):
    username: str
    email: str
    password: str
    contact: str
    created_at: Optional[datetime] = datetime.utcnow()
    
class UserProfile(BaseModel):
    username: str
    email: str
    contact: str
    
class EditUsername(BaseModel):
    username: str

# Request model by updating username
class UpdateUsernameRequest(BaseModel):
    username: str
    
class EditEmail(BaseModel):
    email: str   
    
# Define the request model
class UpdateEmailRequest(BaseModel):
    email: str 
    
# Request model for updating password
class UpdatePasswordRequest(BaseModel):
    password: str
    
# Request body model for updating contact
class UpdateContactRequest(BaseModel):
    contact: str

# Model to handle incoming ID token
class Authorised(BaseModel):
    idToken: str  # Expecting the ID token in the request


#Forget Password, reset Password
class PasswordResetRequest(BaseModel):
    email: EmailStr


    

