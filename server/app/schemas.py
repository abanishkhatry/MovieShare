from pydantic import BaseModel, EmailStr

# while registering a new user
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str 

# information user have to fill while logging in
class UserLogin(BaseModel):
    email: EmailStr
    password: str     