import bcrypt
import jwt
from datetime import datetime, timedelta 
from fastapi import Depends, HTTPException, status # Depends is FastAPI’s way of saying: “Run this helper function before the route is called.”
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # gives you a standard way to extract the token from a request's Authorization header
from jwt import PyJWTError, decode 
from sqlalchemy.orm import Session
from app import models, database
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# loading this from .env
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


def hash_password(plain_password: str) -> str: 
    """
    .encode("utf-8") : converts the user entered password to bytes as bcrypt only works with bytes. 
    .gensalt() : creates a unique salt (random data) that ensures even if two users choose the same password, their hashes will be different.
    .hashpw() : Runs the password + salt through the bcrypt algorithm to produce a hashed version.
    .decode("utf-8") : Converts the hashed bytes back into a string so we can store it in a database.

    """
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# This function checks if the entered password (during login) matches the stored, hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    It encodes the plain text password (from login input) to bytes 
    Encodes the stored hashed password (from the DB) to bytes
    Then bcrypt.checkpw() compares them internally using the same hashing algorithm and salt used when the password was first created
    
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# creating a token using encode from jwt
def create_access_token(data: dict, expires_delta: int = 30):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes = expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

# This defines how FastAPI will look for the JWT in the request
oauth2_scheme = HTTPBearer()

# Depends(oauth2_scheme): automatically extracts the Bearer token from the header.
def get_current_user(
        # Uses the oauth2_scheme to extract the Bearer token from the Authorization header of the request.
        # So, credentials will have credentials.scheme: should be 'Bearer' & credentials.credentials: the actual JWT token
        credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
        # Automatically call the get_db() function and pass the result (a database session) into this function.
        # This will get you make db an object that lets you query your database using SQLAlchemy.
        db: Session = Depends(database.get_db)):
    try:
        token = credentials.credentials
        payload = decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_email = payload.get("sub")
        if user_email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = db.query(models.User).filter(models.User.email == user_email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )