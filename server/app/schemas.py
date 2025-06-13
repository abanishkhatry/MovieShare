from pydantic import BaseModel, EmailStr
from datetime import datetime

# seeking informations that are only required for login/authentication
class UserAuth(BaseModel): 
    username: str
    email: EmailStr
    hashed_password: str 
    created_at: datetime 


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str 