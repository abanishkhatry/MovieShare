from fastapi import APIRouter, HTTPException, Depends, status 
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.auth import hash_password,verify_password, create_access_token, get_current_user 
from app.schemas import UserAuth, UserCreate 
from passlib.context import CryptContext
from sqlalchemy.orm import Session 
from app import models
from app.database import get_db 


# Creates a new router that can be included in your main app
router = APIRouter()
# Sets up bcrypt (industry-standard) as your password hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Temporary in-memory "database"
users_db = {}

# class SignupRequest(BaseModel):
#     username: str
#     email: EmailStr
#     password: str

# @router.post("/api/signup")
# def signup(payload: SignupRequest):
#     if payload.email in users_db:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     hashed = hash_password(payload.password)

#     new_user = UserAuth(
#         username=payload.username,
#         email=payload.email,
#         hashed_password=hashed,
#         created_at=datetime.utcnow()
#     )

#     users_db[payload.email] = new_user
#     return {"message": "User created successfully"}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/api/login")
def login(payload: LoginRequest):
    user = users_db.get(payload.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}



@router.get("/api/me")
def read_current_user(user_email: str = Depends(get_current_user)):
    user = users_db.get(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully!"}

@router.get("/api/status")
def status():
    return {"status": "Backend is running"}

