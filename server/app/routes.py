from fastapi import APIRouter, HTTPException, Depends 
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.auth import hash_password,verify_password, create_access_token, get_current_user 
from app.models import UserAuth


router = APIRouter()
# Temporary in-memory "database"
users_db = {}

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

@router.post("/api/signup")
def signup(payload: SignupRequest):
    if payload.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(payload.password)

    new_user = UserAuth(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed,
        created_at=datetime.utcnow()
    )

    users_db[payload.email] = new_user
    return {"message": "User created successfully"}


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


@router.get("/api/status")
def status():
    return {"status": "Backend is running"}

