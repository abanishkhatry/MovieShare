from pydantic import BaseModel, EmailStr
from datetime import datetime

# while registering a new user
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str 

# information user have to fill while logging in
class UserLogin(BaseModel):
    email: EmailStr
    password: str     

# information user have to fill for posting
class PostBase(BaseModel):
    title: str
    content: str    

# inherits from PostBase and helps to create a post
class PostCreate(PostBase):
    pass    

# this is used in returning a receipt to the frontend/client that the server saved/created the post
class PostOut(PostBase):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        #  allows Pydantic to work directly with SQLAlchemy objects
        orm_mode = True
