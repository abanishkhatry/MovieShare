from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# while registering a new user
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str 

# information user have to fill while logging in
class UserLogin(BaseModel):
    email: EmailStr
    password: str     

# helps to set up the user profile, and send these info to the frontend
class UserProfileOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str]
    bio: Optional[str]
    favorite_genre: Optional[str]
    created_at: Optional[str]
    avatar_url : Optional[str]

    class Config:
        orm_mode = True

# helps in updating user's profile. 
class UserProfileUpdate(BaseModel):
    name: Optional[str]
    bio: Optional[str]
    favorite_genre: Optional[str]

# information user have to fill for posting
class PostBase(BaseModel):
    title: str
    content: str   
    visibility : str = "public" 

# inherits from PostBase and helps to create a post
class PostCreate(PostBase):
    pass    

# this is used in returning a receipt to the frontend/client that the server saved/created the post
class PostOut(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    like_count : int
    visibility : str 

    class Config:
        #  allows Pydantic to work directly with SQLAlchemy objects
        orm_mode = True

# structure to write comment for the user
class CommentBase(BaseModel): 
    content : str
# creates a comment when user submits the CommentBase
class CommentCreate(CommentBase): 
     pass 
# For sending comment data to the frontend/server
class CommentOut(CommentBase): 
    id : int 
    created_at : datetime
    post_id : int
    user_id : int 

    class Config : 
        orm_mode = True     


class NotificationOut(BaseModel):
    id: int
    user_id: int
    post_id: int
    type: str
    seen: bool
    created_at: datetime

    class Config:
        orm_mode = True